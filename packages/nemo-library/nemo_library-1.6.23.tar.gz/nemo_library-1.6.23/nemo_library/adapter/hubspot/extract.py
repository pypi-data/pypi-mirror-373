from datetime import datetime
import time
from prefect import get_run_logger
from nemo_library.adapter.hubspot.hubspot_object_type import HubSpotObjectType
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary
from hubspot import HubSpot
from hubspot.crm.associations.models.batch_input_public_object_id import (
    BatchInputPublicObjectId,
)


class HubSpotExtract:
    """
    Adapter for HubSpot API.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def extract_deals(self, filter_deal_pipelines: list[str]) -> None:
        """
        Extract data from HubSpot API and save to files.
        """
        hs = self._getHubSpotAPIToken()

        filehandler = ETLFileHandler()

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
            "amount",
            "dealstage",
            "pipeline",
            "closedate",
            "createdate",
            "hs_lastmodifieddate",
        ]

        pipelines = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.PIPELINES,
        )
        if not pipelines:
            raise ValueError("No pipelines data found to transform")
        pipeline_map = {
            p.get("label", "").lower(): p.get("id")
            for p in pipelines.get("results", [])
        }

        if filter_deal_pipelines == ["*"]:
            filter_deal_pipelines = list(pipeline_map.keys())

        self.logger.info(f"Filtering deals by pipelines: {filter_deal_pipelines}")

        deals = []
        for pipeline_label in filter_deal_pipelines:
            pipeline_id = pipeline_map.get(pipeline_label.lower())
            if not pipeline_id:
                raise ValueError(
                    f"Pipeline '{pipeline_label}' not found in pipelines metadata"
                )

            after = None
            while True:
                search_request = {
                    "filterGroups": [
                        {
                            "filters": [
                                {
                                    "propertyName": "pipeline",
                                    "operator": "EQ",
                                    "value": pipeline_id,
                                }
                            ]
                        }
                    ],
                    "properties": deal_properties,
                    "limit": 100,
                }
                if after:
                    search_request["after"] = after

                res = hs.crm.deals.search_api.do_search(search_request)

                for deal in res.results:
                    deals.append({"id": deal.id, **deal.properties})

                self.logger.info(
                    f"Loaded {len(deals):,} deals from pipeline '{pipeline_label}'"
                )

                # pagination handling
                after = getattr(getattr(res, "paging", None), "next", None)
                after = getattr(after, "after", None)
                if not after:
                    break

        self.logger.info(f"Extracted {len(deals):,} deals from HubSpot")

        # Hubspot returns a proprietary date format. We normalize this into iso
        def normalize_dates(obj: dict) -> dict:
            cd = obj.get("closedate")
            if isinstance(cd, str) and cd.endswith("Z"):
                try:
                    dt = datetime.fromisoformat(cd[:-1] + "+00:00")
                    for field in ["createdate", "closedate", "hs_lastmodifieddate"]:
                        if field in obj:
                            obj[field] = dt.date().isoformat()  # "2024-03-08"
                except ValueError:
                    pass  # falls Format mal anders aussieht
            return obj

        deals = [normalize_dates(deal) for deal in deals]

        # dump the data to a file
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            data=deals,
            entity=HubSpotObjectType.DEALS,
        )

    def extract_pipelines(self) -> None:
        hs = self._getHubSpotAPIToken()
        pipelines = hs.crm.pipelines.pipelines_api.get_all(object_type="deals")

        # dump the data to a file
        filehandler = ETLFileHandler()
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            data=pipelines,
            entity=HubSpotObjectType.PIPELINES,
        )

    def extract_deal_owners(self) -> None:

        # load deal owner
        hs = self._getHubSpotAPIToken()
        owners = hs.crm.owners.get_all()

        # dump the data to a file
        filehandler = ETLFileHandler()
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            data=owners,
            entity=HubSpotObjectType.DEAL_OWNERS,
        )

    def extract_deal_companies(self) -> None:
        hs = self._getHubSpotAPIToken()

        # Load extracted deals data
        filehandler = ETLFileHandler()
        deals = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.DEALS,
        )

        if not deals:
            raise ValueError("No deals data found to transform")

        # we just need the IDs of the deals
        deal_ids = list(set([deal.get("id") for deal in deals]))
        if not deal_ids:
            raise ValueError("No deal IDs found to extract companies for")

        self.logger.info(
            f"Extracting deal-company associations for {len(deal_ids):,} deals"
        )

        deal_companies = []
        batch_size = 1000  # HubSpot API Limit

        for i in range(0, len(deal_ids), batch_size):
            batch_ids = deal_ids[i : i + batch_size]
            batch_input = BatchInputPublicObjectId(inputs=batch_ids)

            associations = hs.crm.associations.batch_api.read(
                from_object_type="deals",
                to_object_type="company",
                batch_input_public_object_id=batch_input,
            )

            for result in associations.results:
                deal_id = result._from.id
                to_dict = result.to
                for to in to_dict:
                    deal_companies.append(
                        {
                            "deal_id": deal_id,
                            "company_id": to.id,
                        }
                    )
            self.logger.info(f"Deal-Company batch {i // batch_size + 1:,} loaded...")

            # Pause to avoid exceeding rate limits
            time.sleep(0.2)

        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            data=deal_companies,
            entity=HubSpotObjectType.DEAL_COMPANIES,
        )

    def extract_companies(self) -> None:
        hs = self._getHubSpotAPIToken()

        # Load extracted deals data
        filehandler = ETLFileHandler()
        deal_companies = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            entity=HubSpotObjectType.DEAL_COMPANIES,
        )
        if not deal_companies:
            raise ValueError("No deal companies data found to transform")

        company_ids = list(
            set([deal_company.get("company_id") for deal_company in deal_companies])
        )

        self.logger.info(f"Extracting {len(company_ids):,} companies from HubSpot")
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

            company_infos = hs.crm.companies.search_api.do_search(search_request)

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
            self.logger.info(
                f"company details: {min(i + batch_size, total_companies):,} out of {total_companies:,} records processed"
            )

            # Pause to avoid exceeding rate limits
            time.sleep(0.2)

        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.EXTRACT,
            data=company_details,
            entity=HubSpotObjectType.COMPANY_DETAILS,
        )

    def _getHubSpotAPIToken(self) -> HubSpot:
        """
        Initializes and returns a HubSpot API client using the API token from the provided configuration.

        Args:
            config (ConfigHandler): An instance of ConfigHandler that contains configuration details,
                                    including the HubSpot API token.

        Returns:
            HubSpot: An instance of the HubSpot API client initialized with the API token.
        """
        hs = HubSpot(access_token=self.config.get_hubspot_api_token())
        return hs
