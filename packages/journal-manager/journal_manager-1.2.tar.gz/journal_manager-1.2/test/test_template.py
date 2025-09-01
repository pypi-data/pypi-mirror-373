from danoan.journal_manager.cli.commands.template_commands.register import (
    register as register_template,
)
from danoan.journal_manager.cli.commands.template_commands.remove import (
    remove as remove_template,
)
from danoan.journal_manager.core import api

from pathlib import Path


def __create_template__(tmp_path, template_name):
    template_location = tmp_path.joinpath(f"template-{template_name}")
    template_location.mkdir()
    template_yml_config_file = template_location.joinpath("mkdocs.tpl.yml")
    template_yml_config_file.touch()

    return template_location


class TestTemplate:
    def test_template_register(self, f_setup_init, tmp_path):
        config_file = api.get_configuration_file()

        template_list_file = api.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 0

        template_name = "research"
        template_location = __create_template__(tmp_path, template_name)

        e_template_filepath = (
            Path(config_file.default_template_folder)
            .joinpath(template_name)
            .expanduser()
            .as_posix()
        )

        register_template(template_name, template_location)
        template_list_file = api.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 1
        assert template_list_file.list_of_template_data[0].name == template_name
        assert (
            template_list_file.list_of_template_data[0].filepath
            == e_template_filepath
        )

    def test_template_remove(self, f_setup_init, tmp_path):
        self.test_template_register(f_setup_init, tmp_path)

        template_list_file = api.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 1

        remove_template("research")
        template_list_file = api.get_template_list_file()
        assert len(template_list_file.list_of_template_data) == 0
