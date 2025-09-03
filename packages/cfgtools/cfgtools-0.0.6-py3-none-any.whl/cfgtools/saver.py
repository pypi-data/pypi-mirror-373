"""
Contains methods for saving config files: _to_yaml(), _to_pickle(), etc.

NOTE: this module is private. All functions and objects are available in the main
`cfgtools` namespace - use that instead.

"""

import json
import pickle
import sys
from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import toml
import yaml

if TYPE_CHECKING:
    from ._typing import ConfigFileFormat, UnwrappedDataObj


__all__ = []


class ConfigSaver:
    """Config saver."""

    def unwrap(self) -> "UnwrappedDataObj":
        """Returns the unwrapped config data."""
        raise NotImplementedError()

    def as_ini_dict(self) -> dict:
        """Reformat the config object with `.ini` format, and returns a dict."""
        raise NotImplementedError()

    def as_toml_dict(self) -> dict:
        """Reformat the config object with `.toml` format, and returns a dict."""
        raise NotImplementedError()

    def to_yaml(
        self, path: str | Path | None = None, /, encoding: str | None = None
    ) -> None:
        """Save the config in a yaml file. See `self.save()` for more details."""
        with open(path, "w", encoding=encoding) as f:
            yaml.safe_dump(self.unwrap(), f, sort_keys=False)

    def to_pickle(self, path: str | Path | None = None, /) -> None:
        """Save the config in a pickle file. See `self.save()` for more details."""
        with open(path, "wb") as f:
            pickle.dump(self.unwrap(), f)

    def to_json(
        self, path: str | Path | None = None, /, encoding: str | None = None
    ) -> None:
        """Save the config in a json file. See `self.save()` for more details."""
        with open(path, "w", encoding=encoding) as f:
            json.dump(self.unwrap(), f)

    def to_ini(
        self, path: str | Path | None = None, /, encoding: str | None = None
    ) -> None:
        """
        Save the config in a ini file. May lose infomation to meet the
        requirements of ini format. See `self.save()` for more details.

        """
        parser = ConfigParser()
        parser.read_dict(self.as_ini_dict())
        with open(path, "w", encoding=encoding) as f:
            parser.write(f)

    def to_toml(
        self, path: str | Path | None = None, /, encoding: str | None = None
    ) -> None:
        """
        Save the config in a toml file. May lose infomation to meet the
        requirements of toml format. See `self.save()` for more details.

        """
        with open(path, "w", encoding=encoding) as f:
            toml.dump(self.as_toml_dict(), f)

    def to_text(
        self, path: str | Path | None = None, /, encoding: str | None = None
    ) -> None:
        """Save the config in a txt file. See `self.save()` for more details."""
        Path(path).write_text(json.dumps(self.unwrap()), encoding=encoding)

    def to_bytes(
        self, path: str | Path | None = None, /, encoding: str | None = None
    ) -> None:
        """Save the config in a bytes file. See `self.save()` for more details."""
        encoding = sys.getdefaultencoding() if encoding is None else encoding
        Path(path).write_bytes(bytes(json.dumps(self.unwrap()), encoding=encoding))

    def save(
        self,
        path: str | Path | None = None,
        fileformat: "ConfigFileFormat | None" = None,
        /,
        encoding: str | None = None,
    ) -> Callable[..., None]:
        """Access the saver."""
        match fileformat:
            case "pickle":
                return self.to_pickle(path)
            case "ini":
                return self.to_ini(path, encoding)
            case "json":
                return self.to_json(path, encoding)
            case "yaml":
                return self.to_yaml(path, encoding)
            case "toml":
                return self.to_toml(path, encoding)
            case "text":
                return self.to_text(path, encoding)
            case "bytes":
                return self.to_bytes(path, encoding)
            case _:
                raise FileFormatError(f"unsupported config file format: {fileformat!r}")


class FileFormatError(Exception):
    """Raised if the file format is not supported."""
