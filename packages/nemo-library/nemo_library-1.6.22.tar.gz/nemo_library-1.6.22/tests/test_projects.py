from datetime import datetime
import pytest
import pandas as pd

from nemo_library.model.column import Column
from nemo_library.model.project import Project
from nemo_library.model.report import Report
from tests.testutils import getNL

IC_PROJECT_NAME = "gs_unit_test_Intercompany"

REPORT_COLUMNS = [
    "Company",
    "CUSTOMER_I_D",
    "CUSTOMER_NAME",
    "FirstInvoiceDate",
    "AnnualContractValue",
]


def test_getProjecs():
    nl = getNL()
    projects = nl.getProjects()
    assert len(projects) > 0
    first_project = projects[0]
    assert first_project.id == "00000000-0000-0000-0000-000000000001"


def test_getProjectID():
    nl = getNL()
    assert (
        nl.getProjectID("Business Processes") == "00000000-0000-0000-0000-000000000001"
    )


def test_getProjectProperty():
    nl = getNL()
    val = nl.getProjectProperty(
        projectname="Business Processes", propertyname="ExpDateFrom"
    )

    assert val is not None, "API call did not return any value"

    try:
        date_val = datetime.strptime(val, "%Y-%m-%d")
    except ValueError:
        pytest.fail(f"Returned value ({val}) is not in the format YYYY-MM-DD")

    assert (
        2000 <= date_val.year <= 2100
    ), "Year is out of the acceptable range (2000-2100)"


def test_createProject():
    nl = getNL()

    # check if project exists (should not)
    projectid = nl.getProjectID(IC_PROJECT_NAME)
    if projectid:
        nl.deleteProjects([projectid])

    # now we can create the project
    nl.createProjects(
        [
            Project(
                displayName=IC_PROJECT_NAME,
                description="used for unit tests of nemo_library",
            )
        ]
    )

    projectid = nl.getProjectID(IC_PROJECT_NAME)
    assert projectid is not None


def test_createImportedColumn():
    nl = getNL()
    nl.createColumns(
        projectname=IC_PROJECT_NAME,
        columns=[
            Column(
                displayName="Rechnungsdatum",
                dataType="date",
                columnType="ExportedColumn",
            )
        ],
    )
    importedColumns = nl.getColumns(IC_PROJECT_NAME)
    assert "Rechnungsdatum" in [ic.displayName for ic in importedColumns]


def test_getColumns():
    nl = getNL()
    ic = nl.getColumns(IC_PROJECT_NAME)
    assert (
        len(ic) == 1
    )  # we have checked the behavior in test_createImportedColumn already...


def test_synchronizeCsvColsAndImportedColumns():
    nl = getNL()
    nl.synchronizeCsvColsAndImportedColumns(
        projectname=IC_PROJECT_NAME,
        filename="./tests/intercompany_NEMO.csv",
    )

    importedColumns = nl.getColumns(IC_PROJECT_NAME)
    assert len(importedColumns) == 21


def test_setProjectMetaData():
    nl = getNL()
    nl.setProjectMetaData(
        IC_PROJECT_NAME,
        processid_column="seriennummer",
        processdate_column="rechnungsdatum",
        corpcurr_value="EUR",
    )
    assert True


def test_ReUploadDataFrame():
    nl = getNL()
    df = pd.read_csv("./tests/intercompany_NEMO.csv", sep=";")
    nl.ReUploadDataFrame(
        projectname=IC_PROJECT_NAME, df=df, update_project_settings=False
    )
    assert True


def test_ReUploadFile():
    nl = getNL()

    nl.ReUploadFile(
        projectname=IC_PROJECT_NAME,
        filename="./tests/intercompany_NEMO.csv",
        update_project_settings=False,
    )

    assert True


def test_focusMoveAttributeBefore():
    nl = getNL()
    nl.focusMoveAttributeBefore(IC_PROJECT_NAME, "Mandant", None)
    assert True


def test_createReports():
    nl = getNL()
    select = f"""WITH Params AS (
    SELECT ADD_MONTHS(
               TO_DATE(CONCAT(YEAR(CURRENT_DATE), '-01-01'), 'YYYY-MM-DD'),
               (FLOOR((MONTH(CURRENT_DATE) - 1) / 3) - 2) * 3
           ) AS ReportStartDate
    FROM DUMMY
),
Invoices AS (
    SELECT
        MANDANT      AS Company,
        ENDKUNDE     AS CUSTOMER_I_D,
        LIZENZNEHMER AS CUSTOMER_NAME,
        Rechnungsdatum AS InvoiceDocDate,
        to_decimal(preis_mit_rabatt) AS InvoiceAmount
    FROM 
        $schema.$table
    WHERE 
        ABRECHNUNGSART = 'SaaS/Cloud'
),
FilteredInvoices AS (
    SELECT
        i1.*
    FROM 
        Invoices i1
    LEFT JOIN 
        Invoices i2 ON i1.CUSTOMER_I_D = i2.CUSTOMER_I_D 
                        AND i1.Company = i2.Company 
                        AND i2.InvoiceDocDate < (SELECT ReportStartDate FROM Params)
    WHERE 
        i2.CUSTOMER_I_D IS NULL 
),
CustomerPayments AS (
    SELECT
        Company,
        CUSTOMER_I_D,
        CUSTOMER_NAME,
        COUNT(DISTINCT InvoiceDocDate) AS NumberOfPayments,
        SUM(InvoiceAmount) AS TotalRevenue,
        MIN(InvoiceDocDate) AS FirstInvoiceDate
    FROM
        FilteredInvoices
    GROUP BY
        Company,
        CUSTOMER_I_D,
        CUSTOMER_NAME
),
CustomerACV AS (
    SELECT
        Company,
        CUSTOMER_I_D,
        CUSTOMER_NAME,
        TotalRevenue,
        NumberOfPayments,
        FirstInvoiceDate,
        (TotalRevenue / NumberOfPayments) * 12 AS AnnualContractValue
    FROM
        CustomerPayments
)
SELECT 
    {"\n\t,".join(REPORT_COLUMNS)}
FROM 
    CustomerACV
"""
    nl.createReports(
        projectname=IC_PROJECT_NAME,
        reports=[
            Report(
                displayName="(BI DATA) 21 NNN Reporting SaaS IC",
                querySyntax=select,
                internalName="bi_data_21_nnn_reporting_saas_ic",
                description="unit test",
                columns=REPORT_COLUMNS,
            )
        ],
    )


def test_LoadReport():
    nl = getNL()
    df = nl.LoadReport(
        projectname=IC_PROJECT_NAME,
        report_name="(BI DATA) 21 NNN Reporting SaaS IC",
    )

    columns_lower = {c.lower() for c in df.columns}
    assert all(col.lower() in columns_lower for col in REPORT_COLUMNS)

    assert len(df) == 22


def test_deleteProject():
    nl = getNL()
    prjid = nl.getProjectID(IC_PROJECT_NAME)
    if prjid is None:
        pytest.skip(f"Project {IC_PROJECT_NAME} does not exist, skipping deletion test.")
    nl.deleteProjects([prjid])
    prjid = nl.getProjectID(IC_PROJECT_NAME)
    assert prjid == None
