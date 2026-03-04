"""
DockRadius Mermaid Generator.
Converts GraphModel into Mermaid diagram strings using template logic.
Deterministic and safe — no LLM involvement.
"""

import logging
from app.models.schemas import GraphModel

logger = logging.getLogger(__name__)

# ─── Node Shape Templates by Type ────────────────────────────────
# Mermaid shapes: round ((...)), stadium ([...]), hex {{}}, rect [...], etc.
_NODE_SHAPES: dict[str, tuple[str, str]] = {
    "host":      ("[[", "]]"),     # Subroutine shape
    "container": ("[",  "]"),      # Rectangle
    "image":     ("([", "])"),     # Stadium
    "port":      ("{{", "}}"),    # Hexagon
    "volume":    ("[(", ")]"),     # Cylinder
    "network":   ("((", "))"),    # Circle
    "command":   (">",  "]"),      # Asymmetric
}

# ─── Style Classes by Node Type ──────────────────────────────────
_STYLE_CLASSES: dict[str, str] = {
    "host":      "hostStyle",
    "container": "containerStyle",
    "image":     "imageStyle",
    "port":      "portStyle",
    "volume":    "volumeStyle",
    "network":   "networkStyle",
    "command":   "commandStyle",
}


def generate_mermaid(graph: GraphModel) -> str:
    """
    Convert a GraphModel into a Mermaid diagram string.

    Args:
        graph: Infrastructure graph with nodes and edges.

    Returns:
        Mermaid diagram string ready for rendering.
    """
    if not graph.nodes:
        return "graph TD\n    empty[No infrastructure to visualize]"

    lines: list[str] = ["graph TD"]

    # Add node definitions
    for node in graph.nodes:
        open_delim, close_delim = _NODE_SHAPES.get(node.node_type, ("[", "]"))
        safe_label = _sanitize_label(node.label)
        lines.append(f"    {node.id}{open_delim}\"{safe_label}\"{close_delim}")

    lines.append("")

    # Add edges
    for edge in graph.edges:
        if edge.label:
            safe_label = _sanitize_label(edge.label)
            lines.append(f"    {edge.source} -->|\"{safe_label}\"| {edge.target}")
        else:
            lines.append(f"    {edge.source} --> {edge.target}")

    lines.append("")

    # Add style class definitions
    lines.append("    classDef hostStyle fill:#1e293b,stroke:#64748b,stroke-width:2px,color:#e2e8f0")
    lines.append("    classDef containerStyle fill:#0f766e,stroke:#14b8a6,stroke-width:2px,color:#f0fdfa")
    lines.append("    classDef imageStyle fill:#1d4ed8,stroke:#60a5fa,stroke-width:2px,color:#eff6ff")
    lines.append("    classDef portStyle fill:#b45309,stroke:#fbbf24,stroke-width:2px,color:#fffbeb")
    lines.append("    classDef volumeStyle fill:#7e22ce,stroke:#a78bfa,stroke-width:2px,color:#f5f3ff")
    lines.append("    classDef networkStyle fill:#be123c,stroke:#fb7185,stroke-width:2px,color:#fff1f2")
    lines.append("    classDef commandStyle fill:#374151,stroke:#9ca3af,stroke-width:2px,color:#f9fafb")

    lines.append("")

    # Apply styles to nodes
    for node in graph.nodes:
        style_class = _STYLE_CLASSES.get(node.node_type)
        if style_class:
            lines.append(f"    class {node.id} {style_class}")

    return "\n".join(lines)


def _sanitize_label(label: str) -> str:
    """Sanitize label for Mermaid syntax safety."""
    # Escape characters that could break Mermaid syntax
    label = label.replace('"', "'")
    label = label.replace("<", "&lt;")
    label = label.replace(">", "&gt;")
    return label
