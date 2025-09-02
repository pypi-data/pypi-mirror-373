import logging
import subprocess
import time
from multiprocessing import Lock, Process
from typing import Any, Optional, Union

from django.conf import settings
from django.db.models import Model

DelayType = Union[int, float]
ArgsType = Union[tuple[str, ...], list[str]]

logger = logging.getLogger(__name__)
lock = Lock()


def run_subprocess(args: ArgsType, delay: Optional[DelayType] = None) -> Optional[subprocess.CompletedProcess]:
    """Run the system command in subprocess."""
    if delay is not None:
        time.sleep(delay)
    logger.info('subprocess.run(%s)', args)
    lock.acquire()
    try:
        return subprocess.run(args, check=False)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error(str(err))
    finally:
        lock.release()
    return None


def run_process(args: ArgsType, delay: Optional[DelayType] = None) -> Process:
    """Run the process and no wait for the result."""
    proc = Process(target=run_subprocess, args=(args, delay))
    proc.start()
    return proc


def reload_site(sender: Optional[Model], **kwargs: dict[str, Any]) -> None:  # pylint: disable=unused-argument
    "Reload the site."
    if settings.RELOAD_SITE:
        run_process(settings.RELOAD_SITE, 3)
