# -----------------------------------------------------------------------------

from collections import namedtuple
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from gitlabcis.utils import (countRecommendations, mapRecommendations,
                             readRecommendations, readYaml)

# -----------------------------------------------------------------------------


def test_count_recommendations():
    assert countRecommendations() == 123

# -----------------------------------------------------------------------------


def test_read_recommendations():
    # options:
    ArgFilters = namedtuple(
        'ArgFilters', ['profile', 'recommendation_ids', 'cis_controls',
                       'implementation_groups', 'skip_recommendation_ids'])

    # controls:
    control1 = {
        'id': '1.1.1', 'profile': '1',
        'cis_controls': [{'id': '2.4', 'implementation_groups': 'IG2'}]}

    control2 = {
        'id': '1.1.12', 'profile': '2',
        'cis_controls': [{'id': '16.1', 'implementation_groups': 'IG3'}]}

    # run:
    @patch('gitlabcis.utils.Path')
    @patch('gitlabcis.utils.readYaml')
    def run_test(mock_read_yaml, mock_path, arg_filters=None,
                 expected_result=None, expect_exit=False):
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.rglob.return_value = ['file1.yml', 'file2.yml']
        mock_read_yaml.side_effect = [control1, control2]

        if expect_exit:
            mock_path.return_value.exists.return_value = False
            with pytest.raises(SystemExit):
                readRecommendations(arg_filters)
        else:
            result = readRecommendations(arg_filters)
            assert result == expected_result

    # Test no filters
    run_test(expected_result=[control1, control2])

    # Test profile filter
    run_test(
        arg_filters=ArgFilters(profile='1', recommendation_ids=None,
                               cis_controls=None, implementation_groups=None,
                               skip_recommendation_ids=None),
        expected_result=[control1]
    )

    # Test recommendation_ids filter
    run_test(
        arg_filters=ArgFilters(profile=None, recommendation_ids=['1.1.12'],
                               cis_controls=None, implementation_groups=None,
                               skip_recommendation_ids=None),
        expected_result=[control2]
    )

    # Test skip_recommendation_ids filter
    run_test(
        arg_filters=ArgFilters(profile=None, recommendation_ids=None,
                               cis_controls=None, implementation_groups=None,
                               skip_recommendation_ids=['1.1.12']),
        expected_result=[control1]
    )

    # Test cis_controls filter
    run_test(
        arg_filters=ArgFilters(profile=None, recommendation_ids=None,
                               cis_controls=['16.1'],
                               implementation_groups=None,
                               skip_recommendation_ids=None),
        expected_result=[control2]
    )

    # Test implementation_groups filter
    run_test(
        arg_filters=ArgFilters(profile=None, recommendation_ids=None,
                               cis_controls=None,
                               implementation_groups=['IG2'],
                               skip_recommendation_ids=None),
        expected_result=[control1]
    )

    # Test directory not found
    run_test(expect_exit=True)

# -----------------------------------------------------------------------------


def test_read_yaml():
    example_input = "key1: value1\nkey2: value2"
    example_output = {'key1': 'value1', 'key2': 'value2'}

    # Test successful read
    with patch('builtins.open', new_callable=mock_open,
               read_data=example_input):
        result = readYaml('dummy_path.yml')
        assert result == example_output

    # Test file not found
    with patch('builtins.open', side_effect=FileNotFoundError), \
         patch('sys.exit') as mock_exit, \
         pytest.raises(SystemExit):
        readYaml('non_existent_file.yml')
        mock_exit.assert_called_once_with(1)

    # Test logging
    with patch('builtins.open', new_callable=mock_open,
               read_data=example_input), \
         patch('logging.debug') as mock_debug:
        readYaml('test_file.yml')
        mock_debug.assert_called_once_with('Opening: test_file.yml')

    # Test invalid YAML content
    with patch('builtins.open', new_callable=mock_open,
               read_data="invalid: yaml: content"), \
            pytest.raises(yaml.YAMLError):
        readYaml('invalid_yaml.yml')

# -----------------------------------------------------------------------------


def test_map_recommendations():
    functionList = [
        Mock(__name__='func1'),
        Mock(__name__='func2'),
        Mock(__name__='func3')
    ]

    recommendations = [{'name': 'func1'}, {'name': 'func2'},
                       {'name': 'func3'}]

    assert len(
        mapRecommendations(functionList, recommendations)
    ) == 3
