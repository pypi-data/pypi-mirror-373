import logging
import os
import pandas as pd
from nemo_library.features.nemo_persistence_api import createReports
from nemo_library.features.nemo_report_api import LoadReport
from nemo_library.model.report import Report
from nemo_library.utils.config import Config
from nemo_library.features.fileingestion import ReUploadDataFrame, ReUploadFile
from nemo_library.utils.migmanutils import (
    getMappingFilePath,
    getMappingRelations,
    sqlQueryInMappingTable,
)

__all__ = ["MigManLoadMapping"]


def MigManLoadMapping(config: Config):
    """
    Loads and processes mapping data for the specified fields in the configuration.

    This function retrieves mapping fields from the configuration, checks for the existence
    of mapping files, uploads the data, and updates the mapping data if necessary. It also
    generates reports and exports mapping templates.

    Args:
        config (Config): The configuration object containing settings for the mapping process.
    """
    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    mapping_fields = config.get_migman_mapping_fields()
    if not mapping_fields:
        logging.info(f"no mapping fields defined")
        return
    mappingrelationsdf = getMappingRelations(config=config)
    if mappingrelationsdf.empty:
        logging.info(f"no mapping relations found, nothing to do")
        return

    # iterate every given field upload data
    for field in mapping_fields:

        logging.info(f"working on mapping field {field}...")

        # check for mapping file
        projectname = f"Mapping {field}"
        file_path = getMappingFilePath(projectname, local_project_directory)
        logging.info(f"checking for data file {file_path}")

        if os.path.exists(file_path):
            datadf = pd.read_csv(
                file_path,
                sep=";",
                dtype=str,
                na_values=["", "nan", "NaN", "None"],
            )
            # replace NaN values with empty strings
            datadf.fillna("", inplace=True)

            ReUploadDataFrame(
                config=config,
                projectname=projectname,
                df=datadf,
                update_project_settings=False,
            )

        # maybe the source data have been updated, so we update our mapping data now
        # sequence is important, we first have to upload the file that was given (see above)
        # since we are now going to overwrite the file with fresh data now

        mappingrelationsdf_filtered = mappingrelationsdf[
            mappingrelationsdf["mapping_field"] == field
        ]

        if mappingrelationsdf_filtered.empty:
            logging.info(
                f"no mapping relations found for field {field}, nothing to do for this field"
            )
            continue

        # collect data
        collectData(
            config=config,
            projectname=projectname,
            field=field,
            mappingrelationsdf=mappingrelationsdf_filtered,
            local_project_directory=local_project_directory,
        )


def collectData(
    config: Config,
    projectname: str,
    field: str,
    mappingrelationsdf: pd.DataFrame,
    local_project_directory: str,
):
    """
    Collects and processes mapping data for a specific field and project.

    This function generates a report for the mapping data, exports it as a CSV file,
    and uploads the file to the specified project.

    Args:
        config (Config): The configuration object containing settings for the mapping process.
        projectname (str): The name of the project to which the mapping data belongs.
        field (str): The specific mapping field being processed.
        mappingrelationsdf (pd.DataFrame): A DataFrame containing mapping relations for the field.
        local_project_directory (str): The local directory where mapping files are stored.
    """
    queryforreport = sqlQueryInMappingTable(
        config=config,
        field=field,
        newProject=False,
        mappingrelationsdf=mappingrelationsdf,
    )
    createReports(
        config=config,
        projectname=projectname,
        reports=[
            Report(
                displayName="source mapping",
                querySyntax=queryforreport,
                description="load all source values and map them",
            )
        ],
    )

    df = LoadReport(
        config=config,
        projectname=projectname,
        report_name="source mapping",
        data_types=str,
    )

    file_path = getMappingFilePath(projectname, local_project_directory)

    # export file as a template for mappings
    df.to_csv(
        file_path,
        index=False,
        sep=";",
        na_rep="",
    )

    # and upload it immediately
    ReUploadDataFrame(
        config=config,
        projectname=projectname,
        df=df,
        update_project_settings=False,
    )
