from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli import utils

import argparse
from typing import List


# -------------------- API --------------------


def deregister(journal_names: List[str]):
    """
    Deregister a journal from the list of registered journals.

    This action will unlist the journal from the list of
    registered journals. Journals manager will not follow
    this journal anymore after this operation.

    This function does not remove any file.

    Args:
        journal_names: A list of journal names to be deregistered.
    Raises:
        InvalidName if one or more journal names are not present in the list of registered journals.
    """
    journal_data_file = api.get_journal_data_file()

    not_found_journal_names = []
    for journal_name in journal_names:
        journal = api.find_journal_by_name(journal_data_file, journal_name)

        if journal:
            journal_data_file.list_of_journal_data.remove(journal)
        else:
            not_found_journal_names.append(journal_name)

    if len(not_found_journal_names) > 0:
        raise exceptions.InvalidName(not_found_journal_names)

    with open(api.get_configuration_file().journal_data_filepath, "w") as f:
        journal_data_file.write(f)


# -------------------- CLI --------------------


def __deregister__(journal_names: List[str], **kwargs):
    utils.ensure_configuration_file_exists()
    try:
        deregister(journal_names)
    except exceptions.InvalidName as ex:
        print(
            f"The journal names: {ex.names} are not present in the list of registered journals. Any deregister was done."
        )


def get_parser(subparser_action=None):
    command_name = "deregister"
    command_description = deregister.__doc__ if deregister.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["d"],
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
        action="extend",
        nargs="+",
        help="Name of the journal to be deregistered",
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=__deregister__)

    return parser
