from typing import Annotated, List
import pathlib
import typer

from zenx.discovery import discover_local_module
from zenx.engine import Engine
from zenx.listeners import Listener
from zenx.pipelines.base import Pipeline
from zenx.resources.gitignore import IGNORES
from zenx.resources.env_example import ENV_EXAMPLE
from zenx.spiders import Spider

BUILTIN_PIPELINES = [
    "preprocess",
    "synoptic_websocket",
    "synoptic_free_websocket",
    "synoptic_grpc",
    "synoptic_grpc_useast1",
    "synoptic_grpc_eucentral1",
    "synoptic_grpc_euwest2",
    "synoptic_grpc_useast1chi2a",
    "synoptic_grpc_useast1nyc2a",
    "synoptic_grpc_apnortheast1",
    "synoptic_discord",
]

app = typer.Typer()


@app.callback()
def callback():
    discover_local_module("spiders")
    discover_local_module("listeners")
    discover_local_module("pipelines")


@app.command(name="list")
def list_all():
    spiders_available = Spider.spider_list()
    listeners_available = Listener.listener_list()
    typer.secho("Available spiders:", fg=typer.colors.GREEN, bold=True)
    for spider in spiders_available:
        typer.echo(f"- {spider}")
    typer.secho("Available listeners:", fg=typer.colors.GREEN, bold=True)
    for listener in listeners_available:
        typer.echo(f"- {listener}")
    
    custom_pipelines = {
        name
        for name, cls in Pipeline._registry.items()
        if not cls.__module__.startswith("zenx.pipelines")
    }
    # The remaining registered pipelines are the active built-in ones.
    builtin_pipelines_active = sorted(
        list(set(Pipeline._registry.keys()) - custom_pipelines)
    )
    typer.secho("Built-in pipelines:", fg=typer.colors.GREEN, bold=True)
    if builtin_pipelines_active:
        for pipeline in builtin_pipelines_active:
            typer.echo(f"- {pipeline}")
    else:
        typer.echo(" (No built-in pipelines are active)")
    if custom_pipelines:
        typer.secho("Custom pipelines:", fg=typer.colors.GREEN, bold=True)
        for pipeline in sorted(list(custom_pipelines)):
            typer.echo(f"- {pipeline}")


@app.command()
def crawl(spiders: List[str], forever: Annotated[bool, typer.Option(help="Run spiders continuously")] = False):
    spiders_available = Spider.spider_list()
    engine = Engine(forever=forever)
    if not spiders_available:
        typer.secho("❌ No spiders found to run.", fg=typer.colors.RED)
        raise typer.Exit()
    
    if len(spiders) > 1:
        for spider in spiders:
            if spider not in spiders_available:
                typer.secho(f"❌ Spider '{spider}' not found. Check available spiders with the 'list' command.", fg=typer.colors.RED)
                raise typer.Exit()
        typer.secho(f"🚀 Starting spiders: {', '.join(spiders)}", fg=typer.colors.CYAN)
        engine.run_spiders(spiders)
    
    elif spiders[0] == "all":
        typer.secho(f"🚀 Starting spiders: {', '.join(spiders_available)}", fg=typer.colors.CYAN)
        engine.run_spiders(spiders_available)
    
    else:
        spider = spiders[0]
        if spider not in spiders_available:
            typer.secho(f"❌ Spider '{spider}' not found. Check available spiders with the 'list' command.", fg=typer.colors.RED)
            raise typer.Exit()
        typer.secho(f"🚀 Starting spider: {spider}", fg=typer.colors.CYAN)
        engine.run_spider(spider)


@app.command()
def listen(listener: str):
    listeners_available = Listener.listener_list()
    engine = Engine(forever=False)
    if not listeners_available :
        typer.secho("❌ No listeners found to run.", fg=typer.colors.RED)
        raise typer.Exit()
    typer.secho(f"🚀 Starting listener: {listener}", fg=typer.colors.CYAN)
    engine.run_listener(listener)


@app.command()
def startproject(project_name: str):
    # e.g project_root/
    # /project_root/{project_name}
    project_path = pathlib.Path(project_name)
    # /project_root/{project_name}/spiders
    spiders_path = project_path / "spiders"
    # /project_root/{project_name}/listeners
    listeners_path = project_path / "listeners"
    # /project_root/zenx.toml
    config_path = project_path.parent / "zenx.toml"
    gitignore_path = project_path.parent / ".gitignore"
    env_example_path = project_path.parent / ".env.example"

    if project_path.exists():
        typer.secho(f"❌ Project '{project_name}' already exists in this directory.", fg=typer.colors.RED)
        raise typer.Exit()
    try:
        spiders_path.mkdir(parents=True, exist_ok=True)
        (spiders_path / "__init__.py").touch()
        listeners_path.mkdir(parents=True, exist_ok=True)
        (listeners_path / "__init__.py").touch()
        config_path.write_text(f'project = "{project_name}"\n')
        gitignore_path.write_text(IGNORES)
        env_example_path.write_text(ENV_EXAMPLE)

        typer.secho(f"✅ Project '{project_name}' created successfully.", fg=typer.colors.GREEN)
    except OSError as e:
        typer.secho(f"❌ Error creating project: {e}", fg=typer.colors.RED)
        raise typer.Exit()

