from typing import TypeVar

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from cms_qe.utils import get_base_url
from cms_qe_auth.utils import get_user_by_uidb64

from .forms import RegisterForm

RF = TypeVar('RF', bound=RegisterForm)


def register(
        request: HttpRequest,
        template_name: str = 'cms_qe/auth/register.html',
        register_form: type[RF] = RegisterForm,
):
    """
    Displays the register form and handles the register action.
    """
    if request.method == 'POST':
        form = register_form(data=request.POST)
        if form.is_valid():  # pylint: disable=R1705
            base_url = get_base_url(request)
            user = form.save(commit=False)
            user.is_active = False
            user.save(base_url=base_url)
            messages.success(request, _('You were successfully registered. Please confirm your email address.'))
            return redirect('register')
        messages.error(request, _('Please correct errors below.'))
    else:
        form = register_form()

    context = {'form': form}
    return TemplateResponse(request, template_name, context)


def activate(
        request: HttpRequest,
        uidb64: str,
        token: str,
        template_name_complete: str = 'cms_qe/auth/email_confirmation_complete.html',
        template_name_fail: str = 'cms_qe/auth/email_confirmation_fail.html',
):
    user = get_user_by_uidb64(uidb64)
    if user and user.activate(token):
        # Use default django authentication backend if multiple authentication backends are configured
        # It doesn't work with custom authentication backends. If you use custom auth backend you should completely
        # rewrite authentication and activation.
        if len(settings.AUTHENTICATION_BACKENDS) > 1:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return TemplateResponse(request, template_name_complete)
    return TemplateResponse(request, template_name_fail)
