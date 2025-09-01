from danoan.journal_manager.core import api, exceptions, model
from danoan.journal_manager.cli import utils

import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional


# -------------------- API --------------------


def register(location_folder: Path, journal_title: str):
    """
    Register an existing journal structure to the list of managed journals.

    Args:
        location_folder: Directory where the journal files are located
        journal_title: The title of the journal.
    Raises:
        InvalidLocation if the given location folder does not exist.
    """
    journal_data_file = api.get_journal_data_file()

    journal_name = utils.journal_name_from_title(journal_title)
    utils.ensure_journal_name_is_unique(journal_data_file, journal_name)

    if not location_folder.exists():
        raise exceptions.InvalidLocation(location_folder)

    journal_data = model.JournalData(
        journal_name,
        location_folder.as_posix(),
        True,
        journal_title,
        datetime.now().isoformat(),
    )
    journal_data_file.list_of_journal_data.append(journal_data)

    with open(api.get_configuration_file().journal_data_filepath, "w") as f:
        journal_data_file.write(f)


# -------------------- CLI --------------------


def __register__(
    location_folder: str, journal_title: Optional[str] = None, **kwargs
):
    utils.ensure_configuration_file_exists()
    if journal_title is None:
        journal_title = Path(location_folder).expanduser().name

    try:
        register(Path(location_folder), journal_title)
    except exceptions.InvalidLocation as ex:
        print(
            f"The given directory: {ex.locations} does not exist. Please specify an existing directory."
        )


def get_parser(subparser_action=None):
    command_name = "register"
    command_description = register.__doc__ if register.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["r"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("location_folder", help="Journal location folder")
    parser.add_argument("--title", dest="journal_title", help="Journal title")

    parser.set_defaults(subcommand_print=parser.print_help, func=__register__)

    return parser
