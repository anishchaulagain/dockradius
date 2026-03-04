"""
DockRadius Analyze Route.
POST /analyze — orchestrates parsing, graph building, Mermaid generation, and LLM analysis.
"""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import (
    CommandRequest,
    AnalyzeResponse,
    ErrorResponse,
)
from app.services.parser import (
    parse_command,
    DockerParserError,
    UnsupportedCommandError,
    SUPPORTED_COMMANDS,
)
from app.services.graph_builder import build_graph
from app.services.mermaid_generator import generate_mermaid
from app.services.llm_service import analyze_with_llm

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or unsupported command"},
    },
    summary="Analyze a Docker command",
    description="Parses a Docker CLI command, generates an infrastructure diagram, and provides AI-powered risk analysis.",
)
async def analyze_command(request: CommandRequest):
    """
    Main analysis endpoint.

    Pipeline:
    1. Parse Docker CLI command → ParsedCommand
    2. Build infrastructure graph → GraphModel
    3. Generate Mermaid diagram → string
    4. LLM risk analysis → AnalysisResult
    5. Return combined response
    """
    logger.info(f"Analyzing command: {request.command[:100]}")

    # Step 1: Parse
    try:
        parsed = parse_command(request.command)
    except UnsupportedCommandError as e:
        logger.warning(f"Unsupported command: {e}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error=str(e),
                supported_commands=SUPPORTED_COMMANDS,
            ).model_dump(),
        )
    except DockerParserError as e:
        logger.warning(f"Parser error: {e}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error=str(e),
                supported_commands=SUPPORTED_COMMANDS,
            ).model_dump(),
        )

    # Step 2: Build graph
    graph = build_graph(parsed)

    # Step 3: Generate Mermaid diagram
    mermaid_diagram = generate_mermaid(graph)

    # Step 4: LLM analysis
    try:
        analysis = analyze_with_llm(parsed)
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Analysis service temporarily unavailable",
        )

    # Step 5: Return combined response
    return AnalyzeResponse(
        mermaid=mermaid_diagram,
        analysis=analysis,
    )
