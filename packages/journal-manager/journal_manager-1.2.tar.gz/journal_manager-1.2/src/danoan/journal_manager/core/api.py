"""
Core methods that form the journal-manager api.
"""

from danoan.journal_manager.core import exceptions, model

import os
from pathlib import Path
from typing import List, Optional

ENV_JOURNAL_MANAGER_CONFIG_FOLDER = "JOURNAL_MANAGER_CONFIG_FOLDER"


# -------------------- Configuration API --------------------


def get_configuration_folder() -> Path:
    """
    Return the value stored by environment variable JOURNAL_MANAGER_CONFIG_FOLDER

    Raises:
        ConfigurationFolderDoesNotExist: if JOURNAL_MANAGER_CONFIG_FOLDER is not set.
    """
    if ENV_JOURNAL_MANAGER_CONFIG_FOLDER not in os.environ:
        raise exceptions.ConfigurationFolderDoesNotExist()

    return Path(os.environ[ENV_JOURNAL_MANAGER_CONFIG_FOLDER]).expanduser()


def get_configuration_filepath():
    """
    Return the path to the journal-manager configuration file.
    """
    return get_configuration_folder().joinpath("config.toml")


def get_configuration_file() -> model.ConfigurationFile:
    """
    Return ConfigurationFile dataclass instantiated from the configuration file.

    Raises:
        ConfigurationFileDoesNotExist: if configuration file does not exist.
    """
    if not get_configuration_filepath().exists():
        raise exceptions.ConfigurationFileDoesNotExist()

    return model.ConfigurationFile.read(get_configuration_filepath())


def get_template_list_file() -> model.JournalTemplateList:
    """
    Return JournalTemplateList dataclass instantiated from the templates register file.
    """
    config_file = get_configuration_file()
    return model.JournalTemplateList.read(config_file.template_data_filepath)


def get_journal_data_file() -> model.JournalDataList:
    """
    Return JournalDataList dataclass instantiated from the journals register file.
    """
    config_file = get_configuration_file()
    return model.JournalDataList.read(config_file.journal_data_filepath)


def create_configuration_file(
    journal_folder_default: Path, templates_folder_default: Path
):
    """
    Create journal-manager application configuration file.

    Additionally, it creates two more configuration files:
        - journal_data.toml
        - template_data.toml

    and a folder to store journal templates.

    Args:
        journal_folder_default: Default location to store journals.
        templates_folder_default: Default location to store journal templates.
        text_editor_default: Path to the default editor used by journal-manager.
    """
    get_configuration_folder().mkdir(parents=True)
    journal_folder_default.mkdir(parents=True)
    templates_folder_default.mkdir(parents=True)

    journal_data_filepath = (
        Path.expanduser(get_configuration_folder())
        .joinpath("journal_data.toml")
        .as_posix()
    )
    journal_template_data_filepath = (
        Path.expanduser(get_configuration_folder())
        .joinpath("template_data.toml")
        .as_posix()
    )

    parameters = model.Parameters()
    with open(get_configuration_filepath().as_posix(), "w") as f:
        model.ConfigurationFile(
            journal_folder_default.as_posix(),
            templates_folder_default.as_posix(),
            journal_data_filepath,
            journal_template_data_filepath,
            parameters,
        ).write(f)

    with open(journal_data_filepath, "w") as f:
        model.JournalDataList([]).write(f)

    with open(journal_template_data_filepath, "w") as f:
        model.JournalTemplateList([]).write(f)


def is_valid_template_path(template_path: Path):
    """
    Validates a journal templates folder.

    The journal template folder must contain the file mkdocs.tpl.yml.

    Args:
        template_path: The journal template folder to check.
    """
    mkdocs_template_path = Path(template_path).joinpath("mkdocs.tpl.yml")
    return mkdocs_template_path.exists()


# -------------------- Data Model Query API --------------------
def find_template_by_name(
    template_file: model.JournalTemplateList, template_name: str
) -> Optional[model.JournalTemplate]:
    """
    Search a registered template by name.

    If the template is not found, a None object is returned.

    Args:
        template_file: Dataclass representation of the journal template register file.
        template_name: Template name.
    """
    for entry in template_file.list_of_template_data:
        if entry.name == template_name:
            return entry
    return None


def find_journal(
    journal_data_file: model.JournalDataList,
    journal_components: model.JournalData,
    logic_operator: model.LogicOperator,
) -> List[model.JournalData]:
    """
    Search among the registered journals all entries that matches the query.

    The `journal_components` is an instance of JournalData. Attributes with
    a None value are not considered in the search.

    Args:
        journal_data_file: Dataclass representation of the journal register file.
        journal_components: Journal attributes being searched.
        logic_operator: If OR, all journals matching at least one attribute are returned.
                        If AND, a journal must match all attributes to be returned.
    """
    results: List[model.JournalData] = []
    for journal_data in journal_data_file.list_of_journal_data:
        potential_matches = 0
        concrete_matches = 0
        for key, value in journal_components.__dict__.items():
            if value is None:
                continue

            potential_matches += 1
            if journal_data.__dict__[key] == value:
                concrete_matches += 1

        if logic_operator == model.LogicOperator.OR:
            if concrete_matches > 0:
                results.append(journal_data)
        elif logic_operator == model.LogicOperator.AND:
            if concrete_matches == potential_matches:
                results.append(journal_data)

    return results


def find_journal_by_name(
    journal_data_file: model.JournalDataList, journal_name: str
) -> Optional[model.JournalData]:
    """
    Search a registered journal by name.

    If the journal is not found, a None object is returned.

    Args:
        journal_data_file: Dataclass representation of the journal register file.
        journal_name: Journal name.
    """
    journal_components = model.JournalData(journal_name, None, None, None, None)
    results = find_journal(
        journal_data_file, journal_components, model.LogicOperator.AND
    )
    if len(results) > 0:
        return results[0]
    else:
        return None


def find_journal_by_location(
    journal_data_file: model.JournalDataList, journal_location: str
) -> Optional[model.JournalData]:
    """
    Search a registered journal by location.

    If the journal is not found, a None object is returned.

    Args:
        journal_data_file: Dataclass representation of the journal register file.
        journal_location: Path to the journal folder.
    """
    journal_components = model.JournalData(
        None, journal_location, None, None, None
    )
    results = find_journal(
        journal_data_file, journal_components, model.LogicOperator.AND
    )
    if len(results) > 0:
        return results[0]
    else:
        return None


def update_journal(
    journal_data_file: model.JournalDataList, journal_data: model.JournalData
):
    """
    Update journal entry in the journal data file.

    Args:
        journal_data_file: Dataclass representation of the journal register file.
        journal_data: Updated journal.
    """

    for i, entry in enumerate(journal_data_file.list_of_journal_data):
        if entry.name == journal_data.name:
            journal_data_file.list_of_journal_data[i] = journal_data
            break

    with open(get_configuration_file().journal_data_filepath, "w") as f:
        journal_data_file.write(f)
