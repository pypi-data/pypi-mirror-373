# src/retemplar/cli.py
"""Minimal retemplar CLI (Typer, MVP)

Commands:
- adopt : attach a repo to a template/ref and create `.retemplar.lock`
- plan  : compute template delta (old → new), cheap structural preview
- apply : apply template changes (conflict markers for merge)
- drift : report drift (stub until 3-way baseline)
"""

import json
import traceback
from dataclasses import asdict
from pathlib import Path

import typer
from rich.console import Console

from retemplar.core import RetemplarCore
from retemplar.lockfile import LockfileError
from retemplar.logging import RetemplarError, get_logger, setup_logging
from retemplar.schema import ManagedPath, RenderRule, RetemplarLock, Strategy

logger = get_logger(__name__)

app = typer.Typer(
    add_completion=False,
    help='Fleet-scale repository templating (RAT).',
)
console = Console()


# ----------------------------
# Global context
# ----------------------------


class Ctx:
    """Global context for CLI commands."""

    def __init__(
        self,
        repo_path: Path,
        verbose: bool,
        debug: bool,
        json_mode: bool,
    ):
        self.repo_path = repo_path
        self.verbose = verbose
        self.debug = debug
        self.json_mode = json_mode


@app.callback()
def main(
    ctx: typer.Context,
    repo: Path = typer.Option(
        Path(),
        '--repo',
        '-R',
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help='Path to the target repository (default: current directory).',
    ),
    verbose: bool = typer.Option(
        False,
        '--verbose',
        '-v',
        help='Show INFO level logs (UX lifecycle events).',
    ),
    debug: bool = typer.Option(
        False,
        '--debug',
        help='Show DEBUG level logs (all internals).',
    ),
    json_mode: bool = typer.Option(
        False,
        '--json',
        help='Output JSON logs instead of Rich formatting (for CI).',
    ),
):
    """Fleet-scale repository templating (RAT)."""
    setup_logging(verbose=verbose, debug=debug, json_mode=json_mode)
    ctx.obj = Ctx(
        repo_path=repo,
        verbose=verbose,
        debug=debug,
        json_mode=json_mode,
    )


def _print_json(data) -> None:
    try:
        console.print_json(data=data)
    except Exception:
        console.print(json.dumps(data, indent=2))


def _parse_variables(var: list[str]) -> dict[str, str]:
    """Parse --var key=value pairs into dictionary."""
    variables = {}
    for var_pair in var:
        if '=' not in var_pair:
            console.print(
                f'[red]Error:[/red] Invalid variable format "{var_pair}". Use --var key=value',
            )
            raise typer.Exit(1)
        key, value = var_pair.split('=', 1)
        variables[key.strip()] = value.strip()
    return variables


def _handle_error(e: Exception, ctx_obj: Ctx) -> None:
    """Handle errors with single user-facing message + structured logging."""
    # Always show clean error to user
    console.print(f'[bold red]Error:[/bold red] {e}')

    # Only log structured error in debug mode (for CI/telemetry in debug builds)
    if ctx_obj.debug:
        if isinstance(e, RetemplarError):
            e.log_structured(logger)
        elif isinstance(e, LockfileError):
            logger.error(
                'lockfile_error',
                error=str(e),
                error_type=type(e).__name__,
            )
        else:
            logger.error(
                'unexpected_error',
                error=str(e),
                error_type=type(e).__name__,
            )

        # Show traceback in debug mode
        console.print('[dim]' + traceback.format_exc() + '[/dim]')

    raise typer.Exit(1)


def _parse_render_opts(opts: list[str]) -> list[RenderRule]:
    """Parse --render specs like FROM:TO or re:PATTERN:TO"""
    rules: list[RenderRule] = []
    for spec in opts:
        if spec.startswith('re:'):
            body = spec[3:]
            if ':' not in body:
                raise typer.BadParameter(
                    f"Regex rule must be 're:PATTERN:REPLACEMENT': {spec}",
                )
            pattern, replacement = body.split(':', 1)
            rules.append(
                RenderRule(
                    pattern=pattern,
                    replacement=replacement,
                    literal=False,
                ),
            )
        else:
            if ':' not in spec:
                raise typer.BadParameter(
                    f"Render rule must be 'FROM:TO' or 're:PATTERN:TO': {spec}",
                )
            pattern, replacement = spec.split(':', 1)
            rules.append(
                RenderRule(
                    pattern=pattern,
                    replacement=replacement,
                    literal=True,
                ),
            )
    return rules


# ----------------------------
# Commands
# ----------------------------


@app.command()
def adopt(
    ctx: typer.Context,
    template: str = typer.Option(
        ...,
        '--template',
        '-t',
        help="Template source, e.g. 'rat:./template-dir@v0'.",
    ),
    managed: list[str] = typer.Option(
        [],
        '--managed',
        '-m',
        help='Glob(s) or path(s) to manage. Repeatable.',
    ),
    ignore: list[str] = typer.Option(
        [],
        '--ignore',
        '-i',
        help='Glob(s) or path(s) to ignore. Repeatable.',
    ),
    render: list[str] = typer.Option(
        [],
        '--render',
        '-r',
        help='Render rule (FROM:TO or re:PATTERN:TO). Repeatable.',
    ),
):
    """Attach the repo to a template/ref and create `.retemplar.lock`."""
    try:
        logger.info('adopt_started', template=template)

        render_rules = _parse_render_opts(render)
        managed_paths_objs = [
            ManagedPath(path=path, strategy=Strategy.ENFORCE)
            for path in managed
        ]

        lock = RetemplarLock(
            template_ref=template,
            managed_paths=managed_paths_objs,
            ignore_paths=ignore,
            render_rules=render_rules,
        )

        core = RetemplarCore(ctx.obj.repo_path)
        core.adopt_template(lock)

        logger.info('adopt_completed', template=template)
        console.print(f'[green]✓[/green] Adopted template: {template}')
        console.print(
            f'[dim]Created .retemplar.lock in {ctx.obj.repo_path}[/dim]',
        )
    except Exception as e:
        _handle_error(e, ctx.obj)


@app.command()
def plan(
    ctx: typer.Context,
    to: str = typer.Option(
        ...,
        '--to',
        help="Target template ref/version, e.g. 'rat:./template-dir@v1'.",
    ),
):
    """Preview structural upgrade plan (cheap, no file diffs)."""
    try:
        logger.info('plan_started', target_ref=to)

        core = RetemplarCore(ctx.obj.repo_path)
        plan_result = core.plan_upgrade(target_ref=to)

        logger.info(
            'plan_completed',
            target_ref=to,
            changes_count=len(plan_result.changes),
            conflicts_count=plan_result.conflicts,
        )

        _print_json(asdict(plan_result))
    except Exception as e:
        _handle_error(e, ctx.obj)


@app.command()
def apply(
    ctx: typer.Context,
    to: str = typer.Option(
        ...,
        '--to',
        help='Target template ref/version to apply.',
    ),
    dry_run: bool = typer.Option(
        False,
        '--dry-run',
        help='Preview actual changes and conflicts.',
    ),
    var: list[str] = typer.Option(
        [],
        '--var',
        help='Override template variables (e.g., --var key=value).',
    ),
):
    """Apply template changes (with content merge)."""
    try:
        # Parse variable overrides
        variables = _parse_variables(var)

        if dry_run:
            logger.info(
                'apply_dry_run_started',
                target_ref=to,
                variables_count=len(variables),
            )
            console.print('[yellow][dry-run][/yellow] Previewing changes...')
        else:
            logger.info(
                'apply_started',
                target_ref=to,
                variables_count=len(variables),
            )

        core = RetemplarCore(ctx.obj.repo_path)
        result = core.apply_changes(
            target_ref=to,
            dry_run=dry_run,
            variables=variables,
        )

        if dry_run:
            logger.info('apply_dry_run_completed', target_ref=to)
            _print_json(asdict(result))
        else:
            logger.info(
                'apply_completed',
                target_ref=to,
                files_changed=result.files_changed,
                conflicts_resolved=result.conflicts_resolved,
            )

            console.print('[green]✓[/green] Applied template changes')
            if result.conflicts_resolved > 0:
                console.print(
                    f'[yellow]![/yellow] {result.conflicts_resolved} file(s) contain conflict markers',
                )
    except Exception as e:
        _handle_error(e, ctx.obj)


@app.command()
def drift(
    ctx: typer.Context,
    as_json: bool = typer.Option(
        False,
        '--json',
        help='Emit machine-readable drift JSON.',
    ),
):
    """Report drift between the lockfile baseline and current repo (stub)."""
    console.print(
        'Drift detection is a work in progress.',
        style='white on red',
    )

    try:
        logger.info('drift_started')

        core = RetemplarCore(ctx.obj.repo_path)
        drift_result = core.detect_drift()

        logger.info(
            'drift_completed',
            baseline_version=drift_result.get('baseline_version'),
        )

        if as_json:
            _print_json(drift_result)
        else:
            console.print('[bold]Drift Report (MVP):[/bold]')
            _print_json(drift_result)
    except Exception as e:
        _handle_error(e, ctx.obj)


@app.command()
def version() -> None:
    """Print retemplar version."""
    try:
        from importlib.metadata import version as _pkg_version

        typer.echo(f'retemplar {_pkg_version("retemplar")}')
    except Exception:
        typer.echo('retemplar 0.0.1')


def _main() -> None:
    app()


if __name__ == '__main__':
    _main()
