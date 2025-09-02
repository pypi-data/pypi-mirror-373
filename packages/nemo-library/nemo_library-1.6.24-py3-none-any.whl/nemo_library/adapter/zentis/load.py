from prefect import get_run_logger
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.adapter.zentis.zentis_object_type import ZentisObjectType
from nemo_library.core import NemoLibrary
from nemo_library.features.fileingestion import ReUploadDataFrame
import pandas as pd


class ZentisLoad:
    """
    Class to handle load of data for the Zentis adapter.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def load(self) -> None:
        """
        Load the extracted and transformed data into Nemo.
        """
        filehandler = ETLFileHandler()

        for entity in ZentisObjectType:
            if entity == ZentisObjectType.JOINED_DATA:
                data = filehandler.readJSON(
                    adapter=ETLAdapter.ZENTIS,
                    step=ETLStep.TRANSFORM,
                    entity=entity,
                )
                self._load_data(entity,data)

    def _load_data(self, entity: ZentisObjectType, data: list) -> None:
        """
        Loads the data into Nemo.
        """
        if not data:
            return

        self.logger.info(f"Loading {entity.label} data into Nemo")
        df = pd.DataFrame(data)
        ReUploadDataFrame(
            config=self.config,
            projectname=f"zentis_{entity.label}",
            df=df,
            update_project_settings=False,
        )

