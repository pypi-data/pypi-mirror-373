from danoan.journal_manager.core import api, model, exceptions
from danoan.journal_manager.cli import utils
from danoan.journal_manager.cli.wrappers import mkdocs_wrapper

import argparse
from datetime import datetime
import os
from pathlib import Path
import shutil
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template


# -------------------- Helper Functions --------------------


def __create_mkdocs_from_template__(
    journal_data: model.JournalData, template: Template
):
    journal_docs_folder = Path(journal_data.location_folder).joinpath("docs")
    journal_docs_folder.mkdir()

    journal_configuration_file = Path(journal_data.location_folder).joinpath(
        "mkdocs.yml"
    )
    with open(journal_configuration_file, "w") as f:
        f.write(template.render({"journal": journal_data}))

    journal_index = journal_docs_folder.joinpath("index.md")
    with open(journal_index, "w") as f:
        f.write(f"# {journal_data.title}")


def __create_mkdocs_from_template_name__(
    journal_data: model.JournalData, template_name: str
):
    config_file = api.get_configuration_file()

    journal_template_list = model.JournalTemplateList.read(
        config_file.template_data_filepath
    )

    template_entry = api.find_template_by_name(
        journal_template_list, template_name
    )
    if not template_entry:
        raise exceptions.InvalidName()

    journal_location_path = Path(journal_data.location_folder)

    template_path = Path(template_entry.filepath)
    shutil.copytree(template_path, journal_location_path)

    if not api.is_valid_template_path(journal_location_path):
        raise exceptions.InvalidTemplate(
            msg="The journal template does not have a mkdocs.tpl.yml."
        )
    else:
        mkdocs_template_path = Path(journal_location_path).joinpath(
            "mkdocs.tpl.yml"
        )
        env = Environment(loader=FileSystemLoader(journal_location_path))
        template = env.get_template("mkdocs.tpl.yml")
        __create_mkdocs_from_template__(journal_data, template)
        os.remove(mkdocs_template_path)


# -------------------- API --------------------


def create(
    journal_title: str,
    journal_location_folder: Path,
    mkdocs_template_name: Optional[str] = None,
):
    """
    Creates a mkdocs journal file structure.

    If the JOURNAL_LOCATION_FOLDER is not given, it uses the default_journal_folder defined
    in the file pointed by the JOURNAL_MANAGER_CONFIG_FOLDER environment variable is used.

    The MKDOCS_TEMPLATE_NAME specifies a template to create the mkdocs.yml file. To see a list
    of available templates, use:

    Example:
        journal-manager setup template

    Args:
        journal_title: Name will be displayed in the html page.
        journal_location_folder: Directory where the journal files will be created.
        mkdocs_template_name (optional): The name of a template file for mkdocs.yml.
    Raises:
        InvalidName if the mkdocs_template_name is not registered.
        InvalidTemplate if the registered template does not have a mkdocs.tpl.yml file.
        InvalidLocation if the journal_location_folder is an existent directory.
    Important:
        If the journal exist already it will be overwrite.
    """
    config_file = api.get_configuration_file()

    journal_name = utils.journal_name_from_title(journal_title)
    journal_data_file = model.JournalDataList.read(
        config_file.journal_data_filepath
    )

    utils.ensure_journal_name_is_unique(journal_data_file, journal_name)

    journal_location = journal_location_folder.joinpath(
        journal_name
    ).expanduser()
    if journal_location.exists():
        raise exceptions.InvalidLocation()

    journal_data = model.JournalData(
        journal_name,
        journal_location.as_posix(),
        True,
        journal_title,
        datetime.now().isoformat(),
    )
    journal_data_file.list_of_journal_data.append(journal_data)

    if mkdocs_template_name:
        __create_mkdocs_from_template_name__(journal_data, mkdocs_template_name)
    else:
        journal_location.mkdir(parents=True)
        mkdocs_wrapper.create(journal_location)

    with open(config_file.journal_data_filepath, "w") as f:
        journal_data_file.write(f)


# -------------------- CLI --------------------


def __create__(
    journal_title: str,
    journal_location_folder: Optional[Path] = None,
    mkdocs_template_name: Optional[str] = None,
    **kwargs,
):
    utils.ensure_configuration_file_exists()
    if journal_location_folder is None:
        journal_location_folder = Path(
            api.get_configuration_file().default_journal_folder
        )

    try:
        create(journal_title, journal_location_folder, mkdocs_template_name)
    except exceptions.InvalidName:
        print(
            f"The template {mkdocs_template_name} does not exist. Please enter an existent template name"
        )
        exit(1)
    except exceptions.InvalidLocation:
        print(
            f"The journal location {journal_location_folder} exists already. Exiting."
        )
        exit(1)
    except exceptions.InvalidTemplate as ex:
        print(f"{ex.msg}. Exiting.")
        exit(1)


def get_parser(subparser_action=None):
    command_name = "create"
    command_description = create.__doc__ if create.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["c"],
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument("journal_title", help="Journal title.")
    parser.add_argument(
        "--journal-folder",
        dest="journal_location_folder",
        help=f"Location where the journal folder will be stored. If empty, the default location is chosen.",
        type=Path,
    )
    parser.add_argument(
        "--template-name",
        dest="mkdocs_template_name",
        help="Template for a mkdocs configuration file. Templates are registered via the setup subcommand.",
    )

    parser.set_defaults(subcommand_help=parser.print_help, func=__create__)

    return parser
