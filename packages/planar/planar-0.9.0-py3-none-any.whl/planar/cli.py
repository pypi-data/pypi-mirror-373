import os
import subprocess
import sys
from pathlib import Path

import typer
import uvicorn
from jinja2 import Environment as JinjaEnvironment
from jinja2 import FileSystemLoader

from planar.config import Environment

app = typer.Typer(help="Planar CLI tool")


def find_default_app_path() -> Path:
    """Checks for default app file paths (app.py, then main.py)."""
    for filename in ["app.py", "main.py"]:
        path = Path(filename)
        if path.is_file():
            typer.echo(f"Found default app file: {path}")
            return path
    typer.echo(
        "Error: Could not find app.py or main.py. Please specify the app file using --path.",
        err=True,
    )
    raise typer.Exit(code=1)


def get_module_str_from_path(app_path: Path) -> str:
    """Converts a file path to a Python module import string."""
    try:
        # Ensure path is absolute before making it relative
        abs_path = app_path.resolve()
        # Find the part relative to the current working directory
        rel_path = abs_path.relative_to(Path.cwd())
        # Remove .py and replace path separators with dots
        module_part = str(rel_path.with_suffix("")).replace(os.path.sep, ".")
        # Add cwd to sys.path if not already there, uvicorn might need it
        if str(Path.cwd()) not in sys.path:
            sys.path.insert(0, str(Path.cwd()))
        return module_part
    except ValueError:
        typer.echo(
            f"Error: App path {app_path} is not within the current working directory structure.",
            err=True,
        )
        typer.echo("Planar must be run from the project root directory.")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error processing app path {app_path}: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("dev")
def dev_command(
    path: Path | None = typer.Argument(
        None,
        help="Optional path to the Python file containing the Planar app instance. Defaults to app.py or main.py.",
        show_default=False,  # Hide default in help, as it's dynamic
    ),
    port: int | None = typer.Option(8000, help="Port to run on"),
    host: str | None = typer.Option("127.0.0.1", help="Host to run on"),
    config: Path | None = typer.Option(
        None, help="Path to config file (default: planar.dev.yaml)"
    ),
    app_name: str = typer.Option(
        "app", "--app", help="Name of the PlanarApp instance variable."
    ),
    script: bool = typer.Option(
        False,
        "--script",
        help="Run as a script with 'uv run' instead of starting a server",
    ),
    ssl_keyfile: str | None = typer.Option(
        None, "--ssl-keyfile", help="Path to SSL key file"
    ),
    ssl_certfile: str | None = typer.Option(
        None, "--ssl-certfile", help="Path to SSL cert file"
    ),
):
    """Run Planar in development mode"""
    run_command(
        Environment.DEV,
        port,
        host,
        config,
        path,
        app_name,
        script,
        ssl_keyfile,
        ssl_certfile,
    )


@app.command("prod")
def prod_command(
    path: Path | None = typer.Argument(
        None,
        help="Optional path to the Python file containing the Planar app instance. Defaults to app.py or main.py.",
        show_default=False,  # Hide default in help, as it's dynamic
    ),
    port: int | None = typer.Option(8000, help="Port to run on"),
    host: str | None = typer.Option("0.0.0.0", help="Host to run on"),
    config: Path | None = typer.Option(
        None, help="Path to config file (default: planar.prod.yaml)"
    ),
    app_name: str = typer.Option(
        "app", "--app", help="Name of the PlanarApp instance variable."
    ),
    script: bool = typer.Option(
        False,
        "--script",
        help="Run as a script with 'uv run' instead of starting a server",
    ),
    ssl_keyfile: str | None = typer.Option(
        None, "--ssl-keyfile", help="Path to SSL key file"
    ),
    ssl_certfile: str | None = typer.Option(
        None, "--ssl-certfile", help="Path to SSL cert file"
    ),
):
    """Run Planar in production mode"""
    run_command(
        Environment.PROD,
        port,
        host,
        config,
        path,
        app_name,
        script,
        ssl_keyfile,
        ssl_certfile,
    )


def run_command(
    env: Environment,
    port: int | None,
    host: str | None,
    config_file: Path | None,
    path: Path | None,
    app_name: str,
    script: bool = False,
    ssl_keyfile: str | None = None,
    ssl_certfile: str | None = None,
):
    """Common logic for both dev and prod commands"""
    os.environ["PLANAR_ENV"] = env.value

    if config_file:
        if not config_file.exists():
            typer.echo(f"Error: Config file {config_file} not found", err=True)
            raise typer.Exit(code=1)
        os.environ["PLANAR_CONFIG"] = str(config_file)

    # Determine the app path
    if path:  # Use the positional argument if provided
        app_path = path
        if not app_path.is_file():
            typer.echo(
                f"Error: Specified app path {app_path} not found or is not a file",
                err=True,
            )
            raise typer.Exit(code=1)
    else:
        app_path = find_default_app_path()  # Finds app.py or main.py

    os.environ["PLANAR_ENTRY_POINT"] = str(app_path)

    if script:
        # Run as a script using uv run
        typer.echo(f"Running script: {app_path}")
        typer.echo(f"Environment: {env.value}")

        try:
            result = subprocess.run(
                ["uv", "run", str(app_path)], env=os.environ.copy(), check=True
            )
            raise typer.Exit(code=result.returncode)
        except subprocess.CalledProcessError as e:
            typer.echo(f"Error running script: {e}", err=True)
            raise typer.Exit(code=e.returncode)
        except FileNotFoundError:
            typer.echo(
                "Error: 'uv' command not found. Please install uv first.", err=True
            )
            raise typer.Exit(code=1)
        except Exception as e:
            typer.echo(f"Error running script: {e}", err=True)
            raise typer.Exit(code=1)
    else:
        # Run as a server using uvicorn
        # Convert path to module string
        module_part = get_module_str_from_path(app_path)
        # TODO: Check that the app_name is a valid variable name in the module
        app_import_string = f"{module_part}:{app_name}"

        typer.echo(f"Using app: {app_import_string}")
        typer.echo(f"Starting Planar in {env.value} mode")

        try:
            uvicorn.run(
                app_import_string,
                host=host or ("127.0.0.1" if env == Environment.DEV else "0.0.0.0"),
                port=port or 8000,
                reload=True if env == Environment.DEV else False,
                timeout_graceful_shutdown=4,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile,
            )
        except Exception as e:
            # Provide more context on import errors
            if isinstance(e, (ImportError, AttributeError)):
                typer.echo(
                    f"Error importing application '{app_import_string}': {e}", err=True
                )
                typer.echo(
                    f"Ensure '{app_path}' exists and contains a variable named '{app_name}'.",
                    err=True,
                )
            else:
                typer.echo(f"Error starting the application: {e}", err=True)
            raise typer.Exit(code=1)


@app.command("scaffold")
def scaffold_project(
    name: str = typer.Option(None, "--name", help="Name of the new project"),
    directory: Path = typer.Option(Path("."), "--directory", help="Target directory"),
):
    """
    Creates a new Planar project with a basic structure and example workflow.
    """
    if not name:
        name = typer.prompt("Project name", default="planar_demo")

    project_dir = directory / name
    if project_dir.exists():
        typer.echo(f"Error: Directory {project_dir} already exists", err=True)
        raise typer.Exit(code=1)

    # Setup Jinja2 template environment
    template_dir = Path(__file__).parent / "scaffold_templates"
    jinja_env = JinjaEnvironment(loader=FileSystemLoader(template_dir))

    # Template context
    context = {"name": name}

    # Create project structure
    try:
        (project_dir / "app" / "db").mkdir(parents=True)
        (project_dir / "app" / "flows").mkdir(parents=True)
    except OSError as exc:
        typer.echo(f"Error creating project structure: {exc}", err=True)
        raise typer.Exit(code=1)

    # Render and write templates
    templates = [
        ("app/__init__.py.j2", "app/__init__.py"),
        ("app/db/entities.py.j2", "app/db/entities.py"),
        ("app/flows/process_invoice.py.j2", "app/flows/process_invoice.py"),
        ("main.py.j2", "main.py"),
        ("pyproject.toml.j2", "pyproject.toml"),
        ("planar.dev.yaml.j2", "planar.dev.yaml"),
        ("planar.prod.yaml.j2", "planar.prod.yaml"),
    ]

    for template_path, output_path in templates:
        template = jinja_env.get_template(template_path)
        content = template.render(context)
        (project_dir / output_path).write_text(content)

    typer.secho(
        f"""
✨ Project '{name}' created successfully!

To get started:
    cd {name}

    Set your OPENAI_API_KEY in a new .env.dev file

    uv run planar dev
    """,
        fg=typer.colors.GREEN,
    )


def main():
    app()


if __name__ == "__main__":
    app()
