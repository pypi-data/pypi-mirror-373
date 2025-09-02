import logging
import os
import pandas as pd
from nemo_library.features.nemo_persistence_api import (
    createReports,
    createRules,
    getColumns,
)
from nemo_library.model.report import Report
from nemo_library.model.rule import Rule
from nemo_library.utils.config import Config
from nemo_library.features.focus import _get_attribute_tree
from nemo_library.utils.utils import get_internal_name

LEVELS = ["PROJECT_NAME", "RULE_GROUP", "RULE_NAME"]


def createOrUpdateRulesByConfigFile(
    config: Config,
    filename: str,
) -> None:

    # read file
    configdf = _import_xlsx_file(filename)

    logging.info(
        f"file '{filename}' sucessfully imported. {len(configdf)} records found"
    )

    # iterate first level
    level0_list = configdf[LEVELS[0]].unique().tolist()
    for level0_item in level0_list:
        _process_level0(
            config=config,
            configdf=configdf,
            level0_item=level0_item,
        )


def _process_level0(
    config: Config,
    configdf: pd.DataFrame,
    level0_item: str,
) -> str:

    logging.info(f"working on {LEVELS[0]}: '{level0_item}'")

    # iterate second level
    level1_list = (
        configdf[configdf[LEVELS[0]] == level0_item][LEVELS[1]].unique().tolist()
    )
    for level1_item in level1_list:
        _process_level1(
            config=config,
            configdf=configdf,
            level0_item=level0_item,
            level1_item=level1_item,
        )


def _process_level1(
    config: Config,
    configdf: pd.DataFrame,
    level0_item: str,
    level1_item: str,
) -> str:

    logging.info(
        f"working on {LEVELS[0]}: '{level0_item}', {LEVELS[1]}: '{level1_item}'"
    )

    # iterate third level
    level2_list = (
        configdf[
            (configdf[LEVELS[0]] == level0_item) & (configdf[LEVELS[1]] == level1_item)
        ][LEVELS[2]]
        .unique()
        .tolist()
    )
    for level2_item in level2_list:
        _process_level2(
            config=config,
            configdf=configdf,
            level0_item=level0_item,
            level1_item=level1_item,
            level2_item=level2_item,
        )


def _process_level2(
    config: Config,
    configdf: pd.DataFrame,
    level0_item: str,
    level1_item: str,
    level2_item: str,
) -> str:

    logging.info(
        f"working on {LEVELS[0]}: '{level0_item}', {LEVELS[1]}: '{level1_item}', {LEVELS[2]}: '{level2_item}'"
    )

    filtereddf = configdf[
        (configdf[LEVELS[0]] == level0_item)
        & (configdf[LEVELS[1]] == level1_item)
        & (configdf[LEVELS[2]] == level2_item)
    ]

    # some attributes must be unique within this group of fields
    unique_attributes = [
        "RESTRICTION",
        "REPORT_FIELD_GROUPS",
        "REPORT_FIELD_LIST",
        "REPORT_EXCEPT_LIST",
        "EXCEPTION",
    ]

    for attribute in unique_attributes:
        field_value = filtereddf[attribute].unique().tolist()
        if len(field_value) > 1:
            raise ValueError(
                f"""{LEVELS[0]}: '{level0_item}', {LEVELS[1]}: '{level1_item}', {LEVELS[2]}: '{level2_item}', attribute '{attribute}' is not unique!
Values provided: {field_value}
Please ensure that all records with same project name and same restriction have all the same value in this field"""
            )
        field_value = (
            ""
            if len(field_value) == 0 or pd.isnull(field_value[0])
            else str(field_value[0])
        )
        match attribute:
            case "RESTRICTION":
                restriction = field_value
            case "REPORT_FIELD_GROUPS":
                report_field_groups = field_value.split(",")
            case "REPORT_FIELD_LIST":
                report_field_list = field_value.split(",")
            case "REPORT_EXCEPT_LIST":
                report_except_list = field_value.split(",")
            case "EXCEPTION":
                exception = field_value

    # resolve report field list
    report_field_list = _get_report_field_list(
        config=config,
        project_name=level0_item,
        report_field_groups=report_field_groups,
        report_field_list=report_field_list,
        report_except_list=report_except_list,
    )

    # build report
    frags_check = []
    frags_msg = []
    for idx, row in filtereddf.iterrows():
        frags_check.append(f"({row["RULE_DEFINITION"]})")
        frags_msg.append(f"WHEN ({row["RULE_DEFINITION"]}) THEN '{row['RULE_NAME']}'")

    select = f"""SELECT 
\tCASE WHEN
\t\t{"\n\t\t  OR ".join(frags_check)} THEN 'check' ELSE 'ok'
\tEND AS STATUS
\t, CASE {"\n\t\t".join(frags_msg)} END AS DEFICIENCY_MESSAGE
\t, {"\n\t, ".join(report_field_list)}
FROM
    $schema.$table
WHERE
    ({restriction})
AND ({exception})
"""

    # create the report
    report_display_name = f"(DEFICIENCIES) {level1_item}, {level2_item}"
    report_internal_name = get_internal_name(report_display_name)

    createReports(
        config=config,
        projectname=level0_item,
        reports=[
            Report(
                displayName=report_display_name,
                internalName=report_internal_name,
                querySyntax=select,
                description=f"Deficiency Mining Report for {level0_item}, {level1_item}, {level2_item}'",
            )
        ],
    )

    createRules(
        config=config,
        projectname=level0_item,
        rules=[
            Rule(
                displayName=level2_item,
                ruleSourceInternalName=report_internal_name,
                ruleGroup=level1_item,
                description=f"Deficiency Mining Rule for {level0_item}, {level1_item}, {level2_item}'",
            )
        ],
    )


def _get_report_field_list(
    config: Config,
    project_name: str,
    report_field_groups: list[str],
    report_field_list: list[str],
    report_except_list: list[str],
) -> list[str]:
    # resolve field groups into field list
    report_field_list = (
        _resolve_field_groups(
            config=config, project_name=project_name, field_groups=report_field_groups
        )
        if report_field_groups and any(report_field_groups)
        else [] + report_field_list if report_field_list else []
    )

    # eliminate douplicates and remove except fields
    report_field_list = list(
        set(report_field_list) - set(report_except_list if report_except_list else [])
    )

    # fields found?
    if not report_field_list:
        raise ValueError("Field list is empty!")

    # validate fields given
    cols_nemo = getColumns(config=config, projectname=project_name)
    cols_nemo_internal = [col.internalName for col in cols_nemo]
    fields_not_existing = set(report_field_list) - set(cols_nemo_internal)
    if fields_not_existing:
        raise ValueError(
            f"""One or many fields not found in project: {fields_not_existing}.
List of fields available: {cols_nemo_internal}"""
        )

    return report_field_list


def _resolve_field_groups(
    config: Config,
    project_name: str,
    field_groups: list[str],
) -> list[str]:
    df = _get_attribute_tree(config=config, projectname=project_name)
    group_internal_names = df["groupInternalName"].unique().tolist()
    groups_not_existing = set(field_groups) - set(group_internal_names)
    if groups_not_existing:
        raise ValueError(
            f"""One or many field groups not found in project '{project_name}': {groups_not_existing}
field groups provided: {field_groups}"""
        )

    filtereddf = df[df["groupInternalName"].isin(field_groups)]
    internalColumnName = filtereddf["internalColumnName"].to_list()
    return internalColumnName


def _import_xlsx_file(
    filename: str,
) -> pd.DataFrame:

    # validate file
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)

    # import file
    df = pd.read_excel(filename)

    # check columns
    expected_columns = [
        "PROJECT_NAME",
        "RULE_GROUP",
        "RULE_NAME",
        "RESTRICTION",
        "REPORT_FIELD_GROUPS",
        "REPORT_FIELD_LIST",
        "REPORT_EXCEPT_LIST",
        "RULE_DEFINITION",
        "EXCEPTION",
        "INCLUDE_IN_GLOBAL",
    ]

    actual_columns = df.columns.to_list()

    missing_columns = set(expected_columns) - set(actual_columns)
    extra_columns = set(actual_columns) - set(expected_columns)

    if missing_columns or extra_columns:
        raise ValueError(
            f"Headers do not match!\n"
            f"Missing columns: {', '.join(missing_columns) if missing_columns else 'None'}\n"
            f"Extra columns: {', '.join(extra_columns) if extra_columns else 'None'}"
        )

    # remove inactive objects
    filtereddf = df[df["INCLUDE_IN_GLOBAL"] == True]

    return filtereddf
