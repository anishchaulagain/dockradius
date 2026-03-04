"""
DockRadius LLM Service.
Sends parsed Docker command data to Groq's Llama 3.3 70B for risk analysis.
LLM is used ONLY for explanation and risk analysis — never for diagram generation.
"""

import json
import logging
from typing import Optional

from groq import Groq

from app.config import get_settings
from app.models.schemas import ParsedCommand, AnalysisResult

settings = get_settings()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are DockRadius AI — a DevOps risk analysis assistant.

You receive a parsed Docker command in JSON format. Your job is to analyze it and return a structured JSON response.

You MUST respond with valid JSON only (no markdown, no explanation outside JSON).

Response schema:
{
  "simple_explanation": "Plain-language explanation of what this command does",
  "technical_explanation": "Detailed technical breakdown of the command behavior",
  "infrastructure_impact": ["List of infrastructure side effects"],
  "risk_level": "low | medium | high",
  "risk_reasons": ["List of reasons for the risk level"],
  "common_mistakes": ["Common mistakes when using this command"],
  "blast_radius_summary": "Summary of what could be affected if something goes wrong"
}

Rules:
- Be precise and technical.
- risk_level must be exactly one of: "low", "medium", "high".
- infrastructure_impact, risk_reasons, and common_mistakes must be arrays of strings.
- Do not generate Mermaid diagrams.
- Do not suggest running any commands.
- Focus on static analysis only.
"""


def analyze_with_llm(parsed: ParsedCommand) -> AnalysisResult:
    """
    Send parsed command to Groq LLM for risk analysis.

    Args:
        parsed: Structured parsed Docker command.

    Returns:
        Validated AnalysisResult from LLM.
    """
    settings = get_settings()

    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        logger.warning("GROQ_API_KEY not configured — returning fallback analysis")
        return _fallback_analysis(parsed)

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        user_message = json.dumps(parsed.model_dump(), indent=2)

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content
        if not raw_content:
            logger.error("LLM returned empty response")
            return _fallback_analysis(parsed)

        # Sanitize and parse JSON
        data = json.loads(raw_content)

        # Validate risk_level
        if data.get("risk_level") not in ("low", "medium", "high"):
            data["risk_level"] = "medium"

        return AnalysisResult(**data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        return _fallback_analysis(parsed)
    except Exception as e:
        logger.error(f"LLM service error: {e}")
        return _fallback_analysis(parsed)


def _fallback_analysis(parsed: ParsedCommand) -> AnalysisResult:
    """Generate a basic deterministic analysis when LLM is unavailable."""
    cmd = parsed.base_command

    risk_map = {
        "run": "medium",
        "build": "low",
        "exec": "high",
        "stop": "medium",
        "rm": "high",
        "network create": "low",
        "volume create": "low",
    }

    explanations = {
        "run": f"Creates and starts a new container from the '{parsed.image or 'specified'}' image.",
        "build": f"Builds a Docker image tagged as '{parsed.image or 'untagged'}'.",
        "exec": f"Executes a command inside the running container '{parsed.container_name or 'specified'}'.",
        "stop": f"Stops the running container '{parsed.container_name or 'specified'}'.",
        "rm": f"Removes the container '{parsed.container_name or 'specified'}' permanently.",
        "network create": f"Creates a new Docker network '{parsed.network or 'specified'}'.",
        "volume create": f"Creates a new Docker volume for persistent data storage.",
    }

    impacts = {
        "run": ["New container instance created", "Port bindings may conflict with existing services"]
            + ([f"Port(s) {', '.join(parsed.ports)} exposed on host"] if parsed.ports else [])
            + ([f"Volume(s) mounted: {', '.join(parsed.volumes)}"] if parsed.volumes else []),
        "build": ["Disk space used for image layers", "Build cache may be utilized"],
        "exec": ["Commands executed inside container environment", "May modify container state"],
        "stop": ["Container processes will be terminated", "Network connections will be dropped"],
        "rm": ["Container and its writable layer will be deleted", "Data not in volumes will be lost"],
        "network create": ["New network namespace created", "Available for container attachment"],
        "volume create": ["Persistent storage volume allocated on host"],
    }

    return AnalysisResult(
        simple_explanation=explanations.get(cmd, f"Executes docker {cmd} command."),
        technical_explanation=f"The 'docker {cmd}' command was parsed with the following parameters: {parsed.model_dump_json()}",
        infrastructure_impact=impacts.get(cmd, [f"Executes docker {cmd}"]),
        risk_level=risk_map.get(cmd, "medium"),
        risk_reasons=[f"Command type '{cmd}' has inherent operational implications"],
        common_mistakes=[f"Running 'docker {cmd}' without understanding the full impact"],
        blast_radius_summary=f"Affects the Docker daemon and any resources referenced by this {cmd} command.",
    )


def suggest_correction(command: str, error: str) -> Optional[str]:
    """
    Uses the LLM to suggest a corrected version of an invalid Docker command.
    """
    if not settings.GROQ_API_KEY:
        return None

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        prompt = f"""
        You are a Docker CLI expert. A user entered an invalid Docker command.
        Command: {command}
        Error: {error}

        Task: Provide ONLY the corrected Docker command string that achieves what the user likely intended, but with valid syntax and flags. 
        If the command is fundamentally unsalvageable, return "null".
        Do not include any explanation or markdown formatting. Just the command string.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that corrects Docker CLI commands."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=100,
        )

        suggestion = response.choices[0].message.content.strip()
        if suggestion.lower() == "null" or not suggestion.startswith("docker"):
            return None
            
        # Clean up any quotes or backticks if LLM didn't follow instructions perfectly
        suggestion = suggestion.strip("`'\"")
        return suggestion

    except Exception as e:
        logger.error(f"Failed to suggest correction: {e}")
        return None
