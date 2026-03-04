"""
DockRadius Graph Builder.
Converts parsed Docker commands into an infrastructure graph model.
Deterministic: same input always produces the same graph.
"""

import logging
from app.models.schemas import ParsedCommand, GraphModel, GraphNode, GraphEdge

logger = logging.getLogger(__name__)


def build_graph(parsed: ParsedCommand) -> GraphModel:
    """
    Build an infrastructure graph from a parsed Docker command.

    Args:
        parsed: Structured ParsedCommand.

    Returns:
        GraphModel with nodes and edges representing infrastructure.
    """
    builder = _BUILDERS.get(parsed.base_command)
    if builder is None:
        logger.warning(f"No graph builder for command: {parsed.base_command}")
        return GraphModel()
    return builder(parsed)


# ─── Builder Functions ────────────────────────────────────────────

def _build_run_graph(p: ParsedCommand) -> GraphModel:
    """Build graph for 'docker run'."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    # Host node
    nodes.append(GraphNode(id="host", label="Host Machine", node_type="host"))

    # Image node
    image_label = p.image or "unknown"
    nodes.append(GraphNode(id="image", label=image_label, node_type="image"))

    # Container node
    container_label = p.container_name or f"{image_label}_container"
    nodes.append(GraphNode(id="container", label=container_label, node_type="container"))

    # Image → Container (pulls/creates)
    edges.append(GraphEdge(source="image", target="container", label="creates"))

    # Host → Container
    edges.append(GraphEdge(source="host", target="container", label="runs"))

    # Port mappings
    for idx, port in enumerate(p.ports):
        port_id = f"port_{idx}"
        nodes.append(GraphNode(id=port_id, label=f"Port {port}", node_type="port"))
        edges.append(GraphEdge(source="host", target=port_id, label="exposes"))
        edges.append(GraphEdge(source=port_id, target="container", label="maps to"))

    # Volume mounts
    for idx, vol in enumerate(p.volumes):
        vol_id = f"volume_{idx}"
        nodes.append(GraphNode(id=vol_id, label=f"Volume {vol}", node_type="volume"))
        edges.append(GraphEdge(source="host", target=vol_id, label="mounts"))
        edges.append(GraphEdge(source=vol_id, target="container", label="attached to"))

    # Network
    if p.network:
        nodes.append(GraphNode(id="network", label=p.network, node_type="network"))
        edges.append(GraphEdge(source="container", target="network", label="connects to"))

    return GraphModel(nodes=nodes, edges=edges)


def _build_build_graph(p: ParsedCommand) -> GraphModel:
    """Build graph for 'docker build'."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    nodes.append(GraphNode(id="host", label="Host Machine", node_type="host"))

    build_context = p.extra_args[0] if p.extra_args else "."
    nodes.append(GraphNode(id="context", label=f"Build Context ({build_context})", node_type="command"))

    image_label = p.image or "unnamed_image"
    nodes.append(GraphNode(id="image", label=image_label, node_type="image"))

    edges.append(GraphEdge(source="host", target="context", label="reads"))
    edges.append(GraphEdge(source="context", target="image", label="builds"))

    return GraphModel(nodes=nodes, edges=edges)


def _build_exec_graph(p: ParsedCommand) -> GraphModel:
    """Build graph for 'docker exec'."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    nodes.append(GraphNode(id="host", label="Host Machine", node_type="host"))

    container_label = p.container_name or "target_container"
    nodes.append(GraphNode(id="container", label=container_label, node_type="container"))

    cmd = " ".join(p.extra_args) if p.extra_args else "command"
    nodes.append(GraphNode(id="exec_cmd", label=cmd, node_type="command"))

    edges.append(GraphEdge(source="host", target="container", label="exec into"))
    edges.append(GraphEdge(source="container", target="exec_cmd", label="runs"))

    return GraphModel(nodes=nodes, edges=edges)


def _build_stop_graph(p: ParsedCommand) -> GraphModel:
    """Build graph for 'docker stop'."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    nodes.append(GraphNode(id="host", label="Host Machine", node_type="host"))

    container_label = p.container_name or "target_container"
    nodes.append(GraphNode(id="container", label=container_label, node_type="container"))

    edges.append(GraphEdge(source="host", target="container", label="stops"))

    return GraphModel(nodes=nodes, edges=edges)


def _build_rm_graph(p: ParsedCommand) -> GraphModel:
    """Build graph for 'docker rm'."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    nodes.append(GraphNode(id="host", label="Host Machine", node_type="host"))

    container_label = p.container_name or "target_container"
    nodes.append(GraphNode(id="container", label=container_label, node_type="container"))

    edges.append(GraphEdge(source="host", target="container", label="removes"))

    return GraphModel(nodes=nodes, edges=edges)


def _build_network_create_graph(p: ParsedCommand) -> GraphModel:
    """Build graph for 'docker network create'."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    nodes.append(GraphNode(id="host", label="Host Machine", node_type="host"))

    net_label = p.network or "unnamed_network"
    nodes.append(GraphNode(id="network", label=net_label, node_type="network"))

    edges.append(GraphEdge(source="host", target="network", label="creates"))

    return GraphModel(nodes=nodes, edges=edges)


def _build_volume_create_graph(p: ParsedCommand) -> GraphModel:
    """Build graph for 'docker volume create'."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    nodes.append(GraphNode(id="host", label="Host Machine", node_type="host"))

    vol_label = p.volumes[0] if p.volumes else "unnamed_volume"
    nodes.append(GraphNode(id="volume", label=vol_label, node_type="volume"))

    edges.append(GraphEdge(source="host", target="volume", label="creates"))

    return GraphModel(nodes=nodes, edges=edges)


# ─── Builder Registry ────────────────────────────────────────────

_BUILDERS = {
    "run": _build_run_graph,
    "build": _build_build_graph,
    "exec": _build_exec_graph,
    "stop": _build_stop_graph,
    "rm": _build_rm_graph,
    "network create": _build_network_create_graph,
    "volume create": _build_volume_create_graph,
}
