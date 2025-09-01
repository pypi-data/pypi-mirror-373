from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli import utils

import argparse
from typing import List, Optional, Iterable


# -------------------- API --------------------


def show(journal_name: str, attribute_names: List[str]) -> Iterable[str]:
    """
    Get attribute data from a registered journal.

    Args:
        journal_name: The journal name
        attribute_names (optional): List of attribute names which values one wants to show
    Returns:
        The attribute value if a single attribute was requested. For two or more
        attributes, several strings are returned. One for line requested attribute.
        The string has the format "attribute_name: attribute_value".
    Raises:
        InvalidName if the journal name is invalid.
        InvalidAttribute if an attribute name is invalid.
    """
    journal_data_file = api.get_journal_data_file()
    journal = api.find_journal_by_name(journal_data_file, journal_name)
    if journal:
        if len(attribute_names) == 0:
            attribute_names = list(journal.__dict__.keys())

        if len(attribute_names) == 1:
            attribute_name = attribute_names[0]
            if attribute_name not in journal.__dict__.keys():
                raise exceptions.InvalidAttribute(attribute_name)
            yield journal.__dict__[attribute_name]
        else:
            for name in attribute_names:
                yield f"{name}:{journal.__dict__[name]}"
    else:
        raise exceptions.InvalidName()


# -------------------- CLI --------------------


def __show__(
    journal_name: str, attribute_names: Optional[List[str]] = None, **kwargs
):
    utils.ensure_configuration_file_exists()
    if not attribute_names:
        attribute_names = []

    # The action 'append' adds a None object if nothing is passed (assuming nargs='?')
    if len(attribute_names) > 0 and attribute_names[0] is None:
        attribute_names.remove(None)

    try:
        for show_entry in show(journal_name, attribute_names):
            print(show_entry)
    except exceptions.InvalidName:
        print(f"The journal name: {journal_name} is not registered.")
    except exceptions.InvalidAttribute as ex:
        print(f"The attribute: {ex.msg} is not registered.")


def get_parser(subparser_action=None):
    command_name = "show"
    command_description = show.__doc__ if show.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            aliases=["s"],
            description=command_description,
            help=command_help,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("journal_name", help="A registered journal name")
    parser.add_argument(
        "attribute_names",
        nargs="?",
        action="append",
        help="Attribute name which value one wants to show.",
    )
    parser.set_defaults(subcommand_help=parser.print_help, func=__show__)

    return parser
