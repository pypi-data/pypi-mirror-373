"""
Exceptions raised by journal-manager api.
"""

from pathlib import Path
from typing import Optional, Iterable, Union


class ConfigurationFileDoesNotExist(BaseException):
    pass


class ConfigurationFolderDoesNotExist(BaseException):
    pass


class EmptyList(BaseException):
    pass


class InvalidName(Exception):
    def __init__(self, names: Iterable[str] = []):
        self.names = names


class InvalidLocation(Exception):
    def __init__(self, locations: Union[Iterable[Path], Path] = []):
        self.locations = locations

    def __iter__(self):
        if isinstance(self.locations, Path):
            yield self.locations
        else:
            return self.locations.__iter__()


class InvalidIncludeAllFolder(Exception):
    def __init__(self, path: Optional[str] = None):
        self.path = path


class InvalidTemplate(Exception):
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg


class InvalidAttribute(Exception):
    def __init__(self, msg: Optional[str] = None):
        self.msg = msg
