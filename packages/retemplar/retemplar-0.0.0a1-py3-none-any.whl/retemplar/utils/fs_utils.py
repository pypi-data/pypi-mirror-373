# src/retemplar/utils/fs_utils.py
"""File system utilities for retemplar."""

from fnmatch import fnmatch
from pathlib import Path, PurePosixPath

import pathspec

from retemplar.constants import REPO_PREFIX_GITHUB, REPO_PREFIX_LOCAL
from retemplar.logging import get_logger
from retemplar.schema import RetemplarLock

logger = get_logger(__name__)


# =============================================================================
# Pure helpers (top of file)
# =============================================================================


def posix(p: Path | str) -> str:
    """Normalize path to POSIX string."""
    return PurePosixPath(str(p)).as_posix()


def match(path: str, pattern: str) -> bool:
    """Glob match with basic '**' support."""
    path = posix(path)
    pattern = posix(pattern)
    if pattern.endswith('/**'):
        return path == pattern[:-3] or path.startswith(pattern[:-3] + '/')
    return fnmatch(path, pattern)


def list_files(root: Path) -> list[str]:
    """All file paths under root (relative, POSIX)."""
    if not root.exists():
        return []

    files = []
    for path in root.rglob('*'):
        if path.is_file():
            rel_path = path.relative_to(root)
            files.append(posix(rel_path))
    return files


def read_text(path: Path) -> str | None:
    """Return file contents as text, or None if binary."""
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return None


def write_text(path: Path, text: str) -> None:
    """Write text to path, creating directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def delete_file(path: Path) -> None:
    if path.exists():
        path.unlink()
        # best-effort prune
        try:
            path.parent.rmdir()
        except OSError:
            pass


def expand_patterns(
    includes: list[str],
    excludes: list[str],
    tpl_root: Path,
) -> set[str]:
    """Expand include/exclude patterns (gitignore style) against cwd and tpl_root.
    Returns a set of matching *files*.
    """
    # Compile specs using gitwildmatch (gitignore-compatible)
    include_spec = pathspec.PathSpec.from_lines('gitwildmatch', includes)
    exclude_spec = pathspec.PathSpec.from_lines('gitwildmatch', excludes)

    files: set[str] = set()

    # Collect candidates from cwd and tpl_root
    for base in [tpl_root]:
        if not base.exists():
            continue
        for path in base.rglob('*'):
            if path.is_file():
                rel = path.relative_to(base).as_posix()
                if include_spec.match_file(rel) and not exclude_spec.match_file(
                    rel,
                ):
                    files.add(rel)

    return files


# =============================================================================
# Template loading
# =============================================================================


def get_managed_files_from_rendered(
    lock: RetemplarLock,
    rendered_files: dict[str, str | bytes],
) -> dict[str, object]:
    """Get files that match managed patterns from pre-rendered file paths."""
    managed_files = {}

    # Use pathspec for gitignore-style ignore patterns
    import pathspec

    ignore_spec = pathspec.PathSpec.from_lines(
        'gitwildmatch',
        lock.ignore_paths or [],
    )

    for file_path in rendered_files:
        # Check if file matches any managed pattern
        rule = next(
            (r for r in lock.managed_paths if match(file_path, r.path)),
            None,
        )
        if rule:
            # Check if file should be ignored using pathspec
            if not ignore_spec.match_file(file_path):
                managed_files[file_path] = rule

    return managed_files


def resolve_template_path(template_repo: str) -> Path:
    """Local folder only:
      - "./template-dir", "/abs/path", ".<something>/..."
    GH refs still TODO (raise).
    """
    if template_repo.startswith(REPO_PREFIX_LOCAL):
        return Path(template_repo[len(REPO_PREFIX_LOCAL) :]).resolve()
    if template_repo.startswith(REPO_PREFIX_GITHUB):
        raise NotImplementedError('GitHub repos not supported yet in MVP')
    raise ValueError(f'Unsupported repo format: {template_repo}')
