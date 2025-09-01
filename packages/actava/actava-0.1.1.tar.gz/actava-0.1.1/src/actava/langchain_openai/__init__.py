"""Static shim for editor/linters.

This package re-exports symbols from `langchain_openai` so that static analyzers
can resolve `actava.langchain_openai` without relying on runtime aliasing.
"""

from __future__ import annotations

from langchain_openai import *  # type: ignore[F401,F403]
