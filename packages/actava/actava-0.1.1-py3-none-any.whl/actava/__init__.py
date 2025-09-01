# Create import-time aliases so `import actava.langchain` works like upstream.
from ._alias import ensure_import_aliases as _ensure_aliases
from .config import init  # re-export

_ensure_aliases()

__all__ = ["init"]
