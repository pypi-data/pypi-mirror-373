from collections import defaultdict
import copy
from dataclasses import fields, is_dataclass
import json
import logging
from pathlib import Path
import re
from typing import Type, TypeVar
from nemo_library.features.nemo_persistence_api import (
    _deserializeMetaDataObject,
    createApplications,
    createAttributeGroups,
    createAttributeLinks,
    createColumns,
    createDiagrams,
    createMetrics,
    createPages,
    createReports,
    createRules,
    createSubProcesses,
    createTiles,
    createVariances,
    deleteApplications,
    deleteAttributeGroups,
    deleteAttributeLinks,
    deleteColumns,
    deleteDiagrams,
    deleteMetrics,
    deletePages,
    deleteReports,
    deleteRules,
    deleteSubprocesses,
    deleteTiles,
    deleteVariances,
    getApplications,
    getAttributeGroups,
    getAttributeLinks,
    getColumns,
    getDiagrams,
    getMetrics,
    getPages,
    getRules,
    getSubProcesses,
    getTiles,
    getVariances,
)
from nemo_library.features.nemo_persistence_api import (
    getDependencyTree,
)
from nemo_library.features.nemo_persistence_api import (
    getReports,
)
from nemo_library.model.application import Application
from nemo_library.model.attribute_group import AttributeGroup
from nemo_library.model.attribute_link import AttributeLink
from nemo_library.model.column import Column
from nemo_library.model.dependency_tree import DependencyTree
from nemo_library.model.diagram import Diagram
from nemo_library.model.metric import Metric
from nemo_library.model.pages import Page
from nemo_library.model.report import Report
from nemo_library.model.rule import Rule
from nemo_library.model.tile import Tile
from nemo_library.model.subprocess import SubProcess
from nemo_library.model.variance import Variance
from nemo_library.utils.config import Config
from nemo_library.utils.utils import FilterType, FilterValue
import uuid

__all__ = [
    "MetaDataLoad",
    "MetaDataDelete",
    "MetaDataCreate",
    "MetaDataHelperUpdateLinkTexts",
    "MetaDataHelperCleanParentAttributeGroupInternalNames",
    "MetaDataHelperAutoResolveApplications",
]

T = TypeVar("T")


def MetaDataLoad(
    config: Config,
    projectname: str,
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
) -> None:

    functions = {
        "applications": getApplications,
        "attributegroups": getAttributeGroups,
        "attributelinks": getAttributeLinks,
        "columns": getColumns,
        "diagrams": getDiagrams,
        "metrics": getMetrics,
        "pages": getPages,
        "reports": getReports,
        "rules": getRules,
        "tiles": getTiles,
        "subprocesses": getSubProcesses,
        "variances": getVariances,
    }

    for name, func in functions.items():
        logging.info(f"load {name} from NEMO")
        data = func(
            config=config,
            projectname=projectname,
            filter=filter,
            filter_type=filter_type,
            filter_value=filter_value,
        )

        _export_data_to_json(config, name, data)


def MetaDataDelete(
    config: Config,
    projectname: str,
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
) -> None:

    get_functions = {
        "applications": getApplications,
        "attributegroups": getAttributeGroups,
        "attributelinks": getAttributeLinks,
        "columns": getColumns,
        "diagrams": getDiagrams,
        "metrics": getMetrics,
        "pages": getPages,
        "reports": getReports,
        "rules": getRules,
        "subprocesses": getSubProcesses,
        "tiles": getTiles,
        "variances": getVariances,
    }

    delete_functions = {
        "subprocesses": deleteSubprocesses,
        "applications": deleteApplications,
        "pages": deletePages,
        "diagrams": deleteDiagrams,
        "tiles": deleteTiles,
        "attributelinks": deleteAttributeLinks,
        "metrics": deleteMetrics,
        "columns": deleteColumns,
        "attributegroups": deleteAttributeGroups,
        "reports": deleteReports,
        "rules": deleteRules,
        "variances": deleteVariances,
    }

    for name, func in get_functions.items():
        logging.info(f"delete {name} from NEMO")
        data = func(
            config=config,
            projectname=projectname,
            filter=filter,
            filter_type=filter_type,
            filter_value=filter_value,
        )

        objects_to_delete = [obj.id for obj in data]

        delete_functions[name](config=config, **{name: objects_to_delete})


def MetaDataHelperUpdateLinkTexts(
    config: Config,
    projectname: str,
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
) -> None:
    logging.info(f"load model from NEMO project {projectname}")
    attributelinks = getAttributeLinks(
        config=config,
        projectname=projectname,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    columns = getColumns(config=config, projectname=projectname)

    for attributelink in attributelinks:
        for col in columns:
            if col.internalName == attributelink.sourceAttributeInternalName:
                attributelink.displayName = col.displayName
                attributelink.displayNameTranslations = col.displayNameTranslations
                if not "en" in attributelink.displayNameTranslations:
                    attributelink.displayNameTranslations["en"] = col.displayName
                break

    _export_data_to_json(config, "attributelinks", attributelinks)


def MetaDataCreate(
    config: Config,
    projectname: str,
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
) -> None:

    # load data from model (JSON)
    logging.info(
        f"load model from JSON files in folder {config.get_metadata_directory()}"
    )
    applications_model = _load_data_from_json(
        config,
        "applications",
        Application,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    attributegroups_model = _load_data_from_json(
        config,
        "attributegroups",
        AttributeGroup,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    # add a root node if not present
    if not any(ag.internalName == "optimate" for ag in attributegroups_model):
        attributegroups_model.append(
            AttributeGroup(
                internalName="optimate",
                displayName="OptiMate",
                displayNameTranslations={"de": "OptiMate", "en": "OptiMate"},
                parentAttributeGroupInternalName=None,
                order="00",
            )
        )
    attributelinks_model = _load_data_from_json(
        config,
        "attributelinks",
        AttributeLink,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    columns_model = _load_data_from_json(
        config,
        "columns",
        Column,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    diagrams_model = _load_data_from_json(
        config,
        "diagrams",
        Diagram,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    metrics_model = _load_data_from_json(
        config,
        "metrics",
        Metric,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    pages_model = _load_data_from_json(
        config,
        "pages",
        Page,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    reports_model = _load_data_from_json(
        config,
        "reports",
        Report,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    rules_model = _load_data_from_json(
        config,
        "rules",
        Rule,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    subprocesses_model = _load_data_from_json(
        config,
        "subprocesses",
        SubProcess,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    tiles_model = _load_data_from_json(
        config,
        "tiles",
        Tile,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    variances_model = _load_data_from_json(
        config,
        "variances",
        Variance,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )

    # sort attribute groups
    hierarchy, _ = _attribute_groups_build_hierarchy(attributegroups_model)
    attributegroups_model = attribute_groups_sort_hierarchy(hierarchy, root_key=None)

    # load data from NEMO
    logging.info(f"load model from NEMO files from project {projectname}")
    applications_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getApplications,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    attributegroups_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getAttributeGroups,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    attributelinks_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getAttributeLinks,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    columns_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getColumns,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    diagrams_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getDiagrams,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    metrics_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getMetrics,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    pages_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getPages,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    reports_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getReports,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    tiles_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getTiles,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    rules_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getRules,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    subprocesses_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getSubProcesses,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    variances_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getVariances,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )

    # reconcile data
    deletions: dict[str, list[T]] = {}
    updates: dict[str, list[T]] = {}
    creates: dict[str, list[T]] = {}

    logging.info(f"reconcile both models")
    for key, model_list, nemo_list in [
        ("applications", applications_model, applications_nemo),
        ("attributegroups", attributegroups_model, attributegroups_nemo),
        ("attributelinks", attributelinks_model, attributelinks_nemo),
        ("columns", columns_model, columns_nemo),
        ("diagrams", diagrams_model, diagrams_nemo),
        ("metrics", metrics_model, metrics_nemo),
        ("pages", pages_model, pages_nemo),
        ("reports", reports_model, reports_nemo),
        ("tiles", tiles_model, tiles_nemo),
        ("rules", rules_model, rules_nemo),
        ("subprocesses", subprocesses_model, subprocesses_nemo),
        ("variances", variances_model, variances_nemo),
    ]:
        nemo_list_cleaned = copy.deepcopy(nemo_list)
        nemo_list_cleaned = _clean_fields(nemo_list_cleaned)

        deletions[key] = _find_deletions(model_list, nemo_list)
        updates[key] = _find_updates(model_list, nemo_list_cleaned)
        creates[key] = _find_new_objects(model_list, nemo_list)

    # Start with deletions
    logging.info(f"start deletions")
    delete_functions = {
        "applications": deleteApplications,
        "pages": deletePages,
        "tiles": deleteTiles,
        "metrics": deleteMetrics,
        "columns": deleteColumns,
        "attributegroups": deleteAttributeGroups,
        "attributelinks": deleteAttributeLinks,
        "diagrams": deleteDiagrams,
        "rules": deleteRules,
        "reports": deleteReports,
        "subprocesses": deleteSubprocesses,
        "variances": deleteVariances,
    }

    for key, delete_function in delete_functions.items():
        if deletions[key]:
            objects_to_delete = [data_nemo.id for data_nemo in deletions[key]]
            delete_function(config=config, **{key: objects_to_delete})

    # Now do updates and creates in a reverse  order
    logging.info(f"start creates and updates")
    create_functions = {
        "attributegroups": createAttributeGroups,
        "reports": createReports,
        "rules": createRules,
        "columns": createColumns,
        "metrics": createMetrics,
        "attributelinks": createAttributeLinks,
        "tiles": createTiles,
        "diagrams": createDiagrams,
        "pages": createPages,
        "applications": createApplications,
        "subprocesses": createSubProcesses,
        "variances": createVariances,
    }

    for key, create_function in create_functions.items():
        # create new objects first
        if creates[key]:
            create_function(
                config=config, projectname=projectname, **{key: creates[key]}
            )
        # now the changes
        if updates[key]:
            create_function(
                config=config, projectname=projectname, **{key: updates[key]}
            )


def MetaDataHelperCleanParentAttributeGroupInternalNames(
    config: Config,
    projectname: str,
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
) -> None:
    metrics_model = _load_data_from_json(
        config,
        "metrics",
        Metric,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    for metric in metrics_model:
        metric.parentAttributeGroupInternalName = ""

    columns_model = _load_data_from_json(
        config,
        "columns",
        Column,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    for column in columns_model:
        column.parentAttributeGroupInternalName = ""
        column.order = ""

    attributelinks_model = _load_data_from_json(
        config,
        "attributelinks",
        AttributeLink,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    for attributelink in attributelinks_model:
        attributelink.parentAttributeGroupInternalName = ""
        attributelink.order = ""

    _export_data_to_json(config, "metrics", metrics_model)
    _export_data_to_json(config, "columns", columns_model)
    _export_data_to_json(config, "attributelinks", attributelinks_model)


def MetaDataHelperAutoResolveApplications(
    config: Config,
    projectname: str,
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
):
    """
    Build the attribute groups model by combining the models of applications, pages,
    diagrams, metrics, and defined columns.

    ASSUMPTION: model and NEMO are in sync (no deletions or updates)
    """

    logging.info(
        f"load model from JSON files in folder {config.get_metadata_directory()}"
    )
    attributegroups_model = _load_data_from_json(
        config,
        "attributegroups",
        AttributeGroup,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    applications_model = _load_data_from_json(
        config,
        "applications",
        Application,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    pages_model = _load_data_from_json(
        config,
        "pages",
        Page,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    metrics_model = _load_data_from_json(
        config,
        "metrics",
        Metric,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    columns_model = _load_data_from_json(
        config,
        "columns",
        Column,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    diagrams_model = _load_data_from_json(
        config,
        "diagrams",
        Diagram,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    attributelinks_model = _load_data_from_json(
        config,
        "attributelinks",
        AttributeLink,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    attribute_groups_metrics = defaultdict(set)

    # build attribute groups tree first
    logging.info(f"build attribute groups tree")

    def addAttributeGroup(new_group: AttributeGroup):
        if not any(
            group.internalName == new_group.internalName
            for group in attributegroups_model
        ):
            attributegroups_model.append(new_group)

    # start with root node
    root = None
    for ag in attributegroups_model:
        if ag.internalName == "optimate":
            root = ag
            break
    if not root:
        root = AttributeGroup(
            internalName="optimate",
            displayName="OptiMate",
            displayNameTranslations={"de": "OptiMate", "en": "OptiMate"},
            parentAttributeGroupInternalName=None,
            order="00",
        )
        addAttributeGroup(root)

    # add a group for each application
    for app in applications_model:
        addAttributeGroup(
            AttributeGroup(
                internalName=f"{app.internalName}_attribute_group",
                displayName=app.displayName,
                displayNameTranslations=app.displayNameTranslations,
                parentAttributeGroupInternalName="optimate",
            )
        )

        # add a group for each page
        for page in app.pages:

            page_ref = None
            for page_search in pages_model:
                if page_search.internalName == page.page:
                    page_ref = page_search
                    break
            if page_ref:
                addAttributeGroup(
                    AttributeGroup(
                        internalName=f"{page_ref.internalName}_attribute_group",
                        displayName=page_ref.displayName,
                        displayNameTranslations=page_ref.displayNameTranslations,
                        parentAttributeGroupInternalName=f"{app.internalName}_attribute_group",
                    )
                )

                # add a group for each diagram
                for visual in page_ref.visuals:
                    if visual.type == "Diagram":
                        diagram_ref = None
                        for diagram_search in diagrams_model:
                            if diagram_search.internalName == visual.content:
                                diagram_ref = diagram_search
                                break
                        if diagram_ref:
                            addAttributeGroup(
                                AttributeGroup(
                                    internalName=f"{diagram_ref.internalName}_attribute_group",
                                    displayName=diagram_ref.displayName,
                                    displayNameTranslations=diagram_ref.displayNameTranslations,
                                    parentAttributeGroupInternalName=f"{page_ref.internalName}_attribute_group",
                                )
                            )
                            for value in diagram_ref.values:
                                attribute_groups_metrics[
                                    f"{diagram_ref.internalName}_attribute_group"
                                ].add(value.column)
                    elif visual.type == "Metric":
                        attribute_groups_metrics[
                            f"{page_ref.internalName}_attribute_group"
                        ].add(visual.content)

    # we have the attribute groups - let's bring them into order
    def assignOrder(parent: AttributeGroup):
        index = 0
        for attribute_group in attributegroups_model:
            if attribute_group.parentAttributeGroupInternalName == parent.internalName:
                attribute_group.order = f"{index:02}"
                index += 1
                assignOrder(attribute_group)

    assignOrder(root)

    # now we move metrics into the groups
    attribute_groups_metrics = {k: list(v) for k, v in attribute_groups_metrics.items()}

    # build reverse lookup: metric → list of attribute groups
    metric_to_groups = defaultdict(list)
    for group, metrics in attribute_groups_metrics.items():
        for metric in metrics:
            metric_to_groups[metric].append(group)

    # clean up duplicates by removing 'overview' if present among duplicates
    for metric, groups in list(metric_to_groups.items()):
        if len(groups) > 1:
            if any("overview" in group for group in groups):
                new_groups = [g for g in groups if "overview" not in g]
                if new_groups:
                    logging.info(
                        f"Removed 'overview' group for metric '{metric}', kept: {new_groups}"
                    )
                    metric_to_groups[metric] = new_groups
                    # also update attribute_groups_metrics accordingly
                    for group in groups:
                        if (
                            "overview" in group
                            and metric in attribute_groups_metrics[group]
                        ):
                            attribute_groups_metrics[group].remove(metric)

    # log remaining duplicates
    for metric, groups in metric_to_groups.items():
        if len(groups) > 1:
            logging.warning(
                f"Metric '{metric}' appears in multiple attribute groups: {groups}"
            )

    # move metrics to the right attribute group
    logging.info(f"move metrics to the right attribute group")
    for metric in metrics_model:
        # find metric in attribute groups
        attribute_group = None
        for key, value in attribute_groups_metrics.items():
            if metric.internalName in value:
                attribute_group = key
                break
        if (
            attribute_group
            and metric.parentAttributeGroupInternalName != attribute_group
        ):
            logging.info(
                f"move metric {metric.internalName} from {metric.parentAttributeGroupInternalName} to {attribute_group}"
            )
            # move metric to the right attribute group
            metric.parentAttributeGroupInternalName = attribute_group

    # now we use the dependency tree to find the right attribute group for the defined and exported columns
    # load metrics from NEMO to get the id of them. This is needed to get the dependency tree
    logging.info(f"get dependency tree for metrics")
    metrics_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getMetrics,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )
    dependency_tree = {
        metric.internalName: _collect_node_objects(d)
        for metric in metrics_nemo
        if (d := getDependencyTree(config=config, id=metric.id)) is not None
    }
    importedcolumns_nemo = _fetch_data_from_nemo(
        config=config,
        projectname=projectname,
        func=getColumns,
        filter="*",
        filter_type=filter_type,
        filter_value=filter_value,
    )

    # move defined columns to the right attribute group and create attribute links for the imported columns
    logging.info(f"move defined columns to the right attribute group")

    def addAttributeLink(new_link: AttributeLink):
        if not any(
            link.parentAttributeGroupInternalName
            == new_link.parentAttributeGroupInternalName
            and link.sourceAttributeInternalName == new_link.sourceAttributeInternalName
            for link in attributelinks_model
        ):
            attributelinks_model.append(new_link)

    for metric_internal_name, values in dependency_tree.items():

        # find metric in model
        metric = None
        for metric_search in metrics_model:
            if metric_search.internalName == metric_internal_name:
                metric = metric_search
                break
        if not metric:
            logging.error(f"metric {metric_internal_name} not found in model")
            continue

        # move defined columns to the right attribute group
        for element in values:
            if element.nodeType == "DefinedColumn":
                # find defined column in model
                defined_column = None
                for defined_column_search in columns_model:
                    if defined_column_search.internalName == element.nodeInternalName:
                        defined_column = defined_column_search
                        break
                if not defined_column:
                    logging.error(
                        f"defined column {element.nodeInternalName} not found in model"
                    )
                    continue

                defined_column.parentAttributeGroupInternalName = (
                    metric.parentAttributeGroupInternalName
                )
            elif element.nodeType == "ExportedColumn":
                # find exported column in model
                imported_column = None
                for imported_column_search in importedcolumns_nemo:
                    if imported_column_search.internalName == element.nodeInternalName:
                        imported_column = imported_column_search
                        break
                if not imported_column:
                    logging.error(
                        f"exported column {element.nodeInternalName} not found in model"
                    )
                    continue
                app = metric.parentAttributeGroupInternalName.split("_")[1]
                addAttributeLink(
                    AttributeLink(
                        sourceAttributeInternalName=imported_column.internalName,
                        parentAttributeGroupInternalName=metric.parentAttributeGroupInternalName,
                        displayNameTranslations={
                            "de": imported_column.displayNameTranslations.get("de", ""),
                            "en": imported_column.displayNameTranslations.get(
                                "en", imported_column.displayName
                            ),
                        },
                        displayName=imported_column.displayName,
                        internalName=f"{root.internalName}_{app}_{imported_column.internalName}_{uuid.uuid4()}".replace(
                            "-", "_"
                        ),
                        sourceMetadataType="column",
                    )
                )

    # export the data to JSON finally
    export = {
        "attributegroups": attributegroups_model,
        "attributelinks": attributelinks_model,
        "metrics": metrics_model,
        "columns": columns_model,
    }
    for name, data in export.items():
        _export_data_to_json(config, name, data)


def _collect_node_objects(tree: DependencyTree) -> list[str]:
    elements = [tree]
    for dep in tree.dependencies:
        elements.extend(_collect_node_objects(dep))
    return elements


def _fetch_data_from_nemo(
    config: Config,
    projectname: str,
    func,
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
):
    return func(
        config=config,
        projectname=projectname,
        filter=filter,
        filter_type=filter_type,
        filter_value=filter_value,
    )


def _load_data_from_json(
    config : Config,
    file: str,
    cls: Type[T],
    filter: str = "*",
    filter_type: FilterType = FilterType.STARTSWITH,
    filter_value: FilterValue = FilterValue.DISPLAYNAME,
) -> list[T]:
    """
    Loads JSON data from a file and converts it into a list of DataClass instances,
    handling nested structures recursively.
    """
    path = Path(config.get_metadata_directory()) / f"{file}.json"
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def match_filter(value: str, filter: str, filter_type: FilterType) -> bool:
        """Applies the given filter to the value."""
        if filter == "*":
            return True
        elif filter_type == FilterType.EQUAL:
            return value == filter
        elif filter_type == FilterType.STARTSWITH:
            return value.startswith(filter)
        elif filter_type == FilterType.ENDSWITH:
            return value.endswith(filter)
        elif filter_type == FilterType.CONTAINS:
            return filter in value
        elif filter_type == FilterType.REGEX:
            return re.search(filter, value) is not None
        return False

    # Apply filter to the data
    filtered_data = [
        item
        for item in data
        if match_filter(item.get(filter_value.value, ""), filter, filter_type)
    ]

    return [_deserializeMetaDataObject(item, cls) for item in filtered_data]


def _find_deletions(model_list: list[T], nemo_list: list[T]) -> list[T]:
    model_keys = {obj.internalName for obj in model_list}
    return [obj for obj in nemo_list if obj.internalName not in model_keys]


def _find_updates(model_list: list[T], nemo_list: list[T]) -> list[T]:
    updates = []
    nemo_dict = {getattr(obj, "internalName"): obj for obj in nemo_list}
    for model_obj in model_list:
        key = getattr(model_obj, "internalName")
        if key in nemo_dict:
            nemo_obj = nemo_dict[key]
            if is_dataclass(model_obj) and is_dataclass(nemo_obj):
                differences = {
                    attr.name: (
                        getattr(model_obj, attr.name),
                        getattr(nemo_obj, attr.name),
                    )
                    for attr in fields(model_obj)
                    if getattr(model_obj, attr.name) != getattr(nemo_obj, attr.name)
                }

            if differences:
                for attrname, (new_value, old_value) in differences.items():
                    logging.info(f"{attrname}: {old_value} --> {new_value}")
                updates.append(model_obj)

    return updates


def _find_new_objects(model_list: list[T], nemo_list: list[T]) -> list[T]:
    nemo_keys = {getattr(obj, "internalName") for obj in nemo_list}
    return [obj for obj in model_list if getattr(obj, "internalName") not in nemo_keys]


def _export_data_to_json(config: Config, file: str, data):
    data = _clean_fields(data)
    if data:

        path = Path(config.get_metadata_directory()) / f"{file}.json"
        
        # Create the output directory if it does not exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                [element.to_dict() for element in data],
                file,
                indent=4,
                ensure_ascii=True,
            )


def _clean_fields(data):
    for element in data:
        element.id = ""
        element.tenant = ""
        element.projectId = ""
        element.tileSourceID = ""

        if isinstance(element, Diagram):
            for value in element.values:
                value.id = ""

        elif isinstance(element, Page):
            for visual in element.visuals:
                visual.id = ""

    return data


def _attribute_groups_build_hierarchy(attribute_groups):
    hierarchy = defaultdict(list)
    group_dict = {group.internalName: group for group in attribute_groups}

    for group in attribute_groups:
        parent_name = group.parentAttributeGroupInternalName
        hierarchy[parent_name].append(group)

    return hierarchy, group_dict


def attribute_groups_sort_hierarchy(hierarchy, root_key=None):
    sorted_list = []

    def add_children(parent):
        for child in sorted(hierarchy.get(parent, []), key=lambda x: x.displayName):
            sorted_list.append(child)
            add_children(child.internalName)

    add_children(root_key)
    return sorted_list
