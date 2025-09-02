from enum import Enum, IntEnum
import logging
import re
from typing import Type


class FilterType(Enum):
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    CONTAINS = "contains"
    REGEX = "regex"
    EQUAL = "equal"


class FilterValue(Enum):
    INTERNALNAME = "internalName"
    DISPLAYNAME = "displayName"
    ID = "id"


class FOXAttributeType(IntEnum):
    Normal = 0
    Header = 1
    Summary = 2
    Expression = 3
    Link = 4
    Classification = 5
    CaseDiscrimination = 6


SUMMARY_FUNCTIONS = {
    # define FUNCTION_COUNT    1
    # define FUNCTION_LIST    2
    # define FUNCTION_SUM    3
    # define FUNCTION_MIN    4
    # define FUNCTION_MAX    5
    # define FUNCTION_AVERAGE   6
    # define FUNCTION_PERCENT   7
    # define FUNCTION_PERCENT_DISPLAYED 8
    # define FUNCTION_PREVIOUS   9
    # define FUNCTION_CELL_WIDTH   10
    # define FUNCTION_NUMBER    11
    # define FUNCTION_NEXT    12
    # define FUNCTION_MEDIAN    13
    # define FUNCTION_STANDARD_DEVIATION 14
    # define FUNCTION_VARIANCE   15
    # define FUNCTION_MODAL    16
    # define FUNCTION_PERCENT_SUM  17
    # define FUNCTION_PERCENT_AVERAGE 18
    # define FUNCTION_ACCUMULATION  19
    # define FUNCTION_PERCENTIL   20
    # define FUNCTION_RANKING   21
    # define FUNCTION_PERCENT_ACCUMULATION 22
    # define FUNCTION_FREQUENCY 23
    1: "Count Distinct",
    2: None,  # List not yet supported
    3: "Sum",
    4: "Minimum",
    5: "Maximum",
    6: "Mean",
    7: "Percent share",
    8: None,  # Percent Displayed not yet supported
    9: None,  # Previous not yet supported
    10: None,  # Cell width not yet supported
    11: None,  # Number not yet supported
    12: None,  # Next not yet supported
    13: "Median",
    14: "Standard Deviation",
    15: "Variance",
    16: None,  # Modal not yet supported
    17: None,  # Percent sum not yet supported
    18: None,  # Percent avg not yet supported
    19: None,  # Accumulation not yet supported
    20: None,  # Percentil not yet supported
    21: None,  # Ranking not yet supported
    22: None,  # Percent Accumulation not yet supported
    23: "Frequency",
}


def get_display_name(column: str, idx: int = None) -> str:
    """
    Returns the display name for a column, optionally including an index.

    Args:
        column (str): The name of the column.
        idx (int, optional): The index to include in the display name. Defaults to None.

    Returns:
        str: The display name for the column.
    """
    if idx:
        return f"{column} ({idx:03})"
    else:
        return column


def get_internal_name(column: str, idx: int = None) -> str:
    """
    Returns the sanitized internal name for a column, optionally including an index.

    Args:
        column (str): The name of the column.
        idx (int, optional): The index to include in the internal name. Defaults to None.

    Returns:
        str: The sanitized internal name for the column.
    """
    return get_sanitized_name(get_display_name(column, idx))


def get_import_name(column: str, idx: int = None) -> str:
    """
    Returns the import name for a column, optionally including an index.

    Args:
        column (str): The name of the column.
        idx (int, optional): The index to include in the import name. Defaults to None.

    Returns:
        str: The import name for the column.
    """
    return get_display_name(column, idx)


def get_sanitized_name(displayName: str) -> str:
    """
    Returns a sanitized version of the display name, suitable for use as an internal name.

    Args:
        displayName (str): The display name to sanitize.

    Returns:
        str: The sanitized name.
    """
    sanitized_name = re.sub(r"[^a-z0-9_]", "_", displayName.lower()).strip()
    if sanitized_name.startswith("_"):
        sanitized_name = "underscore_" + sanitized_name[1:]
    return sanitized_name


def log_error(error_message: str, error_type: Type[BaseException] = ValueError) -> None:
    """
    Logs an error message and raises an exception of the specified type.

    Args:
        error_message (str): The error message to log and include in the exception.
        error_type (Type[BaseException]): The type of exception to raise. Defaults to ValueError.

    Raises:
        BaseException: The exception of the specified type with the provided error message.
    """
    logging.error(error_message)
    raise error_type(error_message)
