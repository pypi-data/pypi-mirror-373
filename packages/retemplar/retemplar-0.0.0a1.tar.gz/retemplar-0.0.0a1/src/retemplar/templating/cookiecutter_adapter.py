# retemplar/templating/cookiecutter_adapter.py
"""Cookiecutter template adapter for retemplar.

This module provides cookiecutter-specific templating support while maintaining
a clean separation between cookiecutter-specific logic and general template management.

Architecture:
- CookiecutterPlan: Cookiecutter-specific data (items to render + context)
- TemplatePlan: Complete template plan (cookiecutter + raw files + fingerprint)

This design allows for future template engines (mustache, handlebars, etc.)
to be added alongside cookiecutter without breaking existing logic.
"""

import hashlib
import json
import runpy
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from retemplar.logging import get_logger
from retemplar.utils import fs_utils
from retemplar.utils.apply_utils import apply_file_changes_from_memory
from retemplar.utils.plan_utils import (
    ChangePlanItem,
    plan_file_changes_from_memory,
)

logger = get_logger(__name__)


@dataclass
class RenderItem:
    """Single file to render/copy from the template to the repo."""

    src_rel: str  # path relative to the inner template dir (may include {{ }})
    dst_rel: str  # final path relative to repo root (templated, .j2 stripped)
    is_text: bool  # True if we will render as text via Jinja, else copy bytes


@dataclass
class TemplateContext:
    """Template execution context - parameters used across cookiecutter operations."""

    tpl_root: Path
    dst_root: Path
    lock: Any  # RetemplarLock object
    variables: dict[str, Any]


@dataclass
class CookiecutterPlan:
    """Cookiecutter-specific rendering plan."""

    items: list[RenderItem]  # Files to be rendered by cookiecutter
    context: dict  # Cookiecutter context variables


@dataclass
class TemplatePlan:
    """Complete template plan including all rendering engines."""

    cookiecutter_plan: CookiecutterPlan
    fingerprint: str  # hash of (entire template + variables)
    rendered_files: dict[
        str,
        str | bytes,
    ]  # ALL template files (cookiecutter + raw)


# ------------- public API -------------


def plan_cookiecutter_template(
    ctx: TemplateContext,
) -> tuple[list[ChangePlanItem], int, TemplatePlan]:
    """Execute cookiecutter planning operation - does all the work once."""
    # Merge variables: lockfile < CLI
    lock_variables = getattr(ctx.lock, 'variables', {}) or {}
    all_variables = {**lock_variables, **ctx.variables}

    # Compute cookiecutter-specific plan (items + context)
    cookiecutter_plan = _compute_cookiecutter_plan(
        tpl_root=ctx.tpl_root,
        repo_root=ctx.dst_root,
        variables_cli=all_variables,
        variables_lock=lock_variables,
    )

    # Render cookiecutter files
    rendered_files_raw = _render_cookiecutter_outputs(
        ctx.tpl_root,
        cookiecutter_plan,
    )
    rendered_files = {str(k): v for k, v in rendered_files_raw.items()}

    # Also include raw files from template root that aren't part of cookiecutter
    all_template_files = _get_all_template_files(ctx.tpl_root, rendered_files)

    # Compute fingerprint for ALL template files (cookiecutter + raw)
    full_fingerprint = _compute_full_template_fingerprint(
        ctx.tpl_root,
        cookiecutter_plan.context,
    )

    # Create complete template plan with ALL template files
    template_plan = TemplatePlan(
        cookiecutter_plan=cookiecutter_plan,
        fingerprint=full_fingerprint,
        rendered_files=all_template_files,
    )

    # Get managed files from ALL template files (cookiecutter + raw)
    managed_files = fs_utils.get_managed_files_from_rendered(
        ctx.lock,
        all_template_files,
    )

    # Plan changes using all template content
    change_plan_items, conflicts = plan_file_changes_from_memory(
        managed_files,
        all_template_files,
        ctx.lock,
        ctx.dst_root,
    )

    return change_plan_items, conflicts, template_plan


def apply_cookiecutter_plan(
    plan_items: list[ChangePlanItem],
    template_plan: TemplatePlan,
    dst_root: Path,
    lock,
) -> tuple[int, int]:
    """Apply a pre-computed cookiecutter plan using pre-rendered files."""
    # Apply changes directly using the rendered content
    files_changed, conflicts_resolved = apply_file_changes_from_memory(
        plan_items,
        template_plan.rendered_files,
        dst_root,
        lock,
    )
    return files_changed, conflicts_resolved


# ------------- shared helpers -------------


def _compute_cookiecutter_plan(
    tpl_root: Path,
    repo_root: Path,
    *,
    variables_cli: Mapping[str, Any] = {},
    variables_lock: Mapping[str, Any] = {},
    exclude_hooks: bool = True,
) -> CookiecutterPlan:
    """Build a rendering plan for a Cookiecutter-like template repo."""
    tpl_root = tpl_root.resolve()
    repo_root = repo_root.resolve()

    inner_dir = _find_inner_template_dir(tpl_root)

    # Build Jinja environment for template rendering
    env = Environment(
        loader=FileSystemLoader(str(inner_dir)),
        undefined=StrictUndefined,  # fail fast on missing variables
        autoescape=False,
        keep_trailing_newline=True,
        lstrip_blocks=False,
        trim_blocks=False,
    )

    # Load cookiecutter.json defaults if present
    cc_json = tpl_root / 'cookiecutter.json'
    defaults = {}
    if cc_json.exists():
        try:
            defaults = json.loads(cc_json.read_text())
        except Exception:
            defaults = {}
    ctx = _merge_context(
        defaults=defaults,
        lock=variables_lock,
        cli=variables_cli,
    )

    pre_hook = tpl_root / 'hooks' / 'pre_gen_project.py'
    ctx = _run_hook(pre_hook, ctx)

    # Walk template tree and build items
    items: list[RenderItem] = []
    for path in inner_dir.rglob('*'):
        if path.is_dir():
            continue

        rel = path.relative_to(inner_dir).as_posix()

        # Skip hooks/ by default
        if exclude_hooks and rel.startswith('hooks/'):
            continue

        # Render filename and strip .j2 suffix
        dst_rel = env.from_string(rel).render(**ctx)
        dst_rel = dst_rel.removesuffix('.j2')

        # Detect text vs binary
        try:
            data = path.read_bytes()
            if len(data) > 512_000:  # Sample large files
                data = data[:512_000]
            data.decode('utf-8')
            is_text = True
        except Exception:
            is_text = False

        items.append(RenderItem(src_rel=rel, dst_rel=dst_rel, is_text=is_text))

    return CookiecutterPlan(
        items=items,
        context=ctx,
    )


def _render_cookiecutter_outputs(
    tpl_root: Path,
    plan: CookiecutterPlan,
) -> dict[Path, bytes | str]:
    """Render/copy all files described by `plan` and return a mapping:
      { Path(dst_rel) -> (str for text, bytes for binary) }

    Write with:
      if isinstance(v, str): out.write_text(v, encoding="utf-8")
      else:                  out.write_bytes(v)
    """
    inner_dir = _find_inner_template_dir(tpl_root)

    # Build Jinja environment for template rendering
    env = Environment(
        loader=FileSystemLoader(str(inner_dir)),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
        lstrip_blocks=False,
        trim_blocks=False,
    )

    outputs: dict[Path, bytes | str] = {}

    for item in plan.items:
        src = inner_dir / item.src_rel
        if item.is_text:
            # Render as text
            template = env.get_template(item.src_rel)
            rendered = template.render(**plan.context)
            outputs[Path(item.dst_rel)] = rendered  # str
        else:
            # Binary passthrough
            outputs[Path(item.dst_rel)] = src.read_bytes()  # bytes

    return outputs


def _merge_context(
    *,
    defaults: Mapping[str, Any],
    lock: Mapping[str, Any],
    cli: Mapping[str, Any],
) -> dict[str, Any]:
    """Simple variable precedence with template variable rendering."""
    # Start with defaults
    merged = dict(defaults or {})

    # Render template variables in defaults (like project_slug from project_name)
    _render_template_variables(merged)
    # Apply higher precedence values
    merged.update(lock or {})
    _render_template_variables(merged)
    merged.update(cli or {})
    _render_template_variables(merged)

    # Create context with both namespaced and flat access (cookiecutter compatibility)
    ctx = {'cookiecutter': dict(merged)}
    ctx.update(merged)

    return ctx


def _render_template_variables(variables: dict[str, Any]) -> None:
    """Render Jinja template variables within cookiecutter.json defaults."""
    # Multiple passes to handle dependent variables
    max_passes = 3  # Avoid infinite loops

    for _ in range(max_passes):
        changed = False
        temp_ctx = {'cookiecutter': dict(variables)}
        temp_ctx.update(variables)

        for key, value in list(variables.items()):
            if isinstance(value, str) and ('{{' in value or '{%' in value):
                try:
                    env = Environment(undefined=StrictUndefined)
                    rendered = env.from_string(value).render(**temp_ctx)
                    if rendered != value:  # Only update if it changed
                        variables[key] = rendered
                        changed = True
                except Exception:
                    # Keep original if rendering fails
                    pass

        # If nothing changed in this pass, we're done
        if not changed:
            break


def _compute_full_template_fingerprint(
    tpl_root: Path,
    context: dict[str, Any],
) -> str:
    """Compute fingerprint of entire template including raw files and context."""
    h = hashlib.sha256()

    # Hash the variables (excluding cookiecutter namespace duplicate)
    variables = {k: v for k, v in context.items() if k != 'cookiecutter'}
    h.update(json.dumps(variables, sort_keys=True).encode())

    # Hash ALL template files (not just cookiecutter inner directory)
    for file_path in sorted(fs_utils.list_files(tpl_root)):
        # Include cookiecutter.json in fingerprint (it affects rendering)
        # Skip hooks directory for consistency with cookiecutter behavior
        if file_path.startswith('hooks/'):
            continue

        h.update(file_path.encode())
        full_path = tpl_root / file_path
        try:
            h.update(full_path.read_bytes())
        except Exception:
            h.update(b'<unreadable>')

    return h.hexdigest()


def _get_all_template_files(
    tpl_root: Path,
    rendered_files: dict[str, str | bytes],
) -> dict[str, str | bytes]:
    """Combine cookiecutter-rendered files with raw files from template root."""
    all_files = dict(rendered_files)  # Start with cookiecutter rendered files

    # Add raw files from template root that aren't in cookiecutter structure
    for file_path in fs_utils.list_files(tpl_root):
        # Skip cookiecutter.json and hooks directory
        if file_path == 'cookiecutter.json' or file_path.startswith('hooks/'):
            continue

        # Skip files that are inside the inner template directory (already rendered)
        inner_dir = _find_inner_template_dir(tpl_root)
        if inner_dir != tpl_root:
            inner_rel = inner_dir.relative_to(tpl_root)
            if file_path.startswith(str(inner_rel) + '/'):
                continue

        # This is a raw file - include it as-is
        full_path = tpl_root / file_path
        try:
            # Try to read as text first
            content = full_path.read_text(encoding='utf-8')
            all_files[file_path] = content
        except UnicodeDecodeError:
            # Fall back to binary
            content = full_path.read_bytes()
            all_files[file_path] = content

    return all_files


def _find_inner_template_dir(tpl_root: Path) -> Path:
    """Cookiecutter repos typically have a single top-level dir named like
    `{{cookiecutter.project_slug}}/` that contains the actual files.

    - If found, return that dir.
    - Else, fall back to the repo root (tolerant).
    """
    try:
        for p in tpl_root.iterdir():
            if p.is_dir() and ('{{' in p.name and '}}' in p.name):
                return p
    except FileNotFoundError:
        pass
    # No brace-named folder; try to pick a single subdir if only one exists
    subdirs = [p for p in tpl_root.iterdir() if p.is_dir()]
    if len(subdirs) == 1:
        return subdirs[0]
    # Fallback: use root
    return tpl_root


def _run_hook(hook_file: Path, ctx: dict) -> dict:
    """Run a Cookiecutter pre/post hook and return a new context.

    - Injects `cookiecutter` dict into globals.
    - Hook mutates that dict.
    - After execution, re-syncs flat keys.
    """
    if not hook_file.exists():
        return ctx

    hook_env = {'cookiecutter': dict(ctx['cookiecutter'])}
    runpy.run_path(str(hook_file), init_globals=hook_env)

    return {
        **ctx,
        'cookiecutter': hook_env['cookiecutter'],
        **hook_env['cookiecutter'],
    }
