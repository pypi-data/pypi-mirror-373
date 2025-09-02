import os.path

import batou.vfs
import pytest
from risclog.batou.source import Source


@pytest.fixture
def source(root):
    root.environment.vfs_sandbox = batou.vfs.Developer(root.environment, None)
    source = Source(
        sources=[
            'git@https://example.com/foo',
            'git@https://example.com/bar branch=BAR',
            'git@https://example.com/baz revision=BAZ',
        ]
    )
    root.component += source

    with open(os.path.join(root.defdir, 'versions.txt'), 'w') as f:
        f.write(
            """\
six==1.14.0
pytest==6.2.5"""
        )
    with open(os.path.join(root.defdir, 'dev-requirements.txt'), 'w') as f:
        f.write('pytest')

    root.component.configure()
    return source


def test_all_targets_are_derived_from_clone_urls(source):
    assert {clone.url: clone.target for clone in source.clones.values()} == {
        'git@https://example.com/foo': source.map('foo'),
        'git@https://example.com/bar': source.map('bar'),
        'git@https://example.com/baz': source.map('baz'),
    }


def test_branches_are_read_from_parameters(source):
    assert source.clones['bar'].branch == 'BAR'


def test_branch_is_set_to_master_if_not_given(source):
    assert source.clones['foo'].branch == 'master'


def test_branch_is_not_set_if_revision_given(source):
    assert source.clones['baz'].branch is None


def test_revisions_are_read_from_parameters(source):
    assert source.clones['foo'].revision is None
    assert source.clones['bar'].revision is None
    assert source.clones['baz'].revision == 'BAZ'


def test_source_can_provide_version_pinnings_for_appenv_requirements(source):
    assert source.pinnings == {'pytest': '6.2.5', 'six': '1.14.0'}


def test_source_can_provide_editable_packages_for_appenv_requirements(source):
    assert source.editable_packages == {
        'foo': source.map('foo'),
        'bar': source.map('bar'),
        'baz': source.map('baz'),
    }


def test_source_can_provide_additional_requirements_for_appenv_requirements(
    source,
):
    assert source.additional_requirements == ['pytest']
