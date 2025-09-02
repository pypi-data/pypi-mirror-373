"""
from cms_qe.views.test_messages import TestMessagesView

urlpatterns = [
    path("test-messages/", TestMessagesView.as_view(), name='test-messages'),
]
"""
from typing import Any

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import RedirectView


class TestMessagesView(RedirectView):
    """Test messages view."""

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Prepare message and redirect to the next."""
        msg = self.request.GET.get("msg", "Test message. ?type=all / debug / info / success / warning / error")
        messages.set_level(self.request, messages.DEBUG)
        if self.request.GET.get("type") in ("debug", "all"):
            messages.debug(self.request, msg)
        if self.request.GET.get("type") in ("info", "all"):
            messages.info(self.request, msg)
        if self.request.GET.get("type") in ("success", "all"):
            messages.success(self.request, msg)
        if self.request.GET.get("type") in ("warning", "all"):
            messages.warning(self.request, msg)
        if self.request.GET.get("type") in ("error", "all"):
            messages.error(self.request, msg)
        return self.request.GET.get("next", "/")
