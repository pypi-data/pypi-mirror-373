import json
import os
import sys
from pathlib import Path

import typer
from actava.deploy.package import build_artifact
from actava.graph import export as export_graph
from rich import print

app = typer.Typer(add_completion=False)


@app.command()
def init():
    """Write a minimal .actava/config and prompt for API key."""
    Path(".actava").mkdir(exist_ok=True)
    cfg = Path(".actava/config")
    api_key = os.getenv("ACTAVA_API_KEY", "")
    if not api_key:
        api_key = typer.prompt("Enter ACTAVA_API_KEY", hide_input=True)
    cfg.write_text(json.dumps({"api_key": api_key}, indent=2))
    print("[green]Wrote .actava/config[/green]")


@app.command("graph-export")
def graph_export(
    entrypoint: str = typer.Argument(..., help="module:graph_object"), out: str = "graph.json"
):
    """Load a LangGraph object and export an ActAVA GraphSpec JSON."""
    # Ensure current working directory is importable for local modules like `app`
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    mod_name, obj_name = entrypoint.split(":")
    mod = __import__(mod_name, fromlist=[obj_name])
    graph_obj = getattr(mod, obj_name)
    spec = export_graph(graph_obj)
    Path(out).write_text(spec.model_dump_json(indent=2))
    print(f"[green]Exported graph to {out}[/green]")


@app.command()
def run(manifest: str = "agent.manifest.yaml", port: int = 8080):
    """Run the agent locally using the manifest's entrypoint."""
    import yaml
    from actava.deploy.manifest import Manifest
    from actava.runtime import ActavaAgentService

    # Ensure current working directory is importable for local modules referenced by manifest
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    mf = Manifest(**yaml.safe_load(Path(manifest).read_text()))
    mod_name, fn_name = mf.entrypoint.split(":")
    mod = __import__(mod_name, fromlist=[fn_name])
    agent_callable = getattr(mod, fn_name)

    svc = ActavaAgentService(agent_callable)
    svc.run(port=port)


@app.command()
def push(
    manifest: str = "agent.manifest.yaml", endpoint: str = "https://api.example.actava/v1/push"
):
    """Build an artifact and push it to ActAVA (stub)."""
    tmp_dir, mf = build_artifact(manifest)
    print(f"Built artifact at: {tmp_dir}")
    # TODO: tar + upload; for now, just echo
    print(f"[yellow]Stub push to {endpoint} (implement later)[/yellow]")


@app.command()
def logs(name: str, follow: bool = True):
    """Tail logs for a deployed agent (stub)."""
    print(f"[yellow]Stub logs for {name}[/yellow]")
    if follow:
        print("[dim]Press Ctrl+C to exit[/dim]")


if __name__ == "__main__":
    app()
