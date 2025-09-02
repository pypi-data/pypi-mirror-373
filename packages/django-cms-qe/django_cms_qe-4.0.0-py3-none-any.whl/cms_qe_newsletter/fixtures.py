from time import time
from unittest import mock

import pytest
from constance.test import override_config
from django.conf import settings
from pytest_data import get_data

from .models import SERVICE_MAILCHIMP, SUBSCRIBE, MailingList, NewsletterPluginModel, Subscriber, SubscribeTask


@pytest.fixture
def cms_qe_newsletter_plugin(request):
    return NewsletterPluginModel(**get_data(
        request,
        'cms_qe_newsletter_plugin_data',
        {
            'title': 'Test Title',
            'fullname_show': False,
            'fullname_require': False,
        }
    ))


@pytest.fixture
def cms_qe_mailing_list(request):
    mailing_list = MailingList(**get_data(
        request,
        'cms_qe_mailing_list_data',
        {
            'name': 'Mail list',
            'external_service': SERVICE_MAILCHIMP,
            'external_id': settings.TEST_MAILCHIMP_LIST_ID,
        }
    ))
    mailing_list.save()
    return mailing_list


@pytest.fixture
def cms_qe_subscriber(request, cms_qe_mailing_list):
    subscriber = Subscriber(**get_data(
        request,
        'cms_qe_subscriber_data',
        {
            'mailing_list': cms_qe_mailing_list,
            'email': f'test{time()}@example.com',
            'first_name': 'Firstname',
            'last_name': 'Lastname',
        }
    ))
    subscriber.save()
    return subscriber


@pytest.fixture
def cms_qe_subscribe_task(request, cms_qe_mailing_list):
    subscribe_task = SubscribeTask(**get_data(
        request,
        'cms_qe_subscribe_task_data',
        {
            'mailing_list': cms_qe_mailing_list,
            'email': f'test{time()}@example.com',
            'first_name': 'Firstname',
            'last_name': 'Lastname',
            'type': SUBSCRIBE,
        }
    ))
    subscribe_task.save()
    return subscribe_task


@pytest.fixture
def mock_mailchimp(request):
    mailchimp_mock = mock.Mock()
    mailchimp_mock.lists.all.return_value = get_data(request, 'cms_qe_mailchimp_list_data', {
        'lists': [
            {'name': 'some_name_1', 'id': 'some_id_1'},
            {'name': 'some_name_2', 'id': 'some_id_2'},
        ],
    })
    mailchimp_mock.lists.members.create.return_value = get_data(request, 'cms_qe_mailchimp_subscribe_data', {
        'id': 'some_test_id',
    })
    mailchimp_mock.lists.members.delete.return_value = None
    with mock.patch('mailchimp3.MailChimp', return_value=mailchimp_mock):
        constance = override_config(
            MAILCHIMP_USERNAME=settings.TEST_MAILCHIMP_USERNAME,
            MAILCHIMP_API_KEY=settings.TEST_MAILCHIMP_API_KEY,
        )
        constance.enable()
        yield
        constance.disable()
