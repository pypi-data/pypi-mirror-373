# -------------------------------------------------------------------------

from gitlabcis.utils.__init__ import readRecommendations

# -------------------------------------------------------------------------


def test_none_argfilters():
    assert readRecommendations(argFilters=None) is not None
