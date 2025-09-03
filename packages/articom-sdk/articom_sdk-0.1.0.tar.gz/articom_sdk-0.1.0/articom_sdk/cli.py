import typer
import uvicorn
import json
import importlib
import sys
import os
from typing import Optional

app = typer.Typer(
    name="articom",
    help="CLI for building and serving Articom skills."
)

def _load_skill_class(skill_path: str):
    """Dynamically loads the skill class from a file path."""
    try:
        module_path, class_name = skill_path.split(":")
        # Add current directory to path to allow for local imports
        sys.path.insert(0, os.getcwd())
        module = importlib.import_module(module_path)
        skill_class = getattr(module, class_name)
        return skill_class
    except (ValueError, ImportError, AttributeError) as e:
        typer.echo(f"Error: Could not load skill '{skill_path}'. Please use the format 'filename:ClassName'.", err=True)
        typer.echo(f"Details: {e}", err=True)
        raise typer.Exit(code=1)

@app.command()
def serve(
    skill_path: str = typer.Argument(..., help="Path to the skill, e.g., 'main:MySkill'"),
    host: str = typer.Option("127.0.0.1", help="The host to bind the server to."),
    port: int = typer.Option(8000, help="The port to run the server on."),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reloading for development.")
):
    """Serves the Articom skill using a Uvicorn server."""
    typer.echo(f"🚀 Starting Articom skill server for '{skill_path}'...")
    
    # We need to pass the import string to uvicorn for reloads to work
    # We create a temporary app factory file
    current_dir = os.getcwd()
    app_factory_string = f"import sys\n" \
                         f"import os\n" \
                         f"sys.path.insert(0, '{current_dir}')\n" \
                         f"from articom_sdk.server import create_app\n" \
                         f"from {skill_path.replace(':', ' import ')}\n" \
                         f"app = create_app({skill_path.split(':')[1]})"

    temp_app_file = "_articom_app_loader.py"
    with open(temp_app_file, "w") as f:
        f.write(app_factory_string)

    try:
        uvicorn.run(
            f"{temp_app_file.replace('.py', '')}:app",
            host=host,
            port=port,
            reload=reload
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_app_file):
            os.remove(temp_app_file)

@app.command(name="generate-manifest")
def generate_manifest(
    skill_path: str = typer.Argument(..., help="Path to the skill, e.g., 'main:MySkill'"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Path to save the manifest file.")
):
    """Generates the skill.json manifest and prints it or saves it to a file."""
    typer.echo(f"🛠️  Generating manifest for '{skill_path}'...")
    skill_class = _load_skill_class(skill_path)
    skill_instance = skill_class()
    manifest = skill_instance.generate_manifest()
    
    manifest_json = json.dumps(manifest, indent=2)
    
    if output:
        with open(output, "w") as f:
            f.write(manifest_json)
        typer.echo(f"✅ Manifest successfully saved to '{output}'")
    else:
        typer.echo(manifest_json)

# For internal use by the SDK, not a user-facing command
class ArticomCLI:
    def __init__(self, skill_class: type):
        self._app = app
        # This is a bit of a hack to allow the example to run easily
        # In a real package, the `articom` script is the entry point
        if __name__ == "articom_sdk.cli":
             self._app()
