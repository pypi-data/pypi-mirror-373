from danoan.journal_manager.core import api, model
from danoan.journal_manager.cli import utils

import argparse
from pathlib import Path
import shutil
import subprocess


# -------------------- API --------------------


def register(template_name: str, template_path: Path):
    """
    Register a journal template.

    A minimal journal template is composed of a mkdocs.yml file with
    optional placeholders. For example

    site_name: {{journal.title}}
    theme: material

    The placeholders follow the jinja2 package syntax.
    Here is the list of available placeholders:

    - {{journal.title}}
    - {{journal.name}}
    - {{journal.location_folder}}
    - {{journal.active}}

    A journal template could have as many files as necessary
    and an arbitrary folder structure.

    The template should be given as a path to the folder that
    contains the files that define the template. These files
    will be copied for each instance of journal that make use
    of that template.

    Args:
        template_name: Name of the template to be registered.
        template_path: Path to a directory containing the template files.
    """
    config_file = api.get_configuration_file()

    if not template_path.exists():
        print(f"The path: {template_path} does not exist.")
        exit(1)

    if not api.is_valid_template_path(template_path):
        print(
            f"The template path: {template_path} does not contain a mkdocs.tpl.yml file."
        )
        exit(1)

    target_template_path = Path(config_file.default_template_folder).joinpath(
        template_name
    )
    target_template_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_path, target_template_path)

    requirements_filepath = template_path / "requirements.txt"
    if requirements_filepath.exists():
        proc_args = ["pip", "install", "-r", str(requirements_filepath)]
        subprocess.run(proc_args)

    template_data = model.JournalTemplate(
        template_name, target_template_path.expanduser().as_posix()
    )
    template_list_file = api.get_template_list_file()
    template_list_file.list_of_template_data.append(template_data)

    with open(api.get_configuration_file().template_data_filepath, "w") as f:
        template_list_file.write(f)


# -------------------- CLI --------------------


def __register_template__(template_name: str, template_path: str, **kwargs):
    utils.ensure_configuration_file_exists()
    register(template_name, Path(template_path))


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
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument("template_name", help="The name of the template.")
    parser.add_argument(
        "template_path",
        help="Path to a directory containing the template structure.",
    )
    parser.set_defaults(func=__register_template__)

    return parser
