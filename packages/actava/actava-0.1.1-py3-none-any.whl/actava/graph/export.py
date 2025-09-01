from typing import Any

from .schema import GraphEdge, GraphNode, GraphSpec


def _infer_kind(fn: Any) -> str:
    name = getattr(fn, "__name__", "").lower()
    if "tool" in name:
        return "tool"
    if "llm" in name or "model" in name:
        return "llm"
    return "function"


def _ref(fn: Any) -> str:
    mod = getattr(fn, "__module__", None)
    name = getattr(fn, "__name__", None)
    if mod and name:
        return f"{mod}:{name}"
    return None


def export(state_graph: Any) -> GraphSpec:
    """
    Attempt to extract nodes/edges from LangGraph state graph.
    Compatible with v0.2+ where possible.
    """
    # Best-effort: try common attrs
    g = getattr(state_graph, "get_graph", None)
    graph = g() if callable(g) else getattr(state_graph, "_graph", None) or state_graph

    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    # Heuristics for typical LangGraph internals
    graph_nodes = getattr(graph, "nodes", [])
    for n in graph_nodes:
        key = getattr(n, "key", None) or getattr(n, "id", None) or str(n)
        fn = getattr(n, "fn", None) or getattr(n, "callable", None)
        nodes.append(GraphNode(id=str(key), kind=_infer_kind(fn), ref=_ref(fn)))

    graph_edges = getattr(graph, "edges", [])
    for e in graph_edges:
        src = getattr(getattr(e, "source", e), "key", None) or getattr(e, "source", None)
        tgt = getattr(getattr(e, "target", e), "key", None) or getattr(e, "target", None)
        cond = getattr(e, "condition", None)
        edges.append(
            GraphEdge(source=str(src), target=str(tgt), condition=str(cond) if cond else None)
        )

    return GraphSpec(nodes=nodes, edges=edges)
