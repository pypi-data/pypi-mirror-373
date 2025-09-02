from nemo_library.model.column import Column
from nemo_library.model.project import Project
from tests.testutils import getNL

HS_PROJECT_NAME = "gs_unit_test_HubSpot"


def test_FetchDealFromHubSpotAndUploadToNEMO():
    nl = getNL()

    # check if project exists (should not)
    project_id = nl.getProjectID(HS_PROJECT_NAME)
    if project_id:
        nl.deleteProjects([project_id])

    nl.createProjects(
        [Project(displayName=HS_PROJECT_NAME, description="project for unit tests")]
    )
    new_columns = []
    new_columns.append(
        Column(displayName="deal_id", dataType="float", columnType="ExportedColumn")
    )
    new_columns.append(
        Column(
            displayName="update_closedate_new_value",
            dataType="date",
            columnType="ExportedColumn",
        )
    )
    nl.createColumns(
        projectname=HS_PROJECT_NAME,
        columns=new_columns,
    )
    nl.setProjectMetaData(
        projectname=HS_PROJECT_NAME,
        processid_column="deal_id",
        processdate_column="update_closedate_new_value",
        corpcurr_value="EUR",
    )
    nl.FetchDealFromHubSpotAndUploadToNEMO(HS_PROJECT_NAME)
    nl.deleteProjects([nl.getProjectID(HS_PROJECT_NAME)])
    assert True
