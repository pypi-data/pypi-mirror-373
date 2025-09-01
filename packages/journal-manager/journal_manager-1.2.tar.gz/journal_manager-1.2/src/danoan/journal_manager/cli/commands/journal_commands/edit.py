from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli import utils
from danoan.journal_manager.cli.wrappers import nvim_wrapper

import argparse
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Optional


# -------------------- API --------------------


def edit(journal_name: str):
    """
    Edit journal files.

    Opens the mkdocs.yml file for edition using the default editor specified
    in the file pointed by JOURNAL_MANAGER_CONFIG_FOLDER.

    Args:
        journal_name: The name of a journal in the registry. If empty a list with
                      the last three modified journals appears for selection.

    Raises:
        NotImplementedError if the requested editor application is not supported.
        InvalidName if the journal name is not registered.
        InvalidAttribute if no text editor has been set.
    """
    journal_data_file = api.get_journal_data_file()

    config_file = api.get_configuration_file()

    if not config_file.parameters.default_text_editor_path:
        raise exceptions.InvalidAttribute("No text editor was defined yet.")

    text_editor_path = Path(config_file.parameters.default_text_editor_path)

    if not text_editor_path:
        raise NotImplementedError(
            "Text editor path not found. Please set it with: jm setup init."
        )

    journal = api.find_journal_by_name(journal_data_file, journal_name)
    if journal:
        journal.last_edit_date = datetime.now().isoformat()
        api.update_journal(journal_data_file, journal)

        mkdocs_config_path = Path(journal.location_folder).joinpath(
            "mkdocs.yml"
        )
        nvim_wrapper.edit_file(
            mkdocs_config_path.expanduser(), text_editor_path
        )
    else:
        raise exceptions.InvalidName()


# -------------------- CLI --------------------


def __edit__(journal_name: Optional[str], **kwargs):
    utils.ensure_configuration_file_exists()

    if not journal_name:
        last_three_journals = sorted(
            api.get_journal_data_file().list_of_journal_data,
            key=lambda entry: entry.last_edit_date,
            reverse=True,
        )[:3]

        for i, journal in enumerate(last_three_journals, 1):
            print(f"({i}): {journal.name}")

        journal_number = int(input("Which item you would like to edit? "))
        journal_name = last_three_journals[journal_number - 1].name

    try:
        edit(journal_name)
    except NotImplementedError as ex:
        print(ex)
    except exceptions.InvalidName:
        print(
            f"Journal {journal_name} does not exist. Please enter an existent journal name."
        )
    except exceptions.InvalidAttribute:
        print(
            dedent(
                """\
                No text editor was set yet. To set one, edit the journal configuration file.
                $ journal-manager setup

                # api.toml
                [parameters]
                default_text_editor_path = "<my_text_editor_path>"
                """
            )
        )


def get_parser(subparser_action=None):
    command_name = "edit"
    command_description = edit.__doc__ if edit.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            help=command_help,
            description=command_description,
            aliases=["e"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("journal_name", nargs="?", help="Journal name")
    parser.set_defaults(subcommand_help=parser.print_help, func=__edit__)

    return parser
