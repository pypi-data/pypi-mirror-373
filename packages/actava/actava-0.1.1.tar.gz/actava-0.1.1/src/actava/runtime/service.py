from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


class InvokeRequest(BaseModel):
    input: Any
    config: dict[str, Any] | None = None


class InvokeResponse(BaseModel):
    output: Any
    events: list[dict] = []


class ActavaAgentService:
    def __init__(self, agent_callable: Callable[[Any, dict[str, Any]], Any]):
        self.app = FastAPI()
        self._agent = agent_callable

        @self.app.get("/healthz")
        def healthz():
            return {"status": "ok"}

        @self.app.post("/invoke", response_model=InvokeResponse)
        def invoke(req: InvokeRequest) -> InvokeResponse:
            out = self._agent(req.input, req.config or {})
            return InvokeResponse(output=out, events=[])

    def run(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        import uvicorn

        uvicorn.run(self.app, host=host, port=port)
