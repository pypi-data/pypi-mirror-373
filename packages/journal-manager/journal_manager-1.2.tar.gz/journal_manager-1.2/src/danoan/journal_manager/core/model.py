"""
Data model for journal-manager api.
"""

from danoan.toml_dataclass import TomlDataClassIO, TomlTableDataClassIO

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, TypeVar, Type, Dict, Any


class LogicOperator(Enum):
    OR = 0
    AND = 1


@dataclass
class Parameters(TomlDataClassIO):
    default_text_editor_path: Optional[str] = None


@dataclass
class ConfigurationFile(TomlDataClassIO):
    T = TypeVar("T", bound="ConfigurationFile")

    default_journal_folder: str
    default_template_folder: str

    journal_data_filepath: str
    template_data_filepath: str
    parameters: Parameters

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> T:
        d["parameters"] = Parameters(**d["parameters"])
        return cls(**d)

    def as_dict(self) -> Dict[str, Any]:
        d = self.__dict__
        d["parameters"] = d["parameters"].as_dict()

        return d


@dataclass
class JournalData(TomlDataClassIO):
    name: str
    location_folder: str
    active: bool
    title: str
    last_edit_date: str


@dataclass
class JournalDataList(TomlTableDataClassIO):
    list_of_journal_data: List[JournalData]


@dataclass
class JournalTemplate(TomlDataClassIO):
    name: str
    filepath: str


@dataclass
class JournalTemplateList(TomlTableDataClassIO):
    list_of_template_data: List[JournalTemplate]


@dataclass
class BuildInstructions(TomlDataClassIO):
    build_location: Optional[str] = None

    build_index: bool = True
    build_inactive: bool = False
    with_http_server: bool = False

    journals_names_to_build: Optional[List[str]] = None
    journals_locations_to_build: Optional[List[str]] = None
    include_all_folder: Optional[str] = None
