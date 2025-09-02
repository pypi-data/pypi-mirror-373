from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cms_qe.utils import get_email
from cms_qe_auth.token import TokenGenerator
from cms_qe_auth.utils import pk_to_uidb64


class MissingBaseURLException(Exception):
    pass


# pylint: disable=model-no-explicit-unicode
class User(AbstractUser):
    class Meta:
        ordering = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_email = self.email

    def save(self, *args, **kwargs):
        # If application does not need username, it just use email instead.
        # Note that Django normalizes username so to make it work we need to change
        # behaviour of normalize_username.
        if not self.username or self.username == self._previous_email:
            self.username = self.email
        if self._previous_email and self.email != self._previous_email:
            self.is_active = False

        is_new = not self.pk

        base_url = kwargs.pop('base_url', None)
        super().save(*args, **kwargs)

        if settings.CMS_QE_AUTH_ENABLED and is_new and not self.is_active:
            if not base_url:
                raise MissingBaseURLException('New user can not be saved without a base url')
            self.send_activation_email(base_url)

    @classmethod
    def normalize_username(cls, username):
        # By default Django normalizes username which converts None into "None".
        if username is None:
            return username
        return super().normalize_username(username)

    def activate(self, token):
        if not self._check_activation_token(token):
            return False
        self.is_active = True
        self.save()
        return True

    def send_activation_email(self, base_url):
        token = self._generate_activation_token()
        activation_url = self._get_absolute_activation_url(base_url=base_url, token=token)
        email = get_email(
            template='cms_qe/auth/email/activation',
            subject=_('Activate your account'),
            to=self.email,
            username=self.username,
            activation_url=activation_url,
        )
        email.send()

    def _generate_activation_token(self):
        return TokenGenerator().make_token(self)

    def _check_activation_token(self, token):
        return TokenGenerator().check_token(self, token)

    def _get_absolute_activation_url(self, base_url, token: str) -> str:
        relative_url = reverse('activate', kwargs={'uidb64': pk_to_uidb64(self.pk), 'token': token})
        return base_url + relative_url
