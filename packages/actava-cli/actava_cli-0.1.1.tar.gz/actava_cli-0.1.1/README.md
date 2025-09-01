# ActAVA CLI

Deploy and manage AI agents on ActAVA's managed cloud platform. Commercial offering for healthcare organizations.

## Installation

```bash
pip install actava-cli
```

## Quick Start

```bash
# Initialize your ActAVA project
actava init

# Export a LangGraph to JSON for deployment
actava graph-export app:my_graph --out graph.json

# Deploy your agent to ActAVA's managed cloud
actava push --manifest agent.manifest.yaml

# Monitor your deployed agent
actava logs my-agent --follow
```

## Commands

### `actava init`
Initialize your ActAVA project with your API credentials and project configuration.

### `actava graph-export <entrypoint> [--out <file>]`
Export a LangGraph object to ActAVA GraphSpec JSON format for deployment.

**Arguments:**
- `entrypoint`: Module and object name (e.g., `app:my_graph`)

**Options:**
- `--out`: Output file path (default: `graph.json`)

### `actava run [--manifest <file>] [--port <port>]`
Run an agent locally for testing before deployment.

**Options:**
- `--manifest`: Manifest file path (default: `agent.manifest.yaml`)
- `--port`: Port to run on (default: `8080`)

### `actava push [--manifest <file>] [--endpoint <url>]`
Deploy your agent to ActAVA's managed cloud platform.

**Options:**
- `--manifest`: Manifest file path (default: `agent.manifest.yaml`)
- `--endpoint`: ActAVA cloud endpoint (default: production)

### `actava logs <name> [--follow]`
Monitor logs for your deployed agent in ActAVA's cloud.

**Arguments:**
- `name`: Agent name

**Options:**
- `--follow`: Follow log output in real-time (default: `true`)

## Manifest Format

Create an `agent.manifest.yaml` file for deployment:

```yaml
name: my-healthcare-agent
entrypoint: "app:agent"
python: "3.11"
deps:
  - langchain-openai>=0.1
  - actava~=0.1
secrets:
  - OPENAI_API_KEY
runtime_cpu: "1 vcpu"
runtime_memory: "2 GiB"
expose:
  - /invoke
graph: "graph.json"
```

## ActAVA Cloud Platform

Deploy your agents to ActAVA's managed cloud platform with:
- **Automatic scaling** based on demand
- **Healthcare compliance** (HIPAA, SOC 2)
- **Built-in monitoring** and alerting
- **Enterprise security** and access controls
- **24/7 support** for healthcare organizations

## Support

- **Commercial Support**: [support.actava.ai](https://support.actava.ai)
- **Documentation**: [docs.actava.ai](https://docs.actava.ai)
- **Enterprise Sales**: [actava.ai](https://actava.ai)

## License

Proprietary software. Licensed for use by ActAVA customers only.
