from dataclasses import dataclass, asdict


@dataclass
class Visual:
    """
    Represents a visual element on a page.

    Attributes:
        column (int): The column position of the visual.
        columnSpan (int): The number of columns the visual spans.
        content (str): The content of the visual.
        contentTranslations (dict[str, str]): Translations of the content.
        id (str): The unique identifier of the visual.
        row (int): The row position of the visual.
        rowSpan (int): The number of rows the visual spans.
        type (str): The type of the visual.
    """

    column: int
    columnSpan: int
    content: str
    contentTranslations: dict[str, str]
    id: str
    row: int
    rowSpan: int
    type: str


@dataclass
class Page:
    """
    Represents a page containing multiple visuals.

    Attributes:
        description (str): The description of the page.
        descriptionTranslations (dict[str, str]): Translations of the description.
        displayName (str): The display name of the page.
        displayNameTranslations (dict[str, str]): Translations of the display name.
        hideIfColumns (list[str]): Columns that hide the page if present.
        internalName (str): The internal name of the page.
        numberOfColumns (int): The number of columns on the page.
        numberOfRows (int): The number of rows on the page.
        showIfColumns (list[str]): Columns that show the page if present.
        visuals (list[Visual]): The visuals contained in the page.
        id (str): The unique identifier of the page.
        projectId (str): The project identifier the page belongs to.
        tenant (str): The tenant identifier the page belongs to.
    """

    description: str
    descriptionTranslations: dict[str, str]
    displayName: str
    displayNameTranslations: dict[str, str]
    hideIfColumns: list[str]
    internalName: str
    numberOfColumns: int
    numberOfRows: int
    showIfColumns: list[str]
    visuals: list[Visual]
    id: str
    projectId: str
    tenant: str
    isCustom: bool = False
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Converts the Page instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Page instance.
        """
        return asdict(self)
