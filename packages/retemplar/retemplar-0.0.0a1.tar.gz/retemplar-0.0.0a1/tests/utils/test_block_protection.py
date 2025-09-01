"""Essential tests for block protection functionality."""

import pytest

from retemplar.utils.blockprotect import (
    enforce_ours_blocks,
    find_ignore_blocks,
)


@pytest.mark.parametrize(
    ('content', 'expected_blocks'),
    [
        pytest.param(
            """
# retemplar:begin id=config mode=ignore
config_value: local_setting  
# retemplar:end id=config
""".strip(),
            {'config'},
            id='single-block',
        ),
        pytest.param(
            """
# retemplar:begin id=db mode=ignore
db: local
# retemplar:end id=db
regular: content
# retemplar:begin id=auth mode=ignore  
auth: custom
# retemplar:end id=auth
""".strip(),
            {'db', 'auth'},
            id='multiple-blocks',
        ),
        pytest.param(
            'regular content without blocks',
            set(),
            id='no-blocks',
        ),
        pytest.param(
            """
# retemplar:begin id=nested mode=ignore
outer: data
  # retemplar:begin id=inner mode=ignore
  inner: data
  # retemplar:end id=inner  
more: data
# retemplar:end id=nested
""".strip(),
            {'nested', 'inner'},
            id='nested-blocks',
        ),
    ],
)
def test_find_ignore_blocks(content: str, expected_blocks: set[str]):
    """Test ignore block detection with various configurations."""
    blocks = find_ignore_blocks(content)
    assert set(blocks.keys()) == expected_blocks


@pytest.mark.parametrize(
    ('ours', 'merged', 'expected_preserved', 'expected_accepted'),
    [
        pytest.param(
            """
# retemplar:begin id=preserve mode=ignore
local: data
# retemplar:end id=preserve
other: content
""".strip(),
            """
# retemplar:begin id=preserve mode=ignore
template: data
# retemplar:end id=preserve  
other: new_content
""".strip(),
            ['local: data'],
            ['new_content'],
            id='basic-preservation',
        ),
        pytest.param(
            """
# retemplar:begin id=db mode=ignore
db_host: localhost
# retemplar:end id=db
# retemplar:begin id=cache mode=ignore
cache_ttl: 3600
# retemplar:end id=cache
regular: old_value
""".strip(),
            """
# retemplar:begin id=db mode=ignore
db_host: production.db
# retemplar:end id=db
# retemplar:begin id=cache mode=ignore
cache_ttl: 300
# retemplar:end id=cache
regular: new_value
""".strip(),
            ['db_host: localhost', 'cache_ttl: 3600'],
            ['new_value'],
            id='multiple-blocks-preservation',
        ),
        pytest.param(
            'no blocks here',
            'template content',
            [],
            ['template content'],
            id='no-blocks-passthrough',
        ),
    ],
)
def test_enforce_ours_blocks(
    ours: str,
    merged: str,
    expected_preserved: list[str],
    expected_accepted: list[str],
):
    """Test block protection enforcement."""
    result, report = enforce_ours_blocks(ours, merged)

    # Check preserved content
    for content in expected_preserved:
        assert content in result

    # Check accepted changes
    for content in expected_accepted:
        assert content in result

    # Check report
    if expected_preserved:
        assert len(report.enforced) > 0
    else:
        assert len(report.enforced) == 0
