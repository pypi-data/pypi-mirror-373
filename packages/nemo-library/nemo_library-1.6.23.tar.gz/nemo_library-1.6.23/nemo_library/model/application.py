from dataclasses import dataclass, asdict, field
from nemo_library.utils.utils import get_internal_name


@dataclass
class Forecast:
    """
    Represents a forecast configuration.

    Attributes:
        groupBy (str): The attribute to group by.
        metric (str): The metric to forecast.
    """

    groupBy: str
    metric: str


@dataclass
class PageReference:
    """
    Represents a reference to a page.

    Attributes:
        order (int): The order of the page.
        page (str): The page identifier.
    """

    order: int
    page: str


@dataclass
class Application:
    """
    Represents an application configuration.

    Attributes:
        active (bool): Indicates if the application is active.
        description (str): The description of the application.
        descriptionTranslations (dict[str, str]): Translations for the description.
        displayName (str): The display name of the application.
        displayNameTranslations (dict[str, str]): Translations for the display name.
        download (str): The download link for the application.
        formatCompact (bool): Indicates if the format is compact.
        internalName (str): The internal name of the application.
        pages (list[PageReference]): List of page references.
        scopeName (str): The scope name of the application.
        changedBy (str): The user who last changed the application.
        changedDate (datetime): The date when the application was last changed.
        id (str): The unique identifier of the application.
        metadataTemplateId (str): The metadata template identifier.
        projectId (str): The project identifier.
        tenant (str): The tenant identifier.
        isCustom (bool): Indicates if the application is custom.
        metadataClassificationInternalName (str): The internal name for metadata classification.
    """

    active: bool = True
    description: str = ""
    descriptionTranslations: dict[str, str] = field(default_factory=dict)
    displayName: str = None
    displayNameTranslations: dict[str, str] = field(default_factory=dict)
    download: str = ""
    formatCompact: bool = False
    internalName: str = None
    pages: list[PageReference] = field(default_factory=list)
    scopeName: str = ""
    id: str = ""
    projectId: str = ""
    tenant: str = ""
    isCustom: bool = False
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Converts the Application instance to a dictionary.

        Returns:
            dict: The dictionary representation of the Application instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name if not provided.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)
