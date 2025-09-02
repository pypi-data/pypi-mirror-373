from importlib.resources import files
from pathlib import Path

"""Constants in the seedcase_sprout module."""

"""The format of the timestamp used in batch file names."""
BATCH_TIMESTAMP_FORMAT = "%Y-%m-%dT%H%M%SZ"

"""Regex pattern for timestamps with the format '%Y-%m-%dT%H%M%SZ'. Must match the
format used by BATCH_TIMESTAMP_FORMAT"""
BATCH_TIMESTAMP_PATTERN = r"\d{4}-\d{2}-\d{2}T\d{6}Z"

"""The name of the timestamp column added to the batch data (only used internally)."""
BATCH_TIMESTAMP_COLUMN_NAME = "_batch_file_timestamp_"

TEMPLATES_PATH = Path(str(files("seedcase_sprout").joinpath("templates")))
