"""
Provides functionality for persistence of data
"""

from calculadorapnav.output_methods.base_output import BaseOutput

# emissions data
from calculadorapnav.output_methods.emissions_data import (
    EmissionsData,
)

# Output to a file
from calculadorapnav.output_methods.file import FileOutput

# Output calling a REST http endpoint
from calculadorapnav.output_methods.http import HTTPOutput

# Output to a logger
from calculadorapnav.output_methods.logger import (
    GoogleCloudLoggerOutput,
    LoggerOutput,
)
