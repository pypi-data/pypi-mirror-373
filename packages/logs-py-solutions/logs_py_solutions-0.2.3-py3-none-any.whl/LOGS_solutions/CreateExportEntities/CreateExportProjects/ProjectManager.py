import csv
import os
from typing import Optional

import logging
import pandas as pd
import openpyxl

from ..Common.Exceptions import CsvReadError, ExcelReadError
from LOGS.Auxiliary.Exceptions import LOGSException
from LOGS.Entities import (
    Project,
    ProjectRequestParameter,
    ProjectPersonPermission,
    PersonRequestParameter,
)
from LOGS.LOGS import LOGS

logging.basicConfig(level=logging.INFO)


class ProjectManager:
    """This class enables the creation of projects in a LOGS instance using a CSV file,
    or the export of projects from a LOGS instance into a CSV file."""

    def __init__(
        self,
        logs: LOGS,
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        export_format: Optional[str] = ".csv",
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API
        :param source_path: Source path for exporting projects in logs instance, defaults to None
        :param target_path: target path for extracting projects of a logs instance in csv file, defaults to None
        """
        self.__logs = logs
        self.__source_path = source_path
        self.__target_path = target_path
        if self.__target_path is not None:
            if self.__target_path.suffix == "":
                self.__target_path = os.path.join(
                    self.__target_path, f"projects_export{export_format}"
                )

        self.__export_format = export_format
        self.__source_format = self.__source_path.suffix if self.__source_path else None

    def create_projects(self):
        """Creates a new project in the LOGS instance."""

        def split_and_strip(val):
            if isinstance(val, list):
                return [str(v).strip() for v in val]
            if pd.isna(val) or val == "":
                return []
            return [v.strip() for v in str(val).split(",")]

        if self.__source_format == ".csv":
            try:
                projects_data = pd.read_csv(
                    self.__source_path,
                    delimiter=";",
                    dtype={"Project Name": str},
                    quotechar='"',
                )
            except Exception as e:
                message = f"Error reading CSV file with the persons: {e}"
                logging.exception(message)
                raise CsvReadError(message) from e

        elif self.__source_format == ".xlsx":
            try:
                projects_data = pd.read_excel(
                    self.__source_path, engine="openpyxl", dtype={"Project Name": str}
                )

            except Exception as e:
                message = f"Error reading Excel file with the projects: {e}"
                logging.exception(message)
                raise ExcelReadError(message) from e
        else:
            raise ValueError(
                f"Unsupported source format: {self.__source_format}. Supported formats are: .csv, .xlsx"
            )

        for col in [
            "Person ID",
            "Admin Permission",
            "Edit Permission",
            "Add Permission",
            "Read Permission",
        ]:
            if col in projects_data.columns:
                projects_data[col] = projects_data[col].apply(split_and_strip)

        for index, project in projects_data.iterrows():
            name_found = False
            for proj in self.__logs.projects(ProjectRequestParameter()):
                if project["Project Name"] == proj.name:
                    logging.info(
                        "Project '%s' already exists. Project will be upgraded.",
                        project["Project Name"],
                    )
                    existing_project = self.__logs.project(proj.id)
                    name_found = True

            if not name_found:
                log_project = Project()
                log_project.name = project["Project Name"]

            person_ids = project["Person ID"]
            admins = project["Admin Permission"]
            edits = project["Edit Permission"]
            adds = project["Add Permission"]
            reads = project["Read Permission"]

            persons_count = len(person_ids)
            if any(persons_count != len(lst) for lst in (admins, edits, adds, reads)):
                logging.error(
                    "There are too few or too many arguments in permission columns for project '%s'. It will be skipped.",
                    project["Project Name"],
                )
                continue

            if not name_found:
                log_project.projectPersonPermissions = []

            for pid, admin, edit, add, read in zip(
                person_ids, admins, edits, adds, reads
            ):
                if self.__logs.persons(PersonRequestParameter(ids=[pid])).count == 0:
                    logging.warning(
                        "Person with id %s does not exist and will be skipped.", pid
                    )
                    continue
                if not isinstance(pid, int):
                    try:
                        pid = int(pid.strip())
                    except ValueError:
                        logging.error(
                            "Invalid person ID '%s' for project '%s'. Skipping.",
                            pid,
                            project["Project Name"],
                        )
                        continue

                def to_bool_if_valid(s):
                    if isinstance(s, str):
                        lower = s.lower()
                        return lower == "true"

                admin = to_bool_if_valid(admin)
                edit = to_bool_if_valid(edit)
                add = to_bool_if_valid(add)
                read = to_bool_if_valid(read)
                if not read:
                    logging.error(
                        "Read permission for person ID '%s' in project '%s' is required. Person will be skipped.",
                        pid,
                        project["Project Name"],
                    )
                    continue

                if None in [admin, edit, add, read]:
                    logging.error(
                        "Invalid permission values for person ID '%s' in project '%s'. Skipping.",
                        pid,
                        project["Project Name"],
                    )
                    continue

                if admin and any(not x for x in (edit, add, read)):
                    logging.error(
                        "Admin permission for person ID '%s' in project '%s' requires all other permissions to be true. Person will be skipped.",
                        pid,
                        project["Project Name"],
                    )
                    continue

                if not name_found:
                    project_permission = ProjectPersonPermission()
                    project_permission.person = pid
                    project_permission.administer = admin
                    project_permission.edit = edit
                    project_permission.add = add
                    # project_permission.read = read
                    log_project.projectPersonPermissions.append(project_permission)
                else:
                    existing_perm = next(
                        (
                            perm
                            for perm in existing_project.projectPersonPermissions
                            if perm.person.id == pid
                        ),
                        None,
                    )

                    if existing_perm:
                        existing_perm.administer = admin
                        existing_perm.edit = edit
                        existing_perm.add = add
                    else:
                        project_permission = ProjectPersonPermission()
                        project_permission.person = pid
                        project_permission.administer = admin
                        project_permission.edit = edit
                        project_permission.add = add
                        # project_permission.read = read
                        existing_project.projectPersonPermissions.append(
                            project_permission
                        )
            try:
                if not name_found:
                    logging.info("Creating project '%s'.", log_project.name)
                    self.__logs.create(log_project)
                    logging.info("Project '%s' created successfully.", log_project.name)
                if name_found:
                    logging.info("Updating project '%s'.", existing_project.name)
                    self.__logs.update(existing_project)
                    logging.info(
                        "Project '%s' updated successfully.", existing_project.name
                    )
            except LOGSException as e:
                logging.error(
                    "Failed to create project '%s'. %s", project["Project Name"], e
                )

    def export_projects_csv(self) -> None:
        """Exports projects from the LOGS instance to a CSV file."""

        heading = [
            "Project Name",
            "Person ID",
            "Admin Permission",
            "Edit Permission",
            "Add Permission",
            "Read Permission",
        ]

        with open(self.__target_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(
                file, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL
            )
            writer.writerow(heading)

            for project in self.__logs.projects(ProjectRequestParameter()):
                project_name = project.name
                persons = []
                admin = []
                edit = []
                add = []
                read = []
                for permission in project.projectPersonPermissions:
                    persons.append(permission.person.id)
                    admin.append(permission.administer)
                    edit.append(permission.edit)
                    add.append(permission.add)
                    read.append(permission.read)
                writer.writerow(
                    [
                        project_name,
                        ",".join(map(str, persons)),
                        ",".join(map(str, admin)),
                        ",".join(map(str, edit)),
                        ",".join(map(str, add)),
                        ",".join(map(str, read)),
                    ]
                )

    def export_projects_excel(self) -> None:
        """Exports projects from the LOGS instance to an Excel file."""

        heading = [
            "Project Name",
            "Person ID",
            "Admin Permission",
            "Edit Permission",
            "Add Permission",
            "Read Permission",
        ]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(heading)

        for project in self.__logs.projects(ProjectRequestParameter()):
            project_name = project.name
            persons = []
            admin = []
            edit = []
            add = []
            read = []
            for permission in project.projectPersonPermissions:
                persons.append(permission.person.id)
                admin.append(permission.administer)
                edit.append(permission.edit)
                add.append(permission.add)
                read.append(permission.read)
            ws.append(
                [
                    project_name,
                    ",".join(map(str, persons)),
                    ",".join(map(str, admin)),
                    ",".join(map(str, edit)),
                    ",".join(map(str, add)),
                    ",".join(map(str, read)),
                ]
            )

        wb.save(self.__target_path)

    def export_projects(self) -> None:
        """Exports projects from the LOGS instance to a CSV file or Excel file."""

        if self.__export_format == ".csv":
            self.export_projects_csv()
        elif self.__export_format == ".xlsx":
            self.export_projects_excel()
        else:
            raise ValueError(
                f"Unsupported export format: {self.__export_format}. Supported formats are: .csv, .xlsx"
            )
