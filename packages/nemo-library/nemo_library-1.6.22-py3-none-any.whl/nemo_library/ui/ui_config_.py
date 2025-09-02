import configparser
import json
from pathlib import Path
from typing import Optional

from nemo_library.core import NemoLibrary

from dataclasses import dataclass, asdict, field

from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

from nemo_library.utils.password_manager import PasswordManager

CONFIG_FILE = Path("configui.json")


@dataclass
class Configuration:
    profile_name: str = ""
    profile_description: str = ""
    tenant: str = ""
    userid: str = ""
    password: str = ""
    environment: str = ""
    hubspot_api_token: str | None = ""
    migman_local_project_directory: str | None = ""
    migman_proALPHA_project_status_file: str | None = ""
    migman_projects: list[str] = field(default_factory=list)
    migman_mapping_fields: list[str] = field(default_factory=list)
    migman_additional_fields: dict[str, list[str]] = field(default_factory=dict)
    migman_multi_projects: dict[str, list[str]] = field(default_factory=dict)
    metadata: str | None = ""

    def to_dict(self, exclude_sensitive: bool = False) -> dict:
        data = asdict(self)
        if exclude_sensitive:
            for key in ["password", "hubspot_api_token"]:
                data.pop(key, None)
        return data


class UIConfig:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.current_profile: Optional[Configuration] = None
        self.profiles: list[Configuration] = []

        if not self.config_file.exists():
            config = configparser.ConfigParser()
            config.read("config.ini")

            self.add_profile(
                Configuration(
                    profile_name="Default Profile",
                    profile_description="Default configuration for Nemo Library UI",
                    tenant=config.get("nemo_library", "tenant", fallback=""),
                    userid=config.get("nemo_library", "userid", fallback=""),
                    password=config.get("nemo_library", "password", fallback=""),
                    environment=config.get("nemo_library", "environment", fallback=""),
                    hubspot_api_token=config.get(
                        "nemo_library", "hubspot_api_token", fallback=""
                    ),
                    migman_local_project_directory=config.get(
                        "nemo_library", "migman_local_project_directory", fallback=""
                    ),
                    migman_proALPHA_project_status_file=config.get(
                        "nemo_library",
                        "migman_proALPHA_project_status_file",
                        fallback="",
                    ),
                    migman_projects=config.get(
                        "nemo_library",
                        "migman_projects",
                        fallback=[],
                    ),
                    migman_mapping_fields=config.get(
                        "nemo_library",
                        "migman_mapping_fields",
                        fallback=[],
                    ),
                    migman_additional_fields=config.get(
                        "nemo_library",
                        "migman_additional_fields",
                        fallback={},
                    ),
                    migman_multi_projects=config.get(
                        "nemo_library",
                        "migman_multi_projects",
                        fallback={},
                    ),
                    metadata=config.get(
                        "nemo_library", "hubspot_api_token", fallback=""
                    ),
                )
            )

        self.load_profiles()

    def load_profiles(self):

        # load file
        data = json.loads(self.config_file.read_text())
        self.profiles = [
            Configuration(**profile) for profile in data.get("profiles", [])
        ]
        current_profile_name = data.get("current_profile_name", None)
        self.set_current_profile(current_profile_name)

        # load password and hubspot_api_token from keyring
        for profile in self.profiles:
            pm = PasswordManager(
                service_name=f"nemo_library_ui_{profile.profile_name}_userid",
                username=profile.userid,
            )
            profile.password = pm.get_password()
            pm = PasswordManager(
                service_name=f"nemo_library_ui_{profile.profile_name}_hubspot",
                username=profile.userid,
            )
            profile.hubspot_api_token = pm.get_password()

    def save_profiles(self):

        # Save the current profile and all profiles to the config file
        json_data = {
            "current_profile_name": (
                self.current_profile.profile_name if self.current_profile else None
            ),
            "profiles": [
                profile.to_dict(exclude_sensitive=True) for profile in self.profiles
            ],
        }
        self.config_file.write_text(json.dumps(json_data, indent=4))

        # save password and hubspot_api_token to keyring
        for profile in self.profiles:
            pm = PasswordManager(
                service_name=f"nemo_library_ui_{profile.profile_name}_userid",
                username=profile.userid,
            )
            pm.set_password(profile.password)
            pm = PasswordManager(
                service_name=f"nemo_library_ui_{profile.profile_name}_hubspot",
                username=profile.userid,
            )
            pm.set_password(profile.hubspot_api_token)

    def set_current_profile(self, profile_name: str):
        if not any(profile.profile_name == profile_name for profile in self.profiles):
            raise ValueError(f"Profile '{profile_name}' not found in profiles.")
        self.current_profile = next(
            (
                profile
                for profile in self.profiles
                if profile.profile_name == profile_name
            ),
            None,
        )
        if len(self.profiles) > 0 and self.current_profile is None:
            raise ValueError(f"Profile '{profile_name}' not found in profiles.")
        st.session_state["active_profile"] = profile_name

    def config_file_exists(self) -> bool:
        return CONFIG_FILE.exists()

    def add_profile(self, profile: Configuration):
        if any(p.profile_name == profile.profile_name for p in self.profiles):
            raise ValueError(
                f"Profile with name '{profile.profile_name}' already exists."
            )
        self.profiles.append(profile)
        self.set_current_profile(profile.profile_name)
        self.save_profiles()

    def delete_profile(self, profile_name: str):
        index = next(
            (i for i, p in enumerate(self.profiles) if p.profile_name == profile_name),
            None,
        )
        if index is None:
            raise ValueError(f"Profile '{profile_name}' not found in profiles.")
        else:
            del self.profiles[index]
            current_profile = next(
                (p for p in self.profiles if p.profile_name != profile_name),
                None,
            )
            if current_profile:
                self.set_current_profile(current_profile.profile_name)

        self.save_profiles()

    def getNL(self):
        return NemoLibrary(
            config_file="", # don't use config file here, use the current profile
            environment=self.current_profile.environment,
            tenant=self.current_profile.tenant,
            userid=self.current_profile.userid,
            password=self.current_profile.password,
            hubspot_api_token=self.current_profile.hubspot_api_token,
            migman_local_project_directory=self.current_profile.migman_local_project_directory,
            migman_proALPHA_project_status_file=self.current_profile.migman_proALPHA_project_status_file,
            migman_projects=self.current_profile.migman_projects,
            migman_mapping_fields=self.current_profile.migman_mapping_fields,
            migman_additional_fields=self.current_profile.migman_additional_fields,
            migman_multi_projects=self.current_profile.migman_multi_projects,
            metadata_directory=self.current_profile.metadata,
        )

    def showSettings(self, st):
        st.subheader("Configuration – Manage Profiles")

        # Show existing profiles
        profile_names = [p.profile_name for p in self.profiles]

        col1, col2 = st.columns(2)

        # ADD PROFILE button at the top
        with col1:
            if st.button("➕ Add new profile"):
                new_profile = Configuration(
                    profile_name="New Profile", profile_description="New description"
                )
                try:
                    self.add_profile(new_profile)
                    st.success(f"Profile '{new_profile.profile_name}' created.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        # Delete profile button
        with col2:
            if st.button("🗑️ Delete this profile"):
                try:
                    self.delete_profile(self.current_profile.profile_name)
                    st.success("Profile deleted.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        if not profile_names:
            st.warning("No profiles available. Please add one.")
            return

        # Select active profile
        selected_profile = st.selectbox(
            "Select active profile",
            profile_names,
            index=(
                profile_names.index(self.current_profile.profile_name)
                if self.current_profile
                else 0
            ),
        )
        if selected_profile != self.current_profile.profile_name:
            self.set_current_profile(selected_profile)
            self.save_profiles()
            st.rerun()

        st.divider()

        # Show editable settings for the selected profile
        if self.current_profile:
            st.markdown(f"### Edit Profile: `{self.current_profile.profile_name}`")
            with st.form("edit_profile_form"):
                profile_name = st.text_input(
                    "Profile name", self.current_profile.profile_name
                )
                profile_description = st.text_input(
                    "Description", self.current_profile.profile_description
                )
                st.divider()
                tenant = st.text_input("Tenant", self.current_profile.tenant)
                userid = st.text_input("User ID", self.current_profile.userid)
                password = st.text_input(
                    "Password", self.current_profile.password, type="password"
                )
                environment = st.text_input(
                    "Environment", self.current_profile.environment
                )
                st.divider()
                hubspot_token = st.text_input(
                    "HubSpot API Token",
                    self.current_profile.hubspot_api_token,
                    type="password",
                )
                st.divider()
                metadata = st.text_input(
                    "Metadata folder", self.current_profile.metadata
                )
                st.divider()
                migman_local_project_directory = st.text_input(
                    "MigMan Local Project Directory",
                    self.current_profile.migman_local_project_directory,
                )
                migman_proALPHA_project_status_file = st.text_input(
                    "MigMan proALPHA Project Status File",
                    self.current_profile.migman_proALPHA_project_status_file,
                )
                migman_projects = st.text_area(
                    "MigMan Projects (comma-separated)",
                    ", ".join(self.current_profile.migman_projects),
                )
                migman_mapping_fields = st.text_area(
                    "MigMan Mapping Fields (comma-separated)",
                    ", ".join(self.current_profile.migman_mapping_fields),
                )
                migman_additional_fields = st.text_area(
                    "MigMan Additional Fields (JSON format)",
                    json.dumps(self.current_profile.migman_additional_fields, indent=4),
                )
                migman_multi_projects = st.text_area(
                    "MigMan Multi Projects (JSON format)",
                    json.dumps(self.current_profile.migman_multi_projects, indent=4),
                )

                submitted = st.form_submit_button("💾 Save changes")
                if submitted:
                    # Apply edits
                    self.current_profile.profile_name = profile_name
                    self.current_profile.profile_description = profile_description
                    self.current_profile.tenant = tenant
                    self.current_profile.userid = userid
                    self.current_profile.password = password
                    self.current_profile.environment = environment
                    self.current_profile.hubspot_api_token = hubspot_token
                    self.current_profile.metadata = metadata
                    self.current_profile.migman_local_project_directory = (
                        migman_local_project_directory
                    )
                    self.current_profile.migman_proALPHA_project_status_file = (
                        migman_proALPHA_project_status_file  #
                    )
                    self.current_profile.migman_projects = [
                        p.strip() for p in migman_projects.split(",") if p.strip()
                    ]
                    self.current_profile.migman_mapping_fields = [
                        f.strip() for f in migman_mapping_fields.split(",") if f.strip()
                    ]
                    try:
                        self.current_profile.migman_additional_fields = json.loads(
                            migman_additional_fields
                        )
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format for MigMan Additional Fields.")
                        return
                    try:
                        self.current_profile.migman_multi_projects = json.loads(
                            migman_multi_projects
                        )
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format for MigMan Multi Projects.")
                        return
                    self.save_profiles()
                    st.success("Profile updated.")
                    st.rerun()
