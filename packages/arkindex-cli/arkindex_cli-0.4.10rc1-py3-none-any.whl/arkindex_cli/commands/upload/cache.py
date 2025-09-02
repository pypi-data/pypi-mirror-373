import json
import logging

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, path):
        self.path = path
        if path.exists():
            self.data = json.loads(self.path.read_text())
            logger.debug(f"Loading cache from {self.path}")
        else:
            self.data = {}
            logger.debug(f"Empty cache from {self.path}")

    def __del__(self):
        logger.debug(f"Saving cache to {self.path}")
        self.path.write_text(
            json.dumps(self.data, default=str, indent=4, sort_keys=True)
        )

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value


def save_cache(func):
    """
    Decorator to automatically save the cache.
    The target function must have a `cache` argument.
    """

    def wrap(*args, **kwargs):
        cache = kwargs.pop("cache")

        try:
            return func(cache=cache, *args, **kwargs)
        except BaseException:
            # Make sure to always save cache
            del cache
            raise

    return wrap
