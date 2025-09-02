from nemo_library.features.nemo_persistence_api import getProjectID
from nemo_library.utils.config import Config
from nemo_library.utils.utils import log_error


import pandas as pd
import requests
from deprecated import deprecated


import json
import re


@deprecated(reason="Please use 'createReports' API instead")
def createOrUpdateReport(
    config: Config,
    projectname: str,
    displayName: str,
    querySyntax: str,
    internalName: str = None,
    description: str = None,
) -> None:
    """
    Creates or updates a report in the specified project within the NEMO system.

    Args:
        config (Config): Configuration object containing connection details and headers.
        projectname (str): The name of the project where the report will be created or updated.
        displayName (str): The display name of the report.
        querySyntax (str): The query syntax that defines the report's data.
        internalName (str, optional): The internal system name of the report. Defaults to a sanitized version of `displayName`.
        description (str, optional): A description of the report. Defaults to an empty string.

    Returns:
        None

    Raises:
        RuntimeError: If any HTTP request fails (non-200/201 status code).

    Notes:
        - Fetches the project ID using `getProjectID`.
        - Retrieves the list of existing reports in the project to check if the report already exists.
        - If the report exists, updates it with the new data using a PUT request.
        - If the report does not exist, creates a new report using a POST request.
        - Logs errors and raises exceptions for failed requests.
    """
    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)

    if not internalName:
        internalName = re.sub(r"[^a-z0-9_]", "_", displayName.lower()).strip()

    # load list of reports first
    response = requests.get(
        config.get_config_nemo_url()
        + "/api/nemo-persistence/metadata/Reports/project/{projectId}/reports".format(
            projectId=project_id
        ),
        headers=headers,
    )
    resultjs = json.loads(response.text)
    df = pd.json_normalize(resultjs)
    df = pd.json_normalize(resultjs)
    if df.empty:
        internalNames = []
    else:
        internalNames = df["internalName"].to_list()
    report_exist = internalName in internalNames

    data = {
        "projectId": project_id,
        "displayName": displayName,
        "internalName": internalName,
        "querySyntax": querySyntax,
        "description": description if description else "",
        "tenant": config.get_tenant(),
    }

    if report_exist:
        df_filtered = df[df["internalName"] == internalName].iloc[0]
        data["id"] = df_filtered["id"]
        response = requests.put(
            config.get_config_nemo_url()
            + "/api/nemo-persistence/metadata/Reports/{id}".format(
                id=df_filtered["id"]
            ),
            headers=headers,
            json=data,
        )

        if response.status_code != 200:
            log_error(
                f"Request failed. Status: {response.status_code}, error: {response.text}"
            )

    else:
        response = requests.post(
            config.get_config_nemo_url() + "/api/nemo-persistence/metadata/Reports",
            headers=headers,
            json=data,
        )

        if response.status_code != 201:
            log_error(
                f"Request failed. Status: {response.status_code}, error: {response.text}"
            )


@deprecated(reason="Please use 'createRules' API instead")
def createOrUpdateRule(
    config: Config,
    projectname: str,
    displayName: str,
    ruleSourceInternalName: str,
    internalName: str = None,
    ruleGroup: str = None,
    description: str = None,
) -> None:
    """
    Creates or updates a rule in the specified project within the NEMO system.

    Args:
        config (Config): Configuration object containing connection details and headers.
        projectname (str): The name of the project where the rule will be created or updated.
        displayName (str): The display name of the rule.
        ruleSourceInternalName (str): The internal name of the rule source that the rule depends on.
        internalName (str, optional): The internal system name of the rule. Defaults to a sanitized version of `displayName`.
        ruleGroup (str, optional): The group to which the rule belongs. Defaults to None.
        description (str, optional): A description of the rule. Defaults to an empty string.

    Returns:
        None

    Raises:
        RuntimeError: If any HTTP request fails (non-200/201 status code).

    Notes:
        - Fetches the project ID using `getProjectID`.
        - Retrieves the list of existing rules in the project to check if the rule already exists.
        - If the rule exists, updates it with the new data using a PUT request.
        - If the rule does not exist, creates a new rule using a POST request.
        - Logs errors and raises exceptions for failed requests.
    """
    headers = config.connection_get_headers()
    project_id = getProjectID(config, projectname)

    if not internalName:
        internalName = re.sub(r"[^a-z0-9_]", "_", displayName.lower()).strip()

    # load list of rules first
    response = requests.get(
        config.get_config_nemo_url()
        + "/api/nemo-persistence/metadata/Rule/project/{projectId}/rules".format(
            projectId=project_id
        ),
        headers=headers,
    )
    resultjs = json.loads(response.text)
    df = pd.json_normalize(resultjs)
    if df.empty:
        internalNames = []
    else:
        internalNames = df["internalName"].to_list()
    rule_exist = internalName in internalNames

    data = {
        "active": True,
        "projectId": project_id,
        "displayName": displayName,
        "internalName": internalName,
        "tenant": config.get_tenant(),
        "description": description if description else "",
        "ruleGroup": ruleGroup,
        "ruleSourceInternalName": ruleSourceInternalName,
    }

    if rule_exist:
        df_filtered = df[df["internalName"] == internalName].iloc[0]
        data["id"] = df_filtered["id"]
        response = requests.put(
            config.get_config_nemo_url()
            + "/api/nemo-persistence/metadata/Rule/{id}".format(id=df_filtered["id"]),
            headers=headers,
            json=data,
        )
        if response.status_code != 200:
            log_error(
                f"Request failed. Status: {response.status_code}, error: {response.text}"
            )
    else:
        response = requests.post(
            config.get_config_nemo_url() + "/api/nemo-persistence/metadata/Rule",
            headers=headers,
            json=data,
        )
        if response.status_code != 201:
            log_error(
                f"Request failed. Status: {response.status_code}, error: {response.text}"
            )