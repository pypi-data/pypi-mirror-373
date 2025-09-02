import json
import logging
import pandas as pd
from nemo_library.features.migman_database import MigManDatabaseLoad
from nemo_library.features.nemo_persistence_api import (
    createColumns,
    createReports,
    getColumns,
    getReports,
)
from nemo_library.features.nemo_report_api import LoadReport
from nemo_library.model.column import Column
from nemo_library.model.migman import MigMan
from nemo_library.model.report import Report
from nemo_library.utils.config import Config
from nemo_library.features.fileingestion import ReUploadDataFrame
from nemo_library.features.focus import focusCoupleAttributes
from nemo_library.utils.migmanutils import (
    getMappingRelations,
)
from nemo_library.utils.utils import (
    FilterType,
    FilterValue,
    get_display_name,
    get_import_name,
    get_internal_name,
    log_error,
)

__all__ = ["MigManApplyMapping"]


def MigManApplyMapping(config: Config) -> None:
    """
    Applies mapping configurations to projects based on the provided configuration.

    Args:
        config (Config): The configuration object containing mapping fields and other settings.

    Returns:
        None
    """

    mapping_fields = config.get_migman_mapping_fields()
    if not mapping_fields:
        logging.info(f"no mapping fields defined")
        return

    # get configuration
    mappingrelationsdf = getMappingRelations(config=config)
    if mappingrelationsdf.empty:
        logging.info(f"no mapping relations found, nothing to do")
        return
    database = MigManDatabaseLoad()

    # extract list of affected projects from that dictionary
    projects = mappingrelationsdf["project"].unique().tolist()

    for project in projects:
        mappingrelationsdf_filtered = mappingrelationsdf[
            mappingrelationsdf["project"] == project
        ]
        if mappingrelationsdf_filtered.empty:
            logging.info(
                f"no mapping relations found for project {project}, nothing to do for this project"
            )
            continue
        
        _process_project(
            config=config,
            project=project,
            mappingrelationsdf=mappingrelationsdf_filtered,
            database=database,
        )


def _process_project(
    config: Config,
    project: str,
    mappingrelationsdf: pd.DataFrame,
    database: list[MigMan],
) -> None:
    """
    Processes a single project by creating new columns, 1ing mappings,
    coupling attributes, and adjusting reports.

    Args:
        config (Config): The configuration object.
        project (str): The name of the project to process.
        mappingrelationsdf (pd.DataFrame): DataFrame containing mapping relations for the project.
        database (list[MigMan]): List of MigMan objects representing the database.

    Returns:
        None
    """

    # create "original" columns first (if not already existing)

    new_columns = []
    cols = getColumns(config=config, projectname=project)
    cols_display_names = [col.displayName for col in cols]
    mapping_columns = mappingrelationsdf["matching_field_display_name"].to_list()
    for mapping_column in mapping_columns:
        mapcol = f"Mapped_{mapping_column}"
        if not mapcol in cols_display_names:
            new_columns.append(
                Column(
                    displayName=get_display_name(mapcol),
                    importName=get_import_name(mapcol),
                    internalName=get_internal_name(mapcol),
                    description=f"Original value of {mapping_column}",
                    dataType="string",
                    columnType="ExportedColumn",
                )
            )

    if new_columns:
        createColumns(
            config=config,
            projectname=project,
            columns=new_columns,
        )
        logging.info(
            f"project '{project}': columns created\n{[json.dumps(col.to_dict(),indent=2) for col in new_columns]}"
        )

    # now lets fill these values
    _apply_mapping(
        config=config,
        project=project,
        importedcolumns=cols,
        mappingrelationsdf=mappingrelationsdf,
    )

    # couple attributes
    _focus_couple_attributes(
        config=config,
        project=project,
        mappingrelationsdf=mappingrelationsdf,
    )

    _adjust_reports(
        config=config,
        project=project,
        importedcolumns=cols,
        mappingrelationsdf=mappingrelationsdf,
        database=database,
    )


def _apply_mapping(
    config: Config,
    project: str,
    importedcolumns: list[Column],
    mappingrelationsdf: pd.DataFrame,
) -> None:
    """
    Applies mapping logic to the project by creating reports and re-uploading data.

    Args:
        config (Config): The configuration object.
        project (str): The name of the project.
        importedcolumns (list[ImportedColumn]): List of imported columns for the project.
        mappingrelationsdf (pd.DataFrame): DataFrame containing mapping relations for the project.

    Returns:
        None
    """
    select_statement = _select_statement(
        config=config,
        importedcolumns=importedcolumns,
        mappingrelationsdf=mappingrelationsdf,
    )

    createReports(
        config=config,
        projectname=project,
        reports=[
            Report(
                displayName="(MAPPING) map data",
                querySyntax=select_statement,
                internalName="MAPPING_map_data",
                description="Map data",
            )
        ],
    )

    df = LoadReport(
        config=config,
        projectname=project,
        report_name="(MAPPING) map data",
        data_types=str,
    )

    if df.empty:
        log_error(f"project '{project}': no data to map, report is empty")

    ReUploadDataFrame(
        config=config,
        projectname=project,
        df=df,
        update_project_settings=False,
        version=3,
        datasource_ids=[{"key": "datasource_id", "value": project}],
    )


def _focus_couple_attributes(
    config: Config,
    project: str,
    mappingrelationsdf: pd.DataFrame,
) -> None:
    """
    Couples attributes for the project based on mapping relations.

    Args:
        config (Config): The configuration object.
        project (str): The name of the project.
        mappingrelationsdf (pd.DataFrame): DataFrame containing mapping relations for the project.

    Returns:
        None
    """

    for idx, row in mappingrelationsdf.iterrows():
        focusCoupleAttributes(
            config=config,
            projectname=project,
            attributenames=[
                row["matching_field_display_name"],
                "Mapped_" + row["matching_field_display_name"],
            ],
            previous_attribute=row["matching_field_display_name"],
        )


def _select_statement(
    config: Config,
    importedcolumns: list[Column],
    mappingrelationsdf: pd.DataFrame,
) -> str:
    """
    Constructs a SQL SELECT statement for mapping data.

    Args:
        config (Config): The configuration object.
        importedcolumns (list[ImportedColumn]): List of imported columns for the project.
        mappingrelationsdf (pd.DataFrame): DataFrame containing mapping relations for the project.

    Returns:
        str: The constructed SQL SELECT statement.
    """

    # filter original-values, they will be re-created again
    importedcolumns = [
        ic for ic in importedcolumns if not ic.displayName.startswith("Mapped_")
    ]

    # start with easy things: select fields that are not touched
    selectfrags = [
        f'data.{ic.internalName} as "{ic.displayName}"' for ic in importedcolumns
    ]

    # add mapped fields now
    selectfrags.extend(
        [
            f"""COALESCE(mapping_{get_internal_name(row["mapping_field"])}.{get_internal_name("target_" + row["mapping_field"])},
                   data.{row["matching_field_internal_name"]}) as "Mapped_{row["matching_field_display_name"]}" """
            for idx, row in mappingrelationsdf.iterrows()
        ]
    )
    joinfrags = []
    for idx, row in mappingrelationsdf.iterrows():
        joinfrag = f"""LEFT JOIN
    $schema.{get_internal_name("PROJECT_MAPPING_" + row["mapping_field"])} mapping_{get_internal_name(row["mapping_field"])}
ON
    mapping_{get_internal_name(row["mapping_field"])}.{get_internal_name("source_" + row["mapping_field"])} = data.{row["matching_field_internal_name"]}"""

        additional_fields = row["additional_fields"]
        if any(additional_fields):
            additional_fields_defined = config.get_migman_additional_fields()
            additional_field_global_definition = additional_fields_defined.get(
                row["mapping_field"], []
            )

            for (label, name, importname), definition in zip(
                additional_fields, additional_field_global_definition
            ):
                joinfrag += f"\n\tAND mapping_{get_internal_name(row["mapping_field"])}.{get_internal_name("source_" + definition)} = data.{name}"
        joinfrags.append(joinfrag)

    select = f"""SELECT
    {"\n\t, ".join(selectfrags)}
FROM
    $schema.$table data
{"\n".join(joinfrags)}
"""

    return select


def _adjust_reports(
    config: Config,
    project: str,
    importedcolumns: list[Column],
    mappingrelationsdf: pd.DataFrame,
    database: list[MigMan],
) -> None:
    """
    Adjusts reports for the project by replacing original columns with mapped columns.

    Args:
        config (Config): The configuration object.
        project (str): The name of the project.
        importedcolumns (list[ImportedColumn]): List of imported columns for the project.
        mappingrelationsdf (pd.DataFrame): DataFrame containing mapping relations for the project.
        database (list[MigMan]): List of MigMan objects representing the database.

    Returns:
        None
    """

    def _adjust_report_query(report_internal_name: str) -> None:
        logging.info(f"adjusting report '{report_internal_name}'")
        reports = getReports(
            config=config,
            projectname=project,
            filter=report_internal_name,
            filter_type=FilterType.EQUAL,
            filter_value=FilterValue.INTERNALNAME,
        )

        # skip fields without reports
        if len(reports) == 1:
            report = reports[0]
            report_query = report.querySyntax
            for internal_name in internal_names:
                report_query = report_query.replace(
                    "\t" + internal_name + " ", f"\tmapped_{internal_name} "
                )
                report_query = report_query.replace(
                    "\t" + internal_name + ",", f"\tmapped_{internal_name},"
                )
            report.querySyntax = report_query
            report_list.append(report)

    report_list = []

    # iterate over all deficiency mining reports and replace the "original" columns with the "mapped" columns
    internal_names = mappingrelationsdf["matching_field_internal_name"].to_list()

    # lets start with the field specific reports
    migman_fields = [
        x
        for x in database
        if x.project == project
        and x.nemo_internal_name in [x.internalName for x in importedcolumns]
    ]
    for field in migman_fields:
        report_display_name = (
            f"(DEFICIENCIES) {field.index:03} {field.nemo_display_name}"
        )
        report_internal_name = get_internal_name(report_display_name)
        _adjust_report_query(report_internal_name)

    # now adjust the project specific reports
    for report in [
        "_customer__all_records_with_message",
        "_deficiencies__global",
        "_migman__all_records_with_no_message",
    ]:
        _adjust_report_query(report)

    createReports(
        config=config,
        projectname=project,
        reports=report_list,
    )
    logging.info(f"project '{project}': reports adjusted")
