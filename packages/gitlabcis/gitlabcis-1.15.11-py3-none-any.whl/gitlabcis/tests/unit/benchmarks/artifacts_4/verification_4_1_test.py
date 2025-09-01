# -----------------------------------------------------------------------------

from unittest.mock import Mock, patch

import pytest  # noqa: F401
from conftest import run

from gitlabcis.benchmarks.artifacts_4 import verification_4_1

# -----------------------------------------------------------------------------


@patch('zipfile.ZipFile')
def test_sign_artifacts_in_build_pipeline(mock_zipfile, glEntity, glObject):

    from gitlab.exceptions import GitlabHttpError
    test = verification_4_1.sign_artifacts_in_build_pipeline

    kwargs = {'isProject': True}
    glEntity.pipelines.list.return_value = []
    run(glEntity, glObject, test, False, **kwargs)

    mockPipeline = Mock()
    mockJob = Mock()
    mockJob.stage = 'test'
    mockPipeline.jobs.list.return_value = [mockJob]
    glEntity.pipelines.list.return_value = [mockPipeline]
    run(glEntity, glObject, test, False, **kwargs)

    mockJob.stage = 'build'
    mockJob.id = 1
    mockPipeline.jobs.list.return_value = [mockJob]
    glEntity.pipelines.list.return_value = [mockPipeline]
    glEntity.jobs.get.return_value.artifacts.return_value = b'fake_artifact'

    mock_zipfile.return_value.__enter__.return_value.namelist.return_value \
        = ['file1.txt', 'file2.txt']

    run(glEntity, glObject, test, False, **kwargs)

    mockPipeline = Mock()
    mockJob = Mock()
    mockJob.stage = 'build'
    mockJob.id = 1
    mockPipeline.jobs.list.return_value = [mockJob]
    glEntity.pipelines.list.return_value = [mockPipeline]
    glEntity.jobs.get.return_value.artifacts.return_value = b'fake_artifact'

    mock_zipfile.return_value.__enter__.return_value.namelist.return_value \
        = ['file1.txt', 'file1.sig', 'file2.txt', 'file2.sig']

    run(glEntity, glObject, test, True, **kwargs)

    glEntity.pipelines.list.side_effect \
        = GitlabHttpError('', response_code=403)

    run(glEntity, glObject, test, None, **kwargs)

    glEntity.pipelines.list.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None  # noqa: E501

    glEntity.pipelines.list.side_effect \
        = GitlabHttpError('', response_code=404)

    run(glEntity, glObject, test, False, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_encrypt_artifacts_before_distribution(glEntity, glObject):

    test = verification_4_1.encrypt_artifacts_before_distribution

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_only_authorized_platforms_can_decrypt_artifacts(glEntity, glObject):

    test = verification_4_1.only_authorized_platforms_can_decrypt_artifacts

    run(glEntity, glObject, test, None)
