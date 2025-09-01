from danoan.journal_manager.core import api, exceptions, model

from danoan.journal_manager.cli import utils
from danoan.journal_manager.cli.commands.journal_commands import (
    activate,
    create,
    deactivate,
    deregister,
    edit,
    show,
    register,
)

import argparse

# -------------------- API --------------------


def list_journals(list_all: bool = False):
    """
    List registered journals.

    list_all: If True, list all journals. Otherwise, list only active journals.

    Returns:
        A string for each registered journal in the format:
        "journal_name:location_folder".
    Raises:
        EmptyList if the journal register is empty.
    """
    journal_components = model.JournalData(None, None, True, None, None)

    if list_all:
        journals_to_list = api.get_journal_data_file().list_of_journal_data
    else:
        journals_to_list = api.find_journal(
            api.get_journal_data_file(),
            journal_components,
            model.LogicOperator.AND,
        )

    if len(journals_to_list) == 0:
        raise exceptions.EmptyList()

    for entry in journals_to_list:
        yield f"{entry.name}:{entry.location_folder}"


# -------------------- CLI --------------------


def __list_journals__(list_all: bool, **kwargs):
    utils.ensure_configuration_file_exists()

    try:
        for journal_list_entry in list_journals(list_all):
            print(journal_list_entry)
    except exceptions.EmptyList:
        print("There is no journal registered yet.")


def get_parser(subparser_action=None):
    command_name = "journal"
    command_description = """
    Collection of commands to edit journals. 

    If no sub-command is given, list the registered journals.
    """
    command_help = command_description

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["j"],
        )
    else:
        parser = argparse.ArgumentParser(
            command_name, description=command_description
        )

    parser.add_argument(
        "--all",
        "-a",
        dest="list_all",
        action="store_true",
        help="List all journals, including the inactive ones",
    )

    list_of_commands = [
        activate,
        create,
        deactivate,
        deregister,
        edit,
        show,
        register,
    ]

    subparser_action = parser.add_subparsers(title="Journal subcommands")
    for command in list_of_commands:
        command.get_parser(subparser_action)

    parser.set_defaults(
        subcommand_help=parser.print_help, func=__list_journals__
    )

    return parser
