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
from app.services.llm_service import analyze_with_llm, suggest_correction

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    # ... (rest of metadata stays same)
)
async def analyze_command(request: CommandRequest):
    # ... (Step 1 start)
    try:
        parsed = parse_command(request.command)
    except UnsupportedCommandError as e:
        logger.warning(f"Unsupported command: {e}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error=str(e),
                command=request.command,
                supported_commands=SUPPORTED_COMMANDS,
            ).model_dump(),
        )
    except DockerParserError as e:
        logger.warning(f"Parser error: {e}")
        
        # New Suggestion Logic
        suggestion = None
        try:
            suggestion = suggest_correction(request.command, str(e))
        except Exception as suggest_err:
            logger.error(f"Suggestion failed: {suggest_err}")

        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error=str(e),
                command=request.command,
                suggestion=suggestion,
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
