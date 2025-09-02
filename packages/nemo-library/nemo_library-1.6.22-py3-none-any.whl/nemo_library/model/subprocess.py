from dataclasses import asdict, dataclass
from uuid import UUID


@dataclass
class SubProcess:
    """
    Represents a subprocess with various attributes including names, descriptions,
    translations, aggregations, and identifiers.
    """

    columnInternalNames: list[str]
    description: str
    descriptionTranslations: dict[str, str]
    displayName: str
    displayNameTranslations: dict[str, str]
    groupByAggregations: dict[str, str]
    groupByColumn: str
    internalName: str
    isAggregation: bool
    timeUnit: str
    id: str
    projectId: UUID
    tenant: str
    isCustom: bool = False
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Converts the SubProcess instance to a dictionary.

        Returns:
            dict: A dictionary representation of the SubProcess instance.
        """
        return asdict(self)
