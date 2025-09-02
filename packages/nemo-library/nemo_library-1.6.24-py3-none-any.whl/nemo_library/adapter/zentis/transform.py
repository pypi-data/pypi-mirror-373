import pandas as pd
from prefect import get_run_logger
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.adapter.zentis.zentis_object_type import ZentisObjectType
from nemo_library.core import NemoLibrary


class ZentisTransform:
    """
    Class to handle transformation of data for the Zentis adapter.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def transform(self) -> None:
        filehandler = ETLFileHandler()

        fertigartikel = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.EXTRACT,
            entity=ZentisObjectType.FERTIGARTIKEL,
        )
        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            data=fertigartikel,
            entity=ZentisObjectType.FERTIGARTIKEL,
        )
        
        rezepturdaten = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.EXTRACT,
            entity=ZentisObjectType.REZEPTURDATEN,
        )
        # Iterate through all dicts and rename key "4c" to "RENAMED_4c"
        for record in rezepturdaten:
            if "4c" in record:
                record["RENAMED_4c"] = record.pop("4c")        
                
        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            data=rezepturdaten,
            entity=ZentisObjectType.REZEPTURDATEN,
        )

    def join(self) -> None:
        filehandler = ETLFileHandler()
        fertigartikel = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            entity=ZentisObjectType.FERTIGARTIKEL,
        )
        rezepturdaten = filehandler.readJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            entity=ZentisObjectType.REZEPTURDATEN,
        )
        dffertigartikel = pd.DataFrame(fertigartikel)
        dfrezepturdaten = pd.DataFrame(rezepturdaten)
        dffertigartikel.columns = [f"Fertigartikel_{col}" for col in dffertigartikel.columns]
        dfrezepturdaten.columns = [f"Rezeptur_{col}" for col in dfrezepturdaten.columns]

        joined = pd.merge(
            dffertigartikel,
            dfrezepturdaten,
            left_on="Fertigartikel_MATNR",
            right_on="Rezeptur_Fertigartikel",
            how="outer",
            indicator=True,
        )

        # Map merge indicator to readable status
        status_map = {
            "both": "matched_both",
            "left_only": "only_fertigartikel",
            "right_only": "only_rezeptur",
        }
        joined["match_status"] = joined["_merge"].map(status_map)

        # (Optional) keep the original merge indicator or drop it
        joined.drop(columns=["_merge"], inplace=True)

        filehandler.writeJSON(
            adapter=ETLAdapter.ZENTIS,
            step=ETLStep.TRANSFORM,
            data=joined.to_dict(orient="records"),
            entity=ZentisObjectType.JOINED_DATA,
        )
