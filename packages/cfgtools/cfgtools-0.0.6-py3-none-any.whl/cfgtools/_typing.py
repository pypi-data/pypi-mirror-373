"""
Contains typing classes.

NOTE: this module is not intended to be imported at runtime.

"""

from typing import TYPE_CHECKING, Callable, Literal

import loggings

from .basic import BasicWrapper
from .templatelib import Flag

if TYPE_CHECKING:
    from .iowrapper import ConfigIOWrapper

loggings.warning("this module is not intended to be imported at runtime")

BasicObj = str | int | float | bool | None | type | Callable | Flag
UnwrappedDataObj = (
    dict[BasicObj, "UnwrappedDataObj"] | list["UnwrappedDataObj"] | BasicObj
)
DataObj = dict[BasicObj, "DataObj"] | list["DataObj"] | BasicObj | BasicWrapper
ConfigFileFormat = Literal[
    "yaml", "yml", "pickle", "pkl", "json", "ini", "text", "txt", "bytes"
]
ColorScheme = Literal["dark", "modern", "high-intensty"]
WrapperStatus = Literal["", "a", "d", "r"]
