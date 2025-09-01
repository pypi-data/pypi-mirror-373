from danoan.journal_manager.core import api, exceptions
from danoan.journal_manager.cli import utils

import argparse
from pathlib import Path
import shutil


# -------------------- API --------------------


def remove(template_name: str):
    """
    Remove a template from the registered templates list.

    Args:
        template_name: Name of a registered template.
    """
    config_file = api.get_configuration_file()

    template_list_file = api.get_template_list_file()

    template = api.find_template_by_name(template_list_file, template_name)
    if template:
        dir_to_remove = Path(template.filepath)
        if (
            dir_to_remove.parent.as_posix()
            == config_file.default_template_folder
        ):
            shutil.rmtree(dir_to_remove)
        else:
            raise RuntimeError(
                f"I've got an unexpected path to remove: {dir_to_remove.as_posix()}. Aborting!"
            )
        template_list_file.list_of_template_data.remove(template)

        with open(
            api.get_configuration_file().template_data_filepath, "w"
        ) as f:
            template_list_file.write(f)
    else:
        raise exceptions.InvalidName()


# -------------------- CLI --------------------


def __remove_template__(template_name: str, **kwargs):
    utils.ensure_configuration_file_exists()
    try:
        remove(template_name)
    except exceptions.InvalidName:
        print(f"Template {template_name} was not found.")
    except RuntimeError as ex:
        print(ex)
        exit(1)


def get_parser(subparser_action=None):
    command_name = "remove"
    command_description = remove.__doc__ if remove.__doc__ else ""
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

    parser.add_argument("template_name", help="Template name")
    parser.set_defaults(func=__remove_template__)

    return parser
