from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli import utils

import argparse
from pathlib import Path
from textwrap import dedent
from typing import Optional


# -------------------- API --------------------


def init_journal_manager(
    default_journal_folder: Path,
    default_template_folder: Path,
    default_text_editor_path: Path,
):
    """
    Initialize journal-manager settings.

    This sets up configuration values of journal-manager.

    Args:
        default_journal_folder: Path to the default location where journals will be created.
        default_template_folder: Path to the default location where journal templates will be stored.
        default_text_editor_path: Path to the text editor used by journal-manager to edit journals.
    """
    config_file = api.get_configuration_file()

    config_file.default_journal_folder = default_journal_folder.as_posix()
    config_file.default_template_folder = default_template_folder.as_posix()
    config_file.parameters.default_text_editor_path = (
        default_text_editor_path.as_posix()
    )

    with open(api.get_configuration_filepath(), "w") as f:
        config_file.write(f)


# -------------------- CLI --------------------


def __init_journal_manager__(
    default_journal_folder: Path,
    default_template_folder: Path,
    default_text_editor: Optional[Path],
    **kwargs,
):
    utils.ensure_configuration_folder_exists()

    config_file_exists_already = True
    try:
        config_file = api.get_configuration_file()
    except exceptions.ConfigurationFileDoesNotExist:
        api.create_configuration_file(
            default_journal_folder, default_template_folder
        )
        config_file_exists_already = False

    current_editor_str_path = None
    if config_file_exists_already:
        current_editor_str_path = (
            config_file.parameters.default_text_editor_path
        )

    new_editor_path = None
    if not default_text_editor:
        if not current_editor_str_path or current_editor_str_path == "":
            new_editor_path = Path(
                input("Enter the path of your default editor (e.g. nvim): ")
            )
        else:
            entered_editor_path = input(
                f"Enter the path of your default editor (type enter to keep the current one: {current_editor_str_path}): "
            )
            if entered_editor_path != "":
                new_editor_path = Path(entered_editor_path)
            else:
                new_editor_path = Path(current_editor_str_path)
    else:
        new_editor_path = default_text_editor

    init_journal_manager(
        default_journal_folder, default_template_folder, new_editor_path
    )
    config_file = api.get_configuration_file()

    if config_file_exists_already:
        start_message = dedent(
            f"""
            The configuration file exists already. 
            It is located at: {api.get_configuration_filepath()} and here it is its content after the update:
            """
        )
    else:
        start_message = dedent(
            f"""
            The configuration file was created and initialized. 
            It is located at: {api.get_configuration_filepath()} and here it is its content:
            """
        )

    print(start_message)
    print(
        dedent(
            f"""
              default_journal_folder={config_file.default_journal_folder}
              default_template_folder={config_file.default_template_folder}
              journal_data_filepath={config_file.journal_data_filepath}
              template_data_filepath={config_file.template_data_filepath}
              
              default_text_editor_path={config_file.parameters.default_text_editor_path}

              You can edit this file directly with the command: jm setup
              """
        )
    )


def get_parser(subparser_action=None):
    command_name = "init"
    command_description = (
        init_journal_manager.__doc__ if init_journal_manager.__doc__ else ""
    )
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
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

    parser.add_argument(
        "--default-journal-folder",
        type=Path,
        help="Directory where journals will be created by default",
        default=api.get_configuration_folder().joinpath("journals"),
    )
    parser.add_argument(
        "--default-template-folder",
        type=Path,
        help="Directory where journals will be created by default",
        default=api.get_configuration_folder().joinpath("templates"),
    )
    parser.add_argument(
        "--default-text-editor",
        type=Path,
        help="Path to text editor used by journal-manager by default.",
    )
    parser.set_defaults(
        subcommand_help=parser.print_help, func=__init_journal_manager__
    )

    return parser
