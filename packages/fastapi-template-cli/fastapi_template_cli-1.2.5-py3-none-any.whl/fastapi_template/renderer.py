"""Template rendering functionality using Jinja2."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, Template


class TemplateRenderer:
    """Handles template rendering using Jinja2."""

    def __init__(self, template_dir: Path):
        """Initialize the template renderer.

        Args:
            template_dir: Path to the templates directory
        """
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Add custom filters
        self.env.filters["snake_case"] = self._snake_case
        self.env.filters["kebab_case"] = self._kebab_case
        self.env.filters["pascal_case"] = self._pascal_case

    def _snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        import re

        text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
        text = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", text)
        text = text.replace("-", "_")
        return text.lower()

    def _kebab_case(self, text: str) -> str:
        """Convert text to kebab-case."""
        import re

        text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", text)
        text = re.sub(r"([a-z\d])([A-Z])", r"\1-\2", text)
        text = text.replace("_", "-")
        return text.lower()

    def _pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        import re

        text = re.sub(r"[-_]", " ", text)
        return "".join(word.capitalize() for word in text.split())

    def render_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """Render a single template with context.

        Args:
            template_path: Path to the template file
            context: Dictionary with template variables

        Returns:
            Rendered template content
        """
        template = self.env.get_template(template_path)
        return template.render(**context)

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render a template string with context.

        Args:
            template_string: The template string
            context: Dictionary with template variables

        Returns:
            Rendered string
        """
        template = Template(template_string)
        return template.render(**context)

    def copy_and_render_tree(
        self,
        source_dir: Path,
        target_dir: Path,
        context: Dict[str, Any],
        exclude_patterns: list[str] | None = None,
    ) -> None:
        """Copy a directory tree and render all .j2 templates.

        Args:
            source_dir: Source directory containing templates
            target_dir: Target directory to create
            context: Dictionary with template variables
            exclude_patterns: List of patterns to exclude
        """
        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", "*.pyc", ".git", ".DS_Store"]

        target_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():
            if any(item.match(pattern) for pattern in exclude_patterns):
                continue

            target_path = target_dir / item.name

            if item.is_dir():
                target_path.mkdir(exist_ok=True)
                self.copy_and_render_tree(item, target_path, context, exclude_patterns)
            elif item.is_file():
                if item.suffix == ".j2":
                    # Render Jinja2 template
                    template_path = str(item.relative_to(self.template_dir)).replace(
                        "\\", "/"
                    )
                    rendered_content = self.render_template(template_path, context)
                    target_file = target_path.with_suffix("")  # Remove .j2 extension
                    target_file.write_text(rendered_content)
                else:
                    # Copy file as-is
                    shutil.copy2(item, target_path)

    def render_project(
        self,
        project_name: str,
        project_type: str,
        orm_type: str,
        target_dir: Path,
        additional_context: Dict[str, Any] | None = None,
    ) -> None:
        """Render a complete project from templates.

        Args:
            project_name: Name of the project
            project_type: 'api' or 'fullstack'
            orm_type: 'sqlalchemy' or 'beanie'
            target_dir: Directory to create the project in
            additional_context: Additional template variables
        """
        if additional_context is None:
            additional_context = {}

        # Base context for all templates
        context = {
            "project_name": project_name,
            "project_type": project_type,
            "orm_type": orm_type,
            "project_name_snake": self._snake_case(project_name),
            "project_name_kebab": self._kebab_case(project_name),
            "project_name_pascal": self._pascal_case(project_name),
            **additional_context,
        }

        # Render common templates
        common_templates = self.template_dir / "common"
        if common_templates.exists():
            self.copy_and_render_tree(common_templates, target_dir, context)

        # Render ORM-specific templates
        orm_templates = self.template_dir / orm_type / project_type
        if orm_templates.exists():
            self.copy_and_render_tree(orm_templates, target_dir, context)

        # Create additional files if needed
        self._create_additional_files(target_dir, context)

    def _create_additional_files(
        self, target_dir: Path, context: Dict[str, Any]
    ) -> None:
        """Create additional files that aren't templates."""
        # Create .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Environment files
.env.local
.env.development.local
.env.test.local
.env.production.local

# Docker
.dockerignore

# Celery
celerybeat-schedule
celerybeat.pid
"""
        (target_dir / ".gitignore").write_text(gitignore_content)

        # Create empty __init__.py files for proper Python packages
        init_files = [
            "app",
            "app/api",
            "app/api/v1",
            "app/api/v1/endpoints",
            "app/core",
            "app/db",
            "app/models",
            "app/schemas",
            "app/workers",
        ]

        for init_path in init_files:
            init_file = target_dir / init_path / "__init__.py"
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.touch()
