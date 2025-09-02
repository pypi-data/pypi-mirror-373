from dataclasses import asdict, dataclass, field

from nemo_library.utils.utils import get_internal_name


@dataclass
class Report:
    """
    A class to represent a report.

    Attributes:
    columns (list[str]): A list of column names.
    description (str): A description of the report.
    descriptionTranslations (dict[str, str]): Translations of the description.
    displayName (str): The display name of the report.
    displayNameTranslations (dict[str, str]): Translations of the display name.
    internalName (str): The internal name of the report.
    querySyntax (str): The query syntax used in the report.
    reportCategories (list[str]): A list of report categories.
    id (str): The unique identifier of the report.
    projectId (str): The project ID associated with the report.
    tenant (str): The tenant associated with the report.
    """

    columns: list[str] = field(default_factory=list)
    description: str = ""
    descriptionTranslations: dict[str, str] = field(default_factory=dict)
    displayName: str = None
    displayNameTranslations: dict[str, str] = field(default_factory=dict)
    internalName: str = None
    querySyntax: str = None
    reportCategories: list[str] = field(default_factory=list)
    id: str = ""
    projectId: str = ""
    tenant: str = ""
    isCustom: bool = False
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Convert the Report instance to a dictionary.

        Returns:
        dict: A dictionary representation of the Report instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name and
        convert column names to uppercase.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)

        self.columns = [col.upper() for col in self.columns] if self.columns else []
