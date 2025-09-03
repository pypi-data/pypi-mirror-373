#!/usr/bin/env python
from chime_frb_api.backends import frb_master  # noqa
from chime_frb_api.core.logger import get_logger  # noqa

try:
    from pkg_resources import get_distribution as _get_distribution

    __version__ = _get_distribution("chime_frb_api").version
except ImportError:
    __version__ = "unknown"
