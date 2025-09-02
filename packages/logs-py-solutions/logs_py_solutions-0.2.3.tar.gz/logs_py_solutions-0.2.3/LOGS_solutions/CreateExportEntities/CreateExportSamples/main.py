#!/usr/bin/env python3

from LOGS import LOGS
import argparse
from pathlib import Path
from ..CreateExportSamples.SampleManager import SampleManager


def main(args=None):
    """Main function to create or export samples in a LOGS instance.
    Important: This classes uses absolute paths. To obtain the correct absolute path, you must ensure
    that the relative path is correct in relation to the directory in which the script is executed.
    If you are not sure, use the absolute path for source_path and target_path"""

    logs = LOGS()

    source_path = args.source_path
    target_path = args.target_path if args.target_path else None

    export_format = args.export_format if args.export_format else "csv"

    # Create samples in the logs instance or export samples from a log instance in a csv file
    if source_path or target_path:
        sample_manager = SampleManager(
            logs,
            source_path=source_path,
            target_path=target_path,
            export_format=export_format,
        )
        if source_path:
            sample_manager.create_samples()
        if target_path:
            sample_manager.export_samples()


def validate_format(args):
    """Validate the export format and ensure it matches the target paths."""

    if args.export_format is None:
        return
    if args.target_path is not None:
        if (
            args.target_path.suffix != ""
            and args.target_path.suffix != args.export_format
        ):
            raise argparse.ArgumentTypeError(
                f"Target path suffix {args.target_path.suffix} does not match the export format {args.export_format}."
            )


def valid_format(value):
    """Validate the export format."""
    valid_formats = [".csv", ".xlsx"]
    if value not in valid_formats:
        raise argparse.ArgumentTypeError(
            f"Invalid format: {value}. Choose from {valid_formats}."
        )
    return value


def valid_target_path(target_path) -> Path:
    """Validates the given paths.

    :param target_path: The target path to validate.

    :return: The absolute path for the target.
    """

    if target_path is not None:
        target_path = Path(target_path).resolve()
        if target_path.suffix != "" and target_path.suffix not in [
            ".csv",
            ".xlsx",
        ]:
            raise ValueError(
                f"Invalid file format: {target_path.suffix}. Supported formats are: .csv, .xlsx"
            )
        return target_path
    else:
        raise argparse.ArgumentTypeError(
            "Please specify a path for the sampple data set."
        )


def valid_source_path(source_path) -> Path:
    """Validates the given source paths.

    :param source_path: The source path to validate.

    :return: The absolute path for the source.
    """

    if source_path is not None:
        source_path = Path(source_path).resolve()
        if not source_path.exists():
            raise argparse.ArgumentTypeError(
                f"Source path does not exist: {source_path}"
            )
        file_extension = source_path.suffix
        if file_extension == "":
            source_path = source_path
        elif file_extension not in [
            ".csv",
            ".xlsx",
        ]:
            raise ValueError(
                f"Invalid file format: {file_extension}. Supported formats are: .csv, .xlsx"
            )
        return source_path
    else:
        raise argparse.ArgumentTypeError(
            "Please specify a path to your CSV or Excel file with the information."
        )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create or export samples in a LOGS instance."
    )

    parser.add_argument(
        "--source_path",
        type=valid_source_path,
        default=None,
        help="Path to the CSV or Excel-file containing sample data. Should be set if you want to create samples.",
    )
    parser.add_argument(
        "--target_path",
        type=valid_target_path,
        default=None,
        help="Path to the directory where exported sample data will be saved. Should be set if you want to export samples.",
    )

    parser.add_argument(
        "--export_format",
        type=valid_format,
        choices=[".csv", ".xlsx"],
        default=".csv",
        help="Format for exported data. Default is 'csv'.",
    )
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    validate_format(args)
    main(args)
