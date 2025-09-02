import requests

from nemo_library.features.nemo_persistence_api import getProjectID
from nemo_library.utils.config import Config
from nemo_library.utils.utils import (
    log_error,
)


def getProjectProperty(
    config: Config,
    projectname: str,
    propertyname: str,
) -> str:
    """
    Retrieves a specific property value of a given project from the server.

    Args:
        config (Config): Configuration object containing connection details and headers.
        projectname (str): The name of the project for which the property is requested.
        propertyname (str): The name of the property to retrieve.

    Returns:
        str: The value of the specified property, with leading and trailing quotation marks removed.

    Raises:
        RuntimeError: If the request to fetch the project property fails (non-200 status code).

    Notes:
        - This function first fetches the project ID using the `getProjectID` function.
        - Constructs an endpoint URL using the project ID and property name.
        - Sends an HTTP GET request to fetch the property value.
        - Logs an error if the request fails and raises an exception.
    """
    project_id = getProjectID(config, projectname)

    headers = config.connection_get_headers()

    ENDPOINT_URL = (
        config.get_config_nemo_url()
        + "/api/nemo-persistence/ProjectProperty/project/{projectId}/{request}".format(
            projectId=project_id, request=propertyname
        )
    )

    response = requests.get(ENDPOINT_URL, headers=headers)

    if response.status_code != 200:
        log_error(
            f"request failed. Status: {response.status_code}, error: {response.text}"
        )

    return response.text[1:-1]  # cut off leading and trailing "


def setProjectMetaData(
    config: Config,
    projectname: str,
    processid_column: str = None,
    processdate_column: str = None,
    corpcurr_value: str = None,
) -> None:
    """
    Updates metadata for a specific project, including process ID, process date, and corporate currency value.

    Args:
        config (Config): Configuration object containing connection details and headers.
        projectname (str): The name of the project to update metadata for.
        processid_column (str, optional): The column name representing the process ID.
        processdate_column (str, optional): The column name representing the process date.
        corpcurr_value (str, optional): The corporate currency value to set.

    Returns:
        None

    Raises:
        RuntimeError: If the HTTP PUT request to update the metadata fails (non-200 status code).

    Notes:
        - Fetches the project ID using `getProjectID`.
        - Constructs a metadata payload based on the provided parameters.
        - Sends an HTTP PUT request to update the project's business process metadata.
        - Logs an error if the request fails and raises an exception.
    """

    headers = config.connection_get_headers()
    projectID = getProjectID(config, projectname)

    data = {}
    if corpcurr_value:
        data["corporateCurrencyValue"] = corpcurr_value
    if processdate_column:
        data["processDateColumnName"] = processdate_column
    if processid_column:
        data["processIdColumnName"] = processid_column

    ENDPOINT_URL = config.get_config_nemo_url() + "/api/nemo-persistence/ProjectProperty/project/{projectId}/BusinessProcessMetadata".format(
        projectId=projectID
    )

    response = requests.put(ENDPOINT_URL, headers=headers, json=data)
    if response.status_code != 200:
        log_error(
            f"Request failed. Status: {response.status_code}, error: {response.text}"
        )
