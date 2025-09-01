# src/retemplar/utils/plan_utils.py
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from retemplar.logging import get_logger
from retemplar.schema import Strategy
from retemplar.utils import fs_utils

logger = get_logger(__name__)


class ChangeKind(Enum):
    CREATE = 'create'
    OVERWRITE = 'overwrite'
    EDIT = 'edit'
    DELETE = 'delete'
    KEEP = 'keep'


@dataclass
class ChangePlanItem:
    path: str
    strategy: str  # "enforce" | "preserve" | "merge"
    kind: str  # "create" | "overwrite" | "edit" | "delete" | "keep"
    note: str = ''
    had_conflict: bool = False


# Planning utility functions (candidate for core planning module)
def plan_preserve_file(
    rel_path: str,
    strategy: str,
    in_tpl: bool,
    in_repo: bool,
) -> list[ChangePlanItem]:
    """Plan changes for preserve strategy."""
    if in_tpl and not in_repo:
        return [
            ChangePlanItem(
                rel_path,
                strategy,
                ChangeKind.CREATE.value,
                'template will create (preserve local thereafter)',
            ),
        ]
    return [
        ChangePlanItem(
            rel_path,
            strategy,
            ChangeKind.KEEP.value,
            'preserve local content',
        ),
    ]


def plan_enforce_file(
    rel_path: str,
    strategy: str,
    in_tpl: bool,
    in_repo: bool,
) -> list[ChangePlanItem]:
    """Plan changes for enforce strategy."""
    if in_tpl and in_repo:
        return [
            ChangePlanItem(
                rel_path,
                strategy,
                ChangeKind.OVERWRITE.value,
                'template will overwrite local file',
            ),
        ]
    if in_tpl and not in_repo:
        return [
            ChangePlanItem(
                rel_path,
                strategy,
                ChangeKind.CREATE.value,
                'template will create file',
            ),
        ]
    if not in_tpl and in_repo:
        return [
            ChangePlanItem(
                rel_path,
                strategy,
                ChangeKind.DELETE.value,
                'template removed file; will delete locally',
            ),
        ]
    return []


def plan_merge_file_from_memory(
    rel_path: str,
    strategy: str,
    in_tpl: bool,
    in_repo: bool,
    rendered_content: str | bytes | None,
    dst_root: Path,
    render_rules,
) -> tuple[list[ChangePlanItem], int]:
    """Plan changes for merge strategy using pre-rendered content."""
    conflicts = 0

    if in_tpl and in_repo:
        ours = fs_utils.read_text(dst_root / rel_path)
        theirs = rendered_content if isinstance(rendered_content, str) else None

        if ours is None or theirs is None:
            had_conflict = True  # binary/unreadable
        else:
            had_conflict = ours != theirs

        if had_conflict:
            conflicts += 1

        return [
            ChangePlanItem(
                rel_path,
                strategy,
                ChangeKind.EDIT.value,
                'merge changes',
                had_conflict=had_conflict,
            ),
        ], conflicts

    if in_tpl and not in_repo:
        return [
            ChangePlanItem(
                rel_path,
                strategy,
                ChangeKind.CREATE.value,
                'template adds file; adopt it',
            ),
        ], conflicts

    if not in_tpl and in_repo:
        return [
            ChangePlanItem(
                rel_path,
                strategy,
                ChangeKind.DELETE.value,
                'template removed file; will delete',
            ),
        ], conflicts

    return [], conflicts


def plan_file_changes_from_memory(
    managed_files: dict,
    rendered_files: dict[str, str | bytes],
    lock,
    dst_root: Path,
) -> tuple[list[ChangePlanItem], int]:
    """Plan changes for each managed file using pre-rendered content."""
    logger.debug(
        'plan_file_changes_from_memory',
        managed_files_count=len(managed_files),
    )

    items: list[ChangePlanItem] = []
    conflicts = 0

    for rel_path, rule in managed_files.items():
        strategy = rule.strategy
        in_tpl = rel_path in rendered_files
        in_repo = (dst_root / rel_path).exists()

        if strategy == Strategy.PRESERVE.value:
            items.extend(
                plan_preserve_file(rel_path, strategy, in_tpl, in_repo),
            )
        elif strategy == Strategy.ENFORCE.value:
            items.extend(plan_enforce_file(rel_path, strategy, in_tpl, in_repo))
        else:  # strategy == "merge"
            merge_items, merge_conflicts = plan_merge_file_from_memory(
                rel_path,
                strategy,
                in_tpl,
                in_repo,
                rendered_files.get(rel_path),
                dst_root,
                lock.render_rules,
            )
            items.extend(merge_items)
            conflicts += merge_conflicts

    return items, conflicts
