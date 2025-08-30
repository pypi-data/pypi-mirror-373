"""Tools command group for managing LangChain tool servers."""

import click
from rich.console import Console

console = Console()

@click.group()
def tools():
    """Manage LangChain tool servers."""
    pass

@tools.command()
@click.argument("name", required=True)
def new(name: str):
    """Create a new toolkit project.
    
    Args:
        name: Name of the toolkit to create
        
    Example:
        langchain tools new my-awesome-toolkit
    """
    from pathlib import Path
    from ..scaffolding import create_toolkit
    
    try:
        create_toolkit(name, Path.cwd())
    except Exception as e:
        console.print(f"[red]Error creating toolkit: {e}[/red]")
        raise click.Abort()

@tools.command()
@click.option("--reload", is_flag=True, help="Enable auto-reload on file changes")
@click.option("--port", default=8000, help="Port to serve on", type=int)
def serve(reload: bool, port: int):
    """Start local development server with no persistence.
    
    Loads tools from the current toolkit and serves them via FastAPI server.
    Must be run from the root of a toolkit created with 'langchain tools new'.
    
    Options:
        --reload: Automatically reload when tool files change
        --port: Port to serve on (default: 8000)
        
    Example:
        langchain tools serve --reload --port 8080
    """
    from pathlib import Path
    
    # Check if we're in a toolkit directory
    if not Path("toolkit.toml").exists():
        console.print("[red]Error: Not in a toolkit directory[/red]")
        console.print("Run this command from the root of a toolkit created with 'langchain tools new'")
        raise click.Abort()
    
    try:
        import subprocess
        import sys
        
        console.print(f"[green]Starting toolkit server on port {port}[/green]")
        if reload:
            console.print("[blue]Auto-reload enabled[/blue]")
        
        # Create a Python script that uses the local environment
        server_script = f'''
from langchain_tool_server import Server
import uvicorn

def create_app():
    return Server.from_toolkit(enable_mcp=True)

if __name__ == "__main__":
    reload = {reload}
    port = {port}
    
    if reload:
        uvicorn.run(
            "__main__:create_app",
            host="0.0.0.0",
            port=port,
            reload=reload,
            factory=True
        )
    else:
        app = create_app()
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=port
        )
'''
        
        # Use current Python environment 
        cmd = [sys.executable, "-c", server_script]
        subprocess.run(cmd, cwd=Path.cwd())
        
    except ValueError as e:
        console.print(f"[red]Error loading toolkit: {e}[/red]")
        raise click.Abort()
    except ImportError:
        console.print("[red]Error: langchain-tool-server not installed[/red]")
        console.print("Install it with: pip install langchain-tool-server")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise click.Abort()

@tools.command()
@click.option("--tag", "-t", default="latest", help="Docker image tag (default: latest)")
@click.option("--platform", default="linux/amd64", help="Target platform (default: linux/amd64)")
def build(tag: str, platform: str):
    """Build a Docker image from the current toolkit.
    
    Creates a production-ready Docker container with the toolkit server.
    Must be run from the root of a toolkit created with 'langchain tools new'.
    
    Options:
        --tag: Docker image tag (default: latest)
        --platform: Target platform (default: linux/amd64)
        
    Example:
        langchain tools build --tag v1.0.0
    """
    from pathlib import Path
    import subprocess
    
    # Check if we're in a toolkit directory
    if not Path("toolkit.toml").exists():
        console.print("[red]Error: Not in a toolkit directory[/red]")
        console.print("Run this command from the root of a toolkit created with 'langchain tools new'")
        raise click.Abort()
    
    try:
        # Get toolkit name from toml
        import tomllib
        with open("toolkit.toml", "rb") as f:
            config = tomllib.load(f)
        
        toolkit_name = config["toolkit"]["name"]
        image_name = f"{toolkit_name}:{tag}"
        
        console.print(f"[green]Building Docker image: {image_name}[/green]")
        console.print(f"[blue]Platform: {platform}[/blue]")
        
        # Create Dockerfile from template using CLI scaffolding (doesn't need local deps)
        from ..scaffolding import create_dockerfile
        
        create_dockerfile(Path.cwd(), toolkit_name)
        
        # Build Docker image
        cmd = [
            "docker", "build",
            "--no-cache",
            "--platform", platform,
            "-t", image_name,
            "."
        ]
        
        console.print(f"[blue]Running: {' '.join(cmd)}[/blue]")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Docker build failed:[/red]")
            console.print(result.stderr)
            raise click.Abort()
        
        console.print(f"[green]✅ Successfully built image: {image_name}[/green]")
        console.print(f"[blue]To run: docker run -p 8000:8000 {image_name}[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error building toolkit: {e}[/red]")
        raise click.Abort()

@tools.command()
@click.option("--server", help="Remote server URL to deploy to")
def deploy(server: str):
    """Deploy current toolkit to a remote tool server.
    
    Discovers all @tool decorated functions in ./tools/ directory,
    extracts their code and schema, and deploys them to a remote
    server with automatic version management.
    
    Options:
        --server: Remote server URL (can also be set in toolkit.toml)
        
    Example:
        langchain tools deploy --server https://tools.company.com
    """
    if server:
        console.print(f"[green]Deploying to server: {server}[/green]")
    else:
        console.print("[green]Deploying to server from toolkit.toml[/green]")
    
    # TODO: Implement deployment logic
    console.print("[yellow]⚠️  Not implemented yet[/yellow]")