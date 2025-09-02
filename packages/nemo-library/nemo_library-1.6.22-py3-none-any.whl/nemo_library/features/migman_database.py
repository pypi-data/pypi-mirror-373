import importlib
import json
import logging
import re
from typing import Tuple
import pandas as pd
from nemo_library.features.migman_snow_scaper import SNOWScraper
from nemo_library.model.migman import MigMan
from nemo_library.utils.utils import (
    get_display_name,
    get_import_name,
    get_internal_name,
)

__all__ = [
    "MigManDatabaseInit",
    "MigManDatabaseLoad",
    "MigManDatabaseSave",
    "MigManDatabaseAddWebInformation",
]


def MigManDatabaseInit() -> None:
    """
    Initialize the MigMan database by processing template files and saving the data.

    This function reads all template files from the specified directory, processes
    them to extract relevant information, and saves the resulting database to a JSON file.
    """
    database = []
    dfs = []
    for resource in importlib.resources.contents(
        "nemo_library.templates.migmantemplates"
    ):
        df = _process_file(resource)
        dfs.append(df)
        for index, row in df.iterrows():
            database.append(
                MigMan(
                    project=row["project_name"],
                    postfix=row["postfix"],
                    index=index,
                    desc_section_column=row["Column"],
                    desc_section_column_name=row["Column Name"],
                    desc_section_location_in_proalpha=row["Location in proALPHA"],
                    desc_section_data_type=row["Data Type"],
                    desc_section_format=row["Format"],
                    header_section_label=row["migman_header_label"],
                    nemo_display_name=get_display_name(row["migman_header_label"]),
                    nemo_internal_name=get_internal_name(row["migman_header_label"]),
                    nemo_import_name=get_import_name(row["migman_header_label"]),
                )
            )

    MigManDatabaseSave(database)


def MigManDatabaseLoad() -> list[MigMan]:
    """
    Load the MigMan database from a JSON file.

    Returns:
        list[MigMan]: A list of MigMan objects loaded from the database.
    """
    with importlib.resources.open_text(
        "nemo_library.templates", "migmantemplates.json"
    ) as file:
        data = json.load(file)

    return [MigMan(**element) for element in data]


def MigManDatabaseSave(database: list[MigMan]) -> None:
    """
    Save the MigMan database to a JSON file.

    Args:
        database (list[MigMan]): The database to save, represented as a list of MigMan objects.
    """
    with open(
        "./nemo_library/templates/migmantemplates.json", "w", encoding="utf-8"
    ) as file:
        json.dump(
            [element.to_dict() for element in database],
            file,
            indent=4,
            ensure_ascii=True,
        )


def MigManDatabaseAddWebInformation() -> None:
    """
    Add web information to the MigMan database by scraping data.

    This function loads the existing database, uses the SNOWScraper to scrape
    additional information, and saves the updated database.
    """
    database = MigManDatabaseLoad()
    scraper = SNOWScraper(database)
    scraper.scrape()
    MigManDatabaseSave(database)


def _process_file(resource: str) -> pd.DataFrame:
    """
    Process a single template file to extract and structure its data.

    Args:
        resource (str): The name of the template file to process.

    Returns:
        pd.DataFrame: A DataFrame containing the processed data from the file.
    """
    # strip project name and postfix from file name
    project, postfix = _extract_project_and_postfix(resource)
    logging.info(
        f"Processing file '{resource}' for project '{project}' with postfix '{postfix}'"
    )

    # load dummy headers from first line
    dummyheaders = _import_dummy_header(resource)
    dfdesc = _import_datadescription(resource, dummyheaders)
    df = _add_calculated_fields(dfdesc, project, postfix)
    return df


def _extract_project_and_postfix(resource: str) -> Tuple[str, str]:
    """
    Extract the project name and postfix from the given resource string.

    Args:
        resource (str): The resource string (e.g., filename).

    Returns:
        Tuple[str, str]: A tuple containing the project name and postfix.
                         Returns (None, None) if the pattern does not match.
    """
    pattern = re.compile(
        r"^Template (?P<project>.*?) (?P<postfix>MAIN|Add\d+)\.csv$", re.IGNORECASE
    )
    match = pattern.match(resource)
    if match:
        return match.group("project"), match.group("postfix")
    else:
        logging.error(f"filename '{resource}' does not match expected pattern")
        return None, None


def _import_dummy_header(resource: str) -> pd.DataFrame:
    """
    Import the dummy header from the first line of the template file.

    Args:
        resource (str): The name of the template file.

    Returns:
        pd.DataFrame: A DataFrame containing the dummy header.
    """
    with importlib.resources.open_binary(
        "nemo_library.templates.migmantemplates", resource
    ) as file:

        dfdummy = pd.read_csv(
            file,
            nrows=1,
            encoding="ISO-8859-1",
            sep=";",
        )

    dummyheaders = dfdummy.columns
    return dummyheaders


def _import_datadescription(resource: str, dummyheaders: pd.DataFrame) -> pd.DataFrame:
    """
    Import the data description from the template file and map it to the dummy headers.

    Args:
        resource (str): The name of the template file.
        dummyheaders (pd.DataFrame): The dummy headers extracted from the file.

    Returns:
        pd.DataFrame: A DataFrame containing the data description with mapped headers.
    """
    with importlib.resources.open_binary(
        "nemo_library.templates.migmantemplates", resource
    ) as file:
        dfdesc = pd.read_csv(
            file,
            skiprows=2,
            encoding="ISO-8859-1",
            sep=";",
        )
    dfdesc["migman_header_label"] = dummyheaders

    dfdesc["Format"] = dfdesc["Data Type"]
    dfdesc["Data Type"] = dfdesc["Location in Proalpha"]
    dfdesc["Location in proALPHA"] = dfdesc["Description / Remark"]
    dfdesc.drop(columns=["Description / Remark"], inplace=True)

    dfdesc.loc[dfdesc["Location in proALPHA"].isna(), "Location in proALPHA"] = dfdesc[
        "migman_header_label"
    ]
    dfdesc.loc[dfdesc["Column Name"].isna(), "Column Name"] = dfdesc["Column"]
    dfdesc.loc[dfdesc["Data Type"].isna(), "Data Type"] = "CHARACTER"
    dfdesc.loc[dfdesc["Format"].isna(), "Format"] = "x(20)"
    return dfdesc


def _add_calculated_fields(
    dfdesc: pd.DataFrame, project: str, postfix: str
) -> pd.DataFrame:
    """
    Add calculated fields to the data description DataFrame.

    Args:
        dfdesc (pd.DataFrame): The data description DataFrame.
        project (str): The project name.
        postfix (str): The postfix (e.g., "MAIN" or "Add1").

    Returns:
        pd.DataFrame: The updated DataFrame with calculated fields.
    """
    dfdesc["project_name"] = project
    dfdesc["postfix"] = postfix if postfix != "MAIN" else ""
    dfdesc["display_name"] = dfdesc.apply(
        lambda row: get_display_name(row["migman_header_label"], row.name), axis=1
    )
    dfdesc["internal_name"] = dfdesc.apply(
        lambda row: get_internal_name(row["migman_header_label"], row.name), axis=1
    )
    dfdesc["import_name"] = dfdesc.apply(
        lambda row: get_import_name(row["migman_header_label"], row.name), axis=1
    )
    return dfdesc
