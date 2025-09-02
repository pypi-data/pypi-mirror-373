# -------------------------------------------------------------------------

import logging
from pathlib import Path
from sys import exit

import yaml

from . import ci  # noqa: F401

# -----------------------------------------------------------------------------
# count recommendations:
# -----------------------------------------------------------------------------


def countRecommendations():
    return len(list(
        Path(f'{Path(__file__).parent.parent}/recommendations').rglob('*.yml')
    ))

# -----------------------------------------------------------------------------
# Load the recommendations:
# -----------------------------------------------------------------------------


def readRecommendations(argFilters=None):

    _rDir = Path(f'{Path(__file__).parent.parent}/recommendations')

    logging.debug(f'recommendations directory: {_rDir}')

    if not _rDir.exists():
        print(
            f'Error: Recommendations directory {_rDir} was not found'
        )
        exit(1)

    # -------------------------------------------------------------------------
    # Gather all recommendations:
    # -------------------------------------------------------------------------

    recommendationFiles = list(_rDir.rglob('*.yml'))

    if argFilters is None:

        recommendations = [readYaml(r) for r in recommendationFiles]
        logging.debug(f'Loaded: {len(recommendations)} recommendations')

        return recommendations

    # -------------------------------------------------------------------------
    # Filter recommendations based on user input:
    # -------------------------------------------------------------------------

    logging.debug(f'Filtering with args: {argFilters}')

    recommendations = []

    for r in recommendationFiles:

        yamlData = readYaml(r)

        cisControls = yamlData.get('cis_controls', [])

        # ---------------------------------------------------------------------

        # if a profile was provided and it doesn't match in the recommendation:
        if argFilters.profile:
            if argFilters.profile != yamlData.get('profile'):
                continue

        # if a recommendation id was provided but it doesn't match:
        if argFilters.recommendation_ids:
            if yamlData.get('id') not in argFilters.recommendation_ids:
                continue

        # if a user wishes to skip certain recommendation id's:
        if argFilters.skip_recommendation_ids:
            if yamlData.get('id') in argFilters.skip_recommendation_ids:
                continue

        # ---------------------------------------------------------------------
        # Iterate through the CIS Controls:
        # ---------------------------------------------------------------------

        # if a CIS Control ID was provided and it's not found:
        if argFilters.cis_controls:
            _cisIds = set([cis.get('id') for cis in cisControls])

            if not set(argFilters.cis_controls).intersection(_cisIds):
                continue

        # if an implementation group was provided and it's not found:
        if argFilters.implementation_groups:

            if not set(argFilters.implementation_groups).intersection(
                set([
                    control.get('implementation_groups')
                    for control in cisControls
                    ])):
                continue

        # for everything else, append it, this allows a user to pass no
        # args and they return all the recommendations...
        recommendations.append(yamlData)

    return recommendations

# -----------------------------------------------------------------------------
# Read a recommendation file:
# -----------------------------------------------------------------------------


def readYaml(recommendation):
    """
    Desc: This function takes a str path to a yaml file, reads it and
          returns it.
    """

    logging.debug(f'Opening: {recommendation}')

    try:
        with open(recommendation, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f'Error: Failed to find recommendation: {recommendation}')
        exit(1)

# -----------------------------------------------------------------------------
# Map functions to recommendations:
# -----------------------------------------------------------------------------


def mapRecommendations(functionList, recommendationList):
    """
    Desc: This function maps a function to its relevant recommendation
          It accepts a list of functions, and a list of recommendation dicts.
    """

    mappedFuncs = {func.__name__: func for func in functionList}

    return {
        mappedFuncs[recommendation['name']]: recommendation
        for recommendation in recommendationList
        if recommendation['name'] in mappedFuncs
    }
