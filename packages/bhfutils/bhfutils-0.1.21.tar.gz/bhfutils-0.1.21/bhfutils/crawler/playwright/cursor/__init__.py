import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

### EXPORTS

from .shared.spoof import get_path as path


__all__ = ["path"]