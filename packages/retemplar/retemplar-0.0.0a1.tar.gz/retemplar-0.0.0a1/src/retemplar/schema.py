# src/retemplar/schema.py
"""Minimal lockfile schema for retemplar MVP (RAT-only, file-level ownership).

Deliberately omitted for v0:
- Template Packs (name/version)
- Section rules / 'patch' strategy
- Variables
- Lineage/audit trail
- Content fingerprints (we can add baseline_ref later)

Notes:
- Regex replacements use Python `re.sub` semantics (backrefs like "\\1"), not "$1".
"""

import re
from enum import StrEnum
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from retemplar.constants import (
    REPO_PREFIX_GITHUB,
    REPO_PREFIX_LOCAL,
    TEMPLATE_KIND_RAT,
)


class TemplateRefParseError(ValueError):
    """Raised when template reference parsing fails."""


# -----------------------
# Template source (RAT)
# -----------------------


class TemplateSource(BaseModel):
    """Repo-as-Template (RAT) source."""

    kind: Literal['rat'] = TEMPLATE_KIND_RAT
    # e.g. 'gh:org/repo' OR local path like './template' or '/abs/path'
    repo: str
    # display/tag or commit-ish used at adopt/upgrade (for local you may synthesize 'SNAPSHOT-<hash>')
    ref: str | None = None
    # resolved commit SHA when known (git sources)
    commit: str | None = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('repo')
    @classmethod
    def _validate_repo(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('repo cannot be empty')

        # Git repository (standard git URLs)
        if not v.startswith((REPO_PREFIX_GITHUB, REPO_PREFIX_LOCAL)):
            raise ValueError(
                f"repo: {v} must start with '{REPO_PREFIX_GITHUB}' or '{REPO_PREFIX_LOCAL}'.",
            )
        return v

    @model_validator(mode='after')
    def _ensure_commit_if_sha(self) -> 'TemplateSource':
        # If ref looks like a 40/64-char hex, treat as commit
        if self.commit is None and re.fullmatch(
            r'[0-9a-fA-F]{40}|[0-9a-fA-F]{64}',
            self.ref or '',
        ):
            self.commit = self.ref
        return self


def parse_template_ref(template_ref: str) -> TemplateSource:
    """Parse RAT template reference into TemplateSource.

    Accepted forms (MVP):
      - rat:gh:org/repo@vX
      - rat:local:./template-dir@vX
      - rat:local:/abs/path@vX
      - rat:local:./template-dir           (defaults ref='local')
    """
    if not template_ref.startswith(f'{TEMPLATE_KIND_RAT}:'):
        raise TemplateRefParseError(
            f'MVP only supports RAT templates: {template_ref}',
        )

    ref_part = template_ref[len(TEMPLATE_KIND_RAT) + 1 :]  # strip 'rat:'

    # If explicit @ref present, split it
    if '@' in ref_part:
        repo, ref = ref_part.rsplit('@', 1)
        if not repo:
            raise TemplateRefParseError(
                f'Invalid RAT template (empty repo): {template_ref}',
            )
        if not ref:
            raise TemplateRefParseError(
                f'Invalid RAT template (empty ref): {template_ref}',
            )
        return TemplateSource(repo=repo, ref=ref)

    # No @ref: must be a local path; default ref label
    if ref_part.startswith(REPO_PREFIX_LOCAL):
        return TemplateSource(repo=ref_part)

    # GitHub without @ is ambiguous; require explicit ref
    if ref_part.startswith(REPO_PREFIX_GITHUB):
        raise TemplateRefParseError(
            f'GitHub RAT template ref must include @version: {template_ref}',
        )

    raise TemplateRefParseError(
        f'Unsupported RAT template format: {template_ref}',
    )


# -----------------------
# Ownership configuration
# -----------------------


class Strategy(StrEnum):
    """File management strategy for template upgrades."""

    PRESERVE = 'preserve'
    ENFORCE = 'enforce'
    MERGE = 'merge'


class RenderRule(BaseModel):
    """Regex/literal substitution rule applied to template files during rendering.
    - When literal=True, use plain str.replace.
    - When literal=False, use re.sub with Python backrefs (\\1, \\2).
    """

    pattern: str
    replacement: str
    literal: bool = False

    model_config = ConfigDict(extra='forbid')


class ManagedPath(BaseModel):
    """File/dir pattern (POSIX-style) and strategy.
    Supports '**' and trailing '/**' directory globs, e.g.:
      - "pyproject.toml"
      - ".github/workflows/**"
      - "src/**"
    """

    path: str
    strategy: Strategy

    model_config = ConfigDict(extra='forbid')

    @field_serializer('strategy')
    def serialize_strategy(self, strategy: Strategy) -> str:
        """Serialize Strategy enum as string value."""
        return strategy.value


# -----------------------
# Root lockfile
# -----------------------


class RetemplarLock(BaseModel):
    """Retemplar lockfile configuration.

    Key fields:
    - template_ref: Full template reference (e.g., 'rat:gh:org/repo@v1.0')
    - template: Parsed template object (use template.ref for version)
    - applied_ref: Version that was last successfully applied to this repo
    """

    schema_version: str = '0.1.0'
    template_ref: str

    # Scope
    managed_paths: list[ManagedPath] = Field(default=[])
    ignore_paths: list[str] = Field(default=[])

    # Render rules (regex/literal replacements)
    render_rules: list[RenderRule] = Field(default=[])

    variables: dict[str, str] = Field(default_factory=dict)
    render_fingerprint: str | None = None

    # Applied state - what was last successfully applied to this repo
    applied_ref: str | None = None
    applied_commit: str | None = None

    # Future-proof (optional today):
    # baseline_ref: "git:<sha>" or "dir:<relpath>" — leave None for MVP.
    baseline_ref: str | None = None
    # consumer_commit: repo HEAD at time of apply (git only)
    consumer_commit: str | None = None

    model_config = ConfigDict(extra='forbid')

    @property
    def template(self) -> TemplateSource:
        """Parse template_ref into TemplateSource object."""
        return parse_template_ref(self.template_ref)

    # --- Validators / normalizers ---

    @field_validator('template_ref')
    @classmethod
    def _validate_template_ref(cls, v: str) -> str:
        """Validate template_ref format."""
        try:
            parse_template_ref(v)
            return v
        except TemplateRefParseError as e:
            raise ValueError(str(e)) from e

    @field_validator('managed_paths')
    @classmethod
    def _validate_no_duplicate_paths(
        cls,
        managed_paths: list[ManagedPath],
    ) -> list[ManagedPath]:
        # Check for duplicate paths
        paths = [mp.path for mp in managed_paths]
        if len(paths) != len(set(paths)):
            duplicates = {path for path in paths if paths.count(path) > 1}
            raise ValueError(
                f'Duplicate managed paths: {", ".join(duplicates)}',
            )
        return managed_paths

    @field_validator('baseline_ref')
    @classmethod
    def _validate_baseline_ref(cls, v: str | None) -> str | None:
        if v is None or v.startswith('dir:'):
            return v
        if v.startswith('git:') and len(v) > 4:
            return v
        raise ValueError("baseline_ref must be 'git:<sha>' or 'dir:<relpath>'")

    @model_validator(mode='after')
    def _sync_applied_state(self) -> 'RetemplarLock':
        """Initialize applied state from template on first adoption."""
        template = self.template

        # On first adopt, set applied state to match template
        if self.applied_ref is None:
            self.applied_ref = template.ref
        if self.applied_commit is None:
            self.applied_commit = template.commit

        return self
