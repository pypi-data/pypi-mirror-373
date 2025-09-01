"""Project scaffolding utilities."""

import re
from pathlib import Path
from typing import Dict, Any

import click
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


def sanitize_name(name: str) -> str:
    """Convert toolkit name to valid Python package name."""
    package_name = re.sub(r'[-\s]+', '_', name.lower())
    package_name = re.sub(r'[^a-z0-9_]', '', package_name)
    if package_name and package_name[0].isdigit():
        package_name = f"toolkit_{package_name}"
    return package_name


def create_toolkit(name: str, target_dir: Path) -> None:
    """Create a new toolkit from templates."""
    cli_dir = Path(__file__).parent
    template_dir = cli_dir / "templates" / "toolkit"
    
    toolkit_dir = target_dir / name
    if toolkit_dir.exists():
        raise click.ClickException(f"Directory '{name}' already exists")
    
    # Template context
    context = {
        "toolkit_name": name,
        "package_name": sanitize_name(name)
    }
    package_name = context["package_name"]
    
    console.print(f"[green]Creating toolkit '{name}'[/green]")
    
    # Set up Jinja2
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Process templates
    for template_path in template_dir.rglob("*.j2"):
        rel_path = template_path.relative_to(template_dir)
        output_rel_path = str(rel_path)[:-3]  # Remove .j2
        output_rel_path = output_rel_path.replace("package_name", package_name)
        
        output_path = toolkit_dir / output_rel_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        template = env.get_template(str(rel_path))
        rendered = template.render(**context)
        output_path.write_text(rendered)
        
        console.print(f"  [dim]Created {output_rel_path}[/dim]")
    
    console.print(f"[green]✓ Created toolkit '{name}'[/green]")
    console.print(f"\nNext steps:")
    console.print(f"  [cyan]cd {name}[/cyan]")
    console.print(f"  [cyan]langchain tools serve[/cyan]")


def create_dockerfile(toolkit_dir: Path, toolkit_name: str):
    """Create a Dockerfile for the toolkit."""
    dockerfile_content = f"""# Production Dockerfile for {toolkit_name} toolkit
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install -e .

# Copy toolkit source code
COPY {toolkit_name}/ ./{toolkit_name}/
COPY toolkit.toml ./

# Install latest langchain-tool-server and python-dotenv
RUN pip install --upgrade langchain-tool-server python-dotenv

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the server with dotenv support
CMD ["python", "-c", "from dotenv import load_dotenv; load_dotenv(); from langchain_tool_server import Server; import uvicorn; app = Server.from_toolkit(enable_mcp=True); uvicorn.run(app, host='0.0.0.0', port=8000)"]
"""
    
    dockerfile_path = toolkit_dir / "Dockerfile"
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)
    
    # Also create .dockerignore
    dockerignore_content = """__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.gitignore
.pytest_cache/
.coverage
.venv/
venv/
env/
.env
*.log
.DS_Store
README.md
Dockerfile
.dockerignore
"""
    
    dockerignore_path = toolkit_dir / ".dockerignore"
    with open(dockerignore_path, "w") as f:
        f.write(dockerignore_content)
    
    console.print(f"[green]✓ Created Dockerfile and .dockerignore[/green]")