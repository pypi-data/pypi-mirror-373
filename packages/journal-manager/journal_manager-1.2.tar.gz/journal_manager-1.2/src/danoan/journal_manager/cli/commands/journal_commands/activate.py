from danoan.journal_manager.core import api, exceptions, model
from danoan.journal_manager.cli import utils

import argparse
from typing import List


# -------------------- API --------------------


def activate(journal_names: List[str]):
    """
    Activate a journal.

    An active journal is a journal that is under frequent
    edition and update. It distinguishes from an inactive or
    archived journal.

    Args:
        journal_names: List of journal names.
    Raises:
        InvalidName if one or more journal names are not present in the list of registered journals.
    """
    journal_data_file = api.get_journal_data_file()

    updated_journal_data_list = []
    not_found_journal_names = []
    for journal_name in journal_names:
        journal = api.find_journal_by_name(journal_data_file, journal_name)
        if journal:
            journal.active = True
            updated_journal_data_list.append(journal)
        else:
            not_found_journal_names.append(journal_name)

    if len(not_found_journal_names) > 0:
        raise exceptions.InvalidName(not_found_journal_names)

    for journal in updated_journal_data_list:
        api.update_journal(journal_data_file, journal)


# -------------------- CLI --------------------


def __activate__(journal_names: List[str], **kwargs):
    utils.ensure_configuration_file_exists()
    try:
        activate(journal_names)
    except exceptions.InvalidName as ex:
        print(
            f"The journal names: {ex.names} are not registered. Any activation was done."
        )


def get_parser(subparser_action=None):
    command_name = "activate"
    command_description = activate.__doc__ if activate.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["act"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument(
        "journal_names",
        nargs="+",
        action="store",
        help="Names of journals to activate",
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=__activate__)

    return parser
