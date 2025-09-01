from pydantic import BaseModel


class Manifest(BaseModel):
    name: str
    entrypoint: str  # "module:function"
    python: str = "3.11"
    deps: list[str] = []
    secrets: list[str] = []
    runtime_cpu: str = "1 vcpu"
    runtime_memory: str = "2 GiB"
    expose: list[str] = ["/invoke"]
    graph: str | None = None
