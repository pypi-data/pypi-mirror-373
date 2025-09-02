from datetime import date, datetime
from enum import Enum
import json
import logging
from pathlib import Path

try:
    # Prefect is available in your environment; we still guard the call to get_run_logger()
    from prefect import get_run_logger  # type: ignore

    _PREFECT_AVAILABLE = True
except Exception:
    # If Prefect isn't installed, we still want the class to work outside Prefect
    _PREFECT_AVAILABLE = False

from nemo_library.adapter.utils.structures import ETLAdapter, ETLBaseObjectType, ETLStep
from nemo_library.core import NemoLibrary
import pandas as pd


class ETLFileHandler:
    """
    Base class for handling ETL file operations.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = self._init_logger()

        super().__init__()

    def _init_logger(self) -> logging.Logger:
        """
        Try to obtain Prefect's run logger; if that fails, return a standard logger.
        """
        # 1) Try Prefect run logger if Prefect is available
        if _PREFECT_AVAILABLE:
            try:
                # Will raise if no active flow/task context
                plogger = get_run_logger()
                # Prefect returns a `PrefectLogAdapter`, which behaves like a logger
                plogger.info("Using Prefect run logger.")
                return plogger  # type: ignore[return-value]
            except Exception:
                # No active Prefect context; continue to standard logger
                pass

        # 2) Fallback: standard logging
        logger_name = "nemo.etl"
        logger = logging.getLogger(logger_name)

        # Avoid duplicate handlers if multiple instances are created
        if not logger.handlers:
            # Configure a sensible default format only once
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            )
        logger.info(
            "Using standard Python logger (no active Prefect context detected)."
        )
        return logger

    def readJSON(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
        ignore_nonexistent: bool = False,
    ) -> dict:
        """
        Read data from the file.
        """
        # load the entity data
        etl_dir = self.config.get_etl_directory()
        file_path = (
            Path(etl_dir)
            / f"{adapter.value}"
            / f"{step.value}"
            / f"{filename if filename else entity.filename}.json"
        )

        if not file_path.exists():
            if ignore_nonexistent:
                self.logger.warning(
                    f"File {file_path} does not exist. Returning empty data for entity {entity.label if entity else label}."
                )
                return {}
            else:
                raise FileNotFoundError(f"File {file_path} does not exist.")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not data:
            self.logger.warning(
                f"No data found in file {file_path} for entity {entity.label if entity else label}."
            )
            return {}

        return data

    def _json_default(self, o):
        # Handle HubSpot SDK models and any object with to_dict()
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return o.to_dict()
        # Datetime-like
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        # Enums
        if isinstance(o, Enum):
            return o.value
        # Fallback to string representation
        return str(o)

    def writeJSON(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        data: dict,
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
    ) -> None:
        """
        Write data to the file.
        """
        if data:
            etl_dir = self.config.get_etl_directory()
            file_path = (
                Path(etl_dir)
                / f"{adapter.value}"
                / f"{step.value}"
                / f"{filename if filename else entity.filename}.json"
            )

            # Create the output directory if it does not exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    data, f, indent=4, ensure_ascii=False, default=self._json_default
                )

            self.logger.info(
                f"Data written to {file_path} for entity {entity.label if entity else label}."
            )
        else:
            self.logger.warning(
                f"No data to write for entity {entity.label if entity else label
                }. Skipping file write."
            )

    def writeDF(
        self,
        adapter: ETLAdapter,
        step: ETLStep,
        data: pd.DataFrame,
        entity: ETLBaseObjectType | None,
        filename: str | None = None,
        label: str | None = None,
    ) -> None:
        """
        Write data to the file.
        """
        if not data.empty:
            etl_dir = self.config.get_etl_directory()
            file_path = (
                Path(etl_dir)
                / f"{adapter.value}"
                / f"{step.value}"
                / f"{filename if filename else entity.filename}.csv"
            )

            # Create the output directory if it does not exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save the DataFrame to a CSV file
            data.to_csv(file_path, index=False, encoding="utf-8")

            self.logger.info(
                f"Data written to {file_path} for entity {entity.label if entity else label}."
            )
        else:
            self.logger.warning(
                f"No data to write for entity {entity.label if entity else label}. Skipping file write."
            )
