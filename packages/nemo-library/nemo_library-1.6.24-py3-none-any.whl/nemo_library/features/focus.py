import pandas as pd
import requests
import json

from nemo_library.features.nemo_persistence_api import getColumns
from nemo_library.utils.config import Config
from nemo_library.features.nemo_persistence_api import getProjectID
from nemo_library.utils.utils import log_error

__all__ = ["focusMoveAttributeBefore", "focusCoupleAttributes"]


def focusMoveAttributeBefore(
    config: Config,
    projectname: str,
    sourceDisplayName: str = None,
    sourceInternalName: str = None,
    targetDisplayName: str = None,
    targetInternalName: str = None,
    groupInternalName: str = None,
) -> None:
    """
    Moves an attribute in the focus tree of a specified project, positioning it before a target attribute.

    Args:
        config (Config): Configuration object containing connection details and headers.
        projectname (str): The name of the project where the attribute will be moved.
        sourceDisplayName (str): The display name of the attribute to move.
        targetDisplayName (str, optional): The display name of the attribute before which the source will be positioned. Defaults to None.
        groupInternalName (str, optional): The internal name of the attribute group for grouping purposes. Defaults to None.

    Returns:
        None

    Raises:
        RuntimeError: If any HTTP request fails (non-200/204 status code) or if the source/target attributes are not found.

    Notes:
        - Fetches the project ID using `getProjectID`.
        - Retrieves the attribute tree for the project to locate the source and target attributes.
        - If the target display name is not provided, the source attribute is moved to the top of the group or tree.
        - Sends a PUT request to update the position of the source attribute in the attribute tree.
        - Logs errors and raises exceptions for failed requests or missing attributes.
    """

    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)

    df = _get_attribute_tree(config=config, projectname=projectname)

    # locate source and target object
    if sourceInternalName:
        filtereddf = df[df["internalColumnName"] == sourceInternalName]
    elif sourceDisplayName:
        filtereddf = df[df["label"] == sourceDisplayName]
    else:
        log_error("sourceDisplayName or sourceInternalName must be provided")

    if filtereddf.empty:
        log_error(
            f"could not find source column '{sourceInternalName if sourceInternalName else sourceDisplayName}' to move in focus"
        )
    sourceid = filtereddf.iloc[0]["id"]

    if targetDisplayName:
        if targetInternalName:
            filtereddf = df[df["internalColumnName"] == targetInternalName]
        else:
            filtereddf = df[df["label"] == targetDisplayName]
        if filtereddf.empty:
            log_error(
                f"could not find target column '{targetDisplayName}' to move in focus"
            )
        targetid = filtereddf.iloc[0]["id"]
    else:
        targetid = ""

    # now move the attribute
    data = {
        "sourceAttributes": [sourceid],
        "targetPreviousElementId": targetid,
        "groupInternalName": groupInternalName,
    }

    response = requests.put(
        config.get_config_nemo_url()
        + "/api/nemo-persistence/metadata/AttributeTree/projects/{projectId}/attributes/move".format(
            projectId=project_id
        ),
        headers=headers,
        json=data,
    )

    if response.status_code != 204:
        raise Exception(
            f"Request failed. Status: {response.status_code}, error: {response.text}"
        )


def focusCoupleAttributes(
    config: Config,
    projectname: str,
    attributenames: list[str],
    previous_attribute: str,
) -> None:

    # init
    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)

    # map attribute names to internal names
    cols = getColumns(config=config, projectname=projectname)
    cols_display = [col.id for col in cols if col.displayName in attributenames]

    if len(cols_display) != len(attributenames):
        log_error(
            f"Could not map all attributes to internal ids. Names given: {json.dumps(attributenames,indent=2)}, ids found: {json.dumps(attribute_ids,indent=2)}"
        )

    # resolve previous attribute
    previous_attribute_id = None
    if previous_attribute:
        for ic in cols:
            if ic.displayName == previous_attribute:
                previous_attribute_id = ic.id
        if not previous_attribute_id:
            log_error(f"could not find previous attribute '{previous_attribute}'")

    # we can execute the API call now
    data = {
        "attributeIds": cols_display,
        "previousElementId": previous_attribute_id,
        "containingGroupInternalName": None,
    }

    response = requests.post(
        config.get_config_nemo_url()
        + "/api/nemo-persistence/metadata/AttributeTree/projects/{projectId}/attributes/couple".format(
            projectId=project_id
        ),
        headers=headers,
        json=data,
    )

    if response.status_code != 201:
        raise Exception(
            f"Request failed. Status: {response.status_code}, error: {response.text}"
        )


def _get_attribute_tree(
    config: Config,
    projectname: str,
) -> pd.DataFrame:
    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)

    # load attribute tree
    response = requests.get(
        config.get_config_nemo_url()
        + "/api/nemo-persistence/focus/AttributeTree/projects/{projectId}/attributes".format(
            projectId=project_id
        ),
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception(
            f"Request failed. Status: {response.status_code}, error: {response.text}"
        )

    resultjs = json.loads(response.text)
    return pd.json_normalize(resultjs)
