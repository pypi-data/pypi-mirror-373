import json
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class EmissionsData:
    """
    Output object containing run data
    """

    timestamp: str
    type_process: str
    model_id: str
    ref: float
    duration: float
    emissions: float
    emissions_rate: float
    emissions_batch: float
    emissions_epoch: float
    cpu_power: float
    gpu_power: float
    ram_power: float
    cpu_energy: float
    gpu_energy: float
    ram_energy: float
    energy_consumed: float
    energy_batch: float
    n_batch: int
    time_batch: float
    energy_epoch: float
    n_epoch: int
    time_epoch: float
    model_size: str
    n_parameters: int
    n_features: int
    country_name: str
    country_iso_code: str
    region: str
    cloud_provider: str
    cloud_region: str
    os: str
    python_version: str
    cpu_count: float
    cpu_model: str
    gpu_count: float
    gpu_model: str
    ram_total_size: float
    type_ram: str
    on_cloud: str = "N"
    pue: float = 1

    @property
    def values(self) -> OrderedDict:
        return OrderedDict(self.__dict__.items())

    def compute_delta_emission(self, previous_emission):
        delta_duration = self.duration - previous_emission.duration
        self.duration = delta_duration
        delta_emissions = self.emissions - previous_emission.emissions
        self.emissions = delta_emissions
        self.cpu_energy -= previous_emission.cpu_energy
        self.gpu_energy -= previous_emission.gpu_energy
        self.ram_energy -= previous_emission.ram_energy
        self.energy_consumed -= previous_emission.energy_consumed
        if delta_duration > 0:
            # emissions_rate in g/s : delta_emissions in kg.CO2 / delta_duration in s
            self.emissions_rate = delta_emissions / delta_duration
        else:
            self.emissions_rate = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
