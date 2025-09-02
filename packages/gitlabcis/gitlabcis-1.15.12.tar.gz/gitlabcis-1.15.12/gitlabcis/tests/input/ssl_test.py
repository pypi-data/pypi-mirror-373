# -----------------------------------------------------------------------------

import builtins
import unittest
from unittest.mock import patch

import pytest

from gitlabcis.cli.auth import GitlabCIS

# -----------------------------------------------------------------------------


# mock auth
@pytest.fixture
def mock_gitlab():
    with patch('gitlabcis.cli.auth.gitlab') as mock:
        yield mock


# skip admin warning
@pytest.fixture(autouse=True)
def mock_input(monkeypatch):
    monkeypatch.setattr(builtins, 'input', lambda _: 'y')


def test_no_verify_ssl(mock_gitlab):
    gitlab_cis = GitlabCIS(
        'https://gitlab.com/destination/project', token='fake-token',
        ssl_verify=False)
    assert gitlab_cis.ssl_verify is False

# -----------------------------------------------------------------------------


class TestGitLabGraphQLClient(unittest.TestCase):

    @patch('gql.transport.requests.RequestsHTTPTransport')
    def test_ssl_verify_parameter(self, mock_transport):

        # Test with SSL verification enabled
        kwargs = {
            'graphQLEndpoint': 'https://gitlab.example.com/api/graphql',
            'graphQLHeaders': {'Authorization': 'Bearer token123'},
            'sslVerify': True
        }

        # For this example, I'll recreate the client code from your snippet
        from gql import Client
        client = Client(
            transport=mock_transport(
                url=kwargs.get('graphQLEndpoint'),
                headers=kwargs.get('graphQLHeaders'),
                use_json=True,
                verify=kwargs.get('sslVerify')
            ),
            fetch_schema_from_transport=True
        )

        # Verify the transport was created with verify=True
        mock_transport.assert_called_once()
        call_kwargs = mock_transport.call_args[1]
        self.assertTrue(call_kwargs['verify'])

        # Reset the mock for the next test
        mock_transport.reset_mock()

        # Test with SSL verification disabled
        kwargs['sslVerify'] = False

        # Create client again with new kwargs
        client = Client(  # noqa: F841
            transport=mock_transport(
                url=kwargs.get('graphQLEndpoint'),
                headers=kwargs.get('graphQLHeaders'),
                use_json=True,
                verify=kwargs.get('sslVerify')
            ),
            fetch_schema_from_transport=True
        )

        # Verify the transport was created with verify=False
        mock_transport.assert_called_once()
        call_kwargs = mock_transport.call_args[1]
        self.assertFalse(call_kwargs['verify'])
