from danoan.journal_manager.cli.commands.setup_commands import init

from danoan.journal_manager.core import api, exceptions

from conftest import *
from pathlib import Path
import pytest


# -------------------- Fixtures --------------------
@pytest.fixture(scope="function")
def f_unset_env_variable(monkeypatch):
    monkeypatch.delenv(api.ENV_JOURNAL_MANAGER_CONFIG_FOLDER, raising=False)


# -------------------- Tests --------------------
class TestInit:
    def test_no_environment_variable_set(self, f_unset_env_variable, tmp_path):
        with pytest.raises(exceptions.ConfigurationFolderDoesNotExist) as e:
            api.get_configuration_file()

        assert e.type == exceptions.ConfigurationFolderDoesNotExist

    def test_no_configuration_file_exist(
        self, f_set_env_variable, f_setup_init, tmp_path
    ):
        journal_manager_config_folder = f_set_env_variable[
            "journal_manager_config_folder"
        ]
        default_journal_folder = tmp_path.joinpath("journals").expanduser()
        default_template_folder = tmp_path.joinpath("templates").expanduser()
        default_editor_path = Path("nvim")
        init.init_journal_manager(
            default_journal_folder, default_template_folder, default_editor_path
        )

        config_file = api.get_configuration_file()

        expected_journal_data_filepath = journal_manager_config_folder.joinpath(
            "journal_data.toml"
        ).expanduser()
        expected_template_data_filepath = (
            journal_manager_config_folder.joinpath(
                "template_data.toml"
            ).expanduser()
        )

        assert (
            config_file.default_journal_folder
            == default_journal_folder.as_posix()
        )
        assert (
            config_file.journal_data_filepath
            == expected_journal_data_filepath.as_posix()
        )
        assert (
            config_file.template_data_filepath
            == expected_template_data_filepath.as_posix()
        )
        assert config_file.parameters.default_text_editor_path == "nvim"

    def test_configuration_file_exist(self, f_set_env_variable, tmp_path):
        first_default_journal_folder = tmp_path.joinpath(
            "journals"
        ).expanduser()
        first_default_template_folder = tmp_path.joinpath(
            "templates"
        ).expanduser()
        api.create_configuration_file(
            first_default_journal_folder, first_default_template_folder
        )

        config_file = api.get_configuration_file()
        assert (
            config_file.default_journal_folder
            == first_default_journal_folder.as_posix()
        )

        second_default_journal_folder = tmp_path.joinpath(
            "journals_another_path"
        ).expanduser()
        second_default_template_folder = tmp_path.joinpath(
            "templates_another_path"
        ).expanduser()
        second_default_editor_path = Path("nvim")

        init.init_journal_manager(
            second_default_journal_folder,
            second_default_template_folder,
            second_default_editor_path,
        )
        config_file = api.get_configuration_file()

        assert (
            config_file.default_journal_folder
            == second_default_journal_folder.as_posix()
        )
        assert (
            config_file.default_template_folder
            == second_default_template_folder.as_posix()
        )
