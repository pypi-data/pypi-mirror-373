from dataclasses import dataclass, asdict, field
from nemo_library.utils.utils import get_internal_name
from typing import Dict, List, Optional

@dataclass
class Variance:
    """
    Represents a variance with various properties and settings.
    """

    conflictState: str = "NoConflict"
    description: str = ""
    descriptionTranslations: Dict[str, str] = field(default_factory=dict)
    displayName: Optional[str] = None
    displayNameTranslations: Dict[str, str] = field(default_factory=dict)
    existenceBasedColumnInternalNames: List[str] = field(default_factory=list)
    internalName: Optional[str] = None
    scopeId: str = ""
    valueBasedColumnInternalNames: List[str] = field(default_factory=list)
    id: str = ""
    projectId: str = ""
    tenant: str = ""
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Converts the Variance instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Variance instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name if it is not provided.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)
