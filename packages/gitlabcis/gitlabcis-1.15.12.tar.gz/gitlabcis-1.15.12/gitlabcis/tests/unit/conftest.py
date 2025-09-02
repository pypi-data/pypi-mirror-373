# -----------------------------------------------------------------------------

from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

# -----------------------------------------------------------------------------


@pytest.fixture
def projectRoot(scope='function'):
    try:
        return next(
            p for p in Path(__file__).parents if (p / 'gitlabcis').exists())
    except StopIteration:
        pytest.skip('Parent directory containing "gitlabcis" not found.')

# -----------------------------------------------------------------------------


@pytest.fixture
def recommendationFiles(projectRoot, scope='function'):
    return list(filter(
        lambda pathObj: pathObj.name != 'template.yml',
        Path(f'{projectRoot}/gitlabcis/recommendations').rglob('*.yml')))

# -----------------------------------------------------------------------------


@pytest.fixture
def recommendationDirs(projectRoot, scope='function'):

    dirNames = set()

    for entry in filter(
        lambda pathObj: pathObj.is_dir() is True,
        Path(f'{projectRoot}/gitlabcis/recommendations').rglob('*')
            ):

        dirNames.update(entry.parts)

    return dirNames

# -----------------------------------------------------------------------------


@pytest.fixture
def recommendations(recommendationFiles, scope='module'):
    _recommendations = {}

    for rec in recommendationFiles:

        with open(rec, 'r') as f:
            _data = yaml.safe_load(f)

            _recommendations[_data.get('name')] = _data

    return _recommendations

# -----------------------------------------------------------------------------


@pytest.fixture
def benchmarkFunctions(projectRoot, scope='module'):

    from gitlabcis import benchmarks

    return [
        getattr(getattr(getattr(benchmarks, catFile), subCatFile), func)
        for catFile in dir(benchmarks)
        if not catFile.startswith('__')
        for subCatFile in dir(getattr(benchmarks, catFile))
        if not subCatFile.startswith('__')
        for func in dir(getattr(getattr(benchmarks, catFile), subCatFile))
        if not func.startswith('__')
    ]

# -----------------------------------------------------------------------------


@pytest.fixture(scope="function")
def glEntity():
    # mock a project:
    return Mock()

# -----------------------------------------------------------------------------


@pytest.fixture(scope="function")
def glObject(glEntity):
    # mock a gitlab object:
    return Mock()
