import pytest
from django.contrib.auth import get_user_model
from pytest_data import get_data

from cms_qe_auth.models import User


@pytest.fixture
def user(request):
    data = get_data(
        request, 'user_data', {
            'username': 'user',
            'email': 'user@example.com',
            'is_active': True,
            'password': 'pass'
        }
    )
    password = data['password']
    user = User(**data)
    user.set_password(password)
    user.save(base_url='/')
    return user


@pytest.fixture
def admin_user(request):
    return get_user_model().objects.create_superuser(**get_data(request, 'admin_user_data', {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'password',  # Keep it same with pytest-django.
    }))
