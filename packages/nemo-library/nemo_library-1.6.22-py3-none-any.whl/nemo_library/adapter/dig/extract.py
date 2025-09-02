import json
from pathlib import Path
from prefect import get_run_logger
from nemo_library.adapter.dig.supplier_evaluation import SupplierEvaluation
from nemo_library.core import NemoLibrary


class DigExtract:
    
    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()
    
    def extract(self) -> None:
        self.logger.info("Extracting all DIG objects")
        
        path = Path("nemo_library/adapter/dig/data/")
        
        supplier1 = SupplierEvaluation.from_excel(path / "supplier_evaluation_1.xlsx")
        print(json.dumps(supplier1.to_dict(), indent=2, ensure_ascii=False))