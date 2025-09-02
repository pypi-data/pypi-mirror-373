from cms import api
from cms.models import PageContent, Placeholder
from cms.plugin_rendering import ContentRenderer
from cms.toolbar.toolbar import CMSToolbar
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from djangocms_versioning.constants import DRAFT, PUBLISHED
from djangocms_versioning.models import Version
from sekizai.context import SekizaiContext


def render_plugin(plugin, path='/', **data):
    placeholder = Placeholder.objects.create(slot='test')
    model_instance = api.add_plugin(placeholder, plugin, 'en', **data)
    request = generate_get_request(path)
    request.toolbar = CMSToolbar(request)
    renderer = ContentRenderer(request=request)
    context = SekizaiContext()
    context.update({'request': request, })
    html = renderer.render_plugin(model_instance, context)
    return html


def generate_get_request(path):
    request = RequestFactory().get(path)
    request.user = AnonymousUser()
    request.session = {}
    return request


def generate_post_request(path='', body=None):
    request = RequestFactory().post(path, body)
    request.user = AnonymousUser()
    request.session = {}
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request


# pylint: disable=dangerous-default-value
def create_page(title, language='en', page_params={}, state="publish"):
    page_params.setdefault('overwrite_url', page_params.get('slug'))
    page = api.create_page(title, 'cms_qe/home.html', language, **page_params)
    content = PageContent.admin_manager.get(page=page)
    user, _ = get_user_model().objects.get_or_create(username="tester")
    version = content.versions.last()
    if version is None:
        version_state = PUBLISHED if state == "publish" else DRAFT
        Version.objects.create(content=content, created_by=user, state=version_state)
    else:
        getattr(version, state)(user)  # version.publish(user) / version.unpublish(user)
    return page


# pylint: disable=dangerous-default-value
def create_text_page(title, language='en', page_params={}, plugin_params={}):
    plugin_params.setdefault('body', 'shello')
    page = create_page(title, language, page_params)
    placeholder = page.get_placeholders(language).filter(slot="content").get()
    api.add_plugin(placeholder, 'TextPlugin', language, **plugin_params)
    return page


def create_draft_page(title, language='en', page_params={}, state="unpublish"):
    return create_page(title, language, page_params=page_params, state=state)
