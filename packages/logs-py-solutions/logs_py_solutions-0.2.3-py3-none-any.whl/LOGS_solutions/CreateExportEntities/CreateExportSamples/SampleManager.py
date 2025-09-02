#!/usr/bin/env python3

import csv
import os
from datetime import datetime
from typing import List, Optional, Set, Tuple

import pandas as pd
import logging
import openpyxl

from ..Common.Exceptions import CsvReadError, ExcelReadError
from LOGS.Auxiliary.Exceptions import LOGSException
from LOGS.Entities import (
    Person,
    PersonRequestParameter,
    Project,
    ProjectRequestParameter,
    Sample,
    SampleRequestParameter,
)
from LOGS.LOGS import LOGS


logging.basicConfig(level=logging.INFO)


class SampleManager:
    """This class enables the creation of samples in a LOGS instance using a CSV file,
    or the export of samples from a LOGS instance into a CSV file."""

    def __init__(
        self,
        logs: LOGS,
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        export_format: Optional[str] = ".csv",
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API
        :param source_path: Source path for exporting samples in logs instance, defaults to None
        :param target_path: target path for extracting samples of a logs instance in csv file, defaults to None
        """
        self.__logs = logs
        self.__source_path = source_path
        self.__target_path = target_path
        if self.__target_path is not None:
            if self.__target_path.suffix == "":
                self.__target_path = os.path.join(
                    self.__target_path, f"samples_export{export_format}"
                )

        self.__export_format = export_format
        self.__source_format = self.__source_path.suffix if self.__source_path else None

    def check_projects(self, project_set: Set) -> List[Project]:
        """Checks for each project in the project set whether they exist in the LOGS instance.

        :param person_set: Set with all projects named in the csv file.

        :return: List of Project objects
        """

        projects = []
        logs_project_id = []
        for project in self.__logs.projects(ProjectRequestParameter()):
            projects.append(project)
            logs_project_id.append(project.id)

        for project in project_set:
            if project in logs_project_id:
                continue
            else:
                message = f"The project {project} does not exist in this LOGS instance. The Script is terminated."
                logging.error(message)
                raise ValueError(message)

        return projects

    def check_persons(self, person_set: Set) -> List[Person]:
        """Checks for each person in the person set whether they exist in the LOGS instance.

        :param person_set: Set with all persons named in the csv file.
        """

        persons = []
        logs_persons_login = []
        logs_persons_id = []
        for person in self.__logs.persons(PersonRequestParameter()):
            persons.append(person)
            if person.login is not None:
                logs_persons_login.append(person.login)
            logs_persons_id.append(str(person.id))

        for person in person_set:
            if person in logs_persons_login:
                continue
            if person in logs_persons_id:
                continue
            else:
                message = f"The person {person} does not exist in this LOGS instance. The Script is terminated."
                logging.error(message)
                raise ValueError(message)

        return persons

    def create_attribute_list(
        self, attribute_str: str, attr_obj_list: List, check_person: bool = False
    ) -> List:
        """Creates a list of attributes.

        :param attribute_str: List of attributes of one class type
        :param attribute_class: Class of the attributes
        :param check_person: Should be True, if the attr_obj_list is a list of persons

        :return: List of all attributes in attribute_str.
        """

        attr_str_list = str(attribute_str).split(",")
        attribute_list = []
        for attr_obj in attr_obj_list:
            if str(attr_obj.id) in attr_str_list:
                attribute_list.append(attr_obj)
                continue
            if check_person:
                if attr_obj.login in attr_str_list:
                    attribute_list.append(attr_obj)

        return attribute_list

    def create_samples(self):
        """Creates a sample by the given csv-file."""

        if self.__source_format == ".csv":
            try:
                sample_data = pd.read_csv(
                    self.__source_path,
                    delimiter=";",
                    dtype={"Projects": str, "Prepared By": str},
                    quotechar='"',
                )
            except Exception as e:
                message = f"Error reading CSV file with the samples: {e}"
                logging.exception(message)
                raise CsvReadError(message) from e

        elif self.__source_format in [".xlsx"]:
            try:
                sample_data = pd.read_excel(
                    self.__source_path,
                    dtype={"Projects": str, "Prepared By": str},
                    engine="openpyxl",
                )
            except Exception as e:
                message = f"Error reading Excel file with the samples: {e}"
                logging.exception(message)
                raise ExcelReadError(message) from e
        else:
            raise ValueError(
                f"Unsupported source format: {self.__source_format}. Supported formats are: .csv, .xlsx"
            )

        # Set with all persons of the csv file
        person_set = set()
        # Set with all projects of the csv file
        project_set = set()

        # fill person_set and project_set
        for index, sample in sample_data.iterrows():
            if not pd.isna(sample["Prepared By"]):
                for person in str(sample["Prepared By"]).split(","):
                    person_set.add(person.strip())
            if not pd.isna(sample["Projects"]):
                for project in str(sample["Projects"]).split(","):
                    if project.isdigit():
                        project_set.add(int(project.strip()))

        # Check if the persons and projects exists in the LOGS instance
        persons = self.check_persons(person_set)
        projects = self.check_projects(project_set)

        # Create each sample
        sample_count = 1
        for index, sample in sample_data.iterrows():
            sample_count += 1
            projects = (
                self.create_attribute_list(sample["Projects"].strip(), projects)
                if not pd.isna(sample["Projects"])
                else []
            )
            prepared_by = (
                self.create_attribute_list(sample["Prepared By"].strip(), persons, True)
                if not pd.isna(sample["Prepared By"])
                else []
            )

            log_sample = Sample()
            log_sample.name = str(sample["Name"]).strip()
            log_sample.projects = projects
            log_sample.preparedBy = prepared_by
            log_sample.preparedAt = datetime.fromisoformat(str(sample["Prepared At"]))

            try:
                self.__logs.create(log_sample)
                logging.info("The sample in line %s has been created.", sample_count)
            except LOGSException as e:
                logging.exception(
                    "The sample in line %s could not be created.", sample_count
                )

    def export_samples_csv(self):
        """Export Samples from logs."""

        heading = [
            "Name",
            "Prepared At",
            "Prepared By",
            "Projects",
        ]

        with open(self.__target_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(
                file, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL
            )
            writer.writerow(heading)

            for sample in self.__logs.samples(SampleRequestParameter()):
                projects_str = ""
                persons_prep_str = ""

                if sample.projects is not None:
                    projects_str = ",".join(
                        str(project.id) for project in sample.projects
                    )

                if sample.preparedBy is not None:
                    persons_prep_str = ",".join(
                        str(person.id) for person in sample.preparedBy
                    )

                sample_data = [
                    sample.name,
                    sample.preparedAt.isoformat(),
                    persons_prep_str,
                    projects_str,
                ]

                writer.writerow(sample_data)

    def export_samples_excel(self):
        """Export Samples from logs to an excel file."""

        heading = [
            "Name",
            "Prepared At",
            "Prepared By",
            "Projects",
        ]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(heading)

        for sample in self.__logs.samples(SampleRequestParameter()):
            projects_str = ""
            persons_prep_str = ""

            if sample.projects is not None:
                projects_str = ",".join(str(project.id) for project in sample.projects)

            if sample.preparedBy is not None:
                persons_prep_str = ",".join(
                    str(person.id) for person in sample.preparedBy
                )

            sample_data = [
                sample.name,
                sample.preparedAt.isoformat(),
                persons_prep_str,
                projects_str,
            ]

            ws.append(sample_data)

        wb.save(self.__target_path)

    def export_samples(self):
        """Exports samples from the LOGS instance to a CSV file or Excel file."""

        if self.__export_format == ".csv":
            self.export_samples_csv()
        elif self.__export_format == ".xlsx":
            self.export_samples_excel()
        else:
            raise ValueError(
                f"Invalid export format: {self.__export_format}. Supported formats are: .csv, .xlsx"
            )
