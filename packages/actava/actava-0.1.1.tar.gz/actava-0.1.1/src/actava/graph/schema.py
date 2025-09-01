from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    kind: str
    label: str | None = None
    ref: str | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    condition: str | None = None


class GraphSpec(BaseModel):
    version: str = "actava-graph-v0"
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    metadata: dict[str, str] = {}
