import logging
import os
from nemo_library.features.migman_database import MigManDatabaseLoad
from nemo_library.model.migman import MigMan
from nemo_library.utils.config import Config
from nemo_library.utils.migmanutils import (
    get_migman_fields,
    get_migman_postfixes,
    get_migman_project_list,
    initializeFolderStructure,
    is_migman_project_existing,
)
import pandas as pd


__all__ = ["MigManCreateProjectTemplates"]


def MigManCreateProjectTemplates(config: Config) -> None:
    """
    Creates project templates for MigMan projects based on the provided configuration.

    Args:
        config (Config): Configuration object containing MigMan settings.

    Raises:
        ValueError: If a project is not found in the database.
    """
    # get configuration
    local_project_directory = config.get_migman_local_project_directory()
    multi_projects = config.get_migman_multi_projects()
    projects = get_migman_project_list(config)

    # initialize project folder structure
    initializeFolderStructure(local_project_directory)

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
                    _create_project_template_file(
                        database, local_project_directory, project, addon, postfix
                    )
        else:
            for postfix in postfixes:
                _create_project_template_file(
                    database, local_project_directory, project, None, postfix
                )


def _create_project_template_file(
    database: list[MigMan],
    local_project_directory: str,
    project: str,
    addon: str,
    postfix: str,
) -> None:
    """
    Creates a CSV template file for a specific project, addon, and postfix.

    Args:
        database (list[MigMan]): List of MigMan database entries.
        local_project_directory (str): Path to the local project directory.
        project (str): Name of the project.
        addon (str): Addon name for the project (can be None).
        postfix (str): Postfix for the project (can be None).
    """
    logging.info(
        f"Create project template file for '{project}', addon '{addon}', postfix '{postfix}'"
    )

    columns = get_migman_fields(database, project, postfix)

    data = {col: [""] for col in columns}
    templatedf = pd.DataFrame(data=data, columns=columns)
    templatedf.to_csv(
        os.path.join(
            local_project_directory,
            "templates",
            f"{project}{" " + addon if addon else ""}{(" (" + postfix + ")") if postfix else ""}.csv",
        ),
        index=False,
        sep=";",
        encoding="UTF-8",
    )
