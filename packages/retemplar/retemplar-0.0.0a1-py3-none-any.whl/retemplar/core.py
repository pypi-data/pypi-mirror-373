# src/retemplar/core.py
"""Core retemplar operations (MVP)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from retemplar.lockfile import LockfileManager, LockfileNotFoundError
from retemplar.logging import RetemplarError, get_logger
from retemplar.schema import (
    RetemplarLock,
    TemplateRefParseError,
    parse_template_ref,
)
from retemplar.templating.cookiecutter_adapter import (
    TemplateContext,
    apply_cookiecutter_plan,
    plan_cookiecutter_template,
)
from retemplar.utils import fs_utils, merge_utils
from retemplar.utils.plan_utils import ChangePlanItem

logger = get_logger(__name__)


@dataclass
class PlanResult:
    """Result of plan_upgrade operation."""

    current_version: str
    target_version: str
    changes: list[ChangePlanItem]
    conflicts: int
    block_protection: list[dict[str, Any]]
    template_fingerprint: str
    template_plan: Any  # TemplatePlan from cookiecutter_adapter


@dataclass
class ApplyResult:
    """Result of apply_changes operation."""

    applied_version: str
    files_changed: int
    conflicts_resolved: int
    template_fingerprint: str


class RetemplarCore:
    """Core orchestrator for retemplar operations (refactored MVP)."""

    repo_path: Path

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def adopt_template(
        self,
        lock: RetemplarLock,
        dry_run: bool = False,
    ) -> dict[str, str | list | bool]:
        """Create initial .retemplar.lock (no baseline yet)."""
        logger.debug(
            'adopt_template_started',
            template_ref=lock.template_ref,
            dry_run=dry_run,
            managed_paths_count=len(lock.managed_paths),
        )

        with LockfileManager(self.repo_path) as lockfile_manager:
            if lockfile_manager.exists():
                raise RetemplarError(
                    'Repository already has .retemplar.lock',
                    repo_path=str(self.repo_path),
                )

            if not dry_run:
                try:
                    lockfile_manager.write(lock)
                    logger.debug('lockfile_created')
                except Exception as e:
                    raise RetemplarError(
                        'Failed to create lockfile',
                        repo_path=str(self.repo_path),
                        error=str(e),
                    ) from e

        return {
            'template': lock.template_ref,
            'managed_paths': [mp.path for mp in lock.managed_paths],
            'ignore_paths': lock.ignore_paths,
            'render_rules': lock.render_rules,
            'lockfile_created': not dry_run,
        }

    def plan_upgrade(
        self,
        target_ref: str,
        variables: dict[str, str] = {},
    ) -> PlanResult:
        """Compute a human-readable plan using cookiecutter rendering."""
        logger.debug('plan_upgrade_started', target_ref=target_ref)

        with LockfileManager(self.repo_path) as lockfile_manager:
            if not lockfile_manager.exists():
                raise LockfileNotFoundError(
                    "No .retemplar.lock found. Run 'retemplar adopt' first.",
                )

            lock = lockfile_manager.read()
            logger.debug(
                'lockfile_loaded',
                current_ref=lock.template_ref,
                managed_paths_count=len(lock.managed_paths),
            )

            try:
                target_src = parse_template_ref(target_ref)
            except TemplateRefParseError as e:
                if not target_ref:
                    raise ValueError('target_ref is required for plan') from e
                raise
            tpl_root = fs_utils.resolve_template_path(target_src.repo)

            # Use cookiecutter planning - this shows what WOULD happen
            ctx = TemplateContext(
                tpl_root=tpl_root,
                dst_root=self.repo_path,
                lock=lock,
                variables=variables,
            )
            items, conflicts, template_plan = plan_cookiecutter_template(ctx)

            block_events = merge_utils.scan_block_protection(
                lock.managed_paths or [],
                self.repo_path,
            )

            return PlanResult(
                current_version=lock.template_ref,
                target_version=target_ref,
                changes=items,
                conflicts=conflicts,
                block_protection=block_events,
                template_fingerprint=template_plan.fingerprint,
                template_plan=template_plan,
            )

    def apply_plan(
        self,
        plan_result: PlanResult,
        target_ref: str,
    ) -> ApplyResult:
        """Apply a pre-computed plan."""
        logger.debug(
            'apply_plan_started',
            target_ref=target_ref,
            changes_count=len(plan_result.changes),
        )

        with LockfileManager(self.repo_path) as lockfile_manager:
            if not lockfile_manager.exists():
                raise LockfileNotFoundError(
                    "No .retemplar.lock found. Run 'retemplar adopt' first.",
                )

            lock = lockfile_manager.read()
            try:
                target_src = parse_template_ref(target_ref)
            except TemplateRefParseError as e:
                if not target_ref:
                    raise ValueError('target_ref is required for apply') from e
                raise

            # Apply the planned changes using pre-rendered files
            files_changed, conflicts_resolved = apply_cookiecutter_plan(
                plan_items=plan_result.changes,
                template_plan=plan_result.template_plan,
                dst_root=self.repo_path,
                lock=lock,
            )

            # Update lockfile after successful apply
            self._update_lockfile_after_apply(
                lockfile_manager,
                lock,
                target_ref,
                target_src,
                plan_result.template_fingerprint,
            )

        return ApplyResult(
            applied_version=target_ref,
            files_changed=files_changed,
            conflicts_resolved=conflicts_resolved,
            template_fingerprint=plan_result.template_fingerprint,
        )

    def apply_changes(
        self,
        target_ref: str,
        dry_run: bool = False,
        variables: dict[str, str] = {},
    ) -> ApplyResult:
        """Convenience method: plan + apply in one call."""
        logger.debug(
            'apply_changes_started',
            target_ref=target_ref,
            dry_run=dry_run,
        )

        # Get the plan first
        plan_result = self.plan_upgrade(target_ref, variables)

        if dry_run:
            # For dry run, just return metrics from the plan
            return ApplyResult(
                applied_version=target_ref,
                files_changed=len(plan_result.changes),
                conflicts_resolved=0,  # Planning doesn't resolve conflicts
                template_fingerprint=plan_result.template_fingerprint,
            )

        # For actual application, apply the plan
        return self.apply_plan(plan_result, target_ref)

    def _update_lockfile_after_apply(
        self,
        lockfile_manager: LockfileManager,
        lock: RetemplarLock,
        target_ref: str,
        target_src,
        render_fingerprint: str,
    ) -> None:
        """Update lockfile after successful apply."""
        try:
            updated = lock.model_copy(
                update={
                    'template_ref': target_ref,
                    'applied_ref': target_src.ref,
                    'applied_commit': target_src.commit,
                    'render_fingerprint': render_fingerprint,
                },
            )
            lockfile_manager.write(updated)
            logger.debug(
                'lockfile_updated_after_apply',
                target_ref=target_ref,
                fingerprint=render_fingerprint,
            )
        except Exception as e:
            raise RetemplarError(
                'Failed to update lockfile after applying changes - manual intervention required',
                target_ref=target_ref,
                error=str(e),
                repo_path=str(self.repo_path),
            ) from e

    def detect_drift(self) -> dict[str, str | list]:
        """Detect drift between repo and baseline (placeholder for 3-way)."""
        logger.debug('detect_drift_started')

        with LockfileManager(self.repo_path) as lockfile_manager:
            if not lockfile_manager.exists():
                raise LockfileNotFoundError(
                    "No .retemplar.lock found. Run 'retemplar adopt' first.",
                )

            current_lock = lockfile_manager.read()
            logger.debug(
                'lockfile_loaded_for_drift',
                current_ref=current_lock.template_ref,
                applied_ref=current_lock.applied_ref,
            )

        # TODO: Real implementation needs:
        # - Baseline resolution from applied_ref
        # - 3-way comparison: Base vs Ours vs Theirs
        # - Categorization of changes (template-only, local-only, conflicts)

        return {
            'baseline_version': current_lock.applied_ref
            or getattr(current_lock.template, 'ref', 'unknown'),
            'template_only_changes': [],  # TODO: implement with baseline
            'local_only_changes': [],  # TODO: implement with baseline
            'conflicts': [],  # TODO: implement with baseline
            'unmanaged_files': [],  # TODO: implement
        }
