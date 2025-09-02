from nemo_library.features.nemo_persistence_api import getProjectID
from nemo_library.utils.config import Config
import json
import requests


def createExportConfiguration(
    config: Config,
    projectname: str,
    configuration_id: str,
    datasource_id: str,
    configuration_json: dict,
) -> None:
    """
    Create a new export configuration for a given project.

    Args:
        config (Config): Configuration object with connection details and headers.
        projectname (str): Name of the project.
        configuration_id (str): ID for the export configuration.
        datasource_id (str): ID of the data source.
        configuration_json (dict): Configuration details as a dictionary.

    Raises:
        RuntimeError: If the request fails (status code != 201).
    """
    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)
    parameters = {
        "project_id": project_id,
        "configuration_id": configuration_id,
        "datasource_id": datasource_id,
    }
    ENDPOINT_URL = (
        config.get_config_nemo_url()
        + "/api/nemo-shared-apis/create_export_configuration"
    )

    payload = {
        "project_id": project_id,
        "configuration_id": configuration_id,
        "datasource_id": datasource_id,
        "configuration_json": configuration_json,
    }

    response = requests.post(ENDPOINT_URL, headers=headers, json=payload)

    if response.status_code != 201:
        raise RuntimeError(
            f"request failed. Status: {response.status_code}, error: {response.text}"
        )


def getExportConfiguration(
    config: Config,
    projectname: str,
    configuration_id: str,
    datasource_id: str,
) -> dict:
    """
    Retrieve the export configuration for a given project.

    Args:
        config (Config): Configuration object with connection details and headers.
        projectname (str): Name of the project.
        configuration_id (str): ID for the export configuration.
        datasource_id (str): ID of the data source.

    Returns:
        dict or None: The export configuration as a dictionary, or None if not found.

    Raises:
        RuntimeError: If the request fails (status code != 200 or 404).
    """
    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)
    parameters = {
        "project_id": project_id,
        "configuration_id": configuration_id,
        "datasource_id": datasource_id,
    }

    ENDPOINT_URL = (
        config.get_config_nemo_url() + "/api/nemo-shared-apis/export_configuration"
    )

    response = requests.get(ENDPOINT_URL, headers=headers, params=parameters)

    if response.status_code == 404:
        return None
    
    if response.status_code != 200:
        raise RuntimeError(
            f"request failed. Status: {response.status_code}, error: {response.text}"
        )

    return response.json()["configuration_json"]


def deleteExportConfiguration(
    config: Config,
    projectname: str,
    configuration_id: str,
    datasource_id: str,
) -> None:
    """
    Delete the export configuration for a given project.

    Args:
        config (Config): Configuration object with connection details and headers.
        projectname (str): Name of the project.
        configuration_id (str): ID for the export configuration.
        datasource_id (str): ID of the data source.

    Raises:
        RuntimeError: If the request fails (status code != 200).
    """
    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)
    parameters = {
        "project_id": project_id,
        "configuration_id": configuration_id,
        "datasource_id": datasource_id,
    }

    ENDPOINT_URL = (
        config.get_config_nemo_url()
        + "/api/nemo-shared-apis/delete_export_configuration"
    )

    response = requests.delete(ENDPOINT_URL, headers=headers, params=parameters)

    if response.status_code != 200:
        raise RuntimeError(
            f"request failed. Status: {response.status_code}, error: {response.text}"
        )
