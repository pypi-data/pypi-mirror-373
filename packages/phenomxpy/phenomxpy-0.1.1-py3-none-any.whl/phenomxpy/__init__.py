# Copyright (C) 2023  Cecilio García Quirós
try:
    from ._version import version as __version__
except ModuleNotFoundError:  # development mode
    __version__ = "unknown"

__copyright__ = "2023, Cecilio García Quirós"
__author__ = "Cecilio García Quirós"

from .phenomt.phenomt import IMRPhenomT, IMRPhenomTHM
from .phenomt.phenomtp import IMRPhenomTP, IMRPhenomTPHM

__all__ = ["IMRPhenomT", "IMRPhenomTHM", "IMRPhenomTP", "IMRPhenomTPHM"]
