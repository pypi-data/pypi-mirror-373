from danoan.journal_manager.core import api, exceptions, model

import itertools
from pathlib import Path
import re
from textwrap import dedent
from typing import Iterator, Any, Tuple


# -------------------- "Termination Criteria" --------------------
def ensure_configuration_folder_exists():
    """
    Exit application if configuration folder does not exist.
    """
    try:
        api.get_configuration_folder()
    except exceptions.ConfigurationFolderDoesNotExist:
        print(
            dedent(
                f"""
                    There is no environment variable set for journal-manager.
                    Create the environment variable {api.ENV_JOURNAL_MANAGER_CONFIG_FOLDER} and try again

                    Example:
                    export JOURNAL_MANAGER_CONFIG_FOLDER={Path.home().joinpath(".config","journal-manager")}
                    """
            )
        )
        exit(1)
    except Exception:
        print(
            f"Unexpected error while retrieving {api.ENV_JOURNAL_MANAGER_CONFIG_FOLDER}."
        )
        exit(1)


def ensure_configuration_file_exists():
    """
    Exit application if configuration file does not exist.
    """
    try:
        api.get_configuration_file()
    except exceptions.ConfigurationFileDoesNotExist:
        print(
            dedent(
                """
                The configuration file for journal-manager does not exist. 
                You can create one with the command: journal-manager setup init
                """
            )
        )
        exit(1)
    except Exception:
        print("Unexpected error while retrieving the configuration file.")
        exit(1)


def ensure_journal_name_is_unique(
    journal_data_file: model.JournalDataList, journal_name: str
):
    """
    Exit application if journal name exist already.
    """
    for entry in journal_data_file.list_of_journal_data:
        if entry.name == journal_name:
            print(
                f"A journal with name {journal_name} is registered already. Please, choose a different name."
            )
            exit(1)


def peek_is_empty(iterator: Iterator[Any]) -> Tuple[bool, Iterator[Any]]:
    """
    Check for emptiness of the first element without advancing the iterator.
    """
    try:
        first = next(iterator)
    except StopIteration:
        return True, iterator
    return False, itertools.chain([first], iterator)


# -------------------- "Text Processing" --------------------
def journal_name_from_title(journal_title: str) -> str:
    """
    Return a lower-kebab-case version from a capitalized whitespace separated string.
    """
    return re.sub(r"[\s]+", "-", journal_title.lower().strip())


def journal_title_from_name(journal_name: str) -> str:
    """
    Return a capitalized whitespace separted from a lower-snake-case version of a string.
    """
    return re.sub(r"-", " ", journal_name).capitalize()
