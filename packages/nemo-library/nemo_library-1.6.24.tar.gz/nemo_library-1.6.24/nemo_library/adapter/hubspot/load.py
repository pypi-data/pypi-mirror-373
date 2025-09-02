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
        header = [
            deal for deal in deals if deal.get("dealname").startswith("(FORECAST)")
        ]
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
