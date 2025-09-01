"""Static shim for editor/linters.

Expose selected LangChain modules under the `actava.langchain` namespace.
This keeps imports stable for examples and type checkers.
"""

from __future__ import annotations

# Avoid wildcard re-exports of the entire library; keep surface minimal.
