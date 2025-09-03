"""
Contains implementations of the Public facing API: EmissionsTracker,
OfflineEmissionsTracker and @track_emissions
"""

import dataclasses
import os
import platform
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from calculadorapnav._version import __version__
from calculadorapnav.core.config import get_hierarchical_config
from calculadorapnav.core.emissions import Emissions
from calculadorapnav.core.model_data import ModelData
from calculadorapnav.core.resource_tracker import ResourceTracker
from calculadorapnav.core.units import Energy, Power, Time
from calculadorapnav.core.util import (
    count_cpus,
    suppress,
    hash_token_validate,
    model_id_validate,
    endpoint_url_validate,
)
from calculadorapnav.external.geography import CloudMetadata, GeoMetadata
from calculadorapnav.external.hardware import CPU, GPU, RAM, AppleSiliconChip
from calculadorapnav.external.logger import logger, set_logger_format, set_logger_level
from calculadorapnav.external.scheduler import PeriodicScheduler
from calculadorapnav.input import DataSource
from calculadorapnav.lock import Lock
from calculadorapnav.output import (
    BaseOutput,
    EmissionsData,
    FileOutput,
    HTTPOutput,
    LoggerOutput,
)
from calculadorapnav.core.input_validation import EmissionsInputModel
import time
import functools
from pydantic import ValidationError
from typing import List, Optional, Union

_sentinel = object()


class BaseEmissionsTracker(ABC):
    """
    Primary abstraction with Emissions Tracking functionality.
    Has two abstract methods, `_get_geo_metadata` and `_get_cloud_metadata`
    that are implemented by two concrete classes: `OfflineCarbonTracker`
    and `CarbonTracker.`
    """

    def _set_from_conf(
        self, var, name, default=None, return_type=None, prevent_setter=False
    ):
        """
        Method to standardize private argument setting. Generic flow is:

        * If a value for the variable `var` with name `name` is provided in the
          __init__ constructor: set the the private attribute `self._{name}` to
          that value

        * If no value is provided for `var`, i.e. `var is _sentinel` is True then
          we try to assign a value to it:

            * If there is a value for `name` in the external configuration (config
              files or env variables), then we use it
            * Otherwise `self._{name}` is set to the `default` value

        Additionally, if `return_type` is provided and one of `float` `int` or `bool`,
        the value for `self._{name}` will be parsed to this type.

        Use `prevent_setter=True` for debugging purposes only.

        Args:
            var (Any): The variable's value to set as private attribute
            name (str): The variable's name such that `self._{name}` will be set
                to `var`
            default (Any, optional): The value to use for self._name if no value
                is provided in the constructor and no value is found in the external
                configuration.
                Defaults to None.
            return_type (Any, optional): A type to parse the value to. Defaults to None.
            prevent_setter (bool, optional): Whether to set the private attribute or
                simply return the value. For debugging. Defaults to False.

        Returns:
            [Any]: The value used for `self._{name}`
        """
        # Check the hierarchical configuration has been read parsed and set.
        assert hasattr(self, "_external_conf")
        assert isinstance(self._external_conf, dict)

        # Store final values in _conf
        if not hasattr(self, "_conf"):
            self._conf = {"calculadorapnav_version": __version__}

        value = _sentinel

        # a value for the keyword argument `name` is provided in the constructor:
        # use it
        if var is not _sentinel:
            value = var
        else:
            # no value provided in the constructor for `name`: check in the conf
            # (using the provided default value)
            value = self._external_conf.get(name, default)

            # parse to `return_type` if needed
            if return_type is not None:
                if return_type is bool:
                    value = str(value).lower() == "true"
                else:
                    assert callable(return_type)
                    value = return_type(value)
        # Check conf
        if name == "output_dir":
            if not os.path.exists(value):
                raise OSError(f"Folder '{value}' doesn't exist !")
        if name == "gpu_ids":
            if value is None and os.environ.get("CUDA_VISIBLE_DEVICES"):
                value = os.environ.get("CUDA_VISIBLE_DEVICES")
        # store final value
        self._conf[name] = value
        # set `self._{name}` to `value`
        if not prevent_setter:
            setattr(self, f"_{name}", value)
        # return final value (why not?)
        return value

    def __init__(
        self,
        model_id: Optional[str] = _sentinel,
        endpoint_url: Optional[str] = _sentinel,
        token: Optional[str] = _sentinel,
        type_process: Optional[str] = _sentinel,
        type_ram: Optional[str] = _sentinel,
        n_batch: Optional[int] = _sentinel,
        n_epoch: Optional[int] = _sentinel,
        measure_power_secs: Optional[float] = _sentinel,
        output_dir: Optional[str] = _sentinel,
        output_file: Optional[str] = _sentinel,
        save_to_file: Optional[bool] = _sentinel,
        save_endpoint: Optional[str] = _sentinel,
        save_to_logger: Optional[bool] = _sentinel,
        logging_logger: Optional[LoggerOutput] = _sentinel,
        output_handlers: Optional[List[BaseOutput]] = _sentinel,
        gpu_ids: Optional[List] = _sentinel,
        tracking_mode: Optional[str] = _sentinel,
        log_level: Optional[Union[int, str]] = _sentinel,
        on_csv_write: Optional[str] = _sentinel,
        logger_preamble: Optional[str] = _sentinel,
        default_cpu_power: Optional[int] = _sentinel,
        pue: Optional[int] = _sentinel,
        allow_multiple_runs: Optional[bool] = _sentinel,
    ):
        """
        :param token: API token (requires sign-up for PNAV).
        :param model_id: Model ID to track emissions for.
        :param type_process: Type of process to track. Defaults to None.
                             must be one of "training", "inference".
        :param type_ram: Type of RAM to track. Defaults to None.
                                must be one of "DDR3", "DDR4", "DDR5".
        :param n_batches: Number of batches in the training process.
        :param n_epochs: Number of epochs in the training process.
        :param project_name: Project name for current experiment run, default name
                             is "calculadorapnav".
        :param measure_power_secs: Interval (in seconds) to measure hardware power
                                   usage, defaults to 15.
        :param output_dir: Directory path to which the experiment details are logged,
                           defaults to current directory.
        :param output_file: Name of the output CSV file, defaults to `emissions.csv`.
        :param save_to_file: Indicates if the emission artifacts should be logged to a
                             file, defaults to True.
        :param save_endpoint: Indicates if the emission artifacts should be sent
                            to the calculadorapnav API, defaults to True.
        :param save_to_logger: Indicates if the emission artifacts should be written
                            to a dedicated logger, defaults to False.
        :param logging_logger: LoggerOutput object encapsulating a logging.logger
                            or a Google Cloud logger.
        :param gpu_ids: User-specified known gpu ids to track.
                            Defaults to None, which means that all available gpus will be tracked.
                            It needs to be a list of integers or a comma-separated string.
                            Valid examples: [1, 3, 4] or "1,2".
        :param emissions_endpoint: Optional URL of http endpoint for sending emissions
                                   data.
        :param experiment_id: Id of the experiment.
        :param experiment_name: Label of the experiment

        :param log_level: Global calculadorapnav log level. Accepts one of:
                            {"debug", "info", "warning", "error", "critical"}.
                          Defaults to "info".
        :param on_csv_write: "append" or "update". Whether to always append a new line
                             to the csv when writing or to update the existing `run_id`
                             row (useful when calling`tracker.flush()` manually).
                             Accepts one of "append" or "update". Default is "append".
        :param logger_preamble: String to systematically include in the logger.
                                messages. Defaults to "".
        :param default_cpu_power: cpu power to be used as default if the cpu is not known.
        :param pue: PUE (Power Usage Effectiveness) of the datacenter.
        :param allow_multiple_runs: Allow multiple instances of calculadorapnav running in parallel. Defaults to False.
        """

        # logger.info("base tracker init")
        self._external_conf = get_hierarchical_config()
        self._set_from_conf(allow_multiple_runs, "allow_multiple_runs", False, bool)
        if self._allow_multiple_runs:
            logger.warning(
                "Multiple instances of calculadorapnav are allowed to run at the same time."
            )
        else:
            # Acquire lock file to prevent multiple instances of calculadorapnav running
            # at the same time
            try:
                self._lock = Lock()
                self._lock.acquire()
            except FileExistsError:
                logger.error(
                    f"Error: Another instance of calculadorapnav is probably running as we find `{self._lock.lockfile_path}`. Turn off the other instance to be able to run this one or use `allow_multiple_runs` or delete the file. Exiting."
                )
                # Do not continue if another instance of calculadorapnav is running
                self._another_instance_already_running = True
                return

        self._set_from_conf(gpu_ids, "gpu_ids")
        self._set_from_conf(log_level, "log_level", "info")
        self._set_from_conf(measure_power_secs, "measure_power_secs", 15, float)
        self._set_from_conf(output_dir, "output_dir", ".")
        self._set_from_conf(output_file, "output_file", f"emissions_{type_process}.csv")
        self._set_from_conf(token, "token")
        self._set_from_conf(type_process, "type_process")
        self._set_from_conf(model_id, "model_id")
        self._set_from_conf(endpoint_url, "endpoint_url")
        self._set_from_conf(type_ram, "type_ram", "DDR4")
        self._set_from_conf(n_batch, "n_batch", 0)
        self._set_from_conf(n_epoch, "n_epoch", 0)
        self._set_from_conf(save_to_file, "save_to_file", True, bool)
        self._set_from_conf(save_endpoint, "save_endpoint", True, bool)
        self._set_from_conf(save_to_logger, "save_to_logger", False, bool)
        self._set_from_conf(logging_logger, "logging_logger")
        self._set_from_conf(output_handlers, "output_handlers", [])
        self._set_from_conf(tracking_mode, "tracking_mode", "process")
        self._set_from_conf(on_csv_write, "on_csv_write", "append")
        self._set_from_conf(logger_preamble, "logger_preamble", "")
        self._set_from_conf(default_cpu_power, "default_cpu_power")
        self._set_from_conf(pue, "pue", 1.0, float)

        set_logger_level(self._log_level)
        set_logger_format(self._logger_preamble)

        self._start_time: Optional[float] = None
        self._last_measured_time: float = time.perf_counter()
        self._total_energy: Energy = Energy.from_energy(kWh=0)
        self._total_cpu_energy: Energy = Energy.from_energy(kWh=0)
        self._total_gpu_energy: Energy = Energy.from_energy(kWh=0)
        self._total_ram_energy: Energy = Energy.from_energy(kWh=0)
        self._cpu_power: Power = Power.from_watts(watts=0)
        self._gpu_power: Power = Power.from_watts(watts=0)
        self._ram_power: Power = Power.from_watts(watts=0)
        self._measure_occurrence: int = 0
        self._cloud = None
        self._previous_emissions = None
        self._conf["os"] = platform.platform()
        self._conf["python_version"] = platform.python_version()
        self._conf["cpu_count"] = count_cpus()
        self._geo = None
        self._task_start_measurement_values = {}
        self._task_stop_measurement_values = {}
        self._active_task: Optional[str] = None

        # Tracking mode detection
        ressource_tracker = ResourceTracker(self)
        ressource_tracker.set_CPU_GPU_ram_tracking()

        self._conf["hardware"] = list(map(lambda x: x.description(), self._hardware))

        logger.info(">>> Tracker's metadata:")
        logger.info(f"  Platform system: {self._conf.get('os')}")
        logger.info(f"  Python version: {self._conf.get('python_version')}")
        logger.info(
            f"  CalculadoraPNAV version: {self._conf.get('calculadorapnav_version')}"
        )
        logger.info(f"  Available RAM : {self._conf.get('ram_total_size'):.3f} GB")
        logger.info(f"  CPU count: {self._conf.get('cpu_count')}")
        logger.info(f"  CPU model: {self._conf.get('cpu_model')}")
        logger.info(f"  GPU count: {self._conf.get('gpu_count')}")
        if self._gpu_ids:
            logger.info(
                f"  GPU model: {self._conf.get('gpu_model')} BUT only tracking these GPU ids : {self._conf.get('gpu_ids')}"
            )
        else:
            logger.info(f"  GPU model: {self._conf.get('gpu_model')}")

        # Run `self._measure_power_and_energy` every `measure_power_secs` seconds in a
        # background thread
        self._scheduler = PeriodicScheduler(
            function=self._measure_power_and_energy,
            interval=self._measure_power_secs,
        )

        self._data_source = DataSource()

        cloud: CloudMetadata = self._get_cloud_metadata()

        if cloud.is_on_private_infra:
            self._geo = self._get_geo_metadata()
            self._conf["longitude"] = self._geo.longitude
            self._conf["latitude"] = self._geo.latitude
            self._conf["region"] = cloud.region
            self._conf["provider"] = cloud.provider
        else:
            self._conf["region"] = cloud.region
            self._conf["provider"] = cloud.provider

        self._emissions: Emissions = Emissions(self._data_source)

        self._init_output_methods()

    def _init_output_methods(self, *, api_key: str = None):
        """
        Prepare the different output methods
        """
        if self._save_to_file:
            self._output_handlers.append(
                FileOutput(
                    self._output_file,
                    self._output_dir,
                    self._on_csv_write,
                )
            )

        if self._save_endpoint:
            self._output_handlers.append(HTTPOutput(self._endpoint_url))

    def service_shutdown(self, signum, frame):
        logger.warning("service_shutdown - Caught signal %d" % signum)
        self.stop()

    @suppress(Exception)
    def start(self) -> None:
        """
        Starts tracking the experiment.
        Currently, Nvidia GPUs are supported.
        :return: None
        """
        # if another instance of calculadorapnav is already running, stop here
        if (
            hasattr(self, "_another_instance_already_running")
            and self._another_instance_already_running
        ):
            logger.warning(
                "Another instance of calculadorapnav is already running. Exiting."
            )
            return
        if self._start_time is not None:
            logger.warning("Already started tracking")
            return

        self._last_measured_time = self._start_time = time.perf_counter()
        # Read initial energy for hardware
        for hardware in self._hardware:
            hardware.start()

        self._scheduler.start()

    @suppress(Exception)
    def flush(self) -> Optional[float]:
        """
        Write the emissions to disk or call the API depending on the configuration,
        but keep running the experiment.
        :return: CO2 emissions in kgs
        """
        if self._start_time is None:
            logger.error("You first need to start the tracker.")
            return None

        # Run to calculate the power used from last
        # scheduled measurement to shutdown
        self._measure_power_and_energy()

        emissions_data = self._prepare_emissions_data()
        emissions_data_delta = self._compute_emissions_delta(emissions_data)

        self._persist_data(
            total_emissions=emissions_data, delta_emissions=emissions_data_delta
        )

        return emissions_data.emissions

    @suppress(Exception)
    def stop(self) -> Optional[float]:
        """
        Stops tracking the experiment
        :return: CO2 emissions in kgs
        """
        # if another instance of calculadorapnav is already running, Nothing to do here
        if (
            hasattr(self, "_another_instance_already_running")
            and self._another_instance_already_running
        ):
            logger.warning(
                "Another instance of calculadorapnav is already running. Exiting."
            )
            return
        if not self._allow_multiple_runs:
            # Release the lock
            self._lock.release()
        if self._start_time is None:
            logger.error("You first need to start the tracker.")
            return None

        if self._scheduler:
            self._scheduler.stop()
            self._scheduler = None
        else:
            logger.warning("Tracker already stopped !")

        duration = time.perf_counter() - self._start_time

        self._measure_power_and_energy(duration)

        model_data = ModelData(
            self._type_process,
            self.fn_result,
            self.fn_args,
            self._n_batch,
            self._n_epoch,
            duration,
            self._total_energy,
        )
        model_measurements = model_data.do_model_measurements()

        if isinstance(self, EmissionsTracker):
            self._token = hash_token_validate(self._token)
            # self._model_id = model_id_validate(self._model_id)
            # self._endpoint_url = endpoint_url_validate(self._endpoint_url)

            if not self._token or not self._model_id or not self._endpoint_url:
                try:
                    raise ValueError("Token validation failed. Stopping execution.")
                except Exception as e:
                    logger.error(f"{e}")

        self._save_endpoint = (
            False
            if isinstance(self, OfflineEmissionsTracker)
            or self._token is None
            or self._model_id is None
            else self._save_endpoint
        )

        emissions_data = self._prepare_emissions_data(duration, model_measurements)

        emissions_data_delta = self._compute_emissions_delta(emissions_data)

        self._persist_data(
            total_emissions=emissions_data,
            delta_emissions=emissions_data_delta,
            token=self._token,
            model_id=self._model_id,
            endpoint_url=self._endpoint_url,
        )

        self.final_emissions_data = emissions_data
        self.final_emissions = emissions_data.emissions
        return emissions_data.emissions

    def _persist_data(
        self,
        total_emissions: EmissionsData,
        delta_emissions: EmissionsData,
        token: str = None,
        model_id: str = None,
        endpoint_url: str = None,
    ):
        for handler in self._output_handlers:
            if isinstance(handler, HTTPOutput):
                if self._save_endpoint and token is not None and model_id is not None:
                    handler.out(total_emissions, delta_emissions, token)
            else:
                handler.out(total_emissions, delta_emissions)

    def _prepare_emissions_data(
        self, duration: float = None, model_measurements: dict = None
    ) -> EmissionsData:
        """
        :delta: If 'True', return only the delta comsumption since the last call.
        """
        cloud: CloudMetadata = self._get_cloud_metadata()

        duration: Time = Time.from_seconds(
            duration if duration is not None else time.perf_counter() - self._start_time
        )

        if cloud.is_on_private_infra:
            emissions, ref_twh = self._emissions.get_private_infra_emissions(
                self._total_energy, self._geo
            )
            country_name = self._geo.country_name
            country_iso_code = self._geo.country_iso_code
            region = self._geo.region
            on_cloud = "N"
            cloud_provider = ""
            cloud_region = ""
        else:
            emissions, ref_twh = self._emissions.get_cloud_emissions(
                self._total_energy, cloud, self._geo
            )
            country_name = self._emissions.get_cloud_country_name(cloud)
            country_iso_code = self._emissions.get_cloud_country_iso_code(cloud)
            region = self._emissions.get_cloud_geo_region(cloud)
            on_cloud = "Y"
            cloud_provider = cloud.provider
            cloud_region = cloud.region
        total_emissions = EmissionsData(
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            type_process=self._type_process,
            model_id=self._model_id,
            ref=ref_twh,
            duration=duration.seconds,
            emissions=emissions,
            emissions_rate=emissions / duration.seconds,
            emissions_batch=emissions / self._n_batch if self._n_batch != 0 else 0,
            emissions_epoch=emissions / self._n_epoch if self._n_epoch != 0 else 0,
            cpu_power=self._cpu_power.W,
            gpu_power=self._gpu_power.W,
            ram_power=self._ram_power.W,
            cpu_energy=self._total_cpu_energy.kWh,
            gpu_energy=self._total_gpu_energy.kWh,
            ram_energy=self._total_ram_energy.kWh,
            energy_consumed=self._total_energy.kWh,
            energy_batch=model_measurements["energy_batch"],
            n_batch=self._n_batch,
            time_batch=model_measurements["time_batch"],
            energy_epoch=model_measurements["energy_epoch"],
            n_epoch=self._n_epoch,
            time_epoch=model_measurements["time_epoch"],
            model_size=model_measurements["model_size"],
            n_parameters=model_measurements["num_parameters"],
            n_features=model_measurements["num_features"],
            country_name=country_name,
            country_iso_code=country_iso_code,
            region=region,
            on_cloud=on_cloud,
            cloud_provider=cloud_provider,
            cloud_region=cloud_region,
            os=self._conf.get("os"),
            python_version=self._conf.get("python_version"),
            gpu_count=self._conf.get("gpu_count"),
            gpu_model=self._conf.get("gpu_model"),
            cpu_count=self._conf.get("cpu_count"),
            cpu_model=self._conf.get("cpu_model"),
            ram_total_size=self._conf.get("ram_total_size"),
            type_ram=self._type_ram,
            pue=self._pue,
        )
        logger.debug(total_emissions)
        return total_emissions

    def _compute_emissions_delta(self, total_emissions: EmissionsData) -> EmissionsData:
        delta_emissions: EmissionsData = total_emissions
        if self._previous_emissions is None:
            self._previous_emissions = total_emissions
        else:
            # Create a copy
            delta_emissions = dataclasses.replace(total_emissions)
            # Compute emissions rate from delta
            delta_emissions.compute_delta_emission(self._previous_emissions)
            # TODO : find a way to store _previous_emissions only when
            # TODO : the API call succeeded
            self._previous_emissions = total_emissions
        return delta_emissions

    @abstractmethod
    def _get_geo_metadata(self) -> GeoMetadata:
        """
        :return: Metadata containing geographical info
        """

    @abstractmethod
    def _get_cloud_metadata(self) -> CloudMetadata:
        """
        :return: Metadata containing cloud info
        """

    def _do_measurements(self) -> None:
        for hardware in self._hardware:
            h_time = time.perf_counter()
            # Compute last_duration again for more accuracy
            last_duration = time.perf_counter() - self._last_measured_time
            (
                power,
                energy,
            ) = hardware.measure_power_and_energy(last_duration=last_duration)
            # Apply the PUE of the datacenter to the consumed energy
            energy *= self._pue
            self._total_energy += energy
            if isinstance(hardware, CPU):
                self._total_cpu_energy += energy
                self._cpu_power = power
                logger.info(
                    f"Energy consumed for all CPUs : {self._total_cpu_energy.kWh:.6f} kWh"
                    + f". Total CPU Power : {self._cpu_power.W} W"
                )
            elif isinstance(hardware, GPU):
                self._total_gpu_energy += energy
                self._gpu_power = power
                logger.info(
                    f"Energy consumed for all GPUs : {self._total_gpu_energy.kWh:.6f} kWh"
                    + f". Total GPU Power : {self._gpu_power.W} W"
                )
            elif isinstance(hardware, RAM):
                self._total_ram_energy += energy
                self._ram_power = power
                logger.info(
                    f"Energy consumed for RAM : {self._total_ram_energy.kWh:.6f} kWh"
                    + f". RAM Power : {self._ram_power.W} W"
                )
            elif isinstance(hardware, AppleSiliconChip):
                if hardware.chip_part == "CPU":
                    self._total_cpu_energy += energy
                    self._cpu_power = power
                    logger.info(
                        f"Energy consumed for all CPUs : {self._total_cpu_energy.kWh:.6f} kWh"
                        + f". Total CPU Power : {self._cpu_power.W} W"
                    )
                elif hardware.chip_part == "GPU":
                    self._total_gpu_energy += energy
                    self._gpu_power = power
                    logger.info(
                        f"Energy consumed for all GPUs : {self._total_gpu_energy.kWh:.6f} kWh"
                        + f". Total GPU Power : {self._gpu_power.W} W"
                    )
            else:
                logger.error(f"Unknown hardware type: {hardware} ({type(hardware)})")
            h_time = time.perf_counter() - h_time
            logger.debug(
                f"{hardware.__class__.__name__} : {hardware.total_power().W:,.2f} "
                + f"W during {last_duration:,.2f} s [measurement time: {h_time:,.4f}]"
            )
        logger.info(
            f"{self._total_energy.kWh:.6f} kWh of electricity used since the beginning."
        )

    def _measure_power_and_energy(self, duration: float = None) -> None:
        """
        A function that is periodically run by the `BackgroundScheduler`
        every `self._measure_power_secs` seconds.
        :return: None
        """
        last_duration = (
            duration
            if duration is not None
            else time.perf_counter() - self._last_measured_time
        )

        warning_duration = self._measure_power_secs * 3
        if last_duration > warning_duration:
            warn_msg = (
                "Background scheduler didn't run for a long period"
                + " (%ds), results might be inaccurate"
            )
            logger.warning(warn_msg, last_duration)

        self._do_measurements()
        self._last_measured_time = time.perf_counter()
        self._measure_occurrence += 1

        logger.debug(f"last_duration={last_duration}\n------------------------")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb) -> None:
        self.stop()


class OfflineEmissionsTracker(BaseEmissionsTracker):
    """
    Offline implementation of the `EmissionsTracker`
    In addition to the standard arguments, the following are required.
    """

    @suppress(Exception)
    def __init__(
        self,
        *args,
        country_iso_code: Optional[str] = _sentinel,
        region: Optional[str] = _sentinel,
        cloud_provider: Optional[str] = _sentinel,
        cloud_region: Optional[str] = _sentinel,
        **kwargs,
    ):
        """
        Parameters
        ----------
        country_iso_code: 3 letter ISO Code of the country where the
                                 experiment is being run
        region: The province or region (e.g. California in the US).
                       Currently, this only affects calculations for the United States
                       and Canada
        cloud_provider: The cloud provider specified for estimating emissions
                               intensity, defaults to None.
        cloud_region: The region of the cloud data center, defaults to None.


        """
        self._external_conf = get_hierarchical_config()
        self._set_from_conf(cloud_provider, "cloud_provider")
        self._set_from_conf(cloud_region, "cloud_region")
        self._set_from_conf(country_iso_code, "country_iso_code")
        self._set_from_conf(region, "region")

        logger.info("offline tracker init")

        if self._region is not None:
            assert isinstance(self._region, str)
            self._region: str = self._region.lower()

        if self._country_iso_code:
            try:
                self._country_name: str = DataSource().get_global_energy_mix_data()[
                    self._country_iso_code
                ]["country_name"]
            except KeyError as e:
                logger.error(
                    "Does not support country"
                    + f" with ISO code {self._country_iso_code} "
                    f"Exception occurred {e}, the default ISO code 'ESP' will be used."
                )
                self._country_iso_code = "ESP"
                self._country_name = "Spain"

        super().__init__(*args, **kwargs)

    def _get_geo_metadata(self) -> GeoMetadata:
        return GeoMetadata(
            country_iso_code=self._country_iso_code,
            country_name=self._country_name,
            region=self._region,
        )

    def _get_cloud_metadata(self) -> CloudMetadata:
        if self._cloud is None:
            self._cloud = CloudMetadata(
                provider=self._cloud_provider, region=self._cloud_region
            )
        return self._cloud


class EmissionsTracker(BaseEmissionsTracker):
    """
    An online emissions tracker that auto infers geographical location,
    using the `geojs` API
    """

    def _get_geo_metadata(self) -> GeoMetadata:
        return GeoMetadata.from_geo_js(self._data_source.geo_js_url)

    def _get_cloud_metadata(self) -> CloudMetadata:
        if self._cloud is None:
            self._cloud = CloudMetadata.from_utils()
        return self._cloud


def track_emissions(
    fn: Callable = None,
    token: Optional[str] = _sentinel,
    model_id: Optional[str] = _sentinel,
    endpoint_url: Optional[str] = _sentinel,
    type_process: str = "",
    type_ram: Optional[str] = _sentinel,
    n_batch: Optional[int] = _sentinel,
    n_epoch: Optional[int] = _sentinel,
    measure_power_secs: Optional[int] = _sentinel,
    output_dir: Optional[str] = _sentinel,
    output_file: Optional[str] = _sentinel,
    save_to_file: Optional[bool] = _sentinel,
    save_to_logger: Optional[bool] = _sentinel,
    logging_logger: Optional[LoggerOutput] = _sentinel,
    offline: Optional[bool] = _sentinel,
    gpu_ids: Optional[List] = _sentinel,
    log_level: Optional[Union[int, str]] = _sentinel,
    on_csv_write: Optional[str] = _sentinel,
    logger_preamble: Optional[str] = _sentinel,
    default_cpu_power: Optional[int] = _sentinel,
    pue: Optional[int] = _sentinel,
    country_iso_code: Optional[str] = _sentinel,
    allow_multiple_runs: Optional[bool] = _sentinel,
    region: Optional[str] = _sentinel,
    cloud_provider: Optional[str] = _sentinel,
    cloud_region: Optional[str] = _sentinel,
):
    """
    Decorator to track and log emissions for a function using either `EmissionsTracker` or `OfflineEmissionsTracker`.

    This decorator validates input parameters using a Pydantic model and manages the lifecycle of the emissions tracker.
    It supports both online and offline tracking modes, determined by the `offline` parameter.

    Parameters:
        fn (Callable, optional): The function to decorate. If not provided, returns a decorator.
        token (Optional[str]): Authentication token for online tracking.
        model_id (Optional[str]): Identifier for the model being tracked.
        endpoint_url (Optional[str]): Endpoint URL for emissions tracking.
        type_process (str): Type of process (e.g., "training", "inference").
        type_ram (Optional[str]): Type of RAM used.
        n_batch (Optional[int]): Number of batches processed.
        n_epoch (Optional[int]): Number of epochs processed.
        measure_power_secs (Optional[int]): Interval in seconds for measuring power usage.
        output_dir (Optional[str]): Directory to save output files.
        output_file (Optional[str]): Name of the output file.
        save_to_file (Optional[bool]): Whether to save results to a file.
        save_to_logger (Optional[bool]): Whether to log results.
        logging_logger (Optional[LoggerOutput]): Logger instance for logging.
        offline (Optional[bool]): If True, uses offline tracking mode.
        gpu_ids (Optional[List]): List of GPU IDs to track.
        log_level (Optional[Union[int, str]]): Logging level.
        on_csv_write (Optional[str]): Callback or hook for CSV writing.
        logger_preamble (Optional[str]): Preamble text for logger output.
        default_cpu_power (Optional[int]): Default CPU power (Watt) if not measured.
        pue (Optional[int]): Power Usage Effectiveness value.
        country_iso_code (Optional[str]): ISO code for the country.
        allow_multiple_runs (Optional[bool]): Allow multiple runs in the same process.
        region (Optional[str]): Region identifier.
        cloud_provider (Optional[str]): Cloud provider name.
        cloud_region (Optional[str]): Cloud region name.

    Returns:
        Callable: The decorated function with emissions tracking enabled.

    Raises:
        ValidationError: If input parameters do not pass validation.

    Usage:
        @track_emissions(type_process="training", offline=True)
        def train_model(...):
            ...
    """

    def _decorate(fn: Callable):
        @functools.wraps(fn)
        def wrapped_fn(*args, **kwargs):
            fn_result = None

            input_kwargs = dict(
                token=token,
                model_id=model_id,
                endpoint_url=endpoint_url,
                type_process=type_process,
                type_ram=type_ram,
                n_batch=n_batch,
                n_epoch=n_epoch,
                measure_power_secs=measure_power_secs,
                output_dir=output_dir,
                output_file=output_file,
                save_to_file=save_to_file,
                save_to_logger=save_to_logger,
                logging_logger=logging_logger,
                offline=offline,
                gpu_ids=gpu_ids,
                log_level=log_level,
                on_csv_write=on_csv_write,
                logger_preamble=logger_preamble,
                default_cpu_power=default_cpu_power,
                pue=pue,
                country_iso_code=country_iso_code,
                allow_multiple_runs=allow_multiple_runs,
                region=region,
                cloud_provider=cloud_provider,
                cloud_region=cloud_region,
            )

            try:
                validated = EmissionsInputModel(**input_kwargs)
            except ValidationError as e:
                logger.error(f"Input validation error: {e}")
                raise

            if offline and offline is not _sentinel:
                tracker = OfflineEmissionsTracker(
                    model_id=model_id,
                    type_process=type_process,
                    type_ram=type_ram,
                    n_batch=n_batch,
                    n_epoch=n_epoch,
                    measure_power_secs=measure_power_secs,
                    output_dir=output_dir,
                    output_file=output_file,
                    save_to_file=save_to_file,
                    save_to_logger=save_to_logger,
                    logging_logger=logging_logger,
                    gpu_ids=gpu_ids,
                    log_level=log_level,
                    on_csv_write=on_csv_write,
                    logger_preamble=logger_preamble,
                    default_cpu_power=default_cpu_power,
                    pue=pue,
                    allow_multiple_runs=allow_multiple_runs,
                    country_iso_code=country_iso_code,
                    region=region,
                    cloud_provider=cloud_provider,
                    cloud_region=cloud_region,
                )
            else:
                tracker = EmissionsTracker(
                    token=token,
                    model_id=model_id,
                    endpoint_url=endpoint_url,
                    type_process=type_process,
                    type_ram=type_ram,
                    n_batch=n_batch,
                    n_epoch=n_epoch,
                    measure_power_secs=measure_power_secs,
                    output_dir=output_dir,
                    output_file=output_file,
                    save_to_file=save_to_file,
                    save_to_logger=save_to_logger,
                    logging_logger=logging_logger,
                    gpu_ids=gpu_ids,
                    log_level=log_level,
                    on_csv_write=on_csv_write,
                    logger_preamble=logger_preamble,
                    default_cpu_power=default_cpu_power,
                    pue=pue,
                    allow_multiple_runs=allow_multiple_runs,
                )

            tracker.start()
            try:
                fn_result = fn(*args, **kwargs)
                tracker.fn_result = fn_result
                tracker.fn_args = args
                tracker.fn_kwargs = kwargs
            finally:
                logger.info(
                    "\nGraceful stopping: collecting and writing information.\n"
                    + "Please wait a few seconds..."
                )
                tracker.stop()
                logger.info("Done!\n")

            return fn_result

        return wrapped_fn

    if fn:
        return _decorate(fn)
    return _decorate
