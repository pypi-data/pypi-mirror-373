"""Static shim for editor/linters.

Re-export symbols from `langgraph.prebuilt` so imports like
`from actava.langgraph.prebuilt import create_react_agent` resolve.
"""

from __future__ import annotations

# We intentionally re-export everything to mirror langgraph's surface area.
from langgraph.prebuilt import *  # type: ignore[F401,F403]
