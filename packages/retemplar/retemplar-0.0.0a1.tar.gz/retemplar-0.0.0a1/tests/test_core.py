"""Tests for RetemplarCore operations."""

from pathlib import Path

import pytest

from retemplar.core import RetemplarCore
from retemplar.lockfile import LockfileNotFoundError
from retemplar.logging import RetemplarError
from retemplar.schema import ManagedPath, RetemplarLock, Strategy


@pytest.fixture
def core(tmp_path: Path) -> RetemplarCore:
    """Create RetemplarCore instance for testing."""
    return RetemplarCore(tmp_path)


@pytest.fixture
def mock_template_dir(tmp_path: Path) -> Path:
    """Create a mock cookiecutter template directory with test files."""
    template_dir = tmp_path / 'template'
    template_dir.mkdir()

    # Create cookiecutter.json
    import json

    cookiecutter_json = {'project_name': 'Test Project', 'version': '1.0.0'}
    (template_dir / 'cookiecutter.json').write_text(
        json.dumps(cookiecutter_json),
    )

    # Create inner template directory
    inner_dir = template_dir / '{{cookiecutter.project_name}}'
    inner_dir.mkdir()

    # Create template files inside the inner directory
    (inner_dir / 'README.md').write_text(
        '# {{cookiecutter.project_name}} README\nThis is version {{cookiecutter.version}}.',
    )
    (inner_dir / 'src').mkdir()
    (inner_dir / 'src' / 'main.py').write_text(
        "# {{cookiecutter.project_name}} main.py\nprint('hello from {{cookiecutter.project_name}}')",
    )
    return template_dir


@pytest.fixture(autouse=True)
def mock_template_path(monkeypatch, mock_template_dir):
    """Auto-mock template path resolution to use test template directory."""
    from retemplar.utils import fs_utils

    # Mock template resolution to use test template directory
    monkeypatch.setattr(
        fs_utils,
        'resolve_template_path',
        lambda repo: mock_template_dir,
    )


@pytest.fixture
def sample_lock() -> RetemplarLock:
    """Create sample lock for testing."""
    return RetemplarLock(
        template_ref='rat:local:acme/main-svc@v2025.08.01',
        managed_paths=[
            ManagedPath(path='README.md', strategy=Strategy.ENFORCE),
            ManagedPath(path='src/**', strategy=Strategy.MERGE),
        ],
        variables={'project_name': 'Test Project', 'version': '1.0.0'},
    )


# --- adopt_template ----------------------------------------------------------


def test_adopt_template_success(
    core: RetemplarCore,
    sample_lock: RetemplarLock,
):
    """Test successful template adoption."""
    result = core.adopt_template(sample_lock)

    assert result['template'] == 'rat:local:acme/main-svc@v2025.08.01'
    assert result['lockfile_created'] is True
    assert result['managed_paths'] == ['README.md', 'src/**']

    # Verify lockfile was actually created
    assert (core.repo_path / '.retemplar.lock').exists()


def test_adopt_template_already_exists(
    core: RetemplarCore,
    sample_lock: RetemplarLock,
):
    """Test adoption fails when lockfile already exists."""
    # Create existing lockfile
    (core.repo_path / '.retemplar.lock').write_text('existing')

    with pytest.raises(
        RetemplarError,
        match='Repository already has .retemplar.lock',
    ):
        core.adopt_template(sample_lock)


def test_adopt_template_lockfile_write_error(
    core: RetemplarCore,
    sample_lock: RetemplarLock,
    monkeypatch,
):
    """Test adoption handles lockfile write errors."""
    from retemplar.lockfile import LockfileManager

    def mock_write(self, lock):
        raise OSError('Permission denied')

    monkeypatch.setattr(LockfileManager, 'write', mock_write)

    with pytest.raises(RetemplarError, match='Failed to create lockfile'):
        core.adopt_template(sample_lock)


# --- plan_upgrade ------------------------------------------------------------


def test_plan_upgrade_no_lockfile(core: RetemplarCore):
    """Test plan fails when no lockfile exists."""
    with pytest.raises(LockfileNotFoundError, match='No .retemplar.lock found'):
        core.plan_upgrade('rat:local:acme/main-svc@v2025.09.01')


def test_plan_upgrade_success(core: RetemplarCore, sample_lock: RetemplarLock):
    """Test successful upgrade planning with real mock template."""
    # Create lockfile first
    core.adopt_template(sample_lock)

    result = core.plan_upgrade('rat:local:acme/main-svc@v2025.09.01')

    # Verify the basic plan structure
    assert result.current_version == 'rat:local:acme/main-svc@v2025.08.01'
    assert result.target_version == 'rat:local:acme/main-svc@v2025.09.01'
    assert isinstance(result.changes, list)
    assert isinstance(result.conflicts, int)
    assert isinstance(result.block_protection, list)
    assert hasattr(result, 'template_fingerprint')

    # Should have at least one change for the managed files
    assert len(result.changes) > 0

    # Verify changes have expected structure
    if result.changes:
        change = result.changes[0]
        assert hasattr(change, 'path')
        assert hasattr(change, 'strategy')
        assert hasattr(change, 'kind')


# --- apply_changes -----------------------------------------------------------


def test_apply_changes_no_lockfile(core: RetemplarCore):
    """Test apply fails when no lockfile exists."""
    with pytest.raises(LockfileNotFoundError, match='No .retemplar.lock found'):
        core.apply_changes('rat:local:acme/main-svc@v2025.09.01')


def test_apply_changes_no_target_ref(
    core: RetemplarCore,
    sample_lock: RetemplarLock,
):
    """Test apply fails when no target ref provided."""
    # Create lockfile first
    core.adopt_template(sample_lock)

    with pytest.raises(ValueError, match='target_ref is required'):
        core.apply_changes('')


def test_apply_changes_success(core: RetemplarCore, sample_lock: RetemplarLock):
    """Test successful changes application with real template."""
    # Create lockfile first
    core.adopt_template(sample_lock)

    # Create some local files that will be updated (in the temp repo directory)
    (core.repo_path / 'README.md').write_text('# Old README\nOld content.')

    result = core.apply_changes('rat:local:acme/main-svc@v2025.09.01')

    # Verify the apply results
    assert result.applied_version == 'rat:local:acme/main-svc@v2025.09.01'
    assert hasattr(result, 'files_changed')
    assert hasattr(result, 'conflicts_resolved')

    # Verify lockfile was updated
    from retemplar.lockfile import LockfileManager

    with LockfileManager(core.repo_path) as manager:
        updated_lock = manager.read()
        assert (
            updated_lock.template_ref == 'rat:local:acme/main-svc@v2025.09.01'
        )


def test_apply_changes_lockfile_update_error(
    core: RetemplarCore,
    sample_lock: RetemplarLock,
    monkeypatch,
):
    """Test apply handles lockfile update errors."""
    # Create lockfile first
    core.adopt_template(sample_lock)

    # Mock lockfile write to fail
    from retemplar.lockfile import LockfileManager

    def mock_write(self, lock):
        raise OSError('Disk full')

    monkeypatch.setattr(LockfileManager, 'write', mock_write)

    with pytest.raises(
        RetemplarError,
        match='Failed to update lockfile after applying changes',
    ):
        core.apply_changes('rat:local:acme/main-svc@v2025.09.01')


# --- detect_drift ------------------------------------------------------------


def test_detect_drift_no_lockfile(core: RetemplarCore):
    """Test drift detection fails when no lockfile exists."""
    with pytest.raises(LockfileNotFoundError, match='No .retemplar.lock found'):
        core.detect_drift()


def test_detect_drift_success(core: RetemplarCore, sample_lock: RetemplarLock):
    """Test successful drift detection."""
    # Create lockfile first
    core.adopt_template(sample_lock)

    result = core.detect_drift()

    assert result['baseline_version'] == 'v2025.08.01'
    assert 'template_only_changes' in result
    assert 'local_only_changes' in result
    assert 'conflicts' in result
