from dataclasses import dataclass, asdict, field

from nemo_library.utils.utils import get_internal_name


@dataclass
class AttributeGroup:
    """
    Represents a group of attributes with various properties and settings.
    """

    attributeGroupType: str = "Standard"
    defaultMetricGroup: bool = False
    defaultDefinedColumnGroup: bool = False
    displayName: str | None = None
    displayNameTranslations: dict[str, str] = field(default_factory=dict)
    isCoupled: bool = False
    internalName: str = None
    parentAttributeGroupInternalName: str | None = None
    id: str = ""
    projectId: str = ""
    tenant: str = ""
    isCustom: bool = False
    metadataClassificationInternalName: str = ""
    order: str = ""

    def to_dict(self):
        """
        Converts the AttributeGroup instance to a dictionary.

        Returns:
            dict: A dictionary representation of the AttributeGroup instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name if it is not provided.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)
