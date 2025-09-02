# Same as django.core.mail.backends.filebased.EmailBackend, but save logs with .eml extension.
import datetime
import os
from typing import Optional

from django.core.mail.backends.filebased import EmailBackend


class EmlEmailBackend(EmailBackend):
    """Save logs with .eml extension."""

    _fname: Optional[str]

    def _get_filename(self):
        """Return a unique file name."""
        if self._fname is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            fname = "%s-%s.eml" % (timestamp, abs(id(self)))
            self._fname = os.path.join(self.file_path, fname)
        return self._fname
