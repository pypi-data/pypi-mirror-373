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
    Method,
    MethodRequestParameter,
)
from LOGS.LOGS import LOGS

logging.basicConfig(level=logging.INFO)


class MethodManager:
    """This class enables the creation of methods in a LOGS instance using a CSV file,
    or the export of methods from a LOGS instance into a CSV file."""

    def __init__(
        self,
        logs: LOGS,
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        export_format: Optional[str] = ".csv",
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API
        :param source_path: Source path for exporting methods in logs instance, defaults to None
        :param target_path: target path for extracting methods of a logs instance in csv file, defaults to None
        """
        self.__logs = logs
        self.__source_path = source_path
        self.__target_path = target_path
        if self.__target_path is not None:
            if self.__target_path.suffix == "":
                self.__target_path = os.path.join(
                    self.__target_path, f"method_export{export_format}"
                )

        self.__export_format = export_format
        self.__source_format = self.__source_path.suffix if self.__source_path else None

    def create_methods(self):
        """Creates an method by the given csv-file."""

        if self.__source_format == ".csv":
            try:
                method_data = pd.read_csv(
                    self.__source_path,
                    delimiter=";",
                    dtype={"Name": str, "Full Name": str},
                    quotechar='"',
                )
            except Exception as e:
                message = f"Error reading CSV file with the methods: {e}"
                logging.exception(message)
                raise CsvReadError(message) from e

        elif self.__source_format == ".xlsx":
            try:
                method_data = pd.read_excel(
                    self.__source_path,
                    dtype={"Name": str, "Full Name": str},
                    engine="openpyxl",
                )
            except Exception as e:
                message = f"Error reading Excel file with the methods: {e}"
                logging.exception(message)
                raise ExcelReadError(message) from e
        else:
            raise ValueError(
                f"Unsupported source format: {self.__source_format}. Supported formats are: .csv, .xlsx"
            )

        for line_num, (index, method) in enumerate(method_data.iterrows(), start=1):
            # Create method and set attributes
            log_method = Method()
            if pd.notna(method["Name"]):
                log_method.name = method["Name"].strip()
            if pd.notna(method["Full Name"]):
                log_method.fullName = method["Full Name"].strip()
            try:
                self.__logs.create(log_method)
            except LOGSException as e:
                logging.error(
                    "exceptionThe method in line %s could not be created. %s",
                    line_num,
                    e,
                )

    def export_methods_csv(self):
        """Export method from LOGS."""

        heading = [
            "Name",
            "Full Name",
        ]
        print(f"Exporting names to {self.__target_path}")

        with open(self.__target_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(heading)
            for method in self.__logs.methods(MethodRequestParameter()):
                method_data = [
                    method.name,
                    method.fullName if method.fullName else "",
                ]

                writer.writerow(method_data)

    def export_methods_excel(self):
        """Export methods from LOGS to an Excel file."""

        heading = [
            "Name",
            "Full Name",
        ]

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.append(heading)

        for method in self.__logs.methods(MethodRequestParameter()):
            method_data = [
                method.name,
                method.fullName if method.fullName else "",
            ]
            worksheet.append(method_data)

        workbook.save(self.__target_path)

    def export_methods(self):
        """Export methods from LOGS to the specified format."""
        if self.__export_format == ".csv":
            self.export_methods_csv()
        elif self.__export_format == ".xlsx":
            self.export_methods_excel()
        else:
            raise ValueError(
                f"Unsupported export format: {self.__export_format}. Supported formats are: .csv, .xlsx"
            )
