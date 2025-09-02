from pathlib import Path
from tests.testutils import getNL

PROJECT_NAME = "gs-unit-test-fox"

def test_load_fox_file():
    nl = getNL()
    id = nl.getProjectID(PROJECT_NAME)
    if id:
        nl.deleteProjects([id])
    nl.ReUploadFile(
        projectname=PROJECT_NAME,
        filename="./tests/GuetzowWetter2000.fox",
        update_project_settings=False,
    )

def test_clean():
    nl = getNL()
    id = nl.getProjectID(PROJECT_NAME)
    if id:
        nl.deleteProjects([id])
    assert True  # Ensure the test passes after cleanup