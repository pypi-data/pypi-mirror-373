import importlib
import json
import tempfile
from pathlib import Path

from .manifest import Manifest


def build_artifact(manifest_path: str) -> tuple[str, Manifest]:
    mp = Path(manifest_path)
    raw = mp.read_text()
    if manifest_path.endswith(".json"):
        data = json.loads(raw)
    else:
        try:
            import yaml  # optional for YAML

            data = yaml.safe_load(raw)
        except Exception:
            raise RuntimeError("Install pyyaml to use YAML manifests.")
    mf = Manifest(**data)

    # Resolve the entrypoint to ensure importability
    mod_name, fn_name = mf.entrypoint.split(":")
    importlib.import_module(mod_name)  # raises if missing

    # Create a simple build directory packing manifest + optional graph.json
    tmp = tempfile.mkdtemp(prefix="actava_pkg_")
    Path(tmp, "manifest.json").write_text(json.dumps(mf.model_dump(), indent=2))
    if mf.graph and Path(mf.graph).exists():
        Path(tmp, "graph.json").write_text(Path(mf.graph).read_text())

    return tmp, mf
