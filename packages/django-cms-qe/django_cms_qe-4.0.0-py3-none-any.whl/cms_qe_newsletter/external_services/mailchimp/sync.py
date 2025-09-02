from ...models import SERVICE_MAILCHIMP, MailingList
from .client import MailChimpClient, MailchimpIsNotSetException


def sync_mailing_lists():
    try:
        client = MailChimpClient()
    except MailchimpIsNotSetException:
        return

    result = client.get_lists()
    for mailing_lits in result['lists']:
        if not MailingList.objects.filter(external_service=SERVICE_MAILCHIMP, external_id=mailing_lits['id']).count():
            MailingList.objects.create(
                name=mailing_lits['name'],
                external_service=SERVICE_MAILCHIMP,
                external_id=mailing_lits['id'],
            )


def sync_subscribe(mailing_list_id, email, first_name, last_name):
    return MailChimpClient().subscribe(mailing_list_id, email, first_name, last_name)


def sync_unsubscribe(mailing_list_id, email):
    MailChimpClient().unsubscribe(mailing_list_id, email)
