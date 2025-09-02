from nemo_library import NemoLibrary


def getNL():
    return NemoLibrary(
        config_file="tests/config.ini",
        environment="challenge",
        tenant="pte",
        userid="schug_g_pte_customeradmin",
        password="vdcGz9CT3rX8uwhsLSdxGiDp5naP6kUF",
        migman_local_project_directory="./tests/migman/",
        migman_projects=["Customers", "Ship-To Addresses (Customers)"],
        migman_mapping_fields=["S_Kunde.Kunde"],
        migman_additional_fields={},
        migman_multi_projects={},
        metadata_directory="metadata_optimate",
    )
