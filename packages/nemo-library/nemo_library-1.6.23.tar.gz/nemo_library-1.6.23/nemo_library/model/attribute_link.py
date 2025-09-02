from dataclasses import dataclass, asdict, field
from nemo_library.utils.utils import get_internal_name

@dataclass
class AttributeLink:
    """
    Represents a link between attributes with various properties and settings.

    Fields:
        sourceMetadataType: str
        order: str
        parentAttributeGroupInternalName: str
        sourceAttributeId: str
        sourceAttributeInternalName: str
        displayNameTranslations: dict[str, str]
        displayName: str
        internalName: str
        changedBy: str
        changedDate: str (ISO datetime)
        createdBy: str
        creationDate: str (ISO datetime)
        id: str
        metadataTemplateId: str
        projectId: str
        tenant: str
        metadataClassificationInternalName: str
    """

    sourceMetadataType: str = ""
    order: str = ""
    parentAttributeGroupInternalName: str = ""
    sourceAttributeId: str = ""
    sourceAttributeInternalName: str = ""
    displayNameTranslations: dict[str, str] = field(default_factory=dict)
    displayName: str = None
    internalName: str = None
    id: str = ""
    projectId: str = ""
    tenant: str = ""
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Converts the instance to a dictionary.
        """
        result = asdict(self)
        return result

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name if it is not provided.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)