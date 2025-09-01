"""A custom build hook that uses uv-dynamic-versioning to determine the version and renders a template."""

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
import re
import sys
from typing import Any

from dunamai import Version, bump_version, serialize_pep440, serialize_pvp, serialize_semver
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import jinja2
from jinja2 import Template
from uv_dynamic_versioning import schemas
from uv_dynamic_versioning.base import BasePlugin

from bear_utils.cli._get_version import Version as Ver


@dataclass
class Context:
    version: str
    commit: str
    branch: str
    dirty: bool | None
    major: int
    minor: int
    patch: int
    stage: str
    tagged_metadata: str
    branch_escaped: str
    bump_version: Callable
    serialize_pep440: Callable
    serialize_pvp: Callable
    serialize_semver: Callable

    @classmethod
    def from_version(cls, version: Version) -> "Context":
        """A factory method to create a Context from a dunamai Version object."""
        return cls(
            version=version.base,
            commit=version.commit or "",
            branch=version.branch or "",
            dirty=version.dirty,
            major=base_part(version.base, "major"),
            minor=base_part(version.base, "minor"),
            patch=base_part(version.base, "patch"),
            stage=version.stage or "",
            tagged_metadata=version.tagged_metadata or "",
            branch_escaped=_escape_branch(version.branch) or "",
            bump_version=bump_version,
            serialize_pep440=serialize_pep440,
            serialize_pvp=serialize_pvp,
            serialize_semver=serialize_semver,
        )


def _escape_branch(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"[^a-zA-Z0-9]", "", value)


def get_context(version: Version) -> Context:
    """Get the context for rendering the template."""
    return Context.from_version(version)


def base_part(base: str, part: str) -> int:
    ver: Ver = Ver.from_string(base)
    if part == "major":
        return ver.major
    if part == "minor":
        return ver.minor
    if part == "patch":
        return ver.patch
    return 0


def _get_version(config: schemas.UvDynamicVersioning) -> Version:
    try:
        return Version.from_vcs(
            config.vcs,
            latest_tag=config.latest_tag,
            strict=config.strict,
            tag_branch=config.tag_branch,
            tag_dir=config.tag_dir,
            full_commit=config.full_commit,
            ignore_untracked=config.ignore_untracked,
            pattern=config.pattern,
            pattern_prefix=config.pattern_prefix,
            commit_length=config.commit_length,
        )
    except RuntimeError as e:
        if fallback_version := config.fallback_version:
            return Version(fallback_version)
        raise e from e


class CustomBuildHook(BasePlugin, BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, _: str, __: dict[str, Any]) -> None:  # type: ignore[override]
        """Initialize the build hook."""
        try:
            version: Version = _get_version(self.project_config)
        except RuntimeError:
            version = Version("0.0.0")
        template: str | None = self.config.get("template")
        if template is None:
            raise ValueError("Template not found in configuration.")
        jinja_template: Template = jinja2.Template(template)
        rendered_content: str = jinja_template.render(**asdict(get_context(version)))
        output: str | None = self.config.get("output")
        if output is None:
            raise ValueError("Output path not found in configuration.")
        output_path = Path(output)
        if not output_path.parent.exists():
            print("Cannot find parent directory for output path...exiting.", sys.stderr)
            return
        output_path.write_text(rendered_content)
