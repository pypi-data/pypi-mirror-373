#!/usr/bin/env python3

import csv
import os
from typing import List, Optional, Tuple

import pandas as pd
import logging
import openpyxl

from ..Common.Exceptions import CsvReadError, ExcelReadError
from LOGS.Auxiliary.Exceptions import LOGSException
from LOGS.Entities import Person, PersonRequestParameter, Role, RoleRequestParameter
from LOGS.LOGS import LOGS

logging.basicConfig(level=logging.INFO)


class PersonManager:
    """This class enables the creation of persons in a LOGS instance using a CSV file,
    or the export of persons from a LOGS instance into a CSV file."""

    def __init__(
        self,
        logs: LOGS,
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        export_format: Optional[str] = ".csv",
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API
        :param source_path: Source path for exporting persons in logs instance, defaults to None
        :param target_path: target path for extracting persons of a logs instance in csv file, defaults to None
        """
        self.__logs = logs
        self.__source_path = source_path
        self.__target_path = target_path
        if self.__target_path is not None:
            if self.__target_path.suffix == "":
                self.__target_path = os.path.join(
                    self.__target_path, f"persons_export{export_format}"
                )

        self.__export_format = export_format
        self.__source_format = self.__source_path.suffix if self.__source_path else None

    def check_role(self, role: str, role_list: List) -> Role:
        """
        Retrieves the LOGS role object that matches the given role name, if it exists.

        :param role: The name of the role to match.
        :param role_list: List of all roles in the LOGS instance.

        :return: The LOGS Role object corresponding to the specified role name.
        """

        for r in role_list:
            if r.name == role:
                return r
            else:
                logging.warning(
                    "The role '%s' does not exist in the LOGS instance. It will be skipped.",
                    role,
                )
                return -1

    def create_persons(self):
        """Creates a person by the given csv-file."""

        if self.__source_format == ".csv":
            try:
                personal_data = pd.read_csv(
                    self.__source_path,
                    delimiter=";",
                    dtype={"Office Phone": str, "Notes": str, "Password": str},
                    quotechar='"',
                )
            except Exception as e:
                message = f"Error reading CSV file with the persons: {e}"
                logging.exception(message)
                raise CsvReadError(message) from e

        elif self.__source_format == ".xlsx":
            try:
                personal_data = pd.read_excel(
                    self.__source_path,
                    dtype={"Office Phone": str, "Notes": str, "Password": str},
                    engine="openpyxl",
                )
            except Exception as e:
                message = f"Error reading Excel file with the persons: {e}"
                logging.exception(message)
                raise ExcelReadError(message) from e
        else:
            raise ValueError(
                f"Unsupported source format: {self.__source_format}. Supported formats are: .csv, .xlsx"
            )

        # Get all roles of the LOGS instance
        role_list = []
        for role in self.__logs.roles(RoleRequestParameter()):
            role_list.append(role)

        for line_num, (index, person) in enumerate(personal_data.iterrows(), start=1):
            # Create person and set attributes excluding roles
            log_person = Person()
            if pd.notna(person["Last Name"]):
                log_person.lastName = person["Last Name"].strip()
            if pd.notna(person["First Name"]):
                log_person.firstName = person["First Name"].strip()
            if pd.notna(person["Login"]):
                log_person.login = person["Login"].strip()
            if pd.notna(person["E-Mail"]):
                log_person.email = person["E-Mail"].strip()
            if pd.notna(person["Office Phone"]):
                log_person.officePhone = person["Office Phone"].strip()
            if pd.notna(person["Password"]):
                log_person.password = person["Password"].strip()
            if pd.notna(person["Notes"]):
                log_person.notes = person["Notes"].strip()

            # Set roles of the person
            log_per_roles = []  # List of all roles of one person
            if not pd.isna(person["Roles"]):
                roles = str(person["Roles"]).split(",")
                for role in roles:
                    role = role.strip()
                    log_role = self.check_role(role, role_list)
                    if log_role == -1:
                        continue
                    log_per_roles.append(log_role)
            if log_person.login:
                log_person.roles = log_per_roles

            try:
                self.__logs.create(log_person)
            except LOGSException as e:
                logging.error(
                    "The person in line %s could not be created. %s", line_num, e
                )

    def export_persons_csv(self):
        """Export Persons from LOGS."""

        heading = [
            "Last Name",
            "First Name",
            "Login",
            "E-Mail",
            "Office Phone",
            "Roles",
            "Notes",
        ]

        with open(self.__target_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(heading)

            for person in self.__logs.persons(PersonRequestParameter()):
                roles_str = ""
                if person.roles is not None:
                    roles_str = ",".join([role.name for role in person.roles])

                person_data = [
                    person.lastName,
                    person.firstName,
                    person.login,
                    person.email,
                    person.officePhone,
                    roles_str,
                    person.notes,
                ]

                writer.writerow(person_data)

    def export_persons_excel(self):
        """Export Persons from LOGS to an Excel file."""

        heading = [
            "Last Name",
            "First Name",
            "Login",
            "E-Mail",
            "Office Phone",
            "Roles",
            "Notes",
        ]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(heading)

        for person in self.__logs.persons(PersonRequestParameter()):
            if person.roles is not None:
                roles_str = ",".join([role.name for role in person.roles])
            else:
                roles_str = ""

            person_data = [
                person.lastName,
                person.firstName,
                person.login,
                person.email,
                person.officePhone,
                roles_str,
                person.notes,
            ]

            ws.append(person_data)

        wb.save(self.__target_path)

    def export_persons(self):
        """Export persons based on the specified export format."""
        if self.__export_format == ".csv":
            self.export_persons_csv()
        elif self.__export_format == ".xlsx":
            self.export_persons_excel()
        else:
            raise ValueError(
                f"Unsupported export format: {self.__export_format}. Supported formats are: .csv, .xlsx"
            )
