"""
Base configuration for quick and easy production use.

By default enables all security options, all useful plugins, etc.
"""

# pylint: disable=wildcard-import
from .app import *
from .auth import *
from .cache import *
from .cms import *
from .constants import *
from .database import *
from .email import *
from .i18n import *
from .logging import *
from .path import *
from .search import *
from .security import *
from .template import *
