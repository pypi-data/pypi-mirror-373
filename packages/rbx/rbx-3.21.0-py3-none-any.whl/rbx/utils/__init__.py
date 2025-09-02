"""Common utility methods."""

__all__ = ["Singleton", "smart_url"]

import re
from threading import Lock
from urllib.parse import urljoin


class Singleton(type):
    """Metaclass providing a thread-safe Singleton interface."""

    _instances = {}
    _singleton_lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._singleton_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def smart_url(url, force_https=False, prefix=None):
    """Return the appropriate URL.

    The returned URL will be:
     - an empty string, when the provided url is None;
     - the provided url, unchanged, when it includes the protocol ('http', 'https' or '//');
     - otherwise, the provided url, optionally prefixed with the given prefix.
     - finally, if force_https is set, we ensure the URL is return with the HTTPS protocol.
    """
    if not url:
        return ""

    if not force_https and (url.startswith("http") or url.startswith("//")):
        return url

    if prefix:
        url = urljoin(prefix, url)

    if force_https:
        match = re.match("http:|https:", url)
        if match:
            _, _, url = url.partition(match.group(0))

        url = urljoin("https://", url)

    return url
