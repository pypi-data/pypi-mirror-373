from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli.wrappers import nvim_wrapper
from danoan.journal_manager.cli.commands.setup_commands import init

import argparse
from pathlib import Path
from typing import Optional

# -------------------- API --------------------


def edit_file(text_filepath: Path):
    config_file = api.get_configuration_file()
    _text_editor_path = config_file.parameters.default_text_editor_path

    if not _text_editor_path:
        raise exceptions.InvalidAttribute("No text editor was defined yet.")

    text_editor_path = Path(_text_editor_path)

    if not Path(text_editor_path).name.startswith("vim") and not Path(
        text_editor_path
    ).name.startswith("nvim"):
        raise NotImplementedError(
            "This application only knows how to start vim or nvim editors."
        )

    nvim_wrapper.edit_file(text_filepath, text_editor_path)


def edit_config_file():
    edit_file(api.get_configuration_filepath().expanduser())


def edit_journal_data_file():
    config_file = api.get_configuration_file()
    edit_file(Path(config_file.journal_data_filepath))


def edit_template_data_file():
    config_file = api.get_configuration_file()
    edit_file(Path(config_file.template_data_filepath))


# -------------------- CLI --------------------


def __open_config_file__(
    journal: Optional[bool], template: Optional[bool], **kwargs
):
    if journal:
        edit_journal_data_file()
    elif template:
        edit_template_data_file()
    else:
        edit_config_file()


def get_parser(subparser_action=None):
    command_name = "setup"
    command_description = """
    Configure journal-manager settings.

    If no sub-command is given, open the configuration file.
    """
    command_help = command_description

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["s"],
        )
    else:
        parser = argparse.ArgumentParser(
            command_name, description=command_description
        )

    list_of_commands = [init]
    subparser_action = parser.add_subparsers(title="Setup subcommands")
    for command in list_of_commands:
        command.get_parser(subparser_action)

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--journal", action="store_true", help="Open journal data file."
    )
    group.add_argument(
        "--template", action="store_true", help="Open template data file."
    )

    parser.set_defaults(
        subcommand_help=parser.print_help, func=__open_config_file__
    )

    return parser
