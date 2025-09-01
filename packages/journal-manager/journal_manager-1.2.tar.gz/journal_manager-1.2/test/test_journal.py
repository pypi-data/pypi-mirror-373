from danoan.journal_manager.cli.commands import journal_commands as jm
from danoan.journal_manager.core import api, model

from danoan.journal_manager.cli.commands.template_commands.register import (
    register as register_template,
)

import argparse
from conftest import *
from datetime import datetime
from pathlib import Path
import pytest


def __create_template__(tmp_path, template_name):
    template_location = tmp_path.joinpath(f"template-{template_name}")
    template_location.mkdir()
    template_yml_config_file = template_location.joinpath("mkdocs.tpl.yml")
    template_yml_config_file.touch()

    return template_location


class TestRegister:
    def test_register_deregister_journal(self, f_setup_init, tmp_path):
        # Register
        first_location_folder = tmp_path.joinpath("first-journal").expanduser()
        first_location_folder.mkdir()
        first_journal_title = "My First Journal Title"
        jm.register.register(first_location_folder, first_journal_title)

        journal_data = api.get_journal_data_file().list_of_journal_data[0]

        assert journal_data.name == "my-first-journal-title"
        assert journal_data.title == first_journal_title
        assert journal_data.location_folder == first_location_folder.as_posix()
        assert journal_data.active == True

        # Register a second one
        second_location_folder = tmp_path.joinpath(
            "second-journal"
        ).expanduser()
        second_location_folder.mkdir()
        second_journal_title = "My Second Journal Title"
        jm.register.register(second_location_folder, second_journal_title)

        list_of_journal_data = api.get_journal_data_file().list_of_journal_data
        assert len(list_of_journal_data) == 2

        # Deregister
        jm.deregister.deregister(["my-first-journal-title"])

        list_of_journal_data = api.get_journal_data_file().list_of_journal_data
        assert len(list_of_journal_data) == 1

        journal_data = api.get_journal_data_file().list_of_journal_data[0]

        assert journal_data.name == "my-second-journal-title"
        assert journal_data.title == second_journal_title
        assert journal_data.location_folder == second_location_folder.as_posix()
        assert journal_data.active == True


class TestActivate:
    def test_activate_deactivate_journal(self, f_setup_init, tmp_path):
        for i in range(5):
            jm.create.create(f"journal-{i}", tmp_path / f"j{i}")

        list_of_journals = api.get_journal_data_file().list_of_journal_data

        journal_title = "My Journal Title"
        jm.register.register(tmp_path, journal_title)

        journal_data = api.find_journal_by_location(
            api.get_journal_data_file(), str(tmp_path)
        )

        assert journal_data
        assert journal_data.title == journal_title
        assert journal_data.active == True

        # Deactivate
        jm.deactivate.deactivate([journal_data.name])
        journal_data = api.find_journal_by_location(
            api.get_journal_data_file(), str(tmp_path)
        )

        assert journal_data
        assert journal_data.title == journal_title
        assert journal_data.active == False

        for journal in list_of_journals:
            found_journal = api.find_journal_by_location(
                api.get_journal_data_file(), journal.location_folder
            )
            assert found_journal is not None
            assert found_journal.active == True

        # Activate

        jm.activate.activate([journal_data.name])
        journal_data = api.find_journal_by_location(
            api.get_journal_data_file(), str(tmp_path)
        )

        assert journal_data
        assert journal_data.title == journal_title
        assert journal_data.active == True

        for journal in list_of_journals:
            found_journal = api.find_journal_by_location(
                api.get_journal_data_file(), journal.location_folder
            )
            assert found_journal is not None
            assert found_journal.active == True


class TestCreate:
    @pytest.mark.parametrize(
        "journal_location_folder_str, template_name",
        [(None, None), ("journals-repository", "research")],
    )
    def test_create_journal(
        self, f_setup_init, tmp_path, journal_location_folder_str, template_name
    ):
        journal_title = "My Journal Title"

        template_name = "research"
        template_location = __create_template__(tmp_path, template_name)
        register_template(template_name, template_location.expanduser())

        journal_location_folder = None
        if journal_location_folder_str:
            journal_location_folder = tmp_path.joinpath(
                journal_location_folder_str
            ).expanduser()

        if not journal_location_folder:
            journal_location_folder = Path(
                api.get_configuration_file().default_journal_folder
            )

        jm.create.create(journal_title, journal_location_folder, template_name)

        journal_data = api.get_journal_data_file().list_of_journal_data[0]
        assert journal_data.title == journal_title
        assert (
            journal_data.location_folder
            == journal_location_folder.joinpath("my-journal-title")
            .expanduser()
            .as_posix()
        )
        assert journal_data.active == True


class TestShow:
    def test_show_one_parameter(self, f_setup_init, tmp_path):
        journal_title = "My Journal Title"
        journal_location_folder = Path(
            api.get_configuration_file().default_journal_folder
        )

        template_name = "research"
        template_location = __create_template__(tmp_path, template_name)
        register_template(template_name, template_location.expanduser())

        jm.create.create(journal_title, journal_location_folder, template_name)
        show_entries = list(jm.show.show("my-journal-title", ["title"]))

        assert len(show_entries) == 1
        assert show_entries[0] == journal_title

        show_entries = list(jm.show.show("my-journal-title", []))

        assert len(show_entries) == len(model.JournalData.__dataclass_fields__)
        assert show_entries[0] == "name:my-journal-title"
