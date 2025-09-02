import time
import logging
import pandas as pd
import re
from hubspot import HubSpot

from hubspot.crm.associations.models.batch_input_public_object_id import (
    BatchInputPublicObjectId,
)
import requests

from bs4 import BeautifulSoup

from nemo_library.utils.config import Config
from nemo_library.features.fileingestion import ReUploadDataFrame
from nemo_library.utils.utils import log_error

from hubspot.crm.companies.exceptions import ApiException

ACTIVITY_TYPES = [
    "calls",
    "communications",
    "emails",
    "feedback_submissions",
    "meetings",
    "notes",
    "postal_mail",
    "tasks",
    "taxes",
]

ACTIVITY_TYPE_DETAILS = {
    "calls": [
        "hubspot_owner_id",
        "hs_call_body",
        "hs_call_direction",
        "hs_call_duration",
        "hs_call_status",
        "hs_call_title",
    ],
    "communications": [
        "hubspot_owner_id",
        "hs_communication_body",
        "hs_communication_channel_type",
    ],
    "emails": [
        "hubspot_owner_id",
        "hs_email_text",
        "hs_email_subject",
        "hs_email_status",
        "hs_email_direction",
    ],
    "feedback_submissions": [],
    "meetings": [
        "hubspot_owner_id",
        "hs_meeting_title",
        "hs_meeting_body",
        "hs_internal_meeting_notes",
        "hs_meeting_location",
        "hs_meeting_start_time",
        "hs_meeting_end_time",
        "hs_meeting_outcome",
    ],
    "notes": ["hubspot_owner_id", "hs_note_body"],
    "postal_mail": ["hubspot_owner_id", "hs_postal_mail_body"],
    "tasks": [
        "hubspot_owner_id",
        "hs_task_body",
        "hs_task_status",
        "hs_task_priority",
        "hs_task_subject",
        "hs_task_type",
    ],
    "taxes": [],
}

DEALSTAGE_MAPPING = {
    "appointmentscheduled": "Unqualified lead​",
    "17193482": "Qualified lead",
    "16072556": "Presentation",
    "presentationscheduled": "Test phase",
    "decisionmakerboughtin": "Negotiation",
    "contractsent": "Commit",
    "closedwon": "closed and won",
    "closedlost": "closed and lost",
}

MAX_RETRIES = 5
RETRY_DELAY = 10


def FetchDealFromHubSpotAndUploadToNEMO(config: Config, projectname: str) -> None:
    """
    Fetches deal data from HubSpot, processes it, and uploads the combined information to a specified NEMO project.

    Args:
        config (Config): Configuration object containing connection details and headers.
        projectname (str): The name of the NEMO project where the deal data will be uploaded.

    Returns:
        None

    Raises:
        RuntimeError: If any step in the HubSpot data retrieval or NEMO upload process fails.

    Notes:
        - Authenticates with HubSpot using the provided configuration.
        - Retrieves deals, deal history, and deal activities from HubSpot.
        - Merges deal history and activities with deal details.
        - Resolves internal fields (e.g., `companyId`, `userId`) to human-readable information.
        - Processes the deal data to map deal stages and other fields.
        - Finally, uploads the processed deal data to the specified NEMO project using `upload_deals_to_NEMO`.
        - Includes optional debugging capability for saving/loading intermediate data as a pickle file.
    """

    hs = getHubSpotAPIToken(config=config)

    # load deals and add information to them
    deals = load_deals_from_HubSpot(hs)

    # load deal changes history
    deal_history = load_deal_history(hs, deals)
    deal_activity = load_activities(hs, deals)
    deal_activity = add_activity_details(hs, deal_activity)

    # concat deal history and deal activity
    history = pd.concat(
        [
            deal_history,
            deal_activity,
        ],
        ignore_index=True,
    )

    # and finally join that with deal details
    deals = deals.merge(history, on="deal_id", how="left")

    # resolve internal fields like companyid, userid, etc. to plain text
    deals = add_company_information(hs, deals)
    deals = add_user_information(hs, deals)
    deals = map_deal_stage(hs, deals)

    # for debugging purposes
    # deals.to_pickle("test.pkl")
    # deals = pd.read_pickle("test.pkl")

    # finally upload data to NEMO
    upload_deals_to_NEMO(config=config, projectname=projectname, deals=deals)


def getHubSpotAPIToken(config: Config) -> HubSpot:
    """
    Initializes and returns a HubSpot API client using the API token from the provided configuration.

    Args:
        config (ConfigHandler): An instance of ConfigHandler that contains configuration details,
                                including the HubSpot API token.

    Returns:
        HubSpot: An instance of the HubSpot API client initialized with the API token.
    """
    hs = HubSpot(access_token=config.get_hubspot_api_token())
    return hs


def load_deals_from_HubSpot(hs: HubSpot) -> pd.DataFrame:
    """
    Loads all deals from the HubSpot CRM and processes them into a pandas DataFrame.

    Parameters:
    -----------
    hs : HubSpot
        An instance of the HubSpot client used to interact with the HubSpot API.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the deals data. The columns are prefixed with "deal_",
        and specific columns have been renamed for clarity. The DataFrame includes
        only the properties specified in `deal_properties`.

    Functionality:
    --------------
    - Retrieves all deals from HubSpot CRM using the specified properties.
    - Converts the retrieved deals into a DataFrame.
    - Extracts nested "properties" from the data and expands them into separate columns.
    - Drops any columns provided by the API that were not explicitly requested.
    - Renames columns to ensure consistency, with all columns prefixed by "deal_".
    - Optionally filters the DataFrame to keep only specific deals (commented out by default).
    """

    # load all deals
    deal_properties = [
        "id",
        "dealname",
        "hubspot_owner_id",
        "revenue_stream",
        "verkauf_uber",
        "belegnummer",
        "budget_bekannt",
        "entscheider_bekannt",
        "entscheider_freigabe",
        "entscheidungsdauer_bekannt",
        "entscheidungsprozess_bekannt",
    ]
    deals = hs.crm.deals.get_all(properties=deal_properties)

    # convert them into data frame
    deals_data = [deal.to_dict() for deal in deals]
    deals_df = pd.DataFrame(deals_data)

    # extract "properties" column and make it new separate columns
    properties_df = pd.json_normalize(deals_df["properties"])
    deals_df = pd.concat([deals_df.drop(columns=["properties"]), properties_df], axis=1)

    # drop columns that have been provided by the API even if we did not request themn
    deals_df.drop(["hs_object_id"], axis=1, inplace=True)

    # rename all columns to have a prefix "deal_"
    deals_df.rename(columns=lambda x: f"deal_{x}", inplace=True)
    deals_df.rename(columns={"deal_belegnummer": "deal_docno"}, inplace=True)

    # debugging: remove all deals but 2

    # deal_ids_to_keep = [
    #     # "8163202199", # HORA
    #     # "8165061386", # Synflex/Schwering & Hasse
    #     "22380066663",  # Börger
    # ]
    # deals_df = deals_df[deals_df["deal_id"].isin(deal_ids_to_keep)]

    logging.info(f"{len(deals_df)} deals loaded from CRM")

    return deals_df


def load_deal_history(hs: HubSpot, deals: pd.DataFrame) -> pd.DataFrame:
    """
    Fetches and processes the historical changes of specified properties for a batch of HubSpot deals.

    This function retrieves historical data for specified properties of HubSpot deals using the HubSpot CRM API.
    It processes changes in the `dealstage`, `amount`, and `closedate` properties, capturing the old and new values
    along with metadata such as the timestamp of the change, the user who made the change, and the source of the change.

    Args:
        hs (HubSpot): An instance of the HubSpot class, which should include an `access_token` attribute for API authentication.
        deals (pd.DataFrame): A pandas DataFrame containing deal information, where each deal should have a unique `deal_id`.

    Returns:
        pd.DataFrame: A DataFrame containing the history of changes for the specified properties. The DataFrame includes:
            - deal_id: The ID of the deal.
            - update_type: A string indicating the type of update (e.g., "dealstage changed").
            - update_<property_name>_old_value: The previous value of the property before the change.
            - update_<property_name>_new_value: The new value of the property after the change.
            - update_timestamp: The timestamp when the change occurred.
            - update_user_id: The ID of the user who made the change, if available.
            - update_source_type: The source type of the change (e.g., manual, API).

    Raises:
        ValueError: If the API response status code is not 200 (OK), indicating a failed request.

    Notes:
        - The API has a batch limit, and the function processes the deals in batches of up to 50.
        - Historical changes are sorted by timestamp before processing to ensure chronological order.
    """

    batch_size = 50  # max API limit for batch with historical data

    deal_ids = deals["deal_id"].unique().tolist()
    num_deal_ids = len(deal_ids)
    base_url = "https://api.hubapi.com/crm/v3/objects/deals/batch/read"

    headers = {
        "Authorization": f"Bearer {hs.access_token}",
        "Content-Type": "application/json",
    }

    all_records = []
    for i in range(0, num_deal_ids, batch_size):
        batch_ids = deal_ids[i : i + batch_size]

        batch_read_input = {
            "inputs": [{"id": deal_id} for deal_id in batch_ids],
            "propertiesWithHistory": [
                "dealstage",
                "amount",
                "closedate",
            ],
        }

        response = requests.post(base_url, json=batch_read_input, headers=headers)

        if response.status_code == 200:
            batch_history = response.json()
            for deal_history in batch_history["results"]:
                deal_id = deal_history["id"]

                # Process historical changes from propertiesWithHistory
                for property_name, history in deal_history.get(
                    "propertiesWithHistory", {}
                ).items():
                    history_sorted = sorted(
                        history, key=lambda x: x["timestamp"]
                    )  # Sort by timestamp
                    previous_value = None
                    for change in history_sorted:
                        # The current value from 'change' is the new value, and the previous one is the old value
                        record = {
                            "deal_id": deal_id,
                            "update_type": f"{property_name} changed",
                            f"update_{property_name}_old_value": previous_value,
                            f"update_{property_name}_new_value": change.get("value"),
                            "update_timestamp": change.get("timestamp"),
                            "update_user_id": change.get("updatedByUserId"),
                            "update_source_type": change.get("sourceType"),
                        }
                        all_records.append(record)
                        previous_value = change.get(
                            "value"
                        )  # Update previous value to current value

        else:
            log_error(
                f"Failed to process batch {i//batch_size + 1} of {num_deal_ids//batch_size + 1}: {response.text}"
            )

        # Status message after processing each batch
        logging.info(
            f"deal history: {min(i + batch_size, num_deal_ids)} out of {num_deal_ids} records processed"
        )

        # Throttle request rate
        time.sleep(0.2)  # 200ms Pause per Request

    # Convert the list of records into a DataFrame
    history_df = pd.DataFrame(all_records)

    return history_df


def add_company_information(hs: HubSpot, deals: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches a DataFrame of deals with associated company information using the HubSpot API.
    This function retrieves the associations between deals and companies, fetches additional
    details about the associated companies, and merges this information into the original
    deals DataFrame.

    Parameters:
    -----------
    hs : HubSpot
        An instance of the HubSpot client, which is used to make API calls to retrieve
        associations and company details.
    deals : pd.DataFrame
        A DataFrame containing deal information. It must include a "deal_id" column
        that uniquely identifies each deal.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the original deal information, enriched with additional
        company details. The resulting DataFrame will have the original columns from the
        `deals` DataFrame, along with added columns for "company_id", "company_name",
        "company_domain", "company_industry", and other relevant fields.

    Notes:
    ------
    - This function uses the HubSpot API to retrieve company associations and company details.
    """

    # Step 1: Retrieve associations between deals and companies
    company_association_rows = []
    deal_ids = deals["deal_id"].unique().tolist()
    batch_size = 1000  # HubSpot API Limit

    for i in range(0, len(deal_ids), batch_size):
        batch_ids = deal_ids[i : i + batch_size]
        batch_input = BatchInputPublicObjectId(inputs=batch_ids)

        try:
            associations = hs.crm.associations.batch_api.read(
                from_object_type="deals",
                to_object_type="company",
                batch_input_public_object_id=batch_input,
            )

            for result in associations.results:
                deal_id = result._from.id
                to_dict = result.to
                for to in to_dict:
                    company_association_rows.append(
                        {
                            "deal_id": deal_id,
                            "company_id": to.id,
                        }
                    )
            logging.info(f"Company batch {i // batch_size + 1} loaded...")

            # Pause to avoid exceeding rate limits
            time.sleep(0.2)

        except Exception as e:
            logging.error(
                f"Error during loading Companies Batch {i // batch_size + 1}: {e}"
            )

    company_association_df = pd.DataFrame(company_association_rows)

    # Create a DataFrame from the expanded rows
    company_association_df = pd.DataFrame(company_association_rows)

    # Step 2: Retrieve company details in batches using the search API
    company_ids = company_association_df["company_id"].unique().tolist()
    company_details = []
    total_companies = len(company_ids)

    # Define the properties you want to fetch (e.g., "industry", "phone", etc.)
    properties_to_fetch = [
        "name",
        "domain",
        "industry",
        "numberofemployees",
        "annualrevenue",
    ]

    batch_size = 100
    for i in range(0, total_companies, batch_size):
        batch = company_ids[i : i + batch_size]

        # Using the search API to fetch company details with specific properties
        filter_group = {
            "filters": [
                {"propertyName": "hs_object_id", "operator": "IN", "values": batch}
            ]
        }
        search_request = {
            "filterGroups": [filter_group],
            "properties": properties_to_fetch,
            "limit": batch_size,
        }

        # Retry-Logik
        for attempt in range(MAX_RETRIES):
            try:
                company_infos = hs.crm.companies.search_api.do_search(search_request)
                break  # erfolgreich – Schleife abbrechen
            except ApiException as e:
                if e.status == 429:
                    logging.warning(f"Rate limit hit (429). Retry in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logging.error(f"Unexpected API error: {e}")
                    raise 
        else:
            log_error(f"Failed to fetch company infos after {MAX_RETRIES} attempts.")


        for company_info in company_infos.results:
            company_details.append(
                {
                    "company_id": company_info.id,
                    "company_name": company_info.properties.get("name", ""),
                    "company_domain": company_info.properties.get("domain", ""),
                    "company_industry": company_info.properties.get("industry", ""),
                    "company_numberofemployees": company_info.properties.get(
                        "numberofemployees", ""
                    ),
                    "company_annualrevenue": company_info.properties.get(
                        "annualrevenue", ""
                    ),
                }
            )

        # Status message after processing each batch
        logging.info(
            f"company association: {min(i + batch_size, total_companies)} out of {total_companies} records processed"
        )

        # Pause to avoid exceeding rate limits
        time.sleep(0.2)

    # Step 3: Create a DataFrame from the company details
    company_df = pd.DataFrame(company_details)

    # Merge the expanded DataFrame with the company_df
    merged_df = company_association_df.merge(company_df, on="company_id", how="left")

    # Merge the original deals DataFrame with the merged_df
    merged_deals = deals.merge(merged_df, on="deal_id", how="left")

    return merged_deals


def load_activities(hs: HubSpot, deals: pd.DataFrame) -> pd.DataFrame:
    """
    Load and associate activities with deals from HubSpot CRM.

    This function retrieves associations between deals and various activity types (e.g., emails, tasks, meetings)
    from the HubSpot CRM. For each deal, it loads the associated activities, organizes the data into a structured
    format, and returns it as a DataFrame.

    Args:
        hs (HubSpot): An instance of the HubSpot client used to interact with the HubSpot CRM API.
        deals (pd.DataFrame): A DataFrame containing deal information, where the 'deal_id' column represents the
                              unique identifiers of the deals to be processed.

    Returns:
        pd.DataFrame: A DataFrame containing the associations between deals and activities. The DataFrame has
                      the following columns:
                      - 'deal_id': The ID of the deal.
                      - 'activity_id': The ID of the associated activity.
                      - 'update_type': The type of activity (e.g., email, task, meeting).
    """
    activity_association_rows = []
    deal_ids = deals["deal_id"].unique().tolist()
    batch_size = 1000

    for activity_type in ACTIVITY_TYPES:
        for i in range(0, len(deal_ids), batch_size):
            batch_ids = deal_ids[i : i + batch_size]
            batch_input = BatchInputPublicObjectId(inputs=batch_ids)

            try:
                associations = hs.crm.associations.batch_api.read(
                    from_object_type="deals",
                    to_object_type=activity_type,
                    batch_input_public_object_id=batch_input,
                )

                for result in associations.results:
                    deal_id = result._from.id
                    to_dict = result.to
                    for to in to_dict:
                        activity_association_rows.append(
                            {
                                "deal_id": deal_id,
                                "activity_id": to.id,
                                "update_type": activity_type,
                            }
                        )

                logging.info(f"{activity_type} batch {i // batch_size + 1} loaded...")

                # Pause to avoid exceeding rate limits
                time.sleep(0.2)

            except Exception as e:
                logging.error(
                    f"Fehler beim Laden von {activity_type} Batch {i // batch_size + 1}: {e}"
                )

    activity_association_df = pd.DataFrame(activity_association_rows)
    return activity_association_df


def fetch_activity_details_batch_via_rest(
    hs: HubSpot,
    activity_type: str,
    activity_ids: list[str],
    properties: list[str],
) -> list[dict]:
    """
    Fetches activity details in batches from the HubSpot CRM using the batch read API.

    This function sends POST requests to the HubSpot CRM API to retrieve details of specified
    activities (e.g., contacts, deals, etc.) based on their IDs. The IDs are processed in
    batches of up to 100 at a time to comply with API limitations.

    Parameters:
    ----------
    hs : HubSpot
        An instance of the HubSpot class containing authentication details, such as the access token.
    activity_type : str
        The type of activity to fetch (e.g., 'contacts', 'deals', etc.).
    activity_ids : list[str]
        A list of activity IDs for which details are to be fetched.
    properties : list[str]
        A list of properties to be retrieved for each activity.

    Returns:
    -------
    list[dict]
        A list of dictionaries containing the properties of each activity fetched.
        Each dictionary corresponds to one activity's details.

    Notes:
    -----
    - The function processes the activity IDs in batches of up to 100 to avoid exceeding
      HubSpot API limits.

    Example:
    --------
    hs = HubSpot(access_token="your_access_token")
    activity_type = "contacts"
    activity_ids = ["123", "456", "789"]
    properties = ["firstname", "lastname", "email"]

    activity_details = fetch_activity_details_batch_via_rest(hs, activity_type, activity_ids, properties)
    """

    # Header is the same for all batches
    headers = {
        "Authorization": f"Bearer {hs.access_token}",
        "Content-Type": "application/json",
    }

    url = f"https://api.hubapi.com/crm/v3/objects/{activity_type}/batch/read"

    results = []
    total_items = len(activity_ids)

    # Split IDs into batches of up to 100
    for i in range(0, total_items, 100):
        batch_ids = activity_ids[i : i + 100]

        # Prepare the data for the batch API request
        data = {
            "properties": properties,
            "inputs": [{"id": obj_id} for obj_id in batch_ids],
        }

        # Execute the POST request to the Batch API
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            batch_results = response.json().get("results", [])
            for idx, result in enumerate(batch_results):
                activity_details = result.get("properties", {})
                results.append(activity_details)

            processed_count = min(i + 100, total_items)
            logging.info(
                f"Processed {processed_count} of {total_items} items for {activity_type}."
            )
            # Pause to avoid exceeding rate limits
            time.sleep(0.2)
        else:
            log_error(
                f"Error fetching batch for {activity_type}: {response.status_code}, {response.text}"
            )

    return results


def add_activity_details(hs: HubSpot, deal_activities: pd.DataFrame) -> pd.DataFrame:
    """
    Adds detailed information for each activity type in a HubSpot deals DataFrame.

    This function takes a DataFrame containing deal activities and enriches it by
    fetching detailed information for each activity type. It retrieves the details
    in batches using the HubSpot REST API and merges the fetched data back into the
    original DataFrame.

    Args:
        hs (HubSpot): An instance of the HubSpot API client used to fetch activity details.
        deal_activities (pd.DataFrame): A DataFrame containing deal activity data, including
                                        `activity_id` and `update_type` columns.

    Returns:
        pd.DataFrame: A DataFrame with enriched activity details, where columns from the
                      fetched activity details are prefixed with "activity_".
                      Additionally, `activity_createdate` is renamed to `update_timestamp`,
                      and `activity_hubspot_owner_id` is renamed to `update_user_id`.
    """

    # Load details for each activity type in batches
    activity_details = []

    for activity_type in ACTIVITY_TYPES:
        # Filter rows for the current activity type
        activity_data = deal_activities[deal_activities["update_type"] == activity_type]
        activity_ids = activity_data["activity_id"].unique().tolist()

        properties_to_fetch = ACTIVITY_TYPE_DETAILS.get(activity_type, [])

        if properties_to_fetch and activity_ids:
            # Fetch the details via REST API
            details = fetch_activity_details_batch_via_rest(
                hs=hs,
                activity_type=activity_type,
                activity_ids=activity_ids,
                properties=properties_to_fetch,
            )
            activity_details.extend(details)

    activity_details_df = pd.DataFrame(activity_details)

    # rename all columns to have a prefix "activity_"
    activity_details_df.rename(
        columns=lambda x: (
            f"activity_{x.replace('hs_', '')}" if not x.startswith("activity_") else x
        ),
        inplace=True,
    )
    # individual renamings

    activity_details_df.rename(
        columns={
            "activity_createdate": "update_timestamp",
            "activity_hubspot_owner_id": "update_user_id",
        },
        inplace=True,
    )

    # Merge the activity details with the original deals DataFrame using deal_id
    merged_df = deal_activities.merge(
        activity_details_df,
        left_on="activity_id",
        right_on="activity_object_id",
        how="left",
    )

    return merged_df


def beautify_deals_drop_columns(deals: pd.DataFrame) -> pd.DataFrame:
    """
    Removes unnecessary columns from a HubSpot deals DataFrame.

    This function is used to clean up a DataFrame containing deal data from HubSpot by dropping
    columns that are often included by default in API responses but are not needed for further
    processing or analysis.

    Parameters:
    -----------
    deals : pd.DataFrame
        A DataFrame containing deal information retrieved from HubSpot, potentially with extra
        columns that are not necessary for analysis.

    Returns:
    --------
    pd.DataFrame
        A cleaned DataFrame with specified unnecessary columns removed. If any of the specified
        columns are not present in the input DataFrame, they will be ignored.

    Notes:
    ------
    The following columns are removed if they exist:
        - "deal_archived"
        - "deal_archived_at"
        - "deal_properties_with_history"
        - "deal_created_at"
        - "deal_updated_at"
    """
    columns_to_drop = [
        "deal_archived",
        "deal_archived_at",
        "deal_properties_with_history",
        "deal_created_at",
        "deal_updated_at",
    ]
    deals = deals.drop(columns=columns_to_drop, errors="ignore")
    return deals


def beautify_deals_handle_date_fields(deals: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes date-related fields within a DataFrame of deals data.

    This function processes the provided DataFrame by identifying and handling various
    date and timestamp fields. Specifically, it addresses the following:

    1. Identifies columns related to creation dates, last modification dates, and timestamps
       (e.g., columns with "createdate", "lastmodifieddate", or "timestamp" in their names).
    2. Identifies specific columns that contain only date values.
    3. Corrects timestamp formats that may lack milliseconds by adding them where missing.
    4. Converts these timestamp strings to proper `datetime` objects.
    5. Removes timezone information from `datetime` objects, if present.
    6. Converts columns that should contain only dates to `date` objects, ensuring
       they are stored without time components.

    Parameters:
    ----------
    deals : pd.DataFrame
        A DataFrame containing deal-related data, with various columns potentially
        representing dates or timestamps.

    Returns:
    -------
    pd.DataFrame
        The input DataFrame with date-related fields standardized and cleaned.

    Notes:
    -----
    - The function assumes that the columns to be processed either contain complete
      timestamps or date-only values.
    - Non-date columns or columns that do not match the specified patterns are left
      unchanged.
    - The function handles errors during conversion by coercing problematic values
      to `NaT` (for datetime) or `NaN` (for dates), ensuring that the DataFrame remains
      consistent.
    """

    # Refine the date_columns selection to exclude columns that are not dates
    datetime_columns = [
        col
        for col in deals.columns
        if "createdate" in col.lower()
        or "lastmodifieddate" in col.lower()
        or "timestamp" in col.lower()
    ]
    date_only_columns = [
        "update_closedate_new_value",
        "update_closedate_old_value",
    ]  # Columns with date only

    # Define a regular expression to match timestamps without milliseconds
    pattern_datetime = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
    pattern_date_only = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")

    # Convert datetime columns and handle missing milliseconds
    for column in datetime_columns:
        # Check and fix timestamps that lack milliseconds
        deals[column] = deals[column].apply(
            lambda x: (
                re.sub(pattern_datetime, x.replace("Z", ".000Z"), x)
                if isinstance(x, str) and pattern_datetime.match(x)
                else x
            )
        )

        # Now, convert the corrected timestamps to datetime
        deals[column] = pd.to_datetime(deals[column], errors="coerce")

        # Remove timezone information if present
        if pd.api.types.is_datetime64tz_dtype(deals[column]):
            deals[column] = deals[column].dt.tz_localize(None)

    # Convert date-only columns by first checking and fixing the format
    for column in date_only_columns:
        if column in deals.columns:
            # Check and fix timestamps that lack milliseconds for date-only columns
            deals[column] = deals[column].apply(
                lambda x: (
                    re.sub(pattern_datetime, x.replace("Z", ".000Z"), x)
                    if isinstance(x, str) and not pattern_date_only.match(x)
                    else x
                )
            )

            # Convert using the full datetime format and then extract the date part
            deals[column] = pd.to_datetime(deals[column], errors="coerce").dt.date

    return deals


def beautify_deals_data_type_conversions(deals: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the data types of specified columns in the deals DataFrame to more appropriate types,
    specifically Int64 and Float64. This function also handles missing or invalid values by replacing
    empty strings and NaN values with 0 before performing the type conversions.

    Parameters:
    ----------
    deals : pd.DataFrame
        The input DataFrame containing deal data, where specific columns need type conversion.

    Returns:
    -------
    pd.DataFrame
        A DataFrame with updated data types for the specified columns.

    Notes:
    -----
    - The function first assigns data types according to the dtype_mapping dictionary.
    - Columns expected to contain integer values are converted to the "Int64" type.
    - Columns expected to contain float values are converted to the "Float64" type.
    - Empty strings and NaN values in the specified numeric columns are replaced with 0 before conversion.
    - If a column is not present in the DataFrame, it is ignored.

    Example:
    -------
    Input DataFrame:
        | deal_id | update_amount_old_value | update_amount_new_value | ... |
        |---------|------------------------|------------------------|-----|
        | '1'     | '100.0'                 | ''                     | ... |
        | '2'     | '200.5'                 | '250.5'                | ... |

    Output DataFrame:
        | deal_id | update_amount_old_value | update_amount_new_value | ... |
        |---------|------------------------|------------------------|-----|
        | 1       | 100.0                   | 0.0                    | ... |
        | 2       | 200.5                   | 250.5                  | ... |
    """

    # assign data types
    dtype_mapping = {
        "deal_id": "Int64",
        "deal_hubspot_owner_id": "Int64",
        "activity_id": "Int64",
        "activity_object_id": "Int64",
        "company_id": "Int64",
        "deal_docno": "Int64",
        "update_amount_old_value": "Float64",
        "update_amount_new_value": "Float64",
        "update_user_id": "Int64",
    }

    # Replace empty strings and NaN values with 0 for all numeric fields before type conversion
    for column, dtype in dtype_mapping.items():
        if column in deals.columns and ("Int" in dtype or "Float" in dtype):
            numeric_cast = pd.Series(deals[column], dtype=dtype)
            if "Int" in dtype:
                deals[column] = pd.to_numeric(numeric_cast, errors="coerce").astype(
                    dtype
                )
            else:
                deals[column] = pd.to_numeric(
                    numeric_cast, downcast="float", errors="coerce"
                )

    return deals


def beautify_deals_clean_text(deals: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and beautifies text data within specified columns of a DataFrame containing deal information.

    This function performs the following operations:
    1. Extracts plain text from HTML content within specified columns.
    2. Cleans the extracted text by removing HTML tags and shortening it to a maximum of 400 characters.
    3. Replaces certain "dangerous" characters and typographic quotes with their safer equivalents or removes them.
    4. Removes emojis and other unwanted symbols.

    Parameters:
    deals (pd.DataFrame): A pandas DataFrame containing deal-related data. The columns expected to contain HTML
                          and text data include:
                          - "activity_call_body"
                          - "activity_call_title"
                          - "activity_email_subject"
                          - "activity_email_text"
                          - "activity_internal_meeting_notes"
                          - "activity_meeting_body"
                          - "activity_note_body"
                          - "activity_task_body"
                          - "activity_task_subject"
                          - "company_name"

    Returns:
    pd.DataFrame: A DataFrame with cleaned and processed text in the specified columns.

    Notes:
    - The function handles only string-type values in the specified columns. Non-string values are left unchanged.
    - The text is truncated to the first 400 characters after HTML tags are stripped.
    - Emojis and other non-alphanumeric symbols specified by the regex pattern are removed.
    - Special characters like typographic quotes, Guillemets, and line breaks are removed or replaced.

    """

    def extract_and_clean_text(html):
        if isinstance(html, str):
            # Extract text from HTML
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()[:400]

            return text
        else:
            return html

    html_columns = [
        "activity_call_body",
        "activity_call_title",
        "activity_email_subject",
        "activity_email_text",
        "activity_internal_meeting_notes",
        "activity_meeting_body",
        "activity_note_body",
        "activity_task_body",
        "activity_task_subject",
        "company_name",
    ]
    for col in html_columns:
        if col in deals.columns:
            deals[col] = deals[col].apply(extract_and_clean_text)

    return deals


def upload_deals_to_NEMO(config: Config, projectname: str, deals: pd.DataFrame) -> None:
    """
    Uploads a DataFrame of deals to the NEMO system after processing and temporarily saving it as a CSV file.

    This function performs the following steps:
    1. Removes timezone information from datetime columns (as Excel does not support timezones).
    2. Drops unnecessary columns from the DataFrame such as "deal_associations", "deal_archived", etc.
    3. Saves the processed DataFrame as a CSV file to a temporary location on disk.
    4. Uploads the temporary CSV file to the NEMO system using the provided configuration and project name.

    Args:
        config (ConfigHandler): A configuration handler object required for the upload process.
        projectname (str): The name of the project to which the deals should be uploaded.
        deals (pd.DataFrame): A pandas DataFrame containing the deals data to be processed and uploaded.

    Returns:
        None

    Raises:
        Any exceptions raised by the underlying methods, such as those for file handling or uploading, will not be caught and should be handled by the caller.

    Notes:
        - The temporary CSV file is automatically deleted after the upload process is complete.
        - The file is saved with a semicolon (;) as the delimiter in the CSV format.

    """

    deals = beautify_deals_drop_columns(deals)
    deals = beautify_deals_handle_date_fields(deals)
    deals = beautify_deals_data_type_conversions(deals)
    deals = beautify_deals_clean_text(deals)

    ReUploadDataFrame(
        config=config,
        projectname=projectname,
        df=deals,
        update_project_settings=True,
        format_data=True,
    )


def add_user_information(hs: HubSpot, deals: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches a DataFrame of HubSpot deals by replacing owner and user ID columns with corresponding owner names.

    This function retrieves all HubSpot owners through the HubSpot API, creates a mapping between HubSpot owner IDs and owner names,
    and then maps this information onto the appropriate columns in the provided deals DataFrame. Specifically, it identifies columns
    in the DataFrame that contain "owner_id" or "user_id" in their names and creates new columns with the same names, replacing "id"
    with "name". The new columns will contain the owner's full name (first and last name concatenated) in place of the ID.

    Parameters:
    -----------
    hs : HubSpot
        An instance of the HubSpot client, used to interact with the HubSpot API.
    deals : pd.DataFrame
        A pandas DataFrame containing deal information, which includes one or more columns with owner or user IDs.

    Returns:
    --------
    pd.DataFrame
        The modified DataFrame with additional columns where owner or user IDs have been replaced by their corresponding names.
        The original ID columns remain unchanged, and the new name columns are added next to them.

    """
    # Load HubSpot owners and create a mapping from hubspot_owner_id to owner name
    owners = hs.crm.owners.get_all()
    owner_mapping = {
        owner.id: f"{owner.first_name} {owner.last_name}" for owner in owners
    }

    # Map internal owner ids to clear names
    columns_to_map = [
        col for col in deals.columns if "owner_id" in col or "user_id" in col
    ]
    for col in columns_to_map:
        deals[col.replace("id", "name")] = deals[col].map(owner_mapping)

    return deals


def map_deal_stage(hs: HubSpot, deals: pd.DataFrame) -> pd.DataFrame:
    """
    Maps internal deal stage keys in a DataFrame to user-friendly text based on predefined mappings.

    This function takes a DataFrame of deals and maps all columns containing "dealstage" in their names
    to more descriptive user-friendly labels using a predefined mapping dictionary. The mapping is applied
    in-place to the columns of the DataFrame.

    Parameters:
    ----------
    hs : HubSpot
        An instance of the HubSpot API client or a related object, which may be used for additional operations
        if needed in future extensions of this function. Currently not used in the function.

    deals : pd.DataFrame
        A pandas DataFrame containing deal data, where one or more columns represent deal stages using internal keys.

    Returns:
    -------
    pd.DataFrame
        The input DataFrame with the deal stage columns mapped to user-friendly text.
    """

    # Map the internal dealstage keys to user-friendly text
    columns_to_map = [col for col in deals.columns if "dealstage" in col]
    for col in columns_to_map:
        deals[col] = deals[col].map(DEALSTAGE_MAPPING)

    return deals
