# ActAVA SDK

Enterprise AI orchestration platform for healthcare organizations. Build, deploy, and manage AI agents on ActAVA's managed cloud platform.

## Installation

```bash
pip install actava
```

## Quick Start

```python
import actava as av
from actava.langchain_openai import ChatOpenAI
from actava.langgraph import StateGraph, END

# Initialize ActAVA with your project credentials
av.init(project="your-project-id", api_key="your-api-key")

# Use LangChain/LangGraph as usual
llm = ChatOpenAI(model="gpt-4o")

def my_function(state):
    return {"result": "processed", **state}

# Create and compile graph
graph = StateGraph(dict)
graph.add_node("process", my_function)
graph.add_edge("process", END)
compiled = graph.compile()

# Export graph for deployment
from actava.graph import export
spec = export(graph)
print(spec.model_dump_json(indent=2))
```

## Features

- **Zero API Changes**: Import `actava.langchain` and `actava.langgraph` with no code changes
- **Auto Telemetry**: Automatic instrumentation with configurable sampling
- **Graph Export**: Export LangGraph DAGs to JSON GraphSpec for deployment
- **Runtime Service**: FastAPI-based runtime service for local testing and cloud deployment
- **Healthcare Focus**: Built with healthcare compliance and security in mind
- **Managed Cloud**: Deploy to ActAVA's managed cloud platform with `actava-cli`

## Deployment

Use the ActAVA CLI to deploy your agents to our managed cloud:

```bash
# Install CLI
pip install actava-cli

# Initialize project
actava init

# Deploy agent
actava push --manifest agent.manifest.yaml
```

## Documentation

For full documentation, visit [docs.actava.ai](https://docs.actava.ai)

## Support

- **Commercial Support**: [support.actava.ai](https://support.actava.ai)
- **Documentation**: [docs.actava.ai](https://docs.actava.ai)
- **Enterprise Sales**: [actava.ai](https://actava.ai)

## License

Proprietary software. Licensed for use by ActAVA customers only.
