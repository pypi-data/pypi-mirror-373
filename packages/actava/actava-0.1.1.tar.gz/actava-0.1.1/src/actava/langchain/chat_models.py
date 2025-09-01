"""Static shim to expose `init_chat_model` under `actava.langchain.chat_models`."""

from __future__ import annotations

from langchain.chat_models import init_chat_model  # noqa: F401

__all__ = ["init_chat_model"]
