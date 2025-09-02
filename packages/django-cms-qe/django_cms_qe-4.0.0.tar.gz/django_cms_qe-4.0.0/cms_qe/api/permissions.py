# from django.conf import settings
from rest_framework.permissions import BasePermission

from .constants import CMS_QE_USER_ACCES_API_PERMISSION


class CmsQeApiPermission(BasePermission):
    """Permission class checking user type."""

    def has_permission(self, request, view):
        """Check user access permission to the API."""
        return request.user.has_perm(CMS_QE_USER_ACCES_API_PERMISSION)
