#!/usr/bin/env python3

import csv
import os
from typing import List, Optional, Tuple

import pandas as pd
import logging
import openpyxl


from ..Common.Exceptions import CsvReadError, ExcelReadError
from LOGS.Auxiliary.Exceptions import LOGSException
from LOGS.Entities import (
    Experiment,
    ExperimentRequestParameter,
    MethodRequestParameter,
)
from LOGS.LOGS import LOGS

logging.basicConfig(level=logging.INFO)


class ExperimentManager:
    """This class enables the creation of experiments in a LOGS instance using a CSV file,
    or the export of experiments from a LOGS instance into a CSV file."""

    def __init__(
        self,
        logs: LOGS,
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        export_format: Optional[str] = ".csv",
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API
        :param source_path: Source path for exporting experiments in logs instance, defaults to None
        :param target_path: target path for extracting experiments of a logs instance in csv file, defaults to None
        """
        self.__logs = logs
        self.__source_path = source_path
        self.__target_path = target_path
        if self.__target_path is not None:
            if self.__target_path.suffix == "":
                self.__target_path = os.path.join(
                    self.__target_path, f"experiment_export{export_format}"
                )

        self.__export_format = export_format
        self.__source_format = self.__source_path.suffix if self.__source_path else None

    def create_experiments(self):
        """Creates an experiment by the given csv-file."""

        if self.__source_format == ".csv":
            try:
                experiment_data = pd.read_csv(
                    self.__source_path,
                    delimiter=";",
                    dtype={"Experiment Name": str, "Method": str},
                    quotechar='"',
                )
            except Exception as e:
                message = f"Error reading CSV file with the experiments: {e}"
                logging.exception(message)
                raise CsvReadError(message) from e

        elif self.__source_format == ".xlsx":
            try:
                experiment_data = pd.read_excel(
                    self.__source_path,
                    dtype={"Experiment Name": str, "Method": str},
                    engine="openpyxl",
                )
            except Exception as e:
                message = f"Error reading Excel file with the experiments: {e}"
                logging.exception(message)
                raise ExcelReadError(message) from e
        else:
            raise ValueError(
                f"Unsupported source format: {self.__source_format}. Supported formats are: .csv, .xlsx"
            )

        def get_method(method_name: str):
            """Retrieves the LOGS method object that matches the given method name, if it exists."""
            methods = self.__logs.methods(MethodRequestParameter(names=[method_name]))

            return methods.first()  # Return the first matching method

        for line_num, (index, experiment) in enumerate(
            experiment_data.iterrows(), start=1
        ):
            # Create experiment and set attributes
            log_experiment = Experiment()
            if pd.notna(experiment["Experiment Name"]):
                log_experiment.name = experiment["Experiment Name"].strip()
            if pd.notna(experiment["Method"]):
                method_name = experiment["Method"].strip()
                logs_method = get_method(method_name)
                if logs_method is not None:
                    log_experiment.method = logs_method
                else:
                    logging.warning(
                        "The method '%s' does not exist in the LOGS instance. The experiment will be skipped.",
                        method_name,
                    )
                    continue  # Skip this experiment if method is not found
            else:
                logging.warning(
                    "No method specified for the experiment in line %s. The experiment will be skipped.",
                    line_num,
                )
                continue
            try:
                self.__logs.create(log_experiment)
            except LOGSException as e:
                logging.error(
                    "The experiment in line %s could not be created. %s", line_num, e
                )

    def export_experiments_csv(self):
        """Export experiment from LOGS."""

        heading = [
            "Experiment Name",
            "Method",
        ]
        print(f"Exporting experiments to {self.__target_path}")

        with open(self.__target_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(heading)
            for experiment in self.__logs.experiments(ExperimentRequestParameter()):
                method_name = experiment.method.name
                experiment_data = [
                    experiment.name,
                    method_name,
                ]

                writer.writerow(experiment_data)

    def export_experiments_excel(self):
        """Export experiments from LOGS to an Excel file."""

        heading = [
            "Experiment Name",
            "Method",
        ]

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.append(heading)

        for experiment in self.__logs.experiments(ExperimentRequestParameter()):
            method_name = experiment.method.name
            experiment_data = [
                experiment.name,
                method_name,
            ]
            worksheet.append(experiment_data)

        workbook.save(self.__target_path)

    def export_experiments(self):
        """Export experiments from LOGS to the specified format."""
        if self.__export_format == ".csv":
            self.export_experiments_csv()
        elif self.__export_format == ".xlsx":
            self.export_experiments_excel()
        else:
            raise ValueError(
                f"Unsupported export format: {self.__export_format}. Supported formats are: .csv, .xlsx"
            )
