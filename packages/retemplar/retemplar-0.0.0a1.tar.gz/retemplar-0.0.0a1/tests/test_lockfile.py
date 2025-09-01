"""Tests for lockfile manager operations."""

from pathlib import Path

import pytest

from retemplar.lockfile import LockfileManager, LockfileNotFoundError
from retemplar.schema import ManagedPath, RetemplarLock, Strategy


def test_lockfile_manager_basic_operations(tmp_path: Path):
    """Test basic lockfile manager operations."""
    manager = LockfileManager(tmp_path)

    # Initial state
    assert manager.repo_root == tmp_path.resolve()
    assert not manager.exists()

    # Error when reading non-existent
    with pytest.raises(LockfileNotFoundError):
        manager.read()


def test_write_and_read_lockfile(tmp_path: Path):
    """Test writing and reading lockfile roundtrip."""
    manager = LockfileManager(tmp_path)

    lock = RetemplarLock(
        template_ref='rat:gh:acme/main-svc@v2025.08.01',
        managed_paths=[
            ManagedPath(path='src/**', strategy=Strategy.MERGE),
        ],
    )

    # Write
    manager.write(lock)
    assert manager.exists()

    # Read back
    read_lock = manager.read()
    assert read_lock.template.repo == 'gh:acme/main-svc'
    assert read_lock.template.ref == 'v2025.08.01'
    assert len(read_lock.managed_paths) == 1
    assert read_lock.managed_paths[0].path == 'src/**'


def test_validation(tmp_path: Path):
    """Test lockfile validation."""
    manager = LockfileManager(tmp_path)

    # Valid lockfile
    lock = RetemplarLock(template_ref='rat:gh:acme/main-svc@v2025.08.01')
    assert manager.validate(lock) == []

    # Invalid - duplicate paths
    lock.managed_paths = [
        ManagedPath(path='file.txt', strategy=Strategy.ENFORCE),
        ManagedPath(path='file.txt', strategy=Strategy.MERGE),
    ]
    errors = manager.validate(lock)
    assert len(errors) > 0
    assert any('Duplicate managed path' in error for error in errors)
