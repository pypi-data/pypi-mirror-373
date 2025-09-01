"""Enhanced CLI for FastAPI Template with integrated template rendering."""

import typer
from pathlib import Path
from typing import Optional

from fastapi_template.renderer import TemplateRenderer

app = typer.Typer(
    name="fastapi-template",
    help="Generate FastAPI projects with best practices",
    add_completion=False,
)


def validate_project_name(name: str) -> str:
    """Validate project name format."""
    import re

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise typer.BadParameter(
            "Project name must start with a letter and contain only letters, numbers, hyphens, and underscores"
        )
    return name


@app.command()
def new(
    name: str = typer.Argument(
        ..., help="Name of the new project", callback=validate_project_name
    ),
    orm: str = typer.Option(
        "sqlalchemy", help="Choose ORM: sqlalchemy | beanie", case_sensitive=False
    ),
    project_type: str = typer.Option(
        "api",
        "--type",
        "--project-type",
        help="Choose type: api | fullstack",
        case_sensitive=False,
    ),
    description: Optional[str] = typer.Option(None, help="Project description"),
    author: Optional[str] = typer.Option(None, help="Project author"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing directory"
    ),
):
    """Create a new FastAPI project with best practices."""

    # Normalize inputs
    orm = orm.lower()
    project_type = project_type.lower()

    # Validate inputs
    if orm not in ["sqlalchemy", "beanie"]:
        typer.echo(f"❌ Invalid ORM: {orm}. Must be 'sqlalchemy' or 'beanie'.")
        raise typer.Exit(1)

    if project_type not in ["api", "fullstack"]:
        typer.echo(
            f"❌ Invalid project type: {project_type}. Must be 'api' or 'fullstack'."
        )
        raise typer.Exit(1)

    # Setup paths
    project_dir = Path.cwd() / name

    if project_dir.exists() and not force:
        typer.echo(f"❌ Directory {name} already exists. Use --force to overwrite.")
        raise typer.Exit(1)
    elif project_dir.exists() and force:
        typer.echo(f"⚠️  Overwriting existing directory: {name}")
        import shutil

        shutil.rmtree(project_dir)

    # Initialize renderer
    template_dir = Path(__file__).parent.parent / "templates"
    renderer = TemplateRenderer(template_dir)

    # Additional context
    additional_context = {
        "description": description or f"A FastAPI {project_type} project using {orm}",
        "author": author or "FastAPI Template",
        "year": 2024,
    }

    typer.echo(f"🚀 Creating FastAPI {project_type} project: {name}")
    typer.echo(f"   ORM: {orm}")
    typer.echo(f"   Type: {project_type}")
    typer.echo()

    try:
        # Render the complete project
        renderer.render_project(
            project_name=name,
            project_type=project_type,
            orm_type=orm,
            target_dir=project_dir,
            additional_context=additional_context,
        )

        typer.echo(f"✅ Project created successfully: {name}")
        typer.echo()
        typer.echo("Next steps:")
        typer.echo(f"  cd {name}")

        if orm == "sqlalchemy":
            typer.echo("  # Initialize database:")
            typer.echo("  alembic upgrade head")
        elif orm == "beanie":
            typer.echo("  # MongoDB will initialize on first connection")

        if project_type == "fullstack":
            typer.echo("  # Start with Docker (includes database):")
            typer.echo("  docker-compose up -d")
        else:
            typer.echo("  # Start development server:")
            typer.echo("  uvicorn app.main:app --reload")

    except Exception as e:
        typer.echo(f"❌ Error creating project: {e}")
        raise typer.Exit(1)


@app.command()
def list_templates():
    """List available templates and configurations."""
    typer.echo("Available templates:")
    typer.echo()

    template_dir = Path(__file__).parent.parent / "templates"

    # List ORM types
    typer.echo("ORM options:")
    for orm_dir in template_dir.iterdir():
        if orm_dir.is_dir() and orm_dir.name in ["sqlalchemy", "beanie"]:
            typer.echo(f"  • {orm_dir.name}")

            # List project types
            typer.echo("    Project types:")
            for project_type_dir in orm_dir.iterdir():
                if project_type_dir.is_dir():
                    typer.echo(f"      • {project_type_dir.name}")

    typer.echo()
    typer.echo("Common templates (always included):")
    common_dir = template_dir / "common"
    if common_dir.exists():
        for item in common_dir.rglob("*.j2"):
            typer.echo(f"  • {item.relative_to(common_dir)}")


@app.command()
def version():
    """Show version information."""
    typer.echo("FastAPI Template CLI v1.0.0")


@app.callback()
def main():
    """FastAPI Template CLI - Generate FastAPI projects with best practices."""
    pass


if __name__ == "__main__":
    app()
