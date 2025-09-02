from prefect import get_run_logger
from nemo_library.adapter.gedys.gedys_object_type import GedysObjectType
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary
from nemo_library.features.fileingestion import ReUploadDataFrame
import pandas as pd


class GedysLoad:
    """
    Class to handle load of data for the Gedys adapter.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def load(self, lload_entities: bool = True, lload_joined: bool = True) -> None:
        """
        Load the extracted and transformed data into Nemo.
        """
        filehandler = ETLFileHandler()

        if lload_entities:
            # load all entities
            for entity in GedysObjectType:
                self.logger.info(f"Loading entity: {entity.label}")
                data = filehandler.readJSON(
                    adapter=ETLAdapter.GEDYS,
                    step=ETLStep.TRANSFORM,
                    entity=entity,
                    ignore_nonexistent=True,  # Ignore if file does not exist
                    filename=(f"02_{entity.filename}_flattened"),
                )

                if not data:
                    self.logger.warning(
                        f"No data found for entity {entity.label}. Skipping load."
                    )
                    continue

                # Convert to DataFrame for loading
                df = pd.DataFrame(data)
                if df.empty:
                    self.logger.warning(
                        f"No data to load for entity {entity.label}. Skipping load."
                    )
                    continue

                filehandler.writeDF(
                    adapter=ETLAdapter.GEDYS,
                    step=ETLStep.LOAD,
                    data=df,
                    entity=entity,
                )
                ReUploadDataFrame(
                    config=self.config,
                    projectname=f"gedys_{entity.filename}",
                    df=df,
                    update_project_settings=False,
                )

        if lload_joined:
            # Load company data
            data = filehandler.readJSON(
                adapter=ETLAdapter.GEDYS,
                step=ETLStep.TRANSFORM,
                entity=None,
                filename=f"03_{GedysObjectType.COMPANY.filename}_joined",
                label=f"{GedysObjectType.COMPANY.label} joined",
            )

            df = pd.DataFrame(data)
            if df.empty:
                raise ValueError("No data to load into Nemo.")

            filehandler.writeDF(
                adapter=ETLAdapter.GEDYS,
                step=ETLStep.LOAD,
                data=df,
                entity=None,  # No specific entity for joined data
                filename=f"{GedysObjectType.COMPANY.filename}_joined",
                label=f"{GedysObjectType.COMPANY.label} joined with opportunities",
            )
            ReUploadDataFrame(
                config=self.config,
                projectname=f"gedys_{GedysObjectType.COMPANY.filename}_joined",
                df=df,
                update_project_settings=False,
            )
