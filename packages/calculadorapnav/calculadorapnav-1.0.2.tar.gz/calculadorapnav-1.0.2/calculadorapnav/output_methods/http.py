import dataclasses
import getpass

import requests

from calculadorapnav.external.logger import logger
from calculadorapnav.output_methods.base_output import BaseOutput
from calculadorapnav.output_methods.emissions_data import EmissionsData


class HTTPOutput(BaseOutput):
    """
    Send emissions data to HTTP endpoint
    Warning : This is an empty model to guide you.
    We do not provide a server.
    """

    def __init__(self, endpoint_url: str):
        self.endpoint_url: str = endpoint_url

    def out(self, total: EmissionsData, delta: EmissionsData, token: str = None):
        payload = dataclasses.asdict(total)
        headers = {"Authorization": f"Bearer {token}"}
        url = self.endpoint_url
        last_exception = None

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code not in (200, 201):
                logger.warning(
                    "HTTP Output returned an unexpected status code: %s",
                    resp.status_code,
                )
            else:
                logger.info(
                    "HTTP Output successfully sent data to %s with status code %s",
                    url,
                    resp.status_code,
                )
            return
        except Exception as e:
            last_exception = e

        logger.error(
            f"Could not establish connection with the supplied endpoint URL: {url} not sending data"
        )
