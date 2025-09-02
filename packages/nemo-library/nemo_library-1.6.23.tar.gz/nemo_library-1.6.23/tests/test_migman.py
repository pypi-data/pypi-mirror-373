import shutil
import pandas as pd

from pathlib import Path
from tests.testutils import getNL


def test_clean():
    nl = getNL()
    nl.MigManDeleteProjects()
    test_dir = Path(nl.config.get_migman_local_project_directory())
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_MigManCreateProjectTemplates():
    nl = getNL()
    test_dir = Path(nl.config.get_migman_local_project_directory())
    if test_dir.exists():
        shutil.rmtree(test_dir)

    assert not test_dir.exists()

    nl.MigManCreateProjectTemplates()

    assert test_dir.exists()
    assert (test_dir / "templates").exists()
    for project in nl.config.get_migman_projects():
        assert (test_dir / "templates" / f"{project}.csv").exists()


def test_MigManPrecheckFiles():
    nl = getNL()
    srcdata_dir = Path(nl.config.get_migman_local_project_directory()) / "srcdata"
    assert srcdata_dir.exists()

    migmanprojects = nl.config.get_migman_projects()
    for project in migmanprojects:
        shutil.copy(
            Path(f"./tests/migman_master/{project}.csv"),
            srcdata_dir / f"{project}.csv",
        )
    precheckstatus = nl.MigManPrecheckFiles()
    assert all(status == "ok" for status in precheckstatus.values())


def test_MigManLoadData():
    nl = getNL()

    srcdata_dir = Path(nl.config.get_migman_local_project_directory()) / "srcdata"
    assert srcdata_dir.exists()

    migmanprojects = nl.config.get_migman_projects()
    for project in migmanprojects:
        shutil.copy(
            Path(f"./tests/migman_master/{project}.csv"),
            srcdata_dir / f"{project}.csv",
        )

    nl.MigManLoadData(fuzzy_matching=False) # for performance reasons, we skip fuzzy matching in tests

    nemo_projects = [project.displayName for project in nl.getProjects()]
    migmanprojects = nl.config.get_migman_projects()

    assert all(project in nemo_projects for project in migmanprojects)

    for project in migmanprojects:
        ic = nl.getColumns(projectname=project)
        ic = [
            x
            for x in ic
            if not x.internalName
            in [
                "datasource_id",
                "timestamp_file",
                "nemo_lib_version",
                "duplicate_check",
                "fuzzy_match_partner",
                "fuzzy_match_score",
                "duplicate_group_key",
                "is_potential_duplicate",
            ]
        ]
        df = pd.read_csv(
            srcdata_dir / f"{project}.csv",
            sep=";",
            dtype=str,
        )
        columns_to_drop = df.columns[df.isna().all()]
        datadf_cleaned = df.drop(columns=columns_to_drop)

        assert len(datadf_cleaned.columns) == len(ic)


def test_MigManCreateMapping():
    nl = getNL()

    mapping_dir = Path(nl.config.get_migman_local_project_directory()) / "mappings"
    assert mapping_dir.exists()

    nl.MigManCreateMapping()

    mappings = nl.config.get_migman_mapping_fields()
    for mapping in mappings:
        assert (mapping_dir / f"Mapping {mapping}.csv").exists()


def test_MigManLoadMapping():
    nl = getNL()
    mapping_dir = Path(nl.config.get_migman_local_project_directory()) / "mappings"
    assert mapping_dir.exists()
    mappings = nl.config.get_migman_mapping_fields()
    for mapping in mappings:
        assert (mapping_dir / f"Mapping {mapping}.csv").exists()

        shutil.copy(
            Path(f"./tests/migman_master/Mapping {mapping}.csv"),
            mapping_dir / f"Mapping {mapping}.csv",
        )

    # nl.MigManLoadMapping()

    for mapping in mappings:
        assert (mapping_dir / f"Mapping {mapping}.csv").exists()

        df = pd.read_csv(
            mapping_dir / f"Mapping {mapping}.csv",
            sep=";",
            dtype=str,
        )

        target_column = f"target {mapping}"
        assert target_column in df.columns
        assert df[target_column].notna().any()


def test_MigManApplyMapping():
    nl = getNL()
    nl.MigManApplyMapping()


def test_MigManExportData():
    nl = getNL()
    nl.MigManExportData()

    migmanprojects = nl.config.get_migman_projects()
    for directory in ["to_customer", "to_proalpha"]:
        assert (
            Path(nl.config.get_migman_local_project_directory()) / directory
        ).exists()

        for project in migmanprojects:
            assert (
                Path(nl.config.get_migman_local_project_directory())
                / directory
                / (
                    f"{project}.csv"
                    if directory == "to_proalpha"
                    else f"{project}_with_messages.csv"
                )
            ).exists()


def test_final():
    nl = getNL()
    nl.MigManDeleteProjects()
    test_dir = Path(nl.config.get_migman_local_project_directory())
    if test_dir.exists():
        shutil.rmtree(test_dir)
