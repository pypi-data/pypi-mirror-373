import logging
import sys
import keyring


class PasswordManager:
    def __init__(self, service_name, username):
        """
        Initializes the PasswordManager with the given service name and username.

        Args:
            service_name (str): The name of the service for which the password is managed.
            username (str): The username associated with the service.
        """
        self.service_name = service_name
        self.username = username

    def set_password(self, password) -> None:
        """
        Stores the password in the Credential Manager (Windows) or Keychain (macOS).

        Args:
            password (str): The password to be stored.
        """
        keyring.set_password(self.service_name, self.username, password)

    def get_password(self) -> str | None:
        """
        Retrieves the password from the Credential Manager (Windows) or Keychain (macOS).

        Returns:
            str: The stored password or None if no password is found.
        """
        return keyring.get_password(self.service_name, self.username)


if __name__ == "__main__":
    # Example usage:
    service_name = "nemo_library"
    username = "my_username"
    password = "my_password"

    pm = PasswordManager(service_name, username)

    # Set password
    pm.set_password(password)
    logging.info(
        f"Password for user '{username}' in service '{service_name}' has been stored."
    )

    # Retrieve password
    retrieved_password = pm.get_password()
    if retrieved_password:
        logging.info(
            f"The stored password for user '{username}' is: {retrieved_password}"
        )
    else:
        logging.info(
            f"No password found for user '{username}' in service '{service_name}'."
        )
