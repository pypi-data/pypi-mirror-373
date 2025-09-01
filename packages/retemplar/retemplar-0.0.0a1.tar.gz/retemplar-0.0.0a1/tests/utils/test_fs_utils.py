"""Tests for filesystem utilities."""

import pytest

from retemplar.schema import ManagedPath, RetemplarLock, Strategy
from retemplar.utils.fs_utils import get_managed_files_from_rendered


@pytest.mark.parametrize(
    'managed_paths, ignore_paths, expected_files',
    [
        (
            [
                '*.txt',
            ],
            [],
            {
                'file1.txt',
                'dir1/file3.txt',
                'dir2/file5.txt',
            },
        ),
        (
            [
                '*.txt',
            ],
            ['dir1'],
            {
                'file1.txt',
                'dir2/file5.txt',
            },
        ),
        (
            [
                '*.txt',
            ],
            ['dir1/**'],
            {
                'file1.txt',
                'dir2/file5.txt',
            },
        ),
        (
            [
                '*.txt',
            ],
            ['dir1/*'],
            {
                'file1.txt',
                'dir2/file5.txt',
            },
        ),
        (
            [
                '*.txt',
            ],
            ['dir1/**/*'],
            {
                'file1.txt',
                'dir2/file5.txt',
            },
        ),
        (
            [
                'dir1/**',
            ],
            [],
            {
                'dir1/file3.txt',
                'dir1/file4.md',
            },
        ),
        (
            [
                '**',
            ],
            ['*.log', 'dir2/**'],
            {
                'file1.txt',
                'dir1/file3.txt',
                'dir1/file4.md',
            },
        ),
    ],
)
def test_get_managed_files(
    managed_paths: list[str],
    ignore_paths: list[str],
    expected_files: set[str],
):
    """Test getting managed files with various patterns from rendered files."""
    # Create rendered files dict simulating all available files
    rendered_files = {
        'file1.txt': 'File 1 content',
        'file2.log': 'File 2 content',
        'dir1/file3.txt': 'File 3 content',
        'dir1/file4.md': 'File 4 content',
        'dir2/file5.txt': 'File 5 content',
    }

    lock = RetemplarLock(
        template_ref='rat:gh:acme/main-svc@v2025.08.01',
        managed_paths=[
            ManagedPath(path=path, strategy=Strategy.MERGE)
            for path in managed_paths
        ],
        ignore_paths=ignore_paths,
    )

    managed_files = get_managed_files_from_rendered(lock, rendered_files)

    assert set(managed_files.keys()) == expected_files
