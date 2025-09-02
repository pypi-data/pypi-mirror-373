import logging
import pandas as pd
from nemo_library.features.nemo_persistence_api import (
    createColumns,
    createReports,
    getColumns,
    getProjects,
)
from nemo_library.features.nemo_persistence_api import createProjects
from nemo_library.features.nemo_report_api import LoadReport
from nemo_library.model.column import Column
from nemo_library.model.project import Project
from nemo_library.model.report import Report
from nemo_library.utils.config import Config
from nemo_library.features.fileingestion import ReUploadFile
from nemo_library.features.focus import focusCoupleAttributes, focusMoveAttributeBefore
from nemo_library.utils.migmanutils import (
    getMappingFilePath,
    getMappingRelations,
    sqlQueryInMappingTable,
)
from nemo_library.utils.utils import (
    get_display_name,
)

__all__ = ["MigManCreateMapping"]


def MigManCreateMapping(config: Config):
    """
    Main function to create mapping projects and upload data.

    This function retrieves configuration details, checks for existing projects,
    and creates new mapping projects for specified fields if they do not already exist.
    It also uploads data, generates mapping templates, and couples attributes.

    Args:
        config (Config): Configuration object containing authentication and system settings.
    """
    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    mapping_fields = config.get_migman_mapping_fields()
    if not mapping_fields:
        logging.info(f"no mapping fields defined")
        return
    additional_fields = config.get_migman_additional_fields()
    mappingrelationsdf = getMappingRelations(config=config)
    if mappingrelationsdf.empty:
        logging.info(f"no mapping relations found, nothing to do")
        return

    # get all projects
    projects_display_names = [project.displayName for project in getProjects(config)]

    # iterate every given field and check whether to create the appropriate project and upload data
    for field in mapping_fields:

        logging.info(f"working on mapping field {field}...")

        mappingrelationsdf_filtered = mappingrelationsdf[
            mappingrelationsdf["mapping_field"] == field
        ]

        if mappingrelationsdf_filtered.empty:
            logging.info(
                f"no mapping relations found for field {field}, nothing to do for this field"
            )
            continue
        
        # if project does not exist, create it
        projectname = f"Mapping {field}"
        if not projectname in projects_display_names:

            # create project
            createMappingProject(config=config, field=field, projectname=projectname)

            # create fields
            createMappingImportedColumnns(
                config=config,
                projectname=projectname,
                field=field,
                additional_fields=additional_fields,
            )

            # collect data and fill template
            loadData(
                config=config,
                projectname=projectname,
                field=field,
                mappingrelationsdf=mappingrelationsdf_filtered,
                local_project_directory=local_project_directory,
            )

            # couple attributes in focus
            coupleAttributes(config=config, projectname=projectname)

        else:
            logging.info(f"project {projectname} found.")


def createMappingProject(
    config: Config,
    projectname: str,
    field: str,
) -> str:
    """
    Creates a mapping project for a specific field if it does not already exist.

    This function checks if a project with the name "Mapping {field}" exists in the system.
    If it does not exist, it creates the project with a description. The function then
    returns the name of the project.

    Args:
        config (Config): Configuration object containing authentication and system settings.
        projectname (str): The name of the project to be created.
        field (str): The name of the field for which the mapping project is to be created.

    Returns:
        str: The name of the mapping project.
    """

    logging.info(f"'{projectname}' not found, create it")
    createProjects(
        config=config,
        projects=[
            Project(displayName=projectname, description=f"Mapping for field '{field}'")
        ],
    )


def createMappingImportedColumnns(
    config: Config,
    projectname: str,
    field: str,
    additional_fields: dict[str, list[str]],
) -> dict[str, str]:
    """
    Creates imported columns for a mapping project.

    This function checks for existing imported columns in the project and adds new ones
    for the specified field and any additional fields.

    Args:
        config (Config): Configuration object containing authentication and system settings.
        projectname (str): The name of the project to which columns are added.
        field (str): The primary field for which columns are created.
        additional_fields (dict[str, list[str]]): Additional fields to include in the project.

    Returns:
        dict[str, str]: A dictionary of created column names and their data types.
    """

    fields = []

    additionalfields_filtered = (
        additional_fields[field]
        if additional_fields and field in additional_fields
        else None
    )
    fields.append(get_display_name(f"source {field}"))
    if additionalfields_filtered:
        for additionalField in additionalfields_filtered:
            fields.append(get_display_name(f"source {additionalField}"))
    fields.append(get_display_name(f"target {field}"))

    cols = getColumns(config=config, projectname=projectname)
    cols_display_name = [col.displayName for col in cols]

    new_columns = []
    for idx, fld in enumerate(fields):
        if not fld in cols_display_name:
            new_columns.append(
                Column(
                    displayName=fld,
                    dataType="string",
                    order=f"{idx:03}",
                    columnType="ExportedColumn",
                )
            )

    if new_columns:
        createColumns(
            config=config,
            projectname=projectname,
            columns=new_columns,
        )
        # move columns into the right order
        logging.info(
            f"Project {projectname} has {len(new_columns)} new columns that are not defined in NEMO. Move them into the right order."
        )
        last_col = None
        for col in sorted(new_columns, key=lambda x: x.order, reverse=True):
            logging.info(
                f"Move column {col.displayName} ({col.internalName}) into the right order"
            )
            focusMoveAttributeBefore(
                config=config,
                projectname=projectname,
                sourceInternalName=col.internalName,
                targetInternalName=last_col,
            )
            last_col = col.internalName


def loadData(
    config: Config,
    projectname: str,
    field: str,
    mappingrelationsdf: pd.DataFrame,
    local_project_directory: str,
) -> None:
    """
    Loads data into a mapping project and generates a mapping template.

    This function creates a report for the mapping project, retrieves the data,
    exports it as a CSV template, and uploads the template to the project.

    Args:
        config (Config): Configuration object containing authentication and system settings.
        projectname (str): The name of the project to which data is loaded.
        field (str): The field for which data is loaded.
        mappingrelationsdf (pd.DataFrame): DataFrame containing mapping relations.
        local_project_directory (str): Local directory path for storing the mapping template.
    """

    queryforreport = sqlQueryInMappingTable(
        config=config,
        field=field,
        newProject=True,
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

    # export file as a template for mappings
    file_path = getMappingFilePath(projectname, local_project_directory)
    df.to_csv(
        file_path,
        index=False,
        sep=";",
        na_rep="",
    )
    logging.info(f"mapping file '{file_path}' generated with source contents")

    # and upload it immediately
    ReUploadFile(
        config=config,
        projectname=projectname,
        filename=file_path,
        update_project_settings=False,
    )


def coupleAttributes(
    config: Config,
    projectname: str,
) -> None:
    """
    Couples attributes in a mapping project.

    This function retrieves imported columns for the project and couples them
    using the focusCoupleAttributes utility.

    Args:
        config (Config): Configuration object containing authentication and system settings.
        projectname (str): The name of the project for which attributes are coupled.
    """

    cols = getColumns(
        config=config,
        projectname=projectname,
    )
    cols_display_name = [col.displayName for col in cols]
    focusCoupleAttributes(
        config=config,
        projectname=projectname,
        attributenames=cols_display_name,
        previous_attribute=None,
    )
