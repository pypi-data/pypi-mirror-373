# -----------------------------------------------------------------------------

from unittest.mock import Mock, patch

import pytest

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

# -----------------------------------------------------------------------------


@pytest.fixture(scope="function")
def unauthorised():
    from gitlab.exceptions import GitlabGetError

    # mock an unauthorised gitlab object:
    return Mock(side_effect=GitlabGetError(response_code=401))

# -----------------------------------------------------------------------------


@pytest.fixture
def gqlClient():
    with patch('gql.Client') as mock:
        yield mock

# -----------------------------------------------------------------------------


def run(glEntity, glObject, test, expectedResult, **kwargs):
    actualResult = test(glEntity, glObject, **kwargs)
    print(f'{expectedResult=} - {actualResult=}')
    assert next(iter(actualResult)) is expectedResult
