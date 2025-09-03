import csv
import os
from typing import List

import pandas as pd

from calculadorapnav.core.util import backup
from calculadorapnav.external.logger import logger
from calculadorapnav.output_methods.base_output import BaseOutput
from calculadorapnav.output_methods.emissions_data import EmissionsData


class FileOutput(BaseOutput):
    """
    Saves experiment artifacts to a file
    """

    def __init__(
        self, output_file_name: str, output_dir: str, on_csv_write: str = "append"
    ):
        if on_csv_write not in {"append", "update"}:
            raise ValueError(
                f"Unknown `on_csv_write` value: {on_csv_write}"
                + " (should be one of 'append' or 'update'"
            )
        self.output_file_name: str = output_file_name
        if not os.path.exists(output_dir):
            raise OSError(f"Folder '{output_dir}' doesn't exist !")
        self.output_dir: str = output_dir
        self.on_csv_write: str = on_csv_write
        self.save_file_path = os.path.join(self.output_dir, self.output_file_name)
        logger.info(
            f"Saving emissions data to file {os.path.abspath(self.save_file_path)}"
        )

    def has_valid_headers(self, data: EmissionsData):
        with open(self.save_file_path) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            dict_from_csv = dict(list(csv_reader)[0])
            list_of_column_names = list(dict_from_csv.keys())
            return list(data.values.keys()) == list_of_column_names

    def out(self, total: EmissionsData, delta: EmissionsData):
        file_exists: bool = os.path.isfile(self.save_file_path)
        if file_exists and not self.has_valid_headers(total):
            logger.info("Backing up old emission file")
            backup(self.save_file_path)
            file_exists = False

        if not file_exists:
            df = pd.DataFrame(columns=total.values.keys())
            new_row = pd.DataFrame.from_records([dict(total.values)])
            if df.empty:
                df = new_row
            else:
                df = pd.concat([df, new_row], ignore_index=True)
        elif self.on_csv_write == "append":
            df = pd.read_csv(self.save_file_path)
            new_row = pd.DataFrame.from_records([dict(total.values)])
            if df.empty:
                df = new_row
            else:
                df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = pd.read_csv(self.save_file_path)
            df_run = df.loc[df.run_id == total.run_id]
            if len(df_run) < 1:
                df = pd.concat([df, pd.DataFrame.from_records([dict(total.values)])])
            elif len(df_run) > 1:
                logger.warning(
                    f"CSV contains more than 1 ({len(df_run)})"
                    + f" rows with current run ID ({total.run_id})."
                    + "Appending instead of updating."
                )
                df = pd.concat([df, pd.DataFrame.from_records([dict(total.values)])])
            else:
                df.at[
                    df.run_id == total.run_id, total.values.keys()
                ] = total.values.values()

        df.to_csv(self.save_file_path, index=False)
