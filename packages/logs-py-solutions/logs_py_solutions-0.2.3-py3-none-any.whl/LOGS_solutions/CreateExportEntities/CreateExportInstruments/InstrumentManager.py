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
    Instrument,
    InstrumentRequestParameter,
    MethodRequestParameter,
)
from LOGS.LOGS import LOGS

logging.basicConfig(level=logging.INFO)


class InstrumentManager:
    """This class enables the creation of instruments in a LOGS instance using a CSV file,
    or the export of instruments from a LOGS instance into a CSV file."""

    def __init__(
        self,
        logs: LOGS,
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        export_format: Optional[str] = ".csv",
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API
        :param source_path: Source path for exporting instruments in logs instance, defaults to None
        :param target_path: target path for extracting instruments of a logs instance in csv file, defaults to None
        """
        self.__logs = logs
        self.__source_path = source_path
        self.__target_path = target_path
        if self.__target_path is not None:
            if self.__target_path.suffix == "":
                self.__target_path = os.path.join(
                    self.__target_path, f"instruments_export{export_format}"
                )

        self.__export_format = export_format
        self.__source_format = self.__source_path.suffix if self.__source_path else None

    def create_instruments(self):
        """Creates an instrument by the given csv-file."""

        if self.__source_format == ".csv":
            try:
                instrument_data = pd.read_csv(
                    self.__source_path,
                    delimiter=";",
                    dtype={"Instrument Name": str, "Method": str},
                    quotechar='"',
                )
            except Exception as e:
                message = f"Error reading CSV file with the instruments: {e}"
                logging.exception(message)
                raise CsvReadError(message) from e

        elif self.__source_format == ".xlsx":
            try:
                instrument_data = pd.read_excel(
                    self.__source_path,
                    dtype={"Instrument Name": str, "Method": str},
                    engine="openpyxl",
                )
            except Exception as e:
                message = f"Error reading Excel file with the instruments: {e}"
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

        for line_num, (index, instrument) in enumerate(
            instrument_data.iterrows(), start=1
        ):
            # Create instrument and set attributes
            log_instrument = Instrument()
            if pd.notna(instrument["Instrument Name"]):
                log_instrument.name = instrument["Instrument Name"].strip()
            if pd.notna(instrument["Method"]):
                method_name = instrument["Method"].strip()
                logs_method = get_method(method_name)
                if logs_method is not None:
                    log_instrument.method = logs_method
                else:
                    logging.warning(
                        "The method '%s' does not exist in the LOGS instance. The instrument will be skipped.",
                        method_name,
                    )
                    continue  # Skip this instrument if method is not found
            else:
                logging.warning(
                    "No method specified for the instrument in line %s. The instrument will be skipped.",
                    line_num,
                )
                continue
            try:
                self.__logs.create(log_instrument)
            except LOGSException as e:
                logging.error(
                    "The instrument in line %s could not be created. %s", line_num, e
                )

    def export_instruments_csv(self):
        """Export instruments from LOGS."""

        heading = [
            "Instrument Name",
            "Method",
        ]
        print(f"Exporting instruments to {self.__target_path}")

        with open(self.__target_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(heading)
            for instrument in self.__logs.instruments(InstrumentRequestParameter()):
                method_name = instrument.method.name
                instrument_data = [
                    instrument.name,
                    method_name,
                ]

                writer.writerow(instrument_data)

    def export_instruments_excel(self):
        """Export instruments from LOGS to an Excel file."""

        heading = [
            "Instrument Name",
            "Method",
        ]

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.append(heading)

        for instrument in self.__logs.instruments(InstrumentRequestParameter()):
            method_name = instrument.method.name
            instrument_data = [
                instrument.name,
                method_name,
            ]
            worksheet.append(instrument_data)

        workbook.save(self.__target_path)

    def export_instruments(self):
        """Export instruments from LOGS to the specified format."""
        if self.__export_format == ".csv":
            self.export_instruments_csv()
        elif self.__export_format == ".xlsx":
            self.export_instruments_excel()
        else:
            raise ValueError(
                f"Unsupported export format: {self.__export_format}. Supported formats are: .csv, .xlsx"
            )
