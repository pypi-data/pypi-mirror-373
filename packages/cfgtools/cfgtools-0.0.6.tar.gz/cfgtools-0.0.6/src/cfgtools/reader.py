"""
Contains methods for reading config files: read_yaml(), read_pickle(), etc.

NOTE: this module is private. All functions and objects are available in the main
`cfgtools` namespace - use that instead.

"""

import json
import pickle
from configparser import (
    ConfigParser,
    DuplicateSectionError,
    MissingSectionHeaderError,
    ParsingError,
)
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import toml
import yaml
from yaml import MarkedYAMLError
from yaml.reader import ReaderError

from .iowrapper import FORMAT_MAPPING, ConfigIOWrapper
from .saver import FileFormatError

if TYPE_CHECKING:
    from ._typing import ConfigFileFormat, UnwrappedDataObj

__all__ = [
    "detect_encoding",
    "read_yaml",
    "read_pickle",
    "read_json",
    "read_ini",
    "read_toml",
    "read_text",
    "read_bytes",
]


def detect_encoding(path: str | Path) -> str:
    """
    Detect the encoding of a file.

    Parameters
    ----------
    path : str | Path
        File path.

    Returns
    -------
    str
        The name of the encoding used to encode the file.

    """
    with open(path, "rb") as f:
        test_line = f.readline()
    return json.detect_encoding(test_line)


def read_yaml(path: str | Path, /, encoding: str | None = None) -> ConfigIOWrapper:
    """
    Read a yaml file.

    Parameters
    ----------
    path : str | Path
        Path of the yaml file.
    encoding : str | None, optional
        The name of the encoding used to decode or encode the file,
        by default None.

    Returns
    --------
    ConfigIOWrapper
        A wrapper for reading and writing config files.

    """
    encoding = detect_encoding(path) if encoding is None else encoding
    with open(path, "r", encoding=encoding) as f:
        cfg = yaml.safe_load(f)
    return ConfigIOWrapper(cfg, "yaml", path=path, encoding=encoding)


def read_pickle(path: str | Path, /) -> ConfigIOWrapper:
    """
    Read a pickle file.

    Parameters
    ----------
    path : str | Path
        Path of the pickle file.

    Returns
    --------
    ConfigIOWrapper
        A wrapper for reading and writing config files.

    """
    with open(path, "rb") as f:
        cfg = pickle.load(f)
    return ConfigIOWrapper(cfg, "pickle", path=path)


def read_json(path: str | Path, /, encoding: str | None = None) -> ConfigIOWrapper:
    """
    Read a json file.

    Parameters
    ----------
    path : str | Path
        Path of the json file.
    encoding : str | None, optional
        The name of the encoding used to decode or encode the file,
        by default None.

    Returns
    --------
    ConfigIOWrapper
        A wrapper for reading and writing config files.

    """
    encoding = detect_encoding(path) if encoding is None else encoding
    with open(path, "r", encoding=encoding) as f:
        cfg = json.load(f)
    return ConfigIOWrapper(cfg, "json", path=path, encoding=encoding)


def read_ini(path: str | Path, /, encoding: str | None = None) -> ConfigIOWrapper:
    """
    Read an ini file.

    Parameters
    ----------
    path : str | Path
        Path of the ini file.
    encoding : str | None, optional
        The name of the encoding used to decode or encode the file,
        by default None.

    Returns
    --------
    ConfigIOWrapper
        A wrapper for reading and writing config files.

    """
    encoding = detect_encoding(path) if encoding is None else encoding
    parser = ConfigParser()
    parser.read(path, encoding=encoding)
    obj = {
        s: {o: _obj_restore(parser.get(s, o)) for o in parser.options(s)}
        for s in parser.sections()
    }
    if len(obj) == 1 and "null" in obj:
        obj = obj["null"]
        if len(obj) == 1 and "null" in obj:
            obj = obj["null"]
    return ConfigIOWrapper(obj, "ini", path=path, encoding=encoding)


def read_toml(path: str | Path, /, encoding: str | None = None) -> ConfigIOWrapper:
    """
    Read a toml file.

    Parameters
    ----------
    path : str | Path
        Path of the toml file.
    encoding : str | None, optional
        The name of the encoding used to decode or encode the file,
        by default None.

    Returns
    --------
    ConfigIOWrapper
        A wrapper for reading and writing config files.

    """
    encoding = detect_encoding(path) if encoding is None else encoding
    with open(path, "r", encoding=encoding) as f:
        obj = toml.load(f)
    if len(obj) == 1 and "null" in obj:
        obj = obj["null"]
    return ConfigIOWrapper(obj, "toml", path=path, encoding=encoding)


def read_text(path: str | Path, /, encoding: str | None = None) -> ConfigIOWrapper:
    """
    Read plain text from a text file.

    Parameters
    ----------
    path : str | Path
        Path of the text file.
    encoding : str | None, optional
        The name of the encoding used to decode or encode the file,
        by default None.

    Returns
    --------
    ConfigIOWrapper
        A wrapper for reading and writing config files.

    """
    encoding = detect_encoding(path) if encoding is None else encoding
    cfg = Path(path).read_text(encoding=encoding)
    return ConfigIOWrapper(cfg, "text", path=path, encoding=encoding)


def read_bytes(path: str | Path, /, encoding: str | None = None) -> ConfigIOWrapper:
    """
    Read bytes from a bytes file.

    Parameters
    ----------
    path : str | Path
        Path of the bytes file.
    encoding : str | None, optional
        The name of the encoding used to decode or encode the file,
        by default None.

    Returns
    --------
    ConfigIOWrapper
        A wrapper for reading and writing config files.

    """
    encoding = detect_encoding(path) if encoding is None else encoding
    cfg = Path(path).read_bytes().decode(encoding)
    return ConfigIOWrapper(cfg, "bytes", path=path, encoding=encoding)


def _obj_restore(string: str) -> "UnwrappedDataObj":
    try:
        return json.loads(string)
    except json.JSONDecodeError:
        return string
    except UnicodeDecodeError:
        return string


class ConfigReader:
    """Config reader."""

    reader_mapping: dict[str, Callable[..., ConfigIOWrapper]] = {
        "pickle": read_pickle,
        "ini": read_ini,
        "json": read_json,
        "yaml": read_yaml,
        "toml": read_toml,
        "text": read_text,
        "bytes": read_bytes,
    }

    @classmethod
    def read(
        cls,
        path: str | Path,
        fileformat: "ConfigFileFormat | None" = None,
        /,
        encoding: str | None = None,
    ) -> ConfigIOWrapper:
        """Read from the config file."""
        if fileformat is None:
            return cls.autoread(path, encoding=encoding)
        encoding = detect_encoding(path) if encoding is None else encoding
        if fileformat not in FORMAT_MAPPING:
            raise FileFormatError(f"unsupported config file format: {fileformat!r}")
        return cls.reader_mapping[FORMAT_MAPPING[fileformat]](path, encoding=encoding)

    @classmethod
    def autoread(
        cls, path: str | Path, /, encoding: str | None = None
    ) -> ConfigIOWrapper:
        """Read from the config file, automatically detecting the fileformat."""
        encoding = detect_encoding(path) if encoding is None else encoding
        try_methods: tuple[Callable[..., ConfigIOWrapper | None]] = (
            cls.__try_pickle,
            cls.__try_ini,
            cls.__try_json,
            cls.__try_yaml,
            cls.__try_toml,
            cls.__try_text,
        )
        for m in try_methods:
            if (wrapper := m(path, encoding=encoding)) is not None:
                return wrapper
        raise FileFormatError(f"failed to read the config file: '{path}'")

    @staticmethod
    def __try_pickle(
        path: str | Path, /, encoding: str | None = None
    ) -> ConfigIOWrapper | None:
        _ = encoding
        try:
            return read_pickle(path)
        except pickle.UnpicklingError:
            return None

    @staticmethod
    def __try_ini(
        path: str | Path, /, encoding: str | None = None
    ) -> ConfigIOWrapper | None:
        try:
            return read_ini(path, encoding=encoding)
        except (MissingSectionHeaderError, ParsingError, DuplicateSectionError):
            return None

    @staticmethod
    def __try_json(
        path: str | Path, /, encoding: str | None = None
    ) -> ConfigIOWrapper | None:
        try:
            return read_json(path, encoding=encoding)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def __try_yaml(
        path: str | Path, /, encoding: str | None = None
    ) -> ConfigIOWrapper | None:
        try:
            return read_yaml(path, encoding=encoding)
        except (ReaderError, MarkedYAMLError):
            return None

    @staticmethod
    def __try_toml(
        path: str | Path, /, encoding: str | None = None
    ) -> ConfigIOWrapper | None:
        try:
            return read_toml(path, encoding=encoding)
        except (ReaderError, MarkedYAMLError):
            return None

    @staticmethod
    def __try_text(
        path: str | Path, /, encoding: str | None = None
    ) -> ConfigIOWrapper | None:
        return read_text(path, encoding=encoding)
