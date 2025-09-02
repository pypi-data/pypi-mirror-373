import logging
import smtplib
import socket
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.module_loading import import_string

ACTION_OK = 250  # Requested mail action okay, completed.

logger = logging.getLogger(__name__)

# pylint:disable=invalid-name


def pk_to_uidb64(pk):
    return urlsafe_base64_encode(force_bytes(pk))


def uidb64_to_pk(uidb64):
    return force_str(urlsafe_base64_decode(uidb64))


def get_user_by_uidb64(uidb64):
    User = get_user_model()
    try:
        pk = uidb64_to_pk(uidb64)
        user = User.objects.get(pk=pk)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return user


class ActionIsNoOkResponse(Exception):
    """Action si not OK response."""


def check_smtp_response(response: tuple[int, bytes]) -> None:
    """Check if response is valid."""
    if response[0] != ACTION_OK:
        raise ActionIsNoOkResponse(force_str(response[1]))


class SMTPCheckRecipient:
    """SMTP server checks recipient email if the server accepts it."""

    def __init__(self, hostname: str):
        self.smtp: Optional[smtplib.SMTP] = None
        self.hostname = hostname

    def connect(self) -> None:
        if self.hostname and self.smtp is None:
            try:
                self.smtp = smtplib.SMTP(self.hostname, timeout=5)
                check_smtp_response(self.smtp.helo())
                check_smtp_response(self.smtp.docmd('MAIL FROM:""'))
            except (ActionIsNoOkResponse, OSError, socket.gaierror, smtplib.SMTPException) as error:
                logger.error(error)

    def close(self) -> None:
        if self.smtp is not None and self.smtp.sock is not None:
            self.smtp.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def check(self, address: str) -> None:
        """Check if SMTP server accepts email address. Raise ValidationError if not."""
        self.connect()
        if self.smtp is not None and self.smtp.sock is not None:
            try:
                code, message = self.smtp.docmd(f'RCPT TO:{address}')
                if code != ACTION_OK:
                    raise ValidationError(force_str(message), code="invalid")
            except (socket.gaierror, smtplib.SMTPException) as error:
                logger.error(error)


def smtp_server_accepts_email_address(address: str) -> None:
    """SMTP server accepts email address. Raise ValidationError if not."""
    backend = import_string(settings.EMAIL_BACKEND)
    if hasattr(backend, "host"):
        # Check only smtp backend.
        with SMTPCheckRecipient(settings.EMAIL_HOST) as checker:
            checker.check(address)
