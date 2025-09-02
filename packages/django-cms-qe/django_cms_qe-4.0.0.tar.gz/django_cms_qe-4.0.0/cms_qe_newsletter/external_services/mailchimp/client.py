from collections.abc import Iterable

from constance import config


# pylint:disable=global-variable-undefined
class MailchimpIsNotSetException(Exception):
    pass


class MailChimpClient:
    """
    Helper class to communicate with MailChimp.
    """

    def __init__(self) -> None:
        """
        Checking if MailChimp API key and username is configured and return a MailChimp API client.
        """
        username = config.MAILCHIMP_USERNAME
        api_key = config.MAILCHIMP_API_KEY
        if api_key and username:
            # Dynamic import so it's possible to mock.
            from mailchimp3 import MailChimp  # pylint:disable=import-outside-toplevel
            self.client = MailChimp(mc_user=username, mc_api=api_key)
        else:
            raise MailchimpIsNotSetException('API key or username for mailchimp is not set.')

    def get_lists(self) -> Iterable[str]:
        """
        :return: List of lists with fields ``id`` and ``name``.
        """
        return self.client.lists.all(get_all=True, fields='lists.name,lists.id')

    def subscribe(self, mailing_list_id, email, first_name, last_name) -> None:
        """
        Add a subscriber and return the id (subscriber_hash).
        """
        new_subscriber = self.client.lists.members.create(mailing_list_id, {
            'email_address': email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': first_name,
                'LNAME': last_name,
            },
        })
        return new_subscriber['id']

    def unsubscribe(self, mailing_list_id, subscriber_hash) -> None:
        """
        Remove a subscriber.
        """
        self.client.lists.members.delete(mailing_list_id, subscriber_hash)
