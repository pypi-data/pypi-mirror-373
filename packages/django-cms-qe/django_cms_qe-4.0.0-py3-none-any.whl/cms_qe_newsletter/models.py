from cms.models import CMSPlugin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

SUBSCRIBE = 1
UNSUBSCRIBE = 2

SERVICE_NONE = 1
SERVICE_MAILCHIMP = 2
SERVICES = (
    (SERVICE_NONE, _('None')),
    (SERVICE_MAILCHIMP, _('Mailchimp')),
)


class NewsletterPluginModel(CMSPlugin):
    """
    Configuration model for newsletter plugin.
    Allows to set:
    * Title
    * Mail lists on mailchimp to which subscribers will be added
    * Show or hide full name
    * Require full name or not
    """

    mailing_lists = models.ManyToManyField(
        'MailingList',
        verbose_name=_('Maillist'),
    )
    title = models.CharField(
        max_length=150,
        verbose_name=_('Title'),
        help_text=_('The title of subscribes that will be shown to users'),
        blank=True
    )
    fullname_show = models.BooleanField(
        verbose_name=_('Show fullname fields'),
        default=False,
    )
    fullname_require = models.BooleanField(
        verbose_name=_('Require fullname'),
        default=False,
    )

    def __str__(self):
        return self.title

    def clean(self):
        if not self.fullname_show and self.fullname_require:
            raise ValidationError(_('Can not hide and require a full name at the same time.'))


class MailingList(models.Model):
    """
    Mailing list model which also synchronize with external services like Mailchimp.
    If ``external_id`` is not set then subscriber is not synchronized.
    """

    name = models.CharField(max_length=50)

    external_service = models.PositiveSmallIntegerField(choices=SERVICES, default=SERVICE_NONE)
    external_id = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.external_service != SERVICE_NONE and not self.external_id:
            raise ValidationError(_('External ID is required when external service selected.'))


class Subscriber(models.Model):
    """
    Subscriber model which also synchronize with external services like Mailchimp.
    If ``external_id`` is not set then subscriber is not synchronized.
    """

    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    email = models.EmailField()
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    external_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        # pylint: disable=no-member
        return _('{} in list {}').format(self.email, self.mailing_list)

    # pylint: disable=signature-differs
    def save(self, *args, **kwargs):
        self.subscribe()
        super().save(*args, **kwargs)

    # pylint: disable=W0222 arguments-differ
    def delete(self, *args, **kwargs):
        self.unsubscribe()
        super().delete(*args, **kwargs)

    def subscribe(self):
        """
        Called before save to create task to sync action with external service.
        """
        if self.mailing_list.external_service == SERVICE_NONE:
            return

        if not self.external_id:
            SubscribeTask.objects.create(
                mailing_list=self.mailing_list,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                type=SUBSCRIBE,
            )

    def unsubscribe(self):
        """
        Called before delete to create task to sync action with external service.
        """
        if self.mailing_list.external_service == SERVICE_NONE:
            return

        if self.external_id:
            SubscribeTask.objects.create(
                mailing_list=self.mailing_list,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                external_id=self.external_id,
                type=UNSUBSCRIBE,
            )
        else:
            # Not sync, just for case cancel any sync task.
            SubscribeTask.objects.filter(
                mailing_list=self.mailing_list,
                email=self.email,
            ).delete()


class SubscribeTask(models.Model):
    """
    Item for task queue for subscribing and unsubscribing members on the external
    service like Mailchimp. The queue can is processed by ``cms-qe-newsletter-sync`` command.
    """

    TASK_TYPES = (
        (SUBSCRIBE, _('Subscribe')),
        (UNSUBSCRIBE, _('Unsubscribe')),
    )

    # The subscriber's parameters are copied to the task,
    # in order not to lose them if the subscriber is removed from the database
    mailing_list = models.ForeignKey(MailingList, null=True, on_delete=models.CASCADE)
    email = models.EmailField()
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    external_id = models.CharField(max_length=10, null=True)

    # Task params:
    type = models.PositiveSmallIntegerField(choices=TASK_TYPES)
    created = models.DateTimeField(auto_now=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField()

    def __str__(self):
        # pylint: disable=no-member
        return _('Task for email {}').format(self.email)

    def failure(self, error_message):
        self.attempts += 1
        self.last_error = error_message
        self.save()

    def should_process(self) -> bool:
        """
        Checks whether task should be tried to process. With less attempts
        it tries more often, with more attempts it waits more time to not
        overwhelm resources.
        """
        time_to_process = self.created + timezone.timedelta(seconds=self.attempts ** 4)
        return time_to_process <= timezone.now()
