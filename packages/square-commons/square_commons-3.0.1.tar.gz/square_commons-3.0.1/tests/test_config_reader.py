import os

import pytest

from square_commons.config_reader import ConfigReader


@pytest.fixture
def sample_config_file(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        """
        [SECTION1]
        KEY1=VALUE1

        [SECTION2]
        KEY2=VALUE2
        """
    )
    return config_file


def test_config_reader_initialization(sample_config_file):
    reader = ConfigReader(str(sample_config_file))
    assert isinstance(reader, ConfigReader)


def test_config_reader_initialization_invalid_path():
    with pytest.raises(FileNotFoundError):
        ConfigReader("non_existent_file.ini")


def test_read_configuration(sample_config_file):
    reader = ConfigReader(str(sample_config_file))
    config = reader.read_configuration()
    assert config == {
        "SECTION1": {"KEY1": "VALUE1"},
        "SECTION2": {"KEY2": "VALUE2"},
    }


def test_read_environment_configuration_variables(mocker, sample_config_file):
    mocker.patch.dict(os.environ, {"KEY1": "ENV_VALUE1"})
    reader = ConfigReader(str(sample_config_file))
    config = reader.read_configuration()
    assert config["SECTION1"]["KEY1"] == "ENV_VALUE1"  # Overrides file value


def test_read_configuration_variable(sample_config_file):
    reader = ConfigReader(str(sample_config_file))
    value = reader._read_configuration_variable("SECTION1", "KEY1")
    assert value == "VALUE1"
