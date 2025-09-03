import sys
from typing import Any, List, Optional, Union
from calculadorapnav.external.logger import logger

if sys.version_info >= (3, 9):
    try:
        from pydantic import BaseModel, field_validator, model_validator

        USE_NEW_VALIDATORS = True
    except ImportError:
        from pydantic import BaseModel, validator

        USE_NEW_VALIDATORS = False
else:
    raise ImportError("Python 3.9 or higher is required.")


class EmissionsInputModel(BaseModel):
    token: Optional[Union[str, object]]
    type_process: str
    type_ram: Optional[Union[str, object]]
    n_batch: Optional[Union[int, object]]
    n_epoch: Optional[Union[int, object]]
    measure_power_secs: Optional[Union[int, object]]
    type_ram: Optional[Union[int, object]]
    output_dir: Optional[Union[str, object]]
    output_file: Optional[Union[str, object]]
    save_to_file: Optional[Union[bool, object]]
    save_to_logger: Optional[Union[bool, object]]
    logging_logger: Optional[Union[Any, object]]
    cloud_provider: Optional[Union[str, object]]
    cloud_region: Optional[Union[str, object]]
    country_iso_code: Optional[Union[str, object]]
    offline: Optional[Union[bool, object]]
    model_id: Optional[Union[str, object]]
    endpoint_url: Optional[Union[str, object]]
    gpu_ids: Optional[Union[List[Any], object]]
    log_level: Optional[Union[int, str, object]]
    on_csv_write: Optional[Union[str, object]]
    logger_preamble: Optional[Union[str, object]]
    default_cpu_power: Optional[Union[int, object]]
    pue: Optional[Union[int, object]]
    allow_multiple_runs: Optional[Union[bool, object]]
    region: Optional[Union[str, object]]

    if USE_NEW_VALIDATORS:

        @field_validator("type_process")
        def validate_type_process(cls, v):
            if type(v) is object:
                return v
            allowed = {"training", "inference"}
            if v not in allowed:
                raise ValueError(f"type_process must be one of {allowed}")
            return v

        @field_validator("type_ram")
        def validate_type_ram(cls, v):
            if type(v) is object:
                return v
            allowed = {"DDR3", "DDR4", "DDR5"}
            if v not in allowed:
                raise ValueError(f"type_ram must be one of {allowed}")
            return v

        @field_validator("on_csv_write")
        def validate_on_csv_write(cls, v):
            allowed = {"append", "update"}
            if isinstance(v, object) and type(v) is object:
                return v
            if v not in allowed:
                raise ValueError(f"on_csv_write must be one of {allowed}")
            return v

        @model_validator(mode="after")
        def validate_offline_country_or_cloud(cls, values):
            offline = getattr(values, "offline", False)
            country = getattr(values, "country_iso_code", None)
            cloud_provider = getattr(values, "cloud_provider", None)
            cloud_region = getattr(values, "cloud_region", None)

            if offline is True:
                # Check if country_iso_code is a valid 3-letter uppercase string
                if isinstance(country, str) and len(country) == 3 and country.isupper():
                    pass  # Valid country code, OK
                # Otherwise, require both cloud_provider and cloud_region as strings
                elif isinstance(cloud_provider, str) and isinstance(cloud_region, str):
                    pass  # Valid cloud provider/region, OK
                else:
                    raise ValueError(
                        "When 'offline' is True, you must provide either 'country_iso_code' (3 uppercase letters) "
                        "or both 'cloud_provider' and 'cloud_region' as strings."
                    )
            return values

        @model_validator(mode="after")
        def validate_model_id_and_endpoint_url(cls, values):
            offline = getattr(values, "offline", False)
            model_id = getattr(values, "model_id", None)
            endpoint_url = getattr(values, "endpoint_url", None)

            if offline != True:
                if (
                    not isinstance(model_id, str)
                    or len(model_id) != 64
                    or not all(c in "0123456789abcdef" for c in model_id)
                ):
                    raise ValueError(
                        "When 'offline' is False, 'model_id' must be a 64-character hexadecimal string (hash)."
                    )
                if not isinstance(endpoint_url, str) or not endpoint_url.startswith(
                    "http"
                ):
                    raise ValueError(
                        "When 'offline' is False, 'endpoint_url' must be a valid URL starting with 'http'."
                    )
            return values

    else:

        @validator("type_process")
        def validate_type_process(cls, v):
            if type(v) is object:
                return v
            allowed = {"training", "inference"}
            if v not in allowed:
                raise ValueError(f"type_process must be one of {allowed}")
            return v

        @validator("type_ram")
        def validate_type_ram(cls, v):
            if type(v) is object:
                return v
            allowed = {"DDR3", "DDR4", "DDR5"}
            if v not in allowed:
                raise ValueError(f"type_ram must be one of {allowed}")
            return v

        @validator("on_csv_write")
        def validate_on_csv_write(cls, v):
            allowed = {"append", "update"}
            if isinstance(v, object) and type(v) is object:
                return v
            if v not in allowed:
                raise ValueError(f"on_csv_write must be one of {allowed}")
            return v

        @validator("offline", always=True)
        def validate_offline_country_or_cloud(cls, v, values):
            offline = v
            country = values.get("country_iso_code")
            cloud_provider = values.get("cloud_provider")
            cloud_region = values.get("cloud_region")

            if offline is True:
                if isinstance(country, str):
                    if not (
                        isinstance(country, str)
                        and len(country) == 3
                        and country.isupper()
                    ):
                        raise ValueError(
                            "When 'offline' is True, 'country_iso_code' must be a string of 3 uppercase letters."
                        )
                elif isinstance(cloud_provider, str) and isinstance(cloud_region, str):
                    pass
                else:
                    raise ValueError(
                        "When 'offline' is True, you must provide either 'country_iso_code' (3 uppercase letters) or both 'cloud_provider' and 'cloud_region' as strings."
                    )
            return v

        @validator("model_id", "endpoint_url", pre=True, always=True)
        def validate_model_id_and_endpoint_url(cls, v, values, field):
            offline = values.get("offline", False)
            if offline != True:
                if field.name == "model_id":
                    if (
                        not isinstance(v, str)
                        or len(v) != 64
                        or not all(c in "0123456789abcdef" for c in v)
                    ):
                        msg = "When 'offline' is False, 'model_id' must be a 64-character hexadecimal string (hash)."
                        logger.error(f"Input validation error: {msg}")
                        raise ValueError(msg)
                elif field.name == "endpoint_url":
                    if not isinstance(v, str) or not v.startswith("http"):
                        msg = "When 'offline' is False, 'endpoint_url' must be a valid URL starting with 'http'."
                        logger.error(f"Input validation error: {msg}")
                        raise ValueError(msg)
            return v
