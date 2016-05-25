from ._version import __version__
from _logger import __logger_root_name__

import logging
logging.getLogger(__logger_root_name__).addHandler(logging.NullHandler())
