import os


def init(
    project: str,
    tenant: str | None = None,
    api_key: str | None = None,
    enable_langsmith: bool = True,
    telemetry_enabled: bool = True,
    sampling: float = 1.0,
) -> None:
    """
    Initialize ActAVA SDK defaults. Call once near startup.
    """
    os.environ["ACTAVA_PROJECT"] = project
    if tenant:
        os.environ["ACTAVA_TENANT"] = tenant
    if api_key:
        os.environ["ACTAVA_API_KEY"] = api_key
    if telemetry_enabled:
        os.environ["ACTAVA_TELEMETRY"] = "1"
    os.environ["ACTAVA_SAMPLING"] = str(sampling)
    if enable_langsmith:
        os.environ.setdefault("LANGSMITH_TRACING", "true")
