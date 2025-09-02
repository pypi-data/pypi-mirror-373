import logging
from functools import lru_cache

from rich.logging import RichHandler

log_settings = {
    "use_rich_logging": True,
}


@lru_cache()
def get_logger(level: str):
    handlers = []
    if log_settings.get("use_rich_logging", False):
        handlers.append(RichHandler(rich_tracebacks=True))

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
    )

    if not log_settings.get("use_rich_logging", False):
        logger = logging.getLogger("rich")
    else:
        logger = logging.getLogger("threedi_cmd")
    return logger


class Dummy(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, *args, **kwargs):
        return self

    def __setattr__(self, *args, **kwargs):
        pass

    def __delattr__(self, *args, **kwargs):
        pass

    def __getitem__(self, *args, **kwargs):
        return self

    def __setitem__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass
