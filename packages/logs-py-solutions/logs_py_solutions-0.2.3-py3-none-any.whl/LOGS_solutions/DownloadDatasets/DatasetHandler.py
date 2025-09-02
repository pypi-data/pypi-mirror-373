#!/usr/bin/env python3

import json
import tempfile
import zipfile
from pathlib import Path

from ..DownloadDatasets.FileHandler import FileHandler
from LOGS.Entities import Dataset


class DatasetHandler:
    """The class handles the parsing and downloading of unpacked data records in separate folders."""

    def __init__(
        self,
        dataset_target_path: Path,
        dataset: Dataset,
        include_metadata: bool = False,
        duplicate_handling: int = 1,
        symlink_path: Path = None,
        original_target_path: Path = None,
    ):
        """Initialization

        :param dataset_target_path: The path where the dataset should be stored
        :param dataset: The dataset which is to be downloaded
        :param include_metadata: True if metadata of datasets, projects and samples should be saved.
        :param duplicate_handling: How datasets with the same name should be handled. 1: rename, 2: overwrite, 3: take first.
        :param symlink_path: Path where the datasets should be sorted by the format with symlinks to the original datasets. If None, no symlinks will be created. (needed for the symlink)
        :param original_target_path: The original path where the dataset is stored (needed for the symlink)
        """

        self.__dataset_target_path = dataset_target_path
        self.__dataset = dataset
        self.__include_metadata = include_metadata
        self.__duplicate_handling = duplicate_handling
        self.__symlink_path = symlink_path  # needed for the symlink
        self.__original_target_path = original_target_path  # needed for the symlink

    def download_dataset_unzip(
        self,
        filename: str = "",
    ):
        """Download the unzipped dataset.

        :param filename: Name of the store dataset. If empty, the name of the dataset will be used.
        """

        temporary_directory = tempfile.TemporaryDirectory()
        temp_dir = Path(temporary_directory.name)

        if not temp_dir.exists():
            raise Exception("Temp path %a does not exist" % temp_dir)

        if not temp_dir.is_dir():
            raise Exception("Temp path %a is not a directory" % temp_dir)

        def count_folders_in_zip(zip_file_path):
            """Count the number of folders in a zip file.

            :param zip_file_path: The path to the zip file.
            """
            folder_count = 0

            with zipfile.ZipFile(zip_file_path, "r") as zip_file:
                for file_info in zip_file.infolist():
                    if file_info.is_dir():
                        folder_count += 1

            return folder_count

        if filename == "":
            filename = FileHandler.clean_filename(self.__dataset.name)
            zip_file = self.__dataset.download(
                temp_dir,
            )

            if count_folders_in_zip(zip_file) == 0:
                target_path = self.__dataset_target_path / FileHandler.clean_foldername(
                    filename
                )

                # handling duplicates
                if target_path.exists():
                    if self.__duplicate_handling == 1:
                        self.__dataset_target_path = (
                            self.__dataset_target_path
                            / f"{FileHandler.clean_foldername(filename)}_id{self.__dataset.id}"
                        )
                    elif self.__duplicate_handling == 2:
                        self.__dataset_target_path = target_path
                    else:
                        return
                else:
                    self.__dataset_target_path = target_path

            # handling duplicates
            if Path(
                self.__dataset_target_path / Path(zip_file).name.split(".")[0]
            ).exists():
                if self.__duplicate_handling == 1:
                    self.__dataset_target_path = (
                        self.__dataset_target_path
                        / f"{FileHandler.clean_foldername(filename)}_id{self.__dataset.id}"
                    )
                elif self.__duplicate_handling == 2:
                    pass
                else:
                    return

            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(self.__dataset_target_path)

        else:
            zip_file = self.__dataset.download(
                self.__dataset_target_path, fileName=filename
            )
            if count_folders_in_zip(zip_file) == 0:
                target_path = self.__dataset_target_path / FileHandler.clean_foldername(
                    filename
                )

                # handling duplicates
                if target_path.exists():
                    if self.__duplicate_handling == 1:
                        self.__dataset_target_path = (
                            self.__dataset_target_path
                            / f"{FileHandler.clean_foldername(filename)}_id{self.__dataset.id}"
                        )
                    elif self.__duplicate_handling == 2:
                        self.__dataset_target_path = target_path
                    else:
                        return
                else:
                    self.__dataset_target_path = target_path

            # handling duplicates
            if Path(
                self.__dataset_target_path / Path(zip_file).name.split(".")[0]
            ).exists():
                if self.__duplicate_handling == 1:
                    self.__dataset_target_path = (
                        self.__dataset_target_path
                        / f"{FileHandler.clean_foldername(filename)}_id{self.__dataset.id}"
                    )
                elif self.__duplicate_handling == 2:
                    pass
                else:
                    return

            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(self.__dataset_target_path)

    def download_dataset(
        self,
        filename: str = "",
    ):
        """Downloads the dataset and stores it in the given path.

        :param filename: Name of the store dataset. If empty, the name of the dataset will be used.
        """

        if filename == "":
            self.download_dataset_unzip()
        else:
            self.download_dataset_unzip(filename=filename)

    def parse_dataset(self):
        """Download all files of the dataset and store it in the given path together with a txt file with all important information."""

        if self.__dataset.name is not None:
            self.download_dataset()
        if self.__include_metadata:
            dataset_information = self.__dataset.toJson()
            dataset_inf_target_path = (
                self.__dataset_target_path / "dataset_information.json"
            )

            with open(dataset_inf_target_path, "w") as file:
                json.dump(dataset_information, file, ensure_ascii=False, indent=4)

        if self.__symlink_path is not None:
            self.create_symlink()

    def create_symlink(self):
        """Create a symlink to the dataset in the format folder."""

        if self.__dataset.format is None:
            symlink_base_path = self.__symlink_path / str("no_format")
        else:
            symlink_base_path = self.__symlink_path / str(self.__dataset.format.id)
        symlink_path = symlink_base_path / self.__dataset_target_path.relative_to(
            self.__original_target_path
        )

        # Create the symlink if it does not exist
        if not symlink_path.is_symlink():
            destination_dir = symlink_path.parent
            destination_dir.mkdir(parents=True, exist_ok=True)
            symlink_path.symlink_to(self.__dataset_target_path)
