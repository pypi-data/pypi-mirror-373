from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime

from nemo_library.utils.utils import get_import_name, get_internal_name


@dataclass
class Column:
    """
    Represents a column with various attributes related to its type, data, and metadata.
    """

    order: str = ""
    parentAttributeGroupInternalName: Optional[str] = None
    categorialType: bool = False
    columnType: str = ""
    containsSensitiveData: bool = False
    dataType: str = "string"
    description: str = ""
    descriptionTranslations: dict[str, str] = field(default_factory=dict)
    focusAggregationFunction: Optional[str] = None
    focusAggregationGroupByTargetType: Optional[str] = "NotApplicable"
    focusAggregationSourceColumnInternalName: Optional[str] = None
    focusGroupByTargetInternalName: Optional[str] = None
    formula: str = ""
    importName: Optional[str] = None
    stringSize: int = 0
    unit: str = ""
    dataClassificationInternalName: Optional[str] = None
    conflictState: Optional[str] = None
    displayNameTranslations: dict[str, str] = field(default_factory=dict)
    displayName: Optional[str] = None
    internalName: Optional[str] = None
    id: str = ""
    projectId: Optional[str] = None
    tenant: str = ""
    metadataClassificationInternalName: Optional[str] = None

    def to_dict(self):
        """
        Converts the Column instance to a dictionary.
        Returns:
            dict: A dictionary representation of the Column instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set importName and internalName if they are not provided.
        """
        if self.importName is None and self.displayName is not None:
            self.importName = get_import_name(self.displayName)

        if self.internalName is None and self.displayName is not None:
            self.internalName = get_internal_name(self.displayName)
