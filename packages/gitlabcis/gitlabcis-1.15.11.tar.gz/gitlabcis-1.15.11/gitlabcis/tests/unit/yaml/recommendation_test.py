# -----------------------------------------------------------------------------


def test_valid_yaml_syntax(recommendations):
    """
    This test ensures that all the required keys are present in the yaml
    recommendation
    """

    # the required keys of the yaml file:
    requiredKeys = [
        'id', 'name', 'title', 'profile', 'category', 'sub_category',
        'description', 'rationale', 'impact', 'audit', 'remediation',
        'default_value', 'references', 'cis_controls', 'additional_info'
    ]

    requiredKeys.sort()

    for yamlName, yamlData in recommendations.items():
        print(f'    - Testing: {yamlData.get("id")} - {yamlName}')  # noqa: E221,E501

        yamlKeys = list(yamlData.keys())
        yamlKeys.sort()

        assert yamlKeys == requiredKeys

# -----------------------------------------------------------------------------


def test_categories(recommendationDirs, recommendations):
    """
    This test ensures that the category inside the yaml recommendation
    matches those of the directories under /recommendations.
    """

    for yamlName, yamlData in recommendations.items():
        print(f'    - Testing: {yamlData.get("id")} - {yamlName}')  # noqa: E221,E501

        _expectedPath = (
            f'{yamlData.get("category")}_{yamlData.get("id").split(".")[0]}'
        )
        assert _expectedPath in recommendationDirs

# -----------------------------------------------------------------------------


def test_sub_categories(recommendationDirs, recommendations):
    """
    This test ensures that the sub_category match those of the directories
    under /recommendations.
    """

    for yamlName, yamlData in recommendations.items():
        print(f'    - Testing: {yamlData.get("id")} - {yamlName}')  # noqa: E221,E501

        _idSplit = yamlData.get('id').split('.')
        _expectedPath = (
            f'{yamlData.get("sub_category")}_{_idSplit[0]}_{_idSplit[1]}'
        )

        assert _expectedPath in recommendationDirs

# -----------------------------------------------------------------------------


def test_duplicate_ids(recommendations):
    """
    This test ensures that there are no duplicate IDs in the yaml files.
    """

    _ids = []

    for yamlName, yamlData in recommendations.items():

        print(f'    - Testing: {yamlData.get("id")} - {yamlName}')  # noqa: E221,E501

        if yamlData['id'] in _ids:
            raise AssertionError(
                f'Duplicate ID: {yamlData["id"]} found in file: {yamlName}'
            )
        _ids.append(yamlData['id'])

# -----------------------------------------------------------------------------


def test_duplicate_names(recommendations):
    """
    This test ensures that there are no duplicate names in the yaml files.
    """

    _names = []

    for yamlName, _yamlData in recommendations.items():
        if yamlName in _names:
            raise AssertionError(
                f'Duplicate Name: {yamlName} found in {yamlName}')
        _names.append(yamlName)

# -----------------------------------------------------------------------------


def test_template_values(recommendations):
    """
    This test ensures that there are no template values still in the file.
    """

    for yamlName, yamlData in recommendations.items():

        _checks = []

        print(f'    - Testing: {yamlData.get("id")} - {yamlName}')  # noqa: E221,E501

        for key, value in yamlData.items():

            # for list items:
            if key == 'references' and value:
                _checks.append('example' not in [v for v in value])

            # for single value items:
            else:
                _checks.append(value != 'example')

            assert False not in _checks
