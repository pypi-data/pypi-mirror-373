import os
import queue
import threading
import time
from contextlib import contextmanager
from typing import Any

import requests
from langchain.callbacks.base import BaseCallbackHandler

INGEST_URL = os.getenv("ACTAVA_INGEST_URL", "https://ingest.example.actava/v1/logs")


def _env_meta() -> dict[str, str | None]:
    return {
        "tenant": os.getenv("ACTAVA_TENANT"),
        "project": os.getenv("ACTAVA_PROJECT"),
    }


class _Emitter:
    def __init__(self) -> None:
        self._q: queue.Queue[dict[str, Any]] = queue.Queue()
        self._worker = threading.Thread(target=self._drain, daemon=True)
        self._worker.start()

    def emit(self, evt: dict[str, Any]) -> None:
        self._q.put(evt)

    def _drain(self) -> None:
        buf: list[dict[str, Any]] = []
        while True:
            evt = self._q.get()
            buf.append(evt)
            if len(buf) >= 50:
                try:
                    requests.post(
                        INGEST_URL,
                        json={"events": buf},
                        headers={"Authorization": f"Bearer {os.getenv('ACTAVA_API_KEY','')}"},
                        timeout=3,
                    )
                except Exception:
                    # TODO: add local fallback buffer
                    pass
                finally:
                    buf.clear()


_emitter = _Emitter()


class ActavaCallbackHandler(BaseCallbackHandler):
    def __init__(self, sampling: float | None = None) -> None:
        self.sampling = sampling or float(os.getenv("ACTAVA_SAMPLING", "1.0"))

    # Example hooks (expand as needed)
    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any) -> None:
        if os.getenv("ACTAVA_TELEMETRY") != "1":
            return
        now = time.time()
        _emitter.emit(
            {
                "ts": now,
                "event": "llm_start",
                "meta": _env_meta(),
                "attrs": {"serialized": serialized, "prompts": prompts[:1]},
            }
        )

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        if os.getenv("ACTAVA_TELEMETRY") != "1":
            return
        now = time.time()
        _emitter.emit(
            {
                "ts": now,
                "event": "llm_end",
                "meta": _env_meta(),
                "attrs": {"response": str(response)[:1000]},
            }
        )


@contextmanager
def telemetry_context():
    """
    Usage:
      with telemetry_context():
          # build or run LC chains/graphs
    Ensures handler gets attached wherever LC checks for default callbacks.
    """
    # LangChain allows passing callbacks per call; here we rely on user passing handler
    # or set env var to signal your own wrappers. This context is a semantic placeholder.
    yield
