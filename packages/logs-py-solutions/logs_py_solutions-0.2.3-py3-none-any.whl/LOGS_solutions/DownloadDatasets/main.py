#!/usr/bin/env python3

from ..DownloadDatasets.DatasetDownloader import DatasetDownloader
import argparse
from typing import List
from pathlib import Path
from LOGS import LOGS


def main(args):
    """Main function to download datasets from a LOGS instance.
    Important: This classes uses absolute paths. To obtain the correct absolute path, you must ensure
    that the relative path is correct in relation to the directory in which the script is executed.
    If you are not sure, use the absolute path for target_path"""

    dataset_downloader = DatasetDownloader(LOGS(), args)
    dataset_downloader.download_datasets_structured()


def valid_path(target_path) -> Path:
    """Validates the given paths.

    :param target_path: The target path to validate.

    :return: The absolute path for the target.
    """

    if target_path is not None:
        target_path = Path(target_path).resolve()
        return target_path
    else:
        raise argparse.ArgumentTypeError(
            "Please specify a path for the project data set."
        )


def valid_ids(project_ids: str) -> List[int]:
    """Validates the project ids

    :param id: ids
    :return: [] if project_ids is None or an empty list, otherwise a list of integers
    """

    if project_ids is None or project_ids == []:
        return []
    else:
        try:
            return [int(i) for i in project_ids.split(",")]
        except:
            raise argparse.ArgumentTypeError(
                f"project_ids has to be integers separated by a comma."
            )


def valid_bool(bool_string: str) -> bool:
    """Validates the given boolean string. The string can be 'true', 'yes', '1', 'false', 'no', or '0'.

    :param bool_string: The boolean string to validate.

    :return: The boolean value of the string.
    """
    if isinstance(bool_string, bool):
        return bool_string
    if bool_string.lower() in ("true", "yes", "1"):
        return True
    elif bool_string.lower() in ("false", "no", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError(
            f"Value '{bool_string}' is not a valid boolean. Use 'true', 'false', 'yes', 'no', '1', or '0'."
        )


def valid_duplicate_handling(
    dataset_handling: int,
) -> int:
    """Validates how datasets with the same name should be handled. Options: 1: rename, 2: overwrite, 3: take first.

    :param duplicate_handling: The duplicate handling to validate.

    :return: The duplicate handling as an integer.
    """

    if int(dataset_handling) not in [1, 2, 3]:
        raise argparse.ArgumentTypeError(
            "Please specify a valid duplicate handling. 1: rename, 2: overwrite, 3: take first."
        )
    try:
        return int(dataset_handling)
    except:
        return 1


def parse_args():
    """Parses the command line arguments.

    :return: The parsed arguments.
    """

    parser = argparse.ArgumentParser(description="Download datasets from the IconLIMS.")
    parser.add_argument(
        "--target_path",
        type=valid_path,
        help="The target path for the downloaded datasets. Default: ./saved_datasets",
        default=Path("./saved_datasets").resolve(),
    )

    parser.add_argument(
        "--project_ids",
        type=valid_ids,
        help="The project ids of the datasets to be downloaded. Has to be integer separated by a comma without spaces. For datasets without projects, use 0 as id. If not set all projects will be downloaded. Default: ''",
        default=[],
    )
    parser.add_argument(
        "--include_metadata",
        type=valid_bool,
        help="Should be set to True if metadata of datasets, projects and samples should be saved. Default: False",
        default=False,
    )

    parser.add_argument(
        "--duplicate_handling",
        type=valid_duplicate_handling,
        help="How an dataset with an existing name should be handled. 1: rename (the ID is appended), 2: overwrite, 3: take first. Default: 1",
        default=1,
    )

    parser.add_argument(
        "--include_sample_projects",
        type=valid_bool,
        help="Set to False if projects should be taken from datasets only. Default: True",
        default=True,
    )

    parser.add_argument(
        "--symlink_path",
        type=valid_path,
        help="Please specify a path if the datasets should be sorted by the format with symlinks to the original datasets. Warning: If you're using a non-Unix-based system, you need administrative privileges to create symbolic links, or you must enable developer mode. Default: None",
        default=None,
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    main(args)
