# All comments and identifiers intentionally in English.

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
import pandas as pd
import math
import re

class SupplierType(Enum):
    """Supplier type (free up if you want more types later)."""
    MANUFACTURER = "Hersteller"
    # Extend as needed:
    DISTRIBUTOR = "Händler"
    SERVICE_PROVIDER = "Dienstleister"
    OTHER = "Sonstiges"

class StatusOption(Enum):
    """Status option for checklist evaluation."""
    YES = "Ja"
    NO = "Nein"
    NA = "N/A"
    UNKNOWN = "Unbekannt"     # No cell selected
    ERROR = "Fehler"          # More than one selection in row
    
@dataclass
class CompanyInfo:
    name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    supplier_type: Optional[SupplierType] = None
    num_locations: Optional[int] = None
    num_employees: Optional[int] = None
    material_service_description: Optional[str] = None

@dataclass
class EvaluationItem:
    code: str                               # e.g. "3.2"
    category: Optional[str]                 # e.g. "3 Qualitätsmanagement"
    title: str                              # e.g. "Qualitätskontrollprozesse und -verfahren"
    responsible: Optional[str] = None       # e.g. "Fred"
    status: StatusOption = StatusOption.UNKNOWN           # Ja/Nein/Unbekannt
    rating: Optional[int] = None            # 1..5
    comment: Optional[str] = None

@dataclass
class SupplierEvaluation:
    company: CompanyInfo = field(default_factory=CompanyInfo)
    items: List[EvaluationItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a fully JSON-serializable dict (Enums -> values)."""
        def convert(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, list):
                return [convert(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            else:
                return obj

        return convert(asdict(self))
    
    @staticmethod
    def _is_intlike(x) -> bool:
        return isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x)) and float(x).is_integer()

    @classmethod
    def from_excel(cls, path: str, sheet: str = "Lieferantenbewertung") -> "SupplierEvaluation":
        """
        Parse your specific Excel layout:
        - Col A: keys (company fields, section numbers, sub-codes like 1.1)
        - Col B: values/descriptions (or section titles)
        - Col C: 'Verantwortlichkeit'
        - Col D/E/F: Status header (we map to tri-state; cells will be empty in template)
        - Col H: Rating (1..5)
        - Col I: Kommentar
        """
        df = pd.read_excel(path, sheet_name=sheet)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        print(df.head(10))

        # Normalize columns by index to be robust to "Unnamed: x" headers.
        col_key = 0
        col_desc = 1
        col_resp = 2
        col_yes = 4
        col_no = 5
        col_na = 6        
        col_rating = 7
        col_comment = 8

        # ---- Company header fields (top rows) ----
        # Row 0..2: Name, Adresse, Kontakt (value in col 1)
        # Row 3: "Art" (value in col 1)
        # Row 0..2 also pair with col 3 labels for locations/employees/description
        # Row 0: col3 "Anzahl Standorte"
        # Row 1: col3 "Anzahl Mitarbeiter"
        # Row 2: col3 "Beschreibung Material / Dienstleistung"
        def read_cell(r: int, c: int):
            try:
                v = df.iloc[r, c]
                return None if (isinstance(v, float) and math.isnan(v)) else v
            except Exception:
                return None

        name = read_cell(0, 1)
        address = read_cell(1, 1)
        contact = read_cell(2, 1)
        supplier_type_raw = read_cell(3, 1)
        supplier_type = None
        if isinstance(supplier_type_raw, str):
            # Map to enum if possible; otherwise leave None.
            st = supplier_type_raw.strip()
            for t in SupplierType:
                if t.value.lower() == st.lower():
                    supplier_type = t
                    break

        # Right side fields (same top rows, col 6 as labels)
        num_locations = read_cell(0, 6)
        num_employees = read_cell(1, 6)
        material_descr = read_cell(2, 6)

        # If later you fill those values into col 4..8, adjust here accordingly.
        # For now, we only carry the labels as schema; values remain None until captured by UI.
        # You can also pass them in externally and set on `company` after loading.

        company = CompanyInfo(
            name=str(name).strip() if isinstance(name, str) else None,
            address=str(address).strip() if isinstance(address, str) else None,
            contact=str(contact).strip() if isinstance(contact, str) else None,
            supplier_type=supplier_type,
            num_locations=num_locations,
            num_employees=num_employees,
            material_service_description=material_descr,
        )

        # ---- Checklist items (categories + sub-items) ----
        items: List[EvaluationItem] = []
        current_category: Optional[str] = None
        code_pattern = re.compile(r"^\d+\.\d+$")

        for _, row in df.iterrows():
            key = row.iloc[col_key]
            desc = row.iloc[col_desc] if len(row) > col_desc else None

            # Section header: "1", "2", ... in col A + title in col B
            if cls._is_intlike(key) and isinstance(desc, str) and desc.strip():
                current_category = f"{int(key)} {desc.strip()}"
                continue

            # Sub-item line like "1.1", "3.2", ...
            if isinstance(key, (str, int, float)) and code_pattern.match(str(key)):
                code = str(key).strip()
                title = str(desc).strip() if isinstance(desc, str) else ""
                responsible = None
                if len(row) > col_resp and isinstance(row.iloc[col_resp], str):
                    responsible = row.iloc[col_resp].strip()

                yes_marked = not pd.isna(row.iloc[col_yes]) and str(row.iloc[col_yes]).strip() != ""
                no_marked = not pd.isna(row.iloc[col_no]) and str(row.iloc[col_no]).strip() != ""
                na_marked = not pd.isna(row.iloc[col_na]) and str(row.iloc[col_na]).strip() != ""

                marked_count = sum([yes_marked, no_marked, na_marked])

                if marked_count == 0:
                    status = StatusOption.UNKNOWN
                elif marked_count > 1:
                    status = StatusOption.ERROR
                else:
                    if yes_marked:
                        status = StatusOption.YES
                    elif no_marked:
                        status = StatusOption.NO
                    elif na_marked:
                        status = StatusOption.NA

                rating = None
                if len(row) > col_rating:
                    val = row.iloc[col_rating]
                    if isinstance(val, (int, float)) and not (isinstance(val, float) and math.isnan(val)):
                        rating = int(val)

                comment = ""
                if len(row) > col_comment and isinstance(row.iloc[col_comment], str):
                    comment = row.iloc[col_comment].strip()

                items.append(
                    EvaluationItem(
                        code=code,
                        category=current_category,
                        title=title,
                        responsible=responsible,
                        status=status,
                        rating=rating,
                        comment=comment,
                    )
                )

        return cls(company=company, items=items)