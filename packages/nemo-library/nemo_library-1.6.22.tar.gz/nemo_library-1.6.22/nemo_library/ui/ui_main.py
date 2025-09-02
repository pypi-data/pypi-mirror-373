from io import StringIO
import json
from pathlib import Path
import threading
import time
import requests
import streamlit as st
from nemo_library.ui.ui_config_ import UIConfig
from nemo_library.utils.utils import FilterType, FilterValue
from nemo_library.version import __version__
from packaging import version

import logging
import pandas as pd
from logging import StreamHandler, getLogger

import streamlit as st

# Initialize logger
app_logger = getLogger()

# Only add StreamHandler if none is already added
if not any(isinstance(h, StreamHandler) for h in app_logger.handlers):
    stream_handler = StreamHandler()
    app_logger.addHandler(stream_handler)
    app_logger.setLevel(logging.INFO)
    app_logger.info("streamlit UI started")

# === Init Config ===
config = UIConfig()
nl = config.getNL()

# Set page configuration
st.set_page_config(page_title="Nemo Library UI", layout="wide")

# format buttons to look like links
st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: transparent;
        color: #007acc;
        border: none;
        padding: 0;
        text-align: left;
    }
    div.stButton > button:hover {
        text-decoration: underline;
        color: #005f99;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- Helper: Fetch latest version from PyPI ---
def get_remote_version() -> str:
    try:
        response = requests.get("https://pypi.org/pypi/nemo_library/json", timeout=5)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except Exception as e:
        st.warning(f"Version check failed: {e}")
        return "not available"


# --- Read query parameters for navigation ---
params = st.query_params
page = params.get("page", "home")
action = params.get("action", None)


def sidebar():
    st.sidebar.title("🧠 NEMO UI")

    with st.sidebar:
        st.markdown("### Navigation")
        if st.button("➡️ MigMan", key="MigMan"):
            st.session_state["page"] = "MigMan"
        if st.button("📁 Projects", key="Projects"):
            st.session_state["page"] = "Projects"
        if st.button("🔣 Metadata", key="MetaData"):
            st.session_state["page"] = "MetaData"
        if st.button("⚙️ Settings", key="settings"):
            st.session_state["page"] = "settings"

    with st.sidebar:
        st.divider()
        if config.current_profile:
            st.markdown(
                f"#### Active Profile: {config.current_profile.profile_name} ({config.current_profile.profile_description})"
            )
            st.markdown(f"#### Environment: {config.current_profile.environment}")
            st.markdown(f"#### Tenant: {config.current_profile.tenant}")
            st.markdown(f"#### User ID: {config.current_profile.userid}")
        else:
            st.markdown("### No Active Profile. Please select one from Settings.")
        st.divider()
        st.markdown(f"#### Version (local): {__version__}")
        st.markdown(f"#### Version (server): {get_remote_version()}")
        if version.parse(__version__) < version.parse(get_remote_version()):
            st.warning(
                "A newer version of nemo_library is available. Please update to the latest version."
            )


class StreamlitLogHandler(logging.Handler):
    def __init__(self, buffer, placeholder):
        super().__init__()
        self.buffer = buffer
        self.placeholder = placeholder

    def emit(self, record):
        msg = self.format(record)
        self.buffer.write(msg + "\n")
        self.placeholder.text(self.buffer.getvalue())


def migman_button(col, label, icon, method, success_message, spinner_message):
    with col:
        if st.button(label, key=label, icon=icon):
            with st.spinner(spinner_message):
                try:
                    method()
                    st.toast(success_message, icon="✅")
                except Exception as e:
                    st.toast(f"An error occurred: {str(e)}", icon="❌")


def show_migman():
    """
    Displays the Migration Manager page with project overview.
    """
    st.header(f"Migration Manager")

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    migman_button(
        col1,
        label="Delete Projects",
        icon="🗑️",
        method=nl.MigManDeleteProjects,
        success_message="Projects deleted successfully.",
        spinner_message="Deleting projects... please wait.",
    )

    migman_button(
        col2,
        label="Create Templates",
        icon="🧱",
        method=nl.MigManCreateProjectTemplates,
        success_message="Project templates successfully created.",
        spinner_message="Create project templates... please wait.",
    )

    migman_button(
        col3,
        label="LoadData",
        icon="📥",
        method=nl.MigManLoadData,
        success_message="Data successfully loaded.",
        spinner_message="Load data... please wait.",
    )
    migman_button(
        col4,
        label="Create Mapping",
        icon="🔗",
        method=nl.MigManCreateMapping,
        success_message="Mapping successfully created.",
        spinner_message="Create Mappping... please wait.",
    )
    migman_button(
        col5,
        label="Load Mapping",
        icon="📂",
        method=nl.MigManLoadMapping,
        success_message="Mapping successfully loaded.",
        spinner_message="Load Mappping... please wait.",
    )
    migman_button(
        col6,
        label="Apply Mapping",
        icon="🔄",
        method=nl.MigManApplyMapping,
        success_message="Mapping successfully applied.",
        spinner_message="Apply Mappping... please wait.",
    )
    migman_button(
        col7,
        label="Export Data",
        icon="📤",
        method=nl.MigManExportData,
        success_message="Data successfully exported.",
        spinner_message="Export Data... please wait.",
    )

    col_all, _ = st.columns([1, 6])

    with col_all:
        if st.button("🚀 ALL", key="ALL"):
            with st.spinner("Running full migration workflow..."):
                try:
                    nl.MigManDeleteProjects()
                    st.toast("Projects deleted successfully.", icon="✅")
                    nl.MigManCreateProjectTemplates()
                    st.toast("Project templates successfully created.", icon="✅")
                    nl.MigManLoadData()
                    st.toast("Data successfully loaded.", icon="✅")
                    nl.MigManCreateMapping()
                    st.toast("Mapping successfully created.", icon="✅")
                    nl.MigManLoadMapping()
                    st.toast("Mapping successfully loaded.", icon="✅")
                    nl.MigManApplyMapping()
                    st.toast("Mapping successfully applied.", icon="✅")
                    nl.MigManExportData()
                    st.toast("Data successfully exported.", icon="✅")
                    st.toast(
                        "Full migration workflow completed successfully.", icon="✅"
                    )
                except Exception as e:
                    st.toast(f"An error occurred: {str(e)}", icon="❌")

    with st.spinner("Running precheck... please wait."):
        migmanstatus = nl.MigManPrecheckFiles()

    if migmanstatus:
        nemo_projects = nl.getProjects()
        data = {"project": [], "status_file": [], "status_nemo": []}
        for project, status in migmanstatus.items():
            data["project"].append(project)
            data["status_file"].append(status)
            data["status_nemo"].append(
                "ok"
                if any(
                    nemo_project.displayName == project
                    for nemo_project in nemo_projects
                )
                else "not found"
            )
        df = pd.DataFrame(data)

        def highlight_errors(row):
            styles = []
            for col in row.index:
                if col == "status_file":
                    if row[col] == "ok":
                        styles.append("")
                    elif row[col].startswith("Warning!"):
                        styles.append("background-color: orange; color: black")
                    else:
                        styles.append("background-color: red; color: black")
                elif col == "status_nemo":
                    if row[col] == "ok":
                        styles.append("")
                    else:
                        styles.append("background-color: orange; color: black")
                else:
                    styles.append("")
            return styles

        styled_df = df.style.apply(highlight_errors, axis=1)
        st.dataframe(
            styled_df,
            use_container_width=True,
            column_config={
                "project": st.column_config.TextColumn(
                    label="Project",
                    width="small",  # Optionen: "small", "medium", "large"
                ),
                "status_file": st.column_config.TextColumn(
                    label="Status (file)", width="medium"
                ),
                "status_nemo": st.column_config.TextColumn(
                    label="Status (nemo)", width="small"
                ),
            },
        )
    else:
        st.write("No projects found in Migration Manager.")


def show_projects():
    """
    Displays the Projects page with a list of projects.
    """
    st.header("Projects Overview")
    projects = nl.getProjects()
    if projects:
        data = [project.to_dict() for project in projects]
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No projects found.")


def meta_button(
    col,
    label,
    icon,
    method,
    selected_project,
    filter_text,
    filter_type,
    filter_value,
    success_message,
    spinner_message,
):
    with col:
        if st.button(label, key=label, icon=icon):
            with st.spinner(spinner_message):
                try:
                    method(
                        projectname=selected_project,
                        filter=filter_text,
                        filter_type=filter_type,
                        filter_value=filter_value,
                    )
                    st.toast(success_message, icon="✅")
                    st.rerun()
                except Exception as e:
                    st.toast(f"An error occurred: {str(e)}", icon="❌")


def show_metadata():
    """
    Displays the Metadata page with a list of metadata items.
    """
    st.header("Metadata")
    path = Path(config.current_profile.metadata)
    if not path.exists():
        st.error(f"Metadata directory '{path}' does not exist. Please check 'Metadata Folder' in settings.")
        return

    with st.spinner("collecting information..."):
        projects = nl.getProjects()
        projectnames = [project.displayName for project in projects]
        if projectnames:
            selected_project = st.selectbox("Select a project", projectnames, index=0)
            filter_text = st.text_input("Filter", value="optimate_sales")
            filtertypes = FilterType.__members__.values()
            filter_type = st.selectbox("Select filter type", filtertypes, index=0)
            filtervalues = FilterValue.__members__.values()
            filter_value = st.selectbox("Select filter value", filtervalues, index=0)
            # display json files in the metadata directory
            metadata_files = list(path.glob("*.json"))
            metadata_files = [
                file
                for file in metadata_files
                if file.name
                in [
                    "applications.json",
                    "attributegroups.json",
                    "attributelinks.json",
                    "columns.json",
                    "diagrams.json",
                    "metrics.json",
                    "pages.json",
                    "reports.json",
                    "rules.json",
                    "subprocesses.json",
                    "tiles.json",
                ]
            ]
            if metadata_files:
                st.write(f"### Metadata files found in directory '{path.absolute()}':")
                data = {
                    "File Name": [],
                    "Size (KB)": [],
                    "Last Modified": [],
                    "Number of Records": [],
                }
                for metadata_file in metadata_files:
                    data["File Name"].append(metadata_file.name)
                    data["Size (KB)"].append(
                        metadata_file.stat().st_size / 1024
                    )  # Convert bytes to KB
                    # Convert last modified time to human-readable format
                    last_modified = time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(metadata_file.stat().st_mtime),
                    )
                    data["Last Modified"].append(last_modified)
                    # Read the number of records in the JSON file
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            jsondata = json.load(f)
                            if isinstance(jsondata, list):
                                records = len(jsondata)
                            elif isinstance(jsondata, dict):
                                records = sum(
                                    len(v) if isinstance(v, list) else 1
                                    for v in jsondata.values()
                                )
                            else:
                                records = 1
                    except Exception as e:
                        records = "Error reading file"
                        app_logger.error(f"Error reading {metadata_file.name}: {e}")
                    data["Number of Records"].append(records)

                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning(
                    f"No metadata files found in the directory '{path.absolute()}'."
                )
                return
        else:
            st.warning("No projects found.")
            return

    st.markdown("### Metadata Actions")
    col1, col2, col3 = st.columns(3)
    meta_button(
        col1,
        "Create Metadata",
        "➕",
        nl.MetaDataCreate,
        selected_project,
        filter_text,
        filter_type,
        filter_value,
        "Metadata created successfully.",
        "Creating metadata... please wait.",
    )
    meta_button(
        col2,
        "Delete Metadata",
        "❌",
        nl.MetaDataDelete,
        selected_project,
        filter_text,
        filter_type,
        filter_value,
        "Metadata deleted successfully.",
        "Deleting metadata... please wait.",
    )
    meta_button(
        col3,
        "Download Metadata",
        "📥",
        nl.MetaDataLoad,
        selected_project,
        filter_text,
        filter_type,
        filter_value,
        "Metadata loaded successfully.",
        "Loading metadata... please wait.",
    )

    st.markdown("### Metadata Helper Actions (work on meta data files)")
    col1, col2 = st.columns(2)
    meta_button(
        col1,
        "Clean Parent Attribute Groups",
        "🧹",
        nl.MetaDataHelperCleanParentAttributeGroupInternalNames,
        selected_project,
        filter_text,
        filter_type,
        filter_value,
        "Parent attribute groups cleaned successfully.",
        "Cleaning parent attribute groups... please wait.",
    )

    st.markdown("### Metadata Helper Actions (work on meta data from NEMO)")
    col1, col2 = st.columns(2)
    meta_button(
        col1,
        "Auto Resolve Applications",
        "🪄",
        nl.MetaDataHelperAutoResolveApplications,
        selected_project,
        filter_text,
        filter_type,
        filter_value,
        "Auto Resolve Applications executed successfully.",
        "Auto Resolve Applications... please wait.",
    )
    meta_button(
        col2,
        "Update Link Texts",
        "🔗",
        nl.MetaDataHelperUpdateLinkTexts,
        selected_project,
        filter_text,
        filter_type,
        filter_value,
        "Link texts updated successfully.",
        "Updating link texts... please wait.",
    )


# === Main Content Bereich ===
def content():

    page = st.session_state.get("page", "home")
    if page == "home":
        st.header("Welcome to the nemo_library UI")
        st.write("Please select a page from the sidebar to get started.")
    elif page == "MigMan":
        show_migman()
    elif page == "Projects":
        show_projects()
    elif page == "MetaData":
        show_metadata()
    elif page == "settings":
        st.header("Settings")
        config.showSettings(st)
    else:
        st.header(f"Page: {page}")
        if hasattr(nl, page):
            method = getattr(nl, page)
            if callable(method):
                result = method()
                st.write(result)
            else:
                st.error(f"{page} is not a callable method.")
        else:
            st.error(f"Page '{page}' not found in nemo_library.")


# === Main Function ===
def main():
    st.set_page_config(page_title="nemo_library UI", layout="wide")
    if not config.config_file_exists():
        st.stop()

    sidebar()
    content()


if __name__ == "__main__":
    main()
