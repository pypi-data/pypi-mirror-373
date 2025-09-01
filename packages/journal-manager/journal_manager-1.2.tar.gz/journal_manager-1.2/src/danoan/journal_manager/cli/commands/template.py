from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli import utils
from danoan.journal_manager.cli.commands.template_commands import (
    register,
    remove,
    show,
)

import argparse
from typing import Iterable


# -------------------- API --------------------


def list_templates() -> Iterable[str]:
    """
    List registered templates.

    Returns:
        A string for each registered template in the format:
        "template_name:template_filepath"
    """
    template_list = api.get_template_list_file().list_of_template_data

    if len(template_list) == 0:
        raise exceptions.EmptyList()

    for entry in template_list:
        yield f"{entry.name}:{entry.filepath}"


# -------------------- CLI --------------------


def __list_templates__(**kwargs):
    utils.ensure_configuration_file_exists()

    try:
        for entry in list_templates():
            print(entry)
    except exceptions.EmptyList:
        print("No template registered yet.")


def get_parser(subparser_action=None):
    command_name = "template"
    command_description = """
    Collection of commands to manage journal templates.

    If no subcommand is given, list the registered templates.
    """
    command_help = command_description

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            aliases=["t"],
            description=command_description,
            help=command_help,
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    subparser_action = parser.add_subparsers()

    list_of_commands = [register, remove, show]
    for command in list_of_commands:
        command.get_parser(subparser_action)

    parser.set_defaults(
        subcommand_help=parser.print_help, func=__list_templates__
    )

    return parser
