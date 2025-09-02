from dataclasses import asdict, dataclass, field
import re
from datetime import datetime
from uuid import UUID


@dataclass
class ColumnDetails:
    """
    Represents the details of a column.

    Attributes:
        displayName (str): The display name of the column.
        id (UUID): The unique identifier of the column.
        internalName (str): The internal name of the column.
    """

    displayName: str
    id: UUID
    internalName: str


@dataclass
class ErrorDetails:
    """
    Represents the details of an error.

    Attributes:
        fileOnlyColumns (list[ColumnDetails]): Columns that are only in the file.
        id (UUID): The unique identifier of the error.
        metadataOnlyColumns (list[ColumnDetails]): Columns that are only in the metadata.
    """

    fileOnlyColumns: list[ColumnDetails]
    id: UUID
    metadataOnlyColumns: list[ColumnDetails]


@dataclass
class Warning:
    """
    Represents a warning in the data source import process.

    Attributes:
        columnId (UUID): The unique identifier of the column.
        databaseDataType (str): The data type in the database.
        fieldName (str): The name of the field.
        fieldNumber (int): The number of the field.
        fieldValue (str): The value of the field.
        id (UUID): The unique identifier of the warning.
        maxLength (int): The maximum length of the field.
        metadataDataType (str): The data type in the metadata.
        rawRowNumber (int): The raw row number.
        rowNumber (int): The row number.
    """

    columnId: UUID
    databaseDataType: str
    fieldName: str
    fieldNumber: int
    fieldValue: str
    id: UUID
    maxLength: int
    metadataDataType: str
    rawRowNumber: int
    rowNumber: int


@dataclass
class DataSourceImportRecord:
    """
    Represents a record of a data source import.

    Attributes:
        endDateTime (datetime): The end date and time of the import.
        errorDetails (ErrorDetails): The details of any errors that occurred.
        errorType (str): The type of error.
        id (UUID): The unique identifier of the import record.
        recordsOmittedDueToWarnings (int): The number of records omitted due to warnings.
        startedByUsername (str): The username of the person who started the import.
        status (str): The status of the import.
        uploadId (str): The unique identifier of the upload.
        warnings (list[Warning]): A list of warnings that occurred during the import.
    """

    endDateTime: datetime
    errorDetails: ErrorDetails
    errorType: str
    id: UUID
    recordsOmittedDueToWarnings: int
    startedByUsername: str
    status: str
    uploadId: str
    warnings: list[Warning]


@dataclass
class ProjectProperty:
    """
    Represents a property of a project.

    Attributes:
        key (str): The key of the property.
        projectId (UUID): The unique identifier of the project.
        tenant (str): The tenant associated with the project.
        value (str): The value of the property.
    """

    key: str
    projectId: UUID
    tenant: str
    value: str


@dataclass
class Project:
    """
    Represents a project.

    Attributes:
        autoDataRefresh (bool): Whether the data refresh is automatic.
        dataSourceImportRecords (list[DataSourceImportRecord]): A list of data source import records.
        description (str): The description of the project.
        descriptionTranslations (dict[str, str]): Translations of the description.
        displayName (str): The display name of the project.
        displayNameTranslations (dict[str, str]): Translations of the display name.
        id (str): The unique identifier of the project.
        importErrorType (str): The type of import error.
        projectProperties (list[ProjectProperty]): A list of project properties.
        s3DataSourcePath (str): The S3 data source path.
        showInitialConfiguration (bool): Whether to show the initial configuration.
        status (str): The status of the project.
        tableName (str): The table name associated with the project.
        tenant (str): The tenant associated with the project.
        type (str): The type of the project.
    """

    autoDataRefresh: bool = True
    dataSourceImportRecords: list[DataSourceImportRecord] = field(default_factory=list)
    description: str = ""
    descriptionTranslations: dict[str, str] = field(default_factory=dict)
    displayName: str = None
    displayNameTranslations: dict[str, str] = field(default_factory=dict)
    id: str = ""
    importErrorType: str = "NoError"
    projectProperties: list[ProjectProperty] = field(default_factory=list)
    s3DataSourcePath: str = ""
    showInitialConfiguration: bool = False
    status: str = "Active"
    tableName: str = None
    tenant: str = ""
    type: str = "IndividualData"
    isCustom: bool = False
    metadataClassificationInternalName: str = ""

    def to_dict(self):
        """
        Converts the Project instance to a dictionary.

        Returns:
            dict: The dictionary representation of the Project instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the table name if not provided.
        """
        if not self.tableName:
            self.tableName = re.sub(
                r"[^A-Z0-9_]", "_", self.displayName.upper()
            ).strip()
            if not self.tableName.startswith("PROJECT_"):
                self.tableName = "PROJECT_" + self.tableName
