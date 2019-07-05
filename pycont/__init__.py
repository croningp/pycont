"""
Custom library designed to control Tricontinent C-series syringe pumps.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
from ._version import __version__
from ._logger import __logger_root_name__
from .controller import MultiPumpController, C3000Controller

import logging
logging.getLogger(__logger_root_name__).addHandler(logging.NullHandler())
