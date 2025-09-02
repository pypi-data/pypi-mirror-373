# -----------------------------------------------------------------------------


def test_function_doc_strings(benchmarkFunctions):
    """
    Test that the function docstring contains id and title of the
    recommendation.
    """

    for benchmark in benchmarkFunctions:
        assert 'id:' in benchmark.__doc__ and 'title:' in benchmark.__doc__

# -----------------------------------------------------------------------------


def test_function_name(benchmarkFunctions, recommendations):
    """
    Test that the function name matches that of a yaml recommendation name.
    """

    _recNames = recommendations.keys()

    for benchmark in benchmarkFunctions:
        assert benchmark.__name__ in _recNames
