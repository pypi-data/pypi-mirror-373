import logging
import os
from nemo_library.features.migman_database import MigManDatabaseLoad
from nemo_library.features.nemo_persistence_api import getProjects
from nemo_library.features.nemo_report_api import LoadReport
from nemo_library.utils.config import Config
from nemo_library.utils.migmanutils import (
    get_migman_postfixes,
    get_migman_project_list,
    getProjectName,
    is_migman_project_existing,
)

__all__ = ["MigManExportData"]


def MigManExportData(config: Config) -> None:
    """
    Exports data for MigMan projects based on the provided configuration.

    This function retrieves the list of projects, checks their existence in the database,
    and exports data for each project and its associated postfixes. If multi-projects
    are configured, it handles exporting data for each addon.

    Args:
        config (Config): The configuration object containing MigMan settings.

    Raises:
        ValueError: If a project is not found in the database.
    """
    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    multi_projects = config.get_migman_multi_projects()
    projects = get_migman_project_list(config)

    project_list_nemo = [project.displayName for project in getProjects(config)]

    # load database
    database = MigManDatabaseLoad()

    for project in projects:

        # check for project in database
        if not is_migman_project_existing(database, project):
            raise ValueError(f"project '{project}' not found in database")

        # get list of postfixes
        postfixes = get_migman_postfixes(database, project)

        # init project
        multi_projects_list = (
            (multi_projects[project] if project in multi_projects else None)
            if multi_projects
            else None
        )
        if multi_projects_list:
            for addon in multi_projects_list:
                for postfix in postfixes:
                    _export_data(
                        config,
                        local_project_directory,
                        project_list_nemo,
                        project,
                        addon,
                        postfix,
                    )
        else:
            for postfix in postfixes:
                _export_data(
                    config,
                    local_project_directory,
                    project_list_nemo,
                    project,
                    None,
                    postfix,
                )


def _export_data(
    config: Config,
    local_project_directory: str,
    project_list_nemo: list[str],
    project: str,
    addon: str,
    postfix: str,
) -> None:
    """
    Exports reports for a specific project, addon, and postfix.

    This function generates and saves CSV files for predefined reports
    based on the project, addon, and postfix. It checks if the project
    is available in NEMO before exporting.

    Args:
        config (Config): The configuration object containing MigMan settings.
        local_project_directory (str): The local directory for storing exported files.
        project_list_nemo (list[str]): List of project names available in NEMO.
        project (str): The name of the project to export.
        addon (str): The addon associated with the project (can be None).
        postfix (str): The postfix associated with the project.

    Returns:
        None
    """
    # export reports
    data = [
        ("to_customer", "_with_messages", "(Customer) All records with message"),
        ("to_proalpha", "", "(MigMan) All records with no message"),
    ]
    project_name = getProjectName(project, addon, postfix)

    if project_name not in project_list_nemo:
        logging.info(
            f"Project '{project_name}' not available in NEMO. No data exported"
        )
        return

    for folder, file_postfix, report_name in data:

        logging.info(
            f"Exporting '{project}', addon '{addon}', postfix '{postfix}', report name: '{report_name}' to '{folder}'"
        )
        file_name = os.path.join(
            local_project_directory,
            folder,
            f"{project_name}{file_postfix}.csv",
        )
        df = LoadReport(
            config=config,
            projectname=project_name,
            report_name=report_name,
            data_types=str,
        )
        df.to_csv(
            file_name,
            index=False,
            sep=";",
            encoding="utf-8-sig",
        )

        logging.info(
            f"File '{file_name}' for '{project}', addon '{addon}', postfix '{postfix}' exported '{report_name}'"
        )
