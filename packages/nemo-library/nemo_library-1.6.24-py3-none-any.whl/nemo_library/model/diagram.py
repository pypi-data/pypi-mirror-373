from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Argument:
    """
    Represents an argument for a diagram.

    Attributes:
        aggregation (str): The aggregation method.
        column (str): The column name.
        dataType (str): The data type of the column.
    """

    aggregation: str
    column: str
    dataType: str


@dataclass
class Value:
    """
    Represents a value in a diagram.

    Attributes:
        aggregation (str): The aggregation method.
        chartType (str): The type of chart.
        column (str): The column name.
        id (str): The unique identifier for the value.
        legend (str): The legend for the value.
        legendTranslations (dict[str, str]): Translations for the legend.
    """

    aggregation: str
    chartType: str
    column: str
    id: str
    legend: str
    legendTranslations: dict[str, str]


@dataclass
class Diagram:
    """
    Represents a diagram with various attributes.

    Attributes:
        alternateVisualization (bool): Indicates if there is an alternate visualization.
        argument (Argument): The argument for the diagram.
        argumentAxisTitle (str): The title of the argument axis.
        argumentAxisTitleTranslations (dict[str, str]): Translations for the argument axis title.
        description (str): The description of the diagram.
        descriptionTranslations (dict[str, str]): Translations for the description.
        displayName (str): The display name of the diagram.
        displayNameTranslations (dict[str, str]): Translations for the display name.
        internalName (str): The internal name of the diagram.
        report (str): The report associated with the diagram.
        summary (str): The summary of the diagram.
        valueAxisTitle (str): The title of the value axis.
        valueAxisTitleTranslations (dict[str, str]): Translations for the value axis title.
        values (list[Value]): The list of values in the diagram.
        id (str): The unique identifier for the diagram.
        projectId (str): The project identifier.
        tenant (str): The tenant identifier.
        isCustom (bool): Indicates if the diagram is custom.
        metadataClassificationInternalName (str): The internal name for metadata classification.
        basedOnMetric (bool): Indicates if the diagram is based on a metric.
    """

    alternateVisualization: bool
    argument: Argument
    argumentAxisTitle: str
    argumentAxisTitleTranslations: dict[str, str]
    description: str
    descriptionTranslations: dict[str, str]
    displayName: str
    displayNameTranslations: dict[str, str]
    internalName: str
    report: str
    summary: str
    valueAxisTitle: str
    valueAxisTitleTranslations: dict[str, str]
    values: list[Value]
    id: str
    projectId: str
    tenant: str
    isCustom: bool = False
    metadataClassificationInternalName: str = ""
    basedOnMetric: bool = False

    def to_dict(self):
        """
        Converts the Diagram instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Diagram instance.
        """
        return asdict(self)
