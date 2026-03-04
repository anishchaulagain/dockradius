"""
DockRadius Pydantic Models.
Defines all request/response schemas and internal data structures.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ─── Request Models ───────────────────────────────────────────────

class CommandRequest(BaseModel):
    """Input schema for the /analyze endpoint."""
    command: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Docker CLI command to analyze",
        examples=["docker run -p 80:80 nginx"],
    )


# ─── Internal Models ──────────────────────────────────────────────

class ParsedCommand(BaseModel):
    """Structured representation of a parsed Docker command."""
    base_command: str = Field(..., description="e.g. 'run', 'build', 'exec'")
    image: Optional[str] = None
    container_name: Optional[str] = None
    ports: list[str] = Field(default_factory=list)
    volumes: list[str] = Field(default_factory=list)
    network: Optional[str] = None
    environment: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    extra_args: list[str] = Field(default_factory=list)
    raw_command: str = ""


class GraphNode(BaseModel):
    """A node in the infrastructure graph."""
    id: str
    label: str
    node_type: str = Field(
        ...,
        description="Type: container, image, port, volume, network, host, command",
    )


class GraphEdge(BaseModel):
    """An edge connecting two graph nodes."""
    source: str
    target: str
    label: str = ""


class GraphModel(BaseModel):
    """Internal infrastructure graph representation."""
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


# ─── LLM Response Models ─────────────────────────────────────────

class AnalysisResult(BaseModel):
    """Validated structure for LLM analysis output."""
    simple_explanation: str = Field(
        default="", description="Plain-language explanation of what the command does"
    )
    technical_explanation: str = Field(
        default="", description="Detailed technical breakdown"
    )
    infrastructure_impact: list[str] = Field(
        default_factory=list, description="List of infrastructure side-effects"
    )
    risk_level: str = Field(
        default="low", description="Risk level: low, medium, or high"
    )
    risk_reasons: list[str] = Field(
        default_factory=list, description="Reasons for the assigned risk level"
    )
    common_mistakes: list[str] = Field(
        default_factory=list, description="Common mistakes when using this command"
    )
    blast_radius_summary: str = Field(
        default="", description="Summary of the blast radius"
    )


# ─── API Response Models ─────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    """Final response from the /analyze endpoint."""
    mermaid: str = Field(..., description="Mermaid diagram string")
    analysis: AnalysisResult


class ErrorResponse(BaseModel):
    """Structured error response."""
    error: str
    supported_commands: list[str] = Field(default_factory=list)
