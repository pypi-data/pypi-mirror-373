from django.contrib.auth import authenticate
from django.db.models import Model
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CmsQeBasicAuthentication(BasicAuthentication):

    def authenticate_credentials(self, userid: str, password: str, request: HttpRequest = None) -> tuple[Model, None]:
        """Check credentials against settings and return AnonymousUser or None."""
        retval = authenticate(request, userid=userid, username=userid, password=password)
        if retval is None:
            raise AuthenticationFailed(_("Invalid username/password."))
        return (retval, None)
