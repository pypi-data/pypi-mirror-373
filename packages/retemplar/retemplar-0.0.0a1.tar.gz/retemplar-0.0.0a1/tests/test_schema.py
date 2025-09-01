"""Tests for lockfile schema validation (MVP)."""

import pytest

from retemplar.schema import (
    ManagedPath,
    RetemplarLock,
    Strategy,
    TemplateSource,
    parse_template_ref,
)

# --- TemplateSource -----------------------------------------------------------


# TODO: Add commits when we support github repos.
@pytest.mark.parametrize(
    ('template_ref', 'expected'),
    [
        pytest.param(
            {
                'repo': 'gh:acme/main-svc',
                'ref': 'v2025.08.01',
                'kind': 'rat',
            },
            TemplateSource(
                repo='gh:acme/main-svc',
                ref='v2025.08.01',
                kind='rat',
            ),
            id='rat-branch',
        ),
        pytest.param(
            {
                'repo': 'gh:acme/main-svc',
                'ref': '06a625788c56465bd2dd8f48d222b9fe7db3d5ec',
            },
            TemplateSource(
                repo='gh:acme/main-svc',
                ref='06a625788c56465bd2dd8f48d222b9fe7db3d5ec',
                commit='06a625788c56465bd2dd8f48d222b9fe7db3d5ec',
                kind='rat',
            ),
            id='rat-commit',
        ),
    ],
)
def test_template_source(template_ref, expected):
    """Test template source validation."""
    source = TemplateSource(**template_ref)
    assert source == expected


@pytest.mark.parametrize(
    ('template_source', 'expected_error'),
    [
        pytest.param(
            {'repo': 'rat:gh:acme', 'ref': 'main-svc'},
            "repo: rat:gh:acme must start with 'gh:' or 'local:'.",
            id='bad-scheme',
        ),
        pytest.param(
            {'repo': '', 'ref': 'v2025.08.01'},
            'repo cannot be empty',
            id='empty-repo',
        ),
    ],
)
def test_template_source_invalid(template_source, expected_error):
    """Test template source with various invalid formats."""
    with pytest.raises(ValueError, match=expected_error):
        TemplateSource(**template_source)


# --- RetemplarLock ------------------------------------------------------------


@pytest.mark.parametrize(
    ('retemplar_lock', 'expected'),
    [
        pytest.param(
            {
                'template_ref': 'rat:gh:acme/main-svc@v2025.08.01',
                'managed_paths': [
                    {'path': '.github/workflows/**', 'strategy': 'enforce'},
                ],
            },
            RetemplarLock(
                template_ref='rat:gh:acme/main-svc@v2025.08.01',
                managed_paths=[
                    ManagedPath(
                        path='.github/workflows/**',
                        strategy=Strategy.ENFORCE,
                    ),
                ],
                applied_ref='v2025.08.01',
            ),
            id='rat-github',
        ),
        pytest.param(
            {
                'template_ref': 'rat:local:/path/to/template',
                'managed_paths': [
                    {'path': 'src/**', 'strategy': 'enforce'},
                ],
            },
            RetemplarLock(
                template_ref='rat:local:/path/to/template',
                managed_paths=[
                    ManagedPath(
                        path='src/**',
                        strategy=Strategy.ENFORCE,
                    ),
                ],
                applied_ref=None,
            ),
            id='rat-local-no-ref',
        ),
    ],
)
def test_retemplar_lock(retemplar_lock, expected):
    """Test basic retemplar lock validation."""
    expected_template_source = parse_template_ref(
        retemplar_lock.get('template_ref'),
    )
    lock = RetemplarLock(**retemplar_lock)
    assert lock == expected
    assert lock.template == expected_template_source


def test_invalid_retemplar_lock_format():
    """Test invalid retemplar lock format."""
    with pytest.raises(ValueError, match='MVP only supports RAT templates'):
        RetemplarLock(template_ref='invalid-format')
