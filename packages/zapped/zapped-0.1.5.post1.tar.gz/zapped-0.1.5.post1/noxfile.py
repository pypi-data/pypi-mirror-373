"""A nox configuration file for automating tasks such as linting, type checking, testing, and documentation building."""

from __future__ import annotations

import nox

PYTHON_VERSIONS = ["3.12", "3.13", "3.14"]


@nox.session(venv_backend="uv", tags=["lint"])
def ruff_check(session: nox.Session) -> None:
    """Run ruff linting and formatting checks (CI-friendly, no changes)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--check",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["lint", "fix"])
def ruff_fix(session: nox.Session) -> None:
    """Run ruff linting and formatting with auto-fix (development)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--fix",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["typecheck"])
def pyright(session: nox.Session) -> None:
    """Run static type checks."""
    session.install("pyright")
    session.run("pyright")


@nox.session(python=PYTHON_VERSIONS, venv_backend="uv")
def tests(session: nox.Session) -> None:
    """Run the unit test suite."""
    session.install("-e", ".")
    session.install("pytest")
    session.run("pytest")


@nox.session(venv_backend="uv", tags=["docs"])
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.install("-e", ".")
    session.install(
        "mkdocs",
        "mkdocs-material",
        "mkdocstrings[python]",
        "mkdocs-gen-files",
        "mkdocs-literate-nav",
        "mkdocs-section-index",
    )
    session.run("mkdocs", "build")


@nox.session(venv_backend="uv", tags=["docs"])
def docs_serve(session: nox.Session) -> None:
    """Build and serve the documentation."""
    session.install("-e", ".")
    session.install(
        "mkdocs",
        "mkdocs-material",
        "mkdocstrings[python]",
        "mkdocs-gen-files",
        "mkdocs-literate-nav",
        "mkdocs-section-index",
    )
    session.run("mkdocs", "serve")
