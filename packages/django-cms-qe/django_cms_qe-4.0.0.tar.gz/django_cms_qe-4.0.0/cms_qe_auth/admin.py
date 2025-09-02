from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User
from .utils import smtp_server_accepts_email_address


class CmsQeAuthUserForm(forms.ModelForm):

    def clean(self):
        field_name = "email"
        if self.cleaned_data.get(field_name) and self.cleaned_data.get("is_active") and \
                self.cleaned_data.get("is_staff"):
            try:
                smtp_server_accepts_email_address(self.cleaned_data[field_name])
            except ValidationError as err:
                msg = _("Enter a valid email or don't enter any.")
                if "email" in self._errors:
                    self._errors[field_name].append(err)
                    self._errors[field_name].append(msg)
                else:
                    self._errors[field_name] = self.error_class([err, msg])
        return self.cleaned_data


class CmsQeAuthUserAdmin(UserAdmin):
    form = CmsQeAuthUserForm


admin.register(User)(CmsQeAuthUserAdmin)
