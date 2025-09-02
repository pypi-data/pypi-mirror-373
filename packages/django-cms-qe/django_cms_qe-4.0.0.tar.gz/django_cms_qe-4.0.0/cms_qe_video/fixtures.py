# pylint: disable=invalid-name
from unittest.mock import Mock

import pytest
from filer.models import File
from pytest_data import get_data

from .models import HostingVideoPlayer, SourceFileVideoPlayer


@pytest.fixture
def cms_qe_video_source_file_video_player_model(request):
    file_mock = Mock(spec=File, name='FileMock')
    file_mock._state = Mock()

    return SourceFileVideoPlayer(
        **get_data(request, 'cms_qe_video_source_file_video_player_model_data', {'source_file': file_mock})
    )


@pytest.fixture
def cms_qe_video_hosting_video_player_model(request):
    return HostingVideoPlayer(**get_data(
        request,
        'cms_qe_video_hosting_video_player_model_data',
    ))
