import os
import re
import subprocess
import sys
import torch
import ast
from contextlib import contextmanager
from os.path import expandvars
from pathlib import Path
from typing import Optional, Union

import cpuinfo
import psutil

from calculadorapnav.external.logger import logger

_sentinel = object()

SLURM_JOB_ID = os.environ.get(
    "SLURM_JOB_ID",  # default
    os.environ.get("SLURM_JOBID"),  # deprecated but may still be used
)


@contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        logger.warning("graceful shutdown. Exceptions:")
        logger.warning(
            exceptions if len(exceptions) != 1 else exceptions[0], exc_info=True
        )
        logger.warning("stopping.")


def resolve_path(path: Union[str, Path]) -> Path:
    """
    Fully resolve a path:
    resolve env vars ($HOME etc.) -> expand user (~) -> make absolute

    Args:
        path (Union[str, Path]): Path to a file or repository to resolve as
            string or pathlib.Path

    Returns:
        pathlib.Path: resolved absolute path
    """
    return Path(expandvars(str(path))).expanduser().resolve()


def backup(file_path: Union[str, Path], ext: Optional[str] = ".bak") -> None:
    """
    Resolves the path to a path then backs it up, adding the extension provided.

    Args:
        file_path (Union[str, Path]): Path to a file to backup.
        ext (Optional[str], optional): extension to append to the filename when
            backing it up. Defaults to ".bak".
    """
    file_path = resolve_path(file_path)
    if not file_path.exists():
        return
    assert file_path.is_file()
    idx = 0
    parent = file_path.parent
    file_name = f"{file_path.name}{ext}"
    backup_path = parent / file_name

    while backup_path.exists():
        file_name = f"{file_path.name}_{idx}{ext}"
        backup_path = parent / file_name
        idx += 1

    file_path.rename(backup_path)


def detect_cpu_model() -> str:
    cpu_info = cpuinfo.get_cpu_info()
    if cpu_info:
        cpu_model_detected = cpu_info.get("brand_raw", "")
        return cpu_model_detected
    return None


def is_mac_os() -> str:
    system = sys.platform.lower()
    return system.startswith("dar")


def is_windows_os() -> str:
    system = sys.platform.lower()
    return system.startswith("win")


def is_linux_os() -> str:
    system = sys.platform.lower()
    return system.startswith("lin")


def count_cpus() -> int:
    if SLURM_JOB_ID is None:
        return psutil.cpu_count()

    try:
        logger.debug(
            "SLURM environment detected for job {SLURM_JOB_ID}, running"
            + " `scontrol show job $SLURM_JOB_ID` to count SLURM-available cpus."
        )
        scontrol = subprocess.check_output(
            [f"scontrol show job {SLURM_JOB_ID}"], shell=True
        ).decode()
    except subprocess.CalledProcessError:
        logger.warning(
            "Error running `scontrol show job $SLURM_JOB_ID` "
            + "to count SLURM-available cpus. Using the machine's cpu count."
        )
        return psutil.cpu_count()

    num_cpus_matches = re.findall(r"NumCPUs=\d+", scontrol)

    if len(num_cpus_matches) == 0:
        logger.warning(
            "Could not find NumCPUs= after running `scontrol show job $SLURM_JOB_ID` "
            + "to count SLURM-available cpus. Using the machine's cpu count."
        )
        return psutil.cpu_count()

    if len(num_cpus_matches) > 1:
        logger.warning(
            "Unexpected output after running `scontrol show job $SLURM_JOB_ID` "
            + "to count SLURM-available cpus. Using the machine's cpu count."
        )
        return psutil.cpu_count()

    num_cpus = num_cpus_matches[0].replace("NumCPUs=", "")
    logger.debug(f"Detected {num_cpus} cpus available on SLURM.")
    return int(num_cpus)


def process_type_validate(process: Optional[str] = None) -> str:
    """
    Validates and ensures the input process type is either 'training' or 'inference'.
    If the `process` argument is not provided or is not a string, the function prompts
    the user to input a valid process type. The input is repeatedly requested until
    a valid value ('training' or 'inference') is provided.
    Args:
        process (Optional[str]): The process type to validate. Can be 'training',
                                 'inference', or None.
    Returns:
        str: A valid process type ('training' or 'inference').
    Raises:
        None: The function does not raise exceptions but relies on user input for validation.
    """
    valid_types = {"training", "inference"}
    if process is None or (
        isinstance(process, object) and not isinstance(process, str)
    ):
        process = (
            input("Type of process is required (training or inference)1:")
            .lower()
            .strip()
        )

    while process not in valid_types:
        print("Invalid input. Type of process must be 'training' or 'inference'.")
        process = (
            input("Type of process is required (training or inference):")
            .lower()
            .strip()
        )
    return process


def hash_token_validate(token_hash):
    """
    Validates and processes a token hash input.

    This function ensures that the provided token hash is a valid 64-character
    hexadecimal string. If the input is invalid or not provided, the user is
    prompted to enter a valid token hash. The input is sanitized by converting
    it to lowercase, stripping whitespace, and removing spaces.

    Args:
        token_hash (str or None): The initial token hash to validate. If None
        or invalid, the user will be prompted to provide a valid token hash.

    Returns:
        str: A valid 64-character hexadecimal token hash.

    Raises:
        None: This function does not raise exceptions but will repeatedly
        prompt the user until a valid token hash is provided.
    """
    if token_hash is None or (
        isinstance(token_hash, object) and not isinstance(token_hash, str)
    ):
        token_hash = (
            input("Token hash for online conection is required:")
            .lower()
            .strip()
            .replace(" ", "")
        )
    # else:
    #     token_hash_input = token_hash if isinstance(token_hash, str) and re.fullmatch(r'[a-f0-9]{64}', token_hash) else input("Invalid input. Token hash must be a 64-character hexadecimal string, Enter the token:").lower().strip().replace(" ", "")
    attempts = 0
    max_attempts = 2
    while not re.fullmatch(r"[a-f0-9]{64}", token_hash):
        if attempts >= max_attempts:
            logger.info(
                "Maximum number of attempts exceeded for token hash input, information not sent."
            )
            return None
        print("Invalid input. Token hash must be a 64-character hexadecimal string.")
        token_hash = input("Enter the token:").lower().strip().replace(" ", "")
        attempts += 1
    return token_hash


def model_id_validate(model_id):
    """
    Valida que el model_id sea un string no vacío y no None.

    Args:
        model_id (str or None): El model_id a validar.

    Returns:
        str or None: Un model_id válido (string no vacío), o None si se exceden los intentos.
    """
    attempts = 0
    max_attempts = 2
    while model_id is None or not isinstance(model_id, str) or not model_id.strip():
        if attempts >= max_attempts:
            logger.info(
                "Maximum number of attempts exceeded for model ID input, information not sent."
            )
            return None
        print("Invalid input. Model ID must be a non-empty string.")
        model_id = input("Enter the model ID:").strip()
        attempts += 1
    return model_id


def endpoint_url_validate(endpoint_url):
    """
    Validates that the endpoint URL is a non-empty string and not None.

    Args:
        endpoint_url (str or None): The endpoint URL to validate.

    Returns:
        str or None: A valid endpoint URL (non-empty string), or None if the maximum number of attempts is exceeded.
    """
    attempts = 0
    max_attempts = 2
    while (
        endpoint_url is None
        or not isinstance(endpoint_url, str)
        or not endpoint_url.strip()
    ):
        if attempts >= max_attempts:
            logger.info(
                "Maximum number of attempts exceeded for endpoint URL input, information not sent."
            )
            return None
        print("Invalid input. Endpoint URL must be a non-empty string.")
        endpoint_url = input("Enter the endpoint URL:").strip()
        attempts += 1
    return endpoint_url


def validate_country_iso_code(country_iso_code, cloud_provider):
    """
    Validates and ensures that the provided country ISO code is a valid
    3-letter uppercase string. If the input is invalid or not provided,
    the user is prompted to enter a valid ISO code.

    Args:
        country_iso_code (str or None): The initial country ISO code to validate.
                                        Can be None or an invalid value.
        cloud_provider (str or None): The cloud provider information.
                                      Can be None or an invalid value.

    Returns:
        str: A valid 3-letter uppercase country ISO code.

    Raises:
        ValueError: If the user fails to provide a valid ISO code after multiple attempts.
    """
    if (
        country_iso_code is None
        or (
            isinstance(country_iso_code, object)
            and not isinstance(country_iso_code, str)
        )
    ) and (
        cloud_provider is None
        or (isinstance(cloud_provider, object) and not isinstance(cloud_provider, str))
    ):
        country_iso_code = input("Country ISO code is required:").upper().strip()
    while not re.fullmatch(r"[A-Z]{3}", country_iso_code):
        print("Invalid input. Country ISO code must be a 3-letter uppercase string.")
        country_iso_code = input("Enter the country ISO code:").upper().strip()
    return country_iso_code


# def arg_model_params(variables_locales):
#     modelo = None
#     for nombre_variable, valor_variable in variables_locales.items():
#         if hasattr(valor_variable, 'modules'):
#             modelo = valor_variable
#             break
#     if modelo is None:
#         logger.info("No se ha encontrado un modelo como parametro.")
#         num_parameters = None
#     else:
#         logger.info("Se ha encontrado un modelo como parametro.")
#         num_parameters = count_parameters(modelo)

#     return num_parameters

# def variable_model_params(variables_funcion, model_name):
#     modelo = None

#     for nodo in ast.walk(variables_funcion):
#         if isinstance(nodo, ast.Assign):
#             for target in nodo.targets:
#                 if isinstance(target, ast.Name) and target.id == model_name:
#                     modelo = nodo.value

# if modelo:
#     print(f"El modelo de entrenamiento es: {ast.dump(modelo)}")
#     num_parameters = count_parameters(modelo)
# else:
#     print("No se encontró ninguna declaración de modelo en la función.")
#     num_parameters = None
# return num_parameters
