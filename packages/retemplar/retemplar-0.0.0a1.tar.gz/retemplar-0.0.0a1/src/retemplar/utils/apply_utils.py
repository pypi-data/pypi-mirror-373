# src/retemplar/utils/apply_utils.py
import shutil
import tempfile
from pathlib import Path

from retemplar.logging import get_logger
from retemplar.utils import fs_utils, merge_utils
from retemplar.utils.blockprotect import enforce_ours_blocks
from retemplar.utils.plan_utils import ChangeKind

logger = get_logger(__name__)


def apply_file_changes_from_memory(
    changes: list,  # List of PlanItem objects
    rendered_files: dict[str, str | bytes],  # Pre-rendered file contents
    dst_root: Path,
    lock,
) -> tuple[int, int]:
    """Apply changes using pre-rendered files from memory."""
    # Create a single temporary directory for the apply operation
    temp_dir = tempfile.mkdtemp()
    temp_root = Path(temp_dir)

    try:
        # Write rendered files to temp directory once
        for dst_path_str, content in rendered_files.items():
            full_path = temp_root / dst_path_str
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, str):
                full_path.write_text(content, encoding='utf-8')
            else:
                full_path.write_bytes(content)

        # Apply changes directly
        files_changed = 0
        conflicts = 0

        for change in changes:
            relative_path = change.path
            strategy = change.strategy
            change_kind = change.kind

            if strategy == 'preserve':
                if apply_preserve_change(
                    relative_path,
                    change_kind,
                    temp_root,
                    dst_root,
                    lock,
                    False,  # dry_run=False
                ):
                    files_changed += 1
            elif strategy == 'enforce':
                if apply_enforce_change(
                    relative_path,
                    change_kind,
                    temp_root,
                    dst_root,
                    lock,
                    False,  # dry_run=False
                ):
                    files_changed += 1
            else:  # strategy == "merge"
                changed, conflict_count = apply_merge_change(
                    relative_path,
                    change_kind,
                    temp_root,
                    dst_root,
                    lock,
                    False,  # dry_run=False
                )
                if changed:
                    files_changed += 1
                conflicts += conflict_count

        return files_changed, conflicts
    finally:
        shutil.rmtree(temp_root)


def apply_preserve_change(
    relative_path: str,
    change_kind: str,
    tpl_root: Path,
    dst_root: Path,
    lock,
    dry_run: bool,
) -> bool:
    """Apply preserve strategy change."""
    dst_file = dst_root / relative_path
    tpl_file = tpl_root / relative_path

    if change_kind == ChangeKind.CREATE.value and not dst_file.exists():
        if not dry_run:
            merge_utils.copy_with_render_and_blockprotect(
                tpl_file,
                dst_file,
                lock.render_rules,
                dst_root,
            )
        return True
    return False


def apply_enforce_change(
    relative_path: str,
    change_kind: str,
    tpl_root: Path,
    dst_root: Path,
    lock,
    dry_run: bool,
) -> bool:
    """Apply enforce strategy change."""
    dst_file = dst_root / relative_path
    tpl_file = tpl_root / relative_path

    if change_kind in (ChangeKind.CREATE.value, ChangeKind.OVERWRITE.value):
        if not dry_run:
            merge_utils.copy_with_render_and_blockprotect(
                tpl_file,
                dst_file,
                lock.render_rules,
                dst_root,
            )
        return True
    if change_kind == ChangeKind.DELETE.value:
        if not dry_run:
            dst_file.unlink(missing_ok=True)
        return True
    return False


def apply_merge_change(
    relative_path: str,
    change_kind: str,
    tpl_root: Path,
    dst_root: Path,
    lock,
    dry_run: bool,
) -> tuple[bool, int]:
    """Apply merge strategy change."""
    dst_file = dst_root / relative_path
    tpl_file = tpl_root / relative_path

    if change_kind == ChangeKind.CREATE.value:
        if not dry_run:
            merge_utils.copy_with_render_and_blockprotect(
                tpl_file,
                dst_file,
                lock.render_rules,
                dst_root,
            )
        return True, 0

    if change_kind == ChangeKind.DELETE.value:
        if not dry_run:
            dst_file.unlink(missing_ok=True)
        return True, 0

    if change_kind == ChangeKind.EDIT.value:
        return apply_merge_edit(
            relative_path,
            dst_file,
            tpl_file,
            lock,
            dry_run,
        )

    return False, 0


def apply_merge_edit(
    relative_path: str,
    dst_file: Path,
    tpl_file: Path,
    lock,
    dry_run: bool,
) -> tuple[bool, int]:
    """Apply merge edit with conflict resolution."""
    try:
        ours = fs_utils.read_text(dst_file)
        theirs = fs_utils.read_text(tpl_file)
    except OSError as e:
        logger.warning('file_read_failed', file=relative_path, error=str(e))
        return False, 1

    if ours is None or theirs is None:
        logger.info('binary_merge_skipped', file=relative_path)
        return False, 1

    try:
        if lock.render_rules:
            theirs = merge_utils.apply_render_rules_text(
                theirs,
                lock.render_rules,
            )
    except (ValueError, OSError) as e:
        logger.error('render_rules_failed', file=relative_path, error=str(e))
        return False, 1

    if ours == theirs:
        return False, 0  # No change needed

    try:
        # Perform merge with conflict markers
        merged = merge_utils.merge_with_conflicts(ours, theirs)
        final, _ = enforce_ours_blocks(ours, merged)

        if not dry_run:
            fs_utils.write_text(dst_file, final)
    except (OSError, ValueError) as e:
        logger.error('file_merge_failed', file=relative_path, error=str(e))
        return False, 1

    return True, 1
