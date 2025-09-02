import configparser
import logging
from pathlib import Path
import requests
import json

from nemo_library.utils.password_manager import PasswordManager

COGNITO_URLS = {
    "demo": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_1ZbUITj21",
    "dev": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_778axETqE",
    "test": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_778axETqE",
    "prod": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_1oayObkcF",
    "challenge": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_U2V9y0lzx",
}
"""
Dictionary mapping environments to their respective Cognito URLs.
"""

COGNITO_APPCLIENT_IDS = {
    "demo": "7tvfugcnunac7id3ebgns6n66u",
    "dev": "4lr89aas81m844o0admv3pfcrp",
    "test": "4lr89aas81m844o0admv3pfcrp",
    "prod": "8t32vcmmdvmva4qvb79gpfhdn",
    "challenge": "43lq8ej98uuo8hvnoi1g880onp",
}
"""
Dictionary mapping environments to their respective Cognito App Client IDs.
"""

NEMO_URLS = {
    "demo": "https://demo.enter.nemo-ai.com",
    "dev": "https://development.enter.nemo-ai.com",
    "test": "https://test.enter.nemo-ai.com",
    "prod": "https://enter.nemo-ai.com",
    "challenge": "https://challenge.enter.nemo-ai.com",
}
"""
Dictionary mapping environments to their respective NEMO URLs.
"""


class Config:
    """
    Configuration class for managing application settings and credentials.

    This class reads configuration values from a file or accepts them as arguments.
    It also provides methods to retrieve environment-specific URLs, tokens, and other settings.
    """

    def __init__(
        self,
        config_file: str = "config.ini",
        environment: str | None = None,
        tenant: str | None = None,
        userid: str | None = None,
        password: str | None = None,
        migman_local_project_directory: str | None = None,
        migman_proALPHA_project_status_file: str | None = None,
        migman_projects: list[str] | None = None,
        migman_mapping_fields: list[str] | None = None,
        migman_additional_fields: dict[str, list[str]] | None = None,
        migman_multi_projects: dict[str, list[str]] | None = None,
        metadata_directory: str | None = None,
        etl_directory: str | None = None,
        hubspot_api_token: str | None = None,
        gedys_user_id: str | None = None,
        gedys_password: str | None = None,
    ):
        """
        Initializes the Config class with optional parameters or values from a configuration file.

        Args:
            config_file (str): Path to the configuration file. Default is "config.ini".
            environment (str): Environment (e.g., "dev", "prod"). Default is None.
            tenant (str): Tenant name. Default is None.
            userid (str): User ID. Default is None.
            password (str): Password. Default is None.
            hubspot_api_token (str): HubSpot API token. Default is None.
            migman_local_project_directory (str): Local project directory for MigMan. Default is None.
            migman_proALPHA_project_status_file (str): Status file for proALPHA projects. Default is None.
            migman_projects (list[str]): List of MigMan projects. Default is None.
            migman_mapping_fields (list[str]): List of mapping fields for MigMan. Default is None.
            migman_additional_fields (dict[str, list[str]]): Additional fields for MigMan. Default is None.
            migman_multi_projects (dict[str, list[str]]): Multi-projects for MigMan. Default is None.
            metadata (str): Path to the metadata. Default is None.
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        read_files = self.config.read(config_file)
        if not read_files:
            logging.warning(f"Warning: Could not read config file: {config_file}")
        else:
            path = Path(read_files[0])
            logging.info(f"Successfully read config file: {path.absolute()}")

        self.tenant = tenant or self.config.get("nemo_library", "tenant", fallback=None)
        logging.info(f"Using tenant: {self.tenant}")
        self.userid = userid or self.config.get("nemo_library", "userid", fallback=None)
        logging.info(f"Using user ID: {self.userid}")
        self.password = password or self.config.get(
            "nemo_library", "password", fallback=None
        )

        if self.password is None:
            pm = PasswordManager(service_name="nemo_library", username=self.userid)
            self.password = pm.get_password()

        self.environment = environment or self.config.get(
            "nemo_library", "environment", fallback=None
        )
        logging.info(f"Using environment: {self.environment}")

        self.migman_local_project_directory = (
            migman_local_project_directory
            or self.config.get(
                "nemo_library", "migman_local_project_directory", fallback=None
            )
        )
        if self.migman_local_project_directory:
            logging.info(
                f"Using MigMan local project directory: {Path(self.migman_local_project_directory).absolute()}"
            )
        else:
            logging.warning("No MigMan local project directory specified.")

        self.migman_proALPHA_project_status_file = (
            migman_proALPHA_project_status_file
            or self.config.get(
                "nemo_library", "migman_proALPHA_project_status_file", fallback=None
            )
        )
        if self.migman_proALPHA_project_status_file:
            logging.info(
                f"Using MigMan proALPHA project status file: {Path(self.migman_proALPHA_project_status_file).absolute()}"
            )
        else:
            logging.warning("No MigMan proALPHA project status file specified.")

        self.migman_projects = migman_projects or (
            json.loads(
                self.config.get("nemo_library", "migman_projects", fallback="null")
            )
            if self.config.has_option("nemo_library", "migman_projects")
            else []
        )
        logging.info(f"Using MigMan projects: {self.migman_projects}")

        self.migman_mapping_fields = migman_mapping_fields or (
            json.loads(
                self.config.get(
                    "nemo_library", "migman_mapping_fields", fallback="null"
                )
            )
            if self.config.has_option("nemo_library", "migman_mapping_fields")
            else []
        )
        logging.info(f"Using MigMan mapping fields: {self.migman_mapping_fields}")

        self.migman_additional_fields = migman_additional_fields or (
            json.loads(
                self.config.get(
                    "nemo_library", "migman_additional_fields", fallback="null"
                )
            )
            if self.config.has_option("nemo_library", "migman_additional_fields")
            else {}
        )
        logging.info(f"Using MigMan additional fields: {self.migman_additional_fields}")

        self.migman_multi_projects = migman_multi_projects or (
            json.loads(
                self.config.get(
                    "nemo_library", "migman_multi_projects", fallback="null"
                )
            )
            if self.config.has_option("nemo_library", "migman_multi_projects")
            else {}
        )
        logging.info(f"Using MigMan multi-projects: {self.migman_multi_projects}")

        self.metadata_directory = metadata_directory or self.config.get(
            "nemo_library", "metadata", fallback=None
        )
        if self.metadata_directory:
            logging.info(f"Using metadata path: {Path(self.metadata_directory).absolute()}")
        else:
            logging.warning("No metadata path specified.")

        self.etl_directory = etl_directory or self.config.get(
            "nemo_library", "etl_directory", fallback=None
        )
        self.hubspot_api_token = hubspot_api_token or self.config.get(
            "nemo_library", "hubspot_api_token", fallback=None
        )
        self.gedys_user_id = gedys_user_id or self.config.get(
            "nemo_library", "gedys_user_id", fallback=None
        )
        logging.info(f"Using Gedys user ID: {self.gedys_user_id}")
        self.gedys_password = gedys_password or self.config.get(
            "nemo_library", "gedys_password", fallback=None
        )

        # Initialize tokens to None to make them persistent later
        self._id_token = None
        self._access_token = None
        self._refresh_token = None

    def get_config_nemo_url(self) -> str:
        """
        Retrieves the NEMO URL based on the current environment.

        Returns:
            str: The NEMO URL for the current environment.

        Raises:
            Exception: If the environment is unknown.
        """
        env = self.get_environment()
        try:
            return NEMO_URLS[env]
        except KeyError:
            raise Exception(f"unknown environment '{env}' provided. Environment must be one of {list(NEMO_URLS.keys())}")

    def get_tenant(self) -> str:
        """
        Retrieves the tenant name.

        Returns:
            str: The tenant name.
        """
        return self.tenant

    def get_userid(self) -> str:
        """
        Retrieves the user ID.

        Returns:
            str: The user ID.
        """
        return self.userid

    def get_password(self) -> str:
        """
        Retrieves the password.

        Returns:
            str: The password.
        """
        return self.password

    def get_environment(self) -> str:
        """
        Retrieves the environment.

        Returns:
            str: The environment.
        """
        return self.environment

    def get_hubspot_api_token(self) -> str:
        """
        Retrieves the HubSpot API token.

        Returns:
            str: The HubSpot API token.
        """
        return self.hubspot_api_token

    def get_migman_local_project_directory(self) -> str:
        """
        Retrieves the local project directory for MigMan.

        Returns:
            str: The local project directory for MigMan.
        """
        return self.migman_local_project_directory

    def get_migman_proALPHA_project_status_file(self) -> str:
        """
        Retrieves the status file for proALPHA projects.

        Returns:
            str: The status file for proALPHA projects.
        """
        return self.migman_proALPHA_project_status_file

    def get_migman_projects(self) -> list[str] | None:
        """
        Retrieves the list of MigMan projects.

        Returns:
            list[str] | None: The list of MigMan projects or None if not set.
        """
        return self.migman_projects

    def get_migman_mapping_fields(self) -> list[str] | None:
        """
        Retrieves the list of mapping fields for MigMan.

        Returns:
            list[str] | None: The list of mapping fields for MigMan or None if not set.
        """
        return self.migman_mapping_fields

    def get_migman_additional_fields(self) -> dict[str, list[str]] | None:
        """
        Retrieves the additional fields for MigMan.

        Returns:
            dict[str, list[str]] | None: The additional fields for MigMan or None if not set.
        """
        return self.migman_additional_fields

    def get_migman_multi_projects(self) -> dict[str, list[str]] | None:
        """
        Retrieves the multi-projects for MigMan.

        Returns:
            dict[str, list[str]] | None: The multi-projects for MigMan or None if not set.
        """
        return self.migman_multi_projects

    def get_gedys_user_id(self) -> str | None:
        """
        Retrieves the user ID for Gedys.

        Returns:
            str: The user ID for Gedys.
        """
        return self.gedys_user_id

    def get_gedys_password(self) -> str | None:
        """
        Retrieves the password for Gedys.

        Returns:
            str: The password for Gedys.
        """
        return self.gedys_password

    def get_etl_directory(self) -> str | None:
        """
        Retrieves the etl_directory

        Returns:
            str: The etl_directory
        """
        return self.etl_directory

    def connection_get_headers(self) -> dict[str, str]:
        """
        Retrieves the headers for the connection.

        Returns:
            dict[str, str]: The headers for the connection.
        """
        tokens = self.connection_get_tokens()
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {tokens[0]}",
            "refresh-token": tokens[2],
            "api-version": "1.0",
        }
        return headers

    def connection_get_cognito_authflow(self) -> str:
        """
        Retrieves the Cognito authentication flow.

        Returns:
            str: The Cognito authentication flow.
        """
        return "USER_PASSWORD_AUTH"

    def connection_get_cognito_url(self) -> str:
        """
        Retrieves the Cognito URL based on the current environment.

        Returns:
            str: The Cognito URL for the current environment.

        Raises:
            Exception: If the environment is unknown.
        """
        env = self.get_environment()
        try:
            return COGNITO_URLS[env]
        except KeyError:
            raise Exception(f"unknown environment '{env}' provided. Environment must be one of {list(COGNITO_URLS.keys())}")

    def connection_get_cognito_appclientid(self) -> str:
        """
        Retrieves the Cognito app client ID based on the current environment.

        Returns:
            str: The Cognito app client ID for the current environment.

        Raises:
            Exception: If the environment is unknown.
        """
        env = self.get_environment()
        try:
            return COGNITO_APPCLIENT_IDS[env]
        except KeyError:
            raise Exception(f"unknown environment '{env}' provided. Environment must be one of {list(COGNITO_APPCLIENT_IDS.keys())}")

    def connection_get_tokens(self) -> tuple[str, str, str]:
        """
        Retrieves the tokens for the connection, caching them after first request.

        Returns:
            tuple[str, str, str]: The ID token, access token, and refresh token.
        """
        # Return cached tokens if they exist
        if self._id_token and self._access_token:
            return self._id_token, self._access_token, self._refresh_token

        headers = {
            "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
            "Content-Type": "application/x-amz-json-1.1",
        }

        authparams = {
            "USERNAME": self.get_userid(),
            "PASSWORD": self.get_password(),
        }

        data = {
            "AuthParameters": authparams,
            "AuthFlow": self.connection_get_cognito_authflow(),
            "ClientId": self.connection_get_cognito_appclientid(),
        }

        # login and get token
        response_auth = requests.post(
            self.connection_get_cognito_url(),
            headers=headers,
            data=json.dumps(data, indent=2),
        )
        if response_auth.status_code != 200:
            raise Exception(
                f"request failed. Status: {response_auth.status_code}, error: {response_auth.text}"
            )
        tokens = json.loads(response_auth.text)
        self._id_token = tokens["AuthenticationResult"]["IdToken"]
        self._access_token = tokens["AuthenticationResult"]["AccessToken"]
        self._refresh_token = tokens["AuthenticationResult"].get("RefreshToken")

        return self._id_token, self._access_token, self._refresh_token

    def get_metadata_directory(self) -> str | None:
        """
        Retrieves the metadata path.

        Returns:
            str: The metadata path.
        """
        return self.metadata_directory

    def testLogin(self) -> None:
        """
        Tests the login by making a request to the NEMO API.

        Raises:
            Exception: If the login fails.
        """
        self.connection_get_headers()
