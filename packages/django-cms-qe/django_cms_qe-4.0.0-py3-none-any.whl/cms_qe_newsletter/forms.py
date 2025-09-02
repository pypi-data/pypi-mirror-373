from django import forms

from cms_qe_newsletter.models import Subscriber


class SubscriberForm(forms.ModelForm):
    """
    Subscribers form validates subscriber data.
    """

    class Meta:
        model = Subscriber
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, fullname_require, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fullname_require = fullname_require
        if fullname_require:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

    # pylint: disable=arguments-differ
    def save(self, commit=True, mailing_lists=None):
        """
        Add a new subscriber to all mail lists which was selected in the plugin settings.
        """
        data = self.cleaned_data
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        if mailing_lists is not None:
            for mailing_list in mailing_lists:
                if not Subscriber.objects.filter(email=email, mailing_list=mailing_list).count():
                    Subscriber.objects.create(
                        mailing_list=mailing_list,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                    )
