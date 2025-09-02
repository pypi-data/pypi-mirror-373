from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect

from .external_services.sync import sync_mailing_lists


# pylint: disable=unused-argument
@staff_member_required
def update_lists(request):
    """
    Download mailing lists from external services like Mailchimp.

    Used in administration in custom button "Synchronize mailing list from external sources".
    """
    sync_mailing_lists()
    return redirect('admin:cms_qe_newsletter_mailinglist_changelist')
