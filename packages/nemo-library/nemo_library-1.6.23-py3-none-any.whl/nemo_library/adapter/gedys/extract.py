import json
from prefect import get_run_logger
import requests
from nemo_library.adapter.gedys.gedys_object_type import GedysObjectType
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary

GEDYS_API_URL = "https://x-test.crm2host.com/gedys"


class GedysExtract:
    """
    Adapter for Gedys API.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        self.gedys_token = self.get_token()
        super().__init__()

    def get_token(self) -> str:
        data = {
            "username": self.config.get_gedys_user_id(),
            "password": self.config.get_gedys_password(),
        }
        response_auth = requests.post(
            f"{GEDYS_API_URL}/api/auth/login",
            data=data,
        )
        if response_auth.status_code != 200:
            raise Exception(
                f"request failed. Status: {response_auth.status_code}, error: {response_auth.text}"
            )
        token = json.loads(response_auth.text)
        return token["token"]

    def extract(self) -> None:
        """
        Extracts data from the Gedys API for all entities.
        """

        # Extract all entities
        for entity in GedysObjectType:
            self.logger.info(f"Extracting entity: {entity.label}")
            self.extract_entity(entity)

    def extract_entity(self, entity: GedysObjectType) -> None:
        """
        Extracts data from the Gedys API for a given entity, handling pagination.

        Args:
            entity (str): The entity to extract data for (e.g., "OrmCRMCompany").

        Returns:
            list: A list of all records extracted from the API.
        """
        headers = {"Authorization": f"Bearer {self.gedys_token}"}
        take = 1000
        skip = 0
        all_data = []

        while True:
            body = {
                "Skip": skip,
                "Take": take,
            }
            params = {"includeRecordHistory": True}
            response = requests.post(
                f"{GEDYS_API_URL}/rest/v1/records/list/{entity.guid}",
                headers=headers,
                json=body,
                params=params,
            )

            if response.status_code != 200:
                raise Exception(
                    f"request failed. Status: {response.status_code}, error: {response.text}, entity: {entity.label}"
                )

            result = response.json()
            data = result.get("Data", [])
            all_data.extend(data)

            total_count = result.get("TotalCount", 0)
            return_count = result.get("ReturnCount", len(data))
            self.logger.info(
                f"Received {return_count:,} records out of {total_count:,} (Skip: {skip:,}). Total so far: {len(all_data):,}."
            )

            skip += return_count
            if skip >= total_count:
                break

        self.logger.info(f"Extracted {len(all_data)} records from {entity.label}.")

        # dump the data to a file
        filehandler = ETLFileHandler()
        filehandler.writeJSON(
            adapter=ETLAdapter.GEDYS,
            step=ETLStep.EXTRACT,
            data=all_data,
            entity=entity,
        )
