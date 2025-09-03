import typer
import uvicorn
import json
import importlib
import importlib.util
import sys
import os
import tempfile
import atexit
from typing import Optional

app = typer.Typer(
    name="articom",
    help="CLI for building and serving Articom skills."
)

def _load_skill_class(skill_path: str):
    """Dynamically loads the skill class from a file path."""
    try:
        if ":" not in skill_path:
            raise ValueError("Skill path must be in format 'module:ClassName'")
            
        module_path, class_name = skill_path.split(":", 1)
        
        # Add current directory to path to allow for local imports
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try to import the module
        try:
            module = importlib.import_module(module_path)
        except ImportError as import_err:
            # Try to import as a file path (without .py extension)
            if os.path.exists(f"{module_path}.py"):
                # Import as file
                spec = importlib.util.spec_from_file_location(module_path, f"{module_path}.py")
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_path] = module
                    spec.loader.exec_module(module)
                else:
                    raise import_err
            else:
                raise import_err
        
        # Get the class from the module
        if not hasattr(module, class_name):
            available_classes = [name for name in dir(module) 
                               if not name.startswith('_') and isinstance(getattr(module, name), type)]
            raise AttributeError(f"Class '{class_name}' not found in module '{module_path}'. "
                               f"Available classes: {available_classes}")
        
        skill_class = getattr(module, class_name)
        
        # Validate it's a proper skill class
        from .skill import _SKILL_METADATA_KEY
        if not hasattr(skill_class, _SKILL_METADATA_KEY):
            raise TypeError(f"Class '{class_name}' is not a valid Articom skill. "
                          f"Make sure it's decorated with @ArticomSkill.")
        
        return skill_class
        
    except (ValueError, ImportError, AttributeError, TypeError) as e:
        typer.echo(f"Error: Could not load skill '{skill_path}'.", err=True)
        typer.echo(f"Please use the format 'filename:ClassName' or 'module.submodule:ClassName'.", err=True)
        typer.echo(f"Details: {e}", err=True)
        
        # Provide additional debugging info
        typer.echo(f"Current working directory: {os.getcwd()}", err=True)
        typer.echo(f"Python path: {sys.path[:3]}...", err=True)  # Show first 3 entries
        
        raise typer.Exit(code=1)

def _create_app_factory(skill_path: str) -> str:
    """Creates a temporary app factory module for uvicorn."""
    module_path, class_name = skill_path.split(":")
    current_dir = os.getcwd()
    
    # Create the app factory content
    app_factory_content = f'''import sys
import os

# Ensure the current directory is in the Python path
current_dir = "{current_dir}"
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from articom_sdk.server import create_app
    from {module_path} import {class_name}
    
    # Create the FastAPI app
    app = create_app({class_name})
    
except ImportError as e:
    import traceback
    print(f"Error importing modules: {{e}}")
    print("Traceback:")
    traceback.print_exc()
    raise
except Exception as e:
    import traceback
    print(f"Error creating app: {{e}}")
    print("Traceback:")
    traceback.print_exc()
    raise
'''
    
    # Create a temporary file in the system temp directory
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, "_articom_app_loader.py")
    
    try:
        with open(temp_file_path, "w") as f:
            f.write(app_factory_content)
        
        # Register cleanup function
        def cleanup():
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass  # Ignore cleanup errors
        
        atexit.register(cleanup)
        
        return temp_file_path
    except Exception as e:
        typer.echo(f"Error: Could not create temporary app loader: {e}", err=True)
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
    
    try:
        # Validate that we can load the skill first
        skill_class = _load_skill_class(skill_path)
        typer.echo(f"✅ Successfully loaded skill class: {skill_class.__name__}")
        
        if reload:
            # For reload mode, we need to use the temporary app factory approach
            typer.echo("📝 Creating temporary app loader for reload mode...")
            temp_app_file = _create_app_factory(skill_path)
            temp_dir = os.path.dirname(temp_app_file)
            
            # Add temp directory to sys.path for import
            if temp_dir not in sys.path:
                sys.path.insert(0, temp_dir)
            
            module_name = os.path.basename(temp_app_file).replace('.py', '')
            typer.echo(f"🔄 Starting server with reload enabled...")
            uvicorn.run(
                f"{module_name}:app",
                host=host,
                port=port,
                reload=reload
            )
        else:
            # For non-reload mode, we can create the app directly
            typer.echo("⚡ Creating FastAPI app directly...")
            from articom_sdk.server import create_app
            app_instance = create_app(skill_class)
            typer.echo(f"🌐 Starting server at http://{host}:{port}")
            uvicorn.run(
                app_instance,
                host=host,
                port=port,
                reload=False
            )
            
    except KeyboardInterrupt:
        typer.echo("\n👋 Server stopped by user.")
    except Exception as e:
        typer.echo(f"❌ Error starting server: {e}", err=True)
        import traceback
        typer.echo("Full traceback:", err=True)
        typer.echo(traceback.format_exc(), err=True)
        raise typer.Exit(code=1)

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
