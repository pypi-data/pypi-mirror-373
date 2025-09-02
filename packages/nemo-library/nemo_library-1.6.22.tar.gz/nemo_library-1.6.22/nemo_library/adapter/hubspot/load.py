from datetime import datetime
from pathlib import Path
import openpyxl
from prefect import get_run_logger
from nemo_library.adapter.hubspot.hubspot_object_type import HubSpotObjectType
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary


class HubSpotLoad:
    """
    Class to handle load of data for the HubSpot adapter.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def load_forecast_call(self) -> None:
        """
        Load forecast call data into the target system.
        """
        # Load transformed deals data
        filehandler = ETLFileHandler()
        deals = filehandler.readJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.TRANSFORM,
            entity=HubSpotObjectType.DEALS,
        )

        # dump the header
        header = [deal for deal in deals if deal.get("dealname").startswith("(FORECAST)")]
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.LOAD,
            entity=HubSpotObjectType.DEALS_FORECAST_HEADER,
            data=header,
        )

        # dump the deals itself
        forecast_deals = [
            deal
            for deal in deals
            if not deal.get("dealname", "").startswith("(FORECAST)")
            and deal.get("closedate")
            and deal.get("amount")
            and float(deal.get("amount")) > 0
            and not deal.get("dealstage") in ["Unqualified lead", "closed and lost"]
        ]
        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.LOAD,
            entity=HubSpotObjectType.DEALS_FORECAST_DEALS,
            data=forecast_deals,
        )

        return
        # now update the forecast file
        # Load the Excel workbook containing the forecast data

        etl_dir = self.config.get_etl_directory()
        file_path = Path(etl_dir) / "hubspot" / "load" / "FCCall.xlsx"

        workbook = openpyxl.load_workbook(file_path)
        # Open the specific worksheet in the workbook
        worksheet = workbook["Access-Datenbasis"]
        worksheet.delete_rows(2, worksheet.max_row)

        for deal in filtered_deals:
            if deal.get("dealname").startswith("(FORECAST)"):
                row = [
                    "hIT",
                    "21",
                    "",
                    "Verbal FC",
                    "Verbal FC",
                    deal.get("dealname").replace("(FORECAST) ", ""),
                    "",
                    deal.get("closedate"),
                    deal.get("closedate"),
                    "",
                    "",
                    deal.get("amount"),
                    "A",
                    "commit",
                    "n",
                    "",
                    "",
                    "License",
                    "Kauf",
                    "hIT",
                    "EUR",
                    None,
                ]
                worksheet.append(row)

        # remove there deals now from list
        forecast_deals = [
            deal
            for deal in filtered_deals
            if not deal.get("dealname", "").startswith("(FORECAST)")
            and deal.get("closedate")
            and deal.get("amount")
            and float(deal.get("amount")) > 0
            and not deal.get("dealstage") in ["Unqualified lead", "closed and lost"]
        ]

        self.logger.info(
            f"filtered {len(deals):,} deals down to {len(forecast_deals):,} for forecast call"
        )

        DEAL_STAGE_SPSTATUS_MAPPING = {
            # "Unqualified lead": "D",
            "Qualified lead": "C",
            "Presentation": "C",
            "Test phase": "C",
            "Negotiation": "B",
            "Commit": "A",
            "closed and won": "K",
            # "closed and lost": "X",
        }
        DEAL_STAGE_STATUS_MAPPING = {
            # "Unqualified lead": "pipeline",
            "Qualified lead": "upside",
            "Presentation": "upside",
            "Test phase": "upside",
            "Negotiation": "probable",
            "Commit": "commit",
            "closed and won": "won",
            # "closed and lost": "lost",
        }
        DEAL_STAGE_CASE_MAPPING = {
            # "Unqualified lead": "",
            "Qualified lead": "b",
            "Presentation": "b",
            "Test phase": "b",
            "Negotiation": "n",
            "Commit": "w",
            "closed and won": "",
            # "closed and lost": "",
        }
        for deal in forecast_deals:

            closedate = deal.get("closedate")
            if isinstance(closedate, datetime):
                closedate = closedate.date()  # keep only date part

            row = [
                "hIT",
                "21",
                "",
                deal.get("id"),
                (
                    deal.get("company_name")
                    if deal.get("company_name")
                    else deal.get("dealname")
                ),
                deal.get(
                    "dealname",
                ),
                deal.get("hubspot_owner_id"),
                closedate,
                closedate,
                "",
                "",
                deal.get("amount"),
                DEAL_STAGE_SPSTATUS_MAPPING.get(
                    deal.get("dealstage"), f"UNDEFINED '{deal.get('dealstage')}'"
                ),
                DEAL_STAGE_STATUS_MAPPING.get(
                    deal.get("dealstage"), f"UNDEFINED '{deal.get('dealstage')}'"
                ),
                DEAL_STAGE_CASE_MAPPING.get(
                    deal.get("dealstage"), f"UNDEFINED '{deal.get('dealstage')}'"
                ),
                "",
                "x" if float(deal.get("amount", 0) or 0) > 20000 else "",
                (
                    "Licence"
                    if deal.get("revenue_stream") == "SW"
                    else (
                        "Subscription"
                        if deal.get("revenue_stream") == "SaaS"
                        else "undefined !!!"
                    )
                ),
                (
                    "Kauf"
                    if deal.get("revenue_stream") == "SW"
                    else (
                        "SaaS / Cloud"
                        if deal.get("revenue_stream") == "SaaS"
                        else "undefined !!!"
                    )
                ),
                "hIT",
                "EUR",
                None,
            ]
            worksheet.append(row)

        # Save the workbook with the updated data
        workbook.save(file_path)

        filehandler.writeJSON(
            adapter=ETLAdapter.HUBSPOT,
            step=ETLStep.LOAD,
            entity=HubSpotObjectType.DEALS_FORECAST_DEALS,
            data=forecast_deals,
        )
