import importlib
import sys
import warnings

ALIASES = {
    "actava.langchain": "langchain",
    "actava.langchain_core": "langchain_core",
    "actava.langchain_community": "langchain_community",
    # LangGraph namespace: keep parent pointing to package to allow submodules
    "actava.langgraph": "langgraph",
    "actava.langgraph.graph": "langgraph.graph",
    "actava.langgraph.prebuilt": "langgraph.prebuilt",
    "actava.langgraph.checkpoint": "langgraph.checkpoint",
    "actava.langchain_openai": "langchain_openai",
}


def _alias_module(alias: str, target: str) -> None:
    try:
        mod = importlib.import_module(target)
        sys.modules[alias] = mod
    except Exception as e:
        warnings.warn(f"ActAVA alias failed: {alias} -> {target}: {e}")


def ensure_import_aliases() -> None:
    for alias, target in ALIASES.items():
        if alias not in sys.modules:
            _alias_module(alias, target)
