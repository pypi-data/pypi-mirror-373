"""
The Carbon Tracker module. The following objects/decorators belong to the Public API
"""

from ._version import __version__  # noqa
from .emissions_tracker import (
    track_emissions,
)

__all__ = ["track_emissions"]
__app_name__ = "calculadorapnav"
