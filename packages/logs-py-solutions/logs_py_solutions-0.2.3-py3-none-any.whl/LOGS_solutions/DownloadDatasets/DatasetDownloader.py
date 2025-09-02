#!/usr/bin/env python3

import json
import os
from typing import Optional
from pathlib import Path
from datetime import datetime, timedelta
import tempfile

from ..DownloadDatasets.DatasetHandler import DatasetHandler
from ..DownloadDatasets.ProgressBar import ProgressBar

from LOGS.Entities import (
    Dataset,
    DatasetRequestParameter,
    DatasetOrder,
    Project,
    ProjectRequestParameter,
)
from LOGS.LOGS import LOGS


class DatasetDownloader:
    """Downloads all datasets"""

    def __init__(
        self,
        logs: LOGS,
        args,
    ):
        """Initialization

        :param logs: LOGS object to access the LOGS web API
        :param target_path: Path where all datasets should be saved.
        :param project_id: List of project ids which should be downloaded
        :param include_metadata: True if metadata of datasets, projects and samples should be saved.
        :param duplicate_handling: How datasets with the same name should be handled. 1: rename, 2: overwrite, 3: take first.
        :param symlink_path: Path where the datasets should be sorted by the format with symlinks to the original datasets. If None, no symlinks will be created.
        :param include_sample_projects: False if projects should be taken from datasets only. If True, all projects with datasets will be downloaded.
        """

        self._logs = logs
        self._target_path = args.target_path
        self._project_ids = args.project_ids
        self._include_metadata = args.include_metadata
        self._duplicate_handling = args.duplicate_handling
        self._symlink_path = args.symlink_path
        self._include_sample_projects = args.include_sample_projects
        self._start_from = self.valid_start_from()

        if self._symlink_path is not None:
            if self.can_create_symlink() is False:
                print(
                    "Error: Symbolic links are not supported on this system. They will not be created."
                )
                self._symlink_path = None

    def can_create_symlink(self) -> bool:
        """Check if the system supports creating symbolic links.
        :return: True if the system supports creating symbolic links, False otherwise.
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            target = tmp_path / "dummy.txt"
            link = tmp_path / "link.txt"

            try:
                # Dummy-Zieldatei anlegen
                target.write_text("symlink test")

                # Versuche symbolischen Link zu erstellen
                link.symlink_to(target)

                # Prüfen, ob der Link korrekt erstellt wurde
                return link.is_symlink() and link.read_text() == "symlink test"

            except (OSError, NotImplementedError):
                return False

    def valid_start_from(self) -> Optional[datetime]:
        """Check if last_state.json exists and return the dateAdded if it exists, else return None.

        :return: datetime object of the last dateAdded or None
        """
        if os.path.exists("last_state.json"):
            with open("last_state.json", "r") as stat:
                data = json.load(stat)

            if isinstance(data, dict):
                if "acquisitionDate" in data:
                    self.startFrom = datetime.fromisoformat(
                        data["acquisitionDate"]
                    ) - timedelta(seconds=1)
                    return self.startFrom
        else:
            return None

    def download_datasets(
        self, project_path: str, sample_path: str, project: Project, dataset: Dataset
    ):
        """Parse and download datasets. Create symlinks if symlink_path is not None. Create metadata files if include_metadata is True.

        :param project_path: Path where the project should be saved.
        :param sample_path: Path where the sample should be saved.
        :param project: Project object
        :param dataset: Dataset object
        """

        sample_path.mkdir(parents=True, exist_ok=True)
        dataset_handler = DatasetHandler(
            dataset_target_path=sample_path,
            dataset=dataset,
            include_metadata=self._include_metadata,
            duplicate_handling=self._duplicate_handling,
            symlink_path=self._symlink_path,
            original_target_path=self._target_path,
        )
        dataset_handler.parse_dataset()

        # create symlink if symlink_path is not None
        if self._symlink_path is not None:
            dataset_handler.create_symlink()

        ProgressBar.update_processed_files()

        if self._include_metadata:
            project_information = self._logs.project(project.id).toJson()
            project_info_path = project_path / "project_information.json"

            if not project_info_path.exists():
                with open(project_info_path, "w") as file:
                    json.dump(
                        project_information,
                        file,
                        ensure_ascii=False,
                        indent=4,
                    )

            if dataset.sample is not None:
                sample_information = self._logs.sample(dataset.sampleId).toJson()
                sample_info_path = sample_path / "sample_information.json"

                if not sample_info_path.exists():
                    with open(sample_info_path, "w") as file:
                        json.dump(
                            sample_information,
                            file,
                            ensure_ascii=False,
                            indent=4,
                        )

    def download_datasets_structured(self):
        """Downloads all datasets structured in the given path."""

        ProgressBar.start_progressbar("Downloading datasets")

        # Parse claimed datasets
        for dataset in self._logs.datasets(
            DatasetRequestParameter(
                isClaimed=True,
                orderby=DatasetOrder("ACQUISITION_DATE_ASC"),
                acquisitionDateFrom=self._start_from,
            )
        ):
            dataset_projects_ids = [project.id for project in dataset.projects]
            with open(Path("./last_state.json"), "w") as stat:
                json.dump(
                    {"acquisitionDate": dataset.acquisitionDate.isoformat()}, stat
                )  # Save last date state in case of interruption

            target_path = self._target_path / "Claimed"
            for project in dataset.projects:
                # If project ids are given, only download datasets from this projects, else download all projects
                if len(self._project_ids) > 0:
                    if project.id in self._project_ids:
                        project_path = target_path / project.name
                        sample_path = project_path / dataset.sample.name
                        self.download_datasets(
                            project_path,
                            sample_path,
                            project,
                            dataset,
                        )

                else:
                    project_path = target_path / project.name
                    sample_path = project_path / dataset.sample.name
                    self.download_datasets(
                        project_path,
                        sample_path,
                        project,
                        dataset,
                    )

            # If include_sample_projects is True, download also projects of samples
            if self._include_sample_projects:
                for project in self._logs.projects(
                    ProjectRequestParameter(sampleIds=[dataset.sampleId])
                ):
                    if project.id not in dataset_projects_ids:
                        # If project ids are given, only download datasets from this projects, else download all projects
                        if len(self._project_ids) > 0:
                            if project.id in self._project_ids:
                                project_path = target_path / project.name
                                sample_path = project_path / dataset.sample.name
                                self.download_datasets(
                                    project_path,
                                    sample_path,
                                    project,
                                    dataset,
                                )
                        else:
                            project_path = target_path / project.name
                            sample_path = project_path / dataset.sample.name
                            self.download_datasets(
                                project_path,
                                sample_path,
                                project,
                                dataset,
                            )

        # Parse unclaimed datasets
        for dataset in self._logs.datasets(
            DatasetRequestParameter(
                isClaimed=False,
                orderby=DatasetOrder("ACQUISITION_DATE_ASC"),
                acquisitionDateFrom=self._start_from,
            )
        ):
            dataset_projects_ids = (
                [project.id for project in dataset.projects]
                if dataset.projects is not None
                else []
            )

            with open(Path("./last_state.json"), "w") as stat:
                json.dump(
                    {"acquisitionDate": dataset.acquisitionDate.isoformat()}, stat
                )  # Save last date state in case of interruption

            target_path = self._target_path / "Unclaimed"

            if dataset.projects is not None:
                for project in dataset.projects:
                    # If project ids are given, only download datasets from this projects, else download all projects
                    if len(self._project_ids) > 0:
                        if project.id in self._project_ids:
                            project_path = target_path / project.name
                            if dataset.sample is not None:
                                sample_path = project_path / dataset.sample.name
                            else:
                                sample_path = project_path / "NoSample"

                            self.download_datasets(
                                project_path,
                                sample_path,
                                project,
                                dataset,
                            )

                    else:
                        project_path = target_path / project.name
                        if dataset.sample is not None:
                            sample_path = project_path / dataset.sample.name
                        else:
                            sample_path = project_path / "NoSample"

                        self.download_datasets(
                            project_path,
                            sample_path,
                            project,
                            dataset,
                        )

            if self._include_sample_projects:
                if dataset.sample is not None:
                    for project in self._logs.projects(
                        ProjectRequestParameter(sampleIds=[dataset.sampleId])
                    ):
                        if project.id not in dataset_projects_ids:
                            # If project ids are given, only download datasets from this projects, else download all projects
                            if len(self._project_ids) > 0:
                                if project.id in self._project_ids:
                                    project_path = target_path / project.name
                                    sample_path = project_path / dataset.sample.name

                                    self.download_datasets(
                                        project_path,
                                        sample_path,
                                        project,
                                        dataset,
                                    )
                            else:
                                project_path = target_path / project.name
                                sample_path = project_path / dataset.sample.name

                                self.download_datasets(
                                    project_path,
                                    sample_path,
                                    project,
                                    dataset,
                                )

            # If the dataset has no sample and no project
            if (
                dataset.sample is None
                and dataset.projects is None
                and (self._project_ids == [] or 0 in self._project_ids)
            ):
                project_path = target_path / "NoProject"
                sample_path = project_path / "NoSample"
                sample_path.mkdir(parents=True, exist_ok=True)
                dataset_handler = DatasetHandler(
                    dataset_target_path=sample_path,
                    dataset=dataset,
                    include_metadata=self._include_metadata,
                    duplicate_handling=self._duplicate_handling,
                    symlink_path=self._symlink_path,
                    original_target_path=self._target_path,
                )
                dataset_handler.parse_dataset()

                # create symlink if symlink_path is not None
                if self._symlink_path is not None:
                    dataset_handler.create_symlink()
                ProgressBar.update_processed_files()

        ProgressBar.stop_progressbar()
