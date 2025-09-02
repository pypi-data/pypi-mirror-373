from dataclasses import dataclass, asdict


@dataclass
class Tile:
    """
    Represents a Tile with various attributes related to its display and metadata.
    """

    aggregation: str
    description: str
    descriptionTranslations: dict[str, str]
    displayName: str
    displayNameTranslations: dict[str, str]
    frequency: str
    graphic: str
    internalName: str
    status: str
    tileGroup: str
    tileGroupTranslations: dict[str, str]
    tileSourceID: str
    tileSourceInternalName: str
    type: str
    unit: str
    id: str
    projectId: str
    tenant: str
    isCustom: bool = False
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Converts the Tile instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Tile instance.
        """
        return asdict(self)
