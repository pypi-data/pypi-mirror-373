"""
App configuration: This will likely change when we have a common location for data files
"""

import atexit
import json
import sys
from contextlib import ExitStack
from typing import Dict

import pandas as pd

if sys.version_info >= (3, 9):
    from importlib.resources import as_file as importlib_resources_as_file
    from importlib.resources import files as importlib_resources_files
else:
    from importlib_resources import as_file as importlib_resources_as_file
    from importlib_resources import files as importlib_resources_files


class DataSource:
    def __init__(self):
        self.config = {
            "endpoint_url": "https://api.pnav.io/v1",
            "geo_js_url": "https://get.geojs.io/v1/ip/geo.json",
            "cloud_emissions_path": "data/cloud/impact.csv",
            "usa_emissions_data_path": "data/private_infra/2016/usa_emissions.json",
            "can_energy_mix_data_path": "data/private_infra/2016/canada_energy_mix.json",  # noqa: E501
            "global_energy_mix_data_path": "data/private_infra/global_energy_mix.json",  # noqa: E501
            "carbon_intensity_per_source_path": "data/private_infra/carbon_intensity_per_source.json",
            "cpu_power_path": "data/hardware/cpu_power.csv",
        }
        self.module_name = "calculadorapnav"

    @property
    def geo_js_url(self):
        return self.config["geo_js_url"]

    @property
    def endpoint_url(self):
        return self.config["endpoint_url"]

    @staticmethod
    def get_ressource_path(package: str, filepath: str):
        file_manager = ExitStack()
        atexit.register(file_manager.close)
        ref = importlib_resources_files(package).joinpath(filepath)
        path = file_manager.enter_context(importlib_resources_as_file(ref))
        return path

    @property
    def cloud_emissions_path(self):
        """
        Resource Extraction from a package
        https://setuptools.readthedocs.io/en/latest/pkg_resources.html#resource-extraction
        """
        return self.get_ressource_path(
            self.module_name, self.config["cloud_emissions_path"]
        )

    @property
    def carbon_intensity_per_source_path(self):
        """
        Get the path from the package resources.
        """
        return self.get_ressource_path(
            self.module_name, self.config["carbon_intensity_per_source_path"]
        )

    @property
    def global_energy_mix_data_path(self):
        return self.get_ressource_path(
            self.module_name, self.config["global_energy_mix_data_path"]
        )

    @property
    def cpu_power_path(self):
        return self.get_ressource_path(self.module_name, self.config["cpu_power_path"])

    def get_global_energy_mix_data(self) -> Dict:
        """
        Returns Global Energy Mix Data
        """
        with open(self.global_energy_mix_data_path) as f:
            global_energy_mix: Dict = json.load(f)
        return global_energy_mix

    def get_cloud_emissions_data(self) -> pd.DataFrame:
        """
        Returns Cloud Regions Impact Data
        """
        return pd.read_csv(self.cloud_emissions_path)

    def get_carbon_intensity_per_source_data(self) -> Dict:
        """
        Returns Carbon intensity per source. In gCO2.eq/kWh.
        """
        with open(self.carbon_intensity_per_source_path) as f:
            carbon_intensity_per_source: Dict = json.load(f)
        return carbon_intensity_per_source

    def get_cpu_power_data(self) -> pd.DataFrame:
        """
        Returns CPU power Data
        """
        return pd.read_csv(self.cpu_power_path)


class DataSourceException(Exception):
    pass
