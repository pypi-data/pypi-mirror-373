#!/usr/bin/env python3
"""Setup configuration for FastAPI Template CLI."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8")

# Read requirements
requirements = [
    "typer[all]>=0.9.0",
    "jinja2>=3.1.0",
    "rich>=13.0.0",
]

setup(
    name="fastapi-template",
    version="1.0.0",
    author="FastAPI Template Team",
    author_email="team@fastapi-template.dev",
    description="A CLI tool for generating production-ready FastAPI projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/fastapi-template",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fastapi-template=fastapi_template.cli:app",
            "fat=fastapi_template.cli:app",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "fastapi_template": [
            "templates/**/*",
        ],
    },
    keywords="fastapi, template, generator, cli, sqlalchemy, beanie, mongodb, postgresql",
    project_urls={
        "Bug Reports": "https://github.com/your-org/fastapi-template/issues",
        "Source": "https://github.com/your-org/fastapi-template",
        "Documentation": "https://github.com/your-org/fastapi-template/wiki",
    },
)
