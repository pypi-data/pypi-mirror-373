import pytest
from pytest_data import get_data

from .models import TablePluginModel


@pytest.fixture
def cms_qe_table_model(request):
    return TablePluginModel(**get_data(request, 'cms_qe_table_model_data', {
        'table': 'auth_user',
        'columns': ['username', 'password'],
        'paging_show': False,
        'paging_per_page': 20,
    }))
