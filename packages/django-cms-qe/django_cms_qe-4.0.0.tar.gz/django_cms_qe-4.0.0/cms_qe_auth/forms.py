from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):  # pylint: disable=too-many-ancestors
    """
    Main form for registration. Extends base Django`s
    ``UserCreationForm`` by including also email.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class PasswordResetFormWithEmailExistenceCheck(PasswordResetForm):
    """
    Adding verification that the user exists in the database to PasswordResetForm.

    https://github.com/django/django/blob/master/django/contrib/auth/views.py
    """

    def clean_email(self):
        email = self.cleaned_data['email']
        if not get_user_model().objects.filter(email=email).exists():  # pylint: disable=no-member
            raise ValidationError(_("Email does not exists"))
        return email
