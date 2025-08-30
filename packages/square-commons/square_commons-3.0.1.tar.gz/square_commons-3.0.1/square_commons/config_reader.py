import configparser
import os
import shutil
from typing import Dict, List


class ConfigReader:
    """
    A class to manage configuration settings from a file and environment variables.
    """

    def __init__(self, file_path: str, sample_file_path: str = None):
        """
        Initializes the ConfigReader with the path to the configuration file.

        :param file_path: Path of the configuration file.
        """
        if not isinstance(file_path, str):
            raise TypeError(
                f"Invalid datatype received for file_path. Expected str, got {type(file_path).__name__}."
            )
        if not os.path.exists(file_path):
            if sample_file_path and os.path.exists(sample_file_path):
                shutil.copyfile(sample_file_path, file_path)
            else:
                raise FileNotFoundError(f"File does not exist at path: {file_path}")

        self.file_path = file_path
        self.config_parser = configparser.RawConfigParser()
        self.config_parser.optionxform = str
        self.config_parser.read(file_path)

    def read_configuration(self) -> Dict[str, Dict[str, str]]:
        """
        Reads the configuration file and returns its contents as a dictionary.

        :return: Dictionary with section names as keys and dictionaries of key-value pairs as values.
        """
        configuration = {}
        for section in self.config_parser.sections():
            environment_variables = self.config_parser.options(section)
            configuration[section] = self._read_environment_configuration_variables(
                section, environment_variables
            )
        return configuration

    def _read_environment_configuration_variables(
        self, section: str, variables: List[str]
    ) -> Dict[str, str]:
        """
        Reads environment variables for the given section. Falls back to configuration file if not found in OS.

        :param section: Section name in the configuration file.
        :param variables: List of variable names to retrieve.
        :return: Dictionary of key-value pairs where keys are variable names and values are their values.
        """
        if not isinstance(section, str):
            raise TypeError(
                f"Invalid datatype received for section. Expected str, got {type(section).__name__}."
            )
        if not isinstance(variables, list):
            raise TypeError(
                f"Invalid datatype received for variables. Expected list, got {type(variables).__name__}."
            )

        config_dict = {}
        for variable in variables:
            value = os.environ.get(variable)
            if value is not None:
                config_dict[variable] = value
            else:
                config_dict[variable] = self._read_configuration_variable(
                    section, variable
                )

        return config_dict

    def _read_configuration_variable(self, section: str, variable_name: str) -> str:
        """
        Reads a single configuration variable from the given section.

        :param section: Section name in the configuration file.
        :param variable_name: Name of the configuration variable.
        :return: The value of the configuration variable.
        """
        if not isinstance(section, str):
            raise TypeError(
                f"Invalid datatype received for section. Expected str, got {type(section).__name__}."
            )
        if not isinstance(variable_name, str):
            raise TypeError(
                f"Invalid datatype received for variable_name. Expected str, got {type(variable_name).__name__}."
            )

        return self.config_parser.get(section, variable_name)
