"""
Contains basic class: BasicWrapper.

NOTE: this module is private. All functions and objects are available in the main
`cfgtools` namespace - use that instead.

"""

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Iterator, Self

from htmlmaster import HTMLTreeMaker

from .css import TREE_CSS_STYLE

if TYPE_CHECKING:
    from ._typing import BasicObj, ColorScheme, DataObj, UnwrappedDataObj, WrapperStatus
    from .iowrapper import ConfigIOWrapper


__all__ = ["MAX_LINE_WIDTH", "ANY", "RETURN", "YIELD", "NEVER"]


MAX_LINE_WIDTH = 88


@dataclass(unsafe_hash=True)
class Flag:
    """Config flags."""

    name: str

    def __repr__(self) -> str:
        return self.name


ANY = Flag("ANY")
RETURN = Flag("RETURN")
YIELD = Flag("YIELD")
NEVER = Flag("NEVER")


class BasicWrapper:
    """
    A wrapper for objects.

    Parameters
    ----------
    data : DataObj
        Data before wrapping.

    Raises
    ------
    TypeError
        Raised if the data has invalid type.

    """

    valid_types = ()
    constructor = object
    sub_constructors = {
        dict: lambda: DictBasicWrapper,
        list: lambda: ListBasicWrapper,
    }

    def __new__(cls, data: "DataObj", *args, **kwargs) -> Self:
        if isinstance(data, cls):
            return data
        if isinstance(data, dict):
            new_class = cls.sub_constructors[dict]()
        elif isinstance(data, list):
            new_class = cls.sub_constructors[list]()
        elif isinstance(data, cls.valid_types):
            new_class = cls
        else:
            raise TypeError(f"invalid type of data: {data.__class__.__name__!r}")
        return cls.constructor.__new__(new_class)

    def __init__(self, data: "DataObj") -> None:
        self.__status: "WrapperStatus" = ""
        self.__replaced_value = None
        if isinstance(data, self.__class__):
            return
        if not isinstance(data, (dict, list)):
            self.__obj = data

    def __getitem__(self, key: "BasicObj", /) -> Self:
        raise TypeError(f"{self.__desc()} is not subscriptable")

    def __setitem__(self, key: "BasicObj", value: "DataObj", /) -> None:
        raise TypeError(f"{self.__desc()} does not support item assignment")

    def __delitem__(self, key: "BasicObj", /) -> None:
        raise TypeError(f"cannot delete {self.__desc()}")

    def __repr__(self) -> str:
        return f"cfgtools.BasicWrapper({self.repr()})"

    def _repr_mimebundle_(self, *_, **__) -> dict[str, str]:
        return {"text/html": self.to_html().make()}

    def __str__(self) -> str:
        return self.repr()

    def __len__(self) -> int:
        raise TypeError(f"{self.__desc()} has no len()")

    def __contains__(self, key: "BasicObj", /) -> bool:
        raise TypeError(f"{self.__desc()} is not iterable")

    def __iter__(self) -> Iterator[Self]:
        raise TypeError(f"{self.__desc()} is not iterable")

    def __bool__(self) -> bool:
        return True

    def __eq__(self, value: Self, /) -> bool:
        return isinstance(value, self.__class__) and self.unwrap() == value.unwrap()

    def repr(self, level: int = 0, is_change_view: bool = False, /) -> str:
        """Represent self."""
        return repr(self.__obj) if level >= 0 else self.repr_flat(is_change_view)

    def repr_flat(self, is_change_view: bool = False, /) -> tuple[int, str]:
        """Represent self in one line."""
        _, string = is_change_view, repr(self.__obj)
        return len(string), string

    def view_change(self, color_scheme: "ColorScheme" = "dark") -> "ChangeView":
        """View the change of self since initialized."""
        _ = color_scheme
        return ChangeView(self.repr(0, True), self.to_html())

    def keys(self) -> "Iterable[BasicObj]":
        """If the data is a mapping, provide a view of its wrapped keys."""
        raise TypeError(f"{self.__desc()} has no method keys()")

    def values(self) -> Iterable[Self]:
        """If the data is a mapping, provide a view of its wrapped values."""
        raise TypeError(f"{self.__desc()} has no method values()")

    def items(self) -> Iterable[tuple["BasicObj", Self]]:
        """If the data is a mapping, provide a view of its wrapped items."""
        raise TypeError(f"{self.__desc()} has no method items()")

    def append(self, obj: "DataObj", /) -> None:
        """If the data is a list, append to its end."""
        raise TypeError(f"{self.__desc()} has no method append()")

    def extend(self, iterable: "Iterable[DataObj]", /) -> None:
        """If the data is a list, extend it."""
        raise TypeError(f"{self.__desc()} has no method extend()")

    def copy(self) -> Self:
        """Copy an instance of self."""
        constructor = self.__class__ if self.constructor is object else self.constructor
        return constructor(self.unwrap())

    def unwrap(self) -> "UnwrappedDataObj":
        """Returns the unwrapped data."""
        return self.__obj

    def unwrap_top_level(self) -> "DataObj":
        """Returns the data, with only the top level unwrapped."""
        return self.__obj

    def isinstance(self, cls: type | list[type]) -> bool:
        """Returns whether config is an instance of cls."""
        return isinstance(self.__obj, cls)

    def get_type(self) -> type:
        """Config type."""
        return self.__obj.__class__

    def asdict(self) -> dict["BasicObj", "UnwrappedDataObj"]:
        """Returns the unwrapped data if it's a mapping."""
        raise TypeError(f"{self.__desc()} can't be converted into a dict")

    def aslist(self) -> list["UnwrappedDataObj"]:
        """Returns the unwrapped data if it's a list."""
        raise TypeError(f"{self.__desc()} can't be converted into a list")

    def to_html(self) -> HTMLTreeMaker:
        """Return an HTMLTreeMaker object for representing self."""
        maker = self.get_html_node()
        maker.setcls("t")
        main_maker = HTMLTreeMaker()
        main_maker.add(maker)
        main_maker.setstyle(TREE_CSS_STYLE)
        main_maker.set_maincls("cfgtools-tree")
        return main_maker

    def get_html_node(self) -> HTMLTreeMaker:
        """
        Return a plain HTMLTreeMaker object for representing the current
        node.

        """
        return HTMLTreeMaker(repr(self.__obj).replace(">", "&gt").replace("<", "&lt"))

    def get_max_line_width(self) -> int:
        """Get the module variable `MAX_LINE_WIDTH`."""
        return getattr(sys.modules[__name__.rpartition(".")[0]], "MAX_LINE_WIDTH")

    def recover(self) -> None:
        """Recover the original data."""
        self.__status = ""

    def delete(self) -> None:
        """Delete self."""
        self.recover()
        self.__status = "d"

    def mark_as_added(self) -> None:
        """Mark self as added."""
        self.recover()
        self.__status = "a"

    def mark_as_replaced(self, value: "BasicWrapper", /) -> None:
        """Mark self as replaced."""
        self.recover()
        if r := value.replaced_value():
            self.__replaced_value = r
        else:
            value.delete()
            self.__replaced_value = value
        self.__status = "r"

    def is_deleted(self) -> bool:
        """If self is marked as deleted."""
        return self.__status == "d"

    def is_present(self) -> bool:
        """If self is marked as deleted."""
        return self.__status != "d"

    def replaced_value(self) -> "BasicWrapper | None":
        """Return the replaced value if exists."""
        if self.__status == "r":
            return self.__replaced_value
        return None

    def get_status(self) -> "WrapperStatus":
        """Get status."""
        return self.__status

    def has_flag(self, flag: Flag, /) -> bool:
        """Returns whether the template includes template flags."""
        return self.__obj == flag

    def replace_flags(
        self, recorder: dict[str, "DataObj"] | None = None, /
    ) -> dict[str, "DataObj"]:
        """Replace all the template flags with callables."""
        if recorder is None:
            recorder = {}
        if self.__obj is Ellipsis:
            self.__obj = ANY
        if not isinstance(self.__obj, Flag):
            return recorder

        if self.__obj == ANY:
            self.__obj = lambda x: True
        elif self.__obj == NEVER:
            self.__obj = lambda x: False
        elif self.__obj == RETURN:
            self.__obj = lambda x: bool(recorder.setdefault("RETURN", x)) or True
        elif self.__obj == YIELD:
            self.__obj = (
                lambda x: bool(recorder.update(YIELD=recorder.get("YIELD", []) + [x]))
                or True
            )
        return recorder

    def __desc(self) -> str:
        return f"config of {self.get_type()}"


class DictBasicWrapper(BasicWrapper):
    """Wrapper of dict."""

    constructor = BasicWrapper
    sub_constructors = {}

    def __init__(self, obj: "DataObj", *args, **kwargs) -> None:
        super().__init__(obj, *args, **kwargs)
        new_obj: dict["BasicObj", BasicWrapper] = {}
        for k, v in obj.items():
            if not isinstance(k, self.valid_types):
                raise TypeError(f"invalid type of key: {k.__class__.__name__!r}")
            if isinstance(v, self.constructor):
                new_obj[k] = v
            else:
                new_obj[k] = self.constructor(v)
        self.__obj = new_obj

    def __getitem__(self, key: "BasicObj", /) -> Self:
        value = self.__obj[key]
        if value.is_deleted():
            raise KeyError(f"{key!r}")
        return value

    def __setitem__(self, key: "BasicObj", value: "DataObj", /) -> None:
        if not isinstance(value, self.constructor):
            value = self.constructor(value)
        if key in self.__obj:
            if r := self.__obj[key].replaced_value():
                value.mark_as_replaced(r)
            else:
                value.mark_as_replaced(self.__obj[key])
        else:
            value.mark_as_added()
        self.__obj[key] = value

    def __delitem__(self, key: "BasicObj", /) -> None:
        self.__obj[key].delete()

    def __len__(self) -> int:
        return len(self.unwrap_top_level())

    def __contains__(self, key: "BasicObj", /) -> bool:
        if key in self.__obj and self.__obj[key].is_present():
            return True
        return False

    def __iter__(self) -> Iterator[Self]:
        return iter(self.unwrap_top_level())

    def repr(self, level: int = 0, is_change_view: bool = False, /) -> str:
        if level == 0:
            lenflat, flat = self.repr_flat(is_change_view)
            if lenflat <= self.get_max_line_width():
                return flat
        seps = _sep(level + 1)
        lines: list[str] = []
        max_line_width = self.get_max_line_width()
        for k, v in self.__obj.items():
            self.__repr_line(k, v, is_change_view, seps, max_line_width, level, lines)
        string = "{\n" + "\n".join(lines) + f"\n{_sep(level)}" "}"
        return string

    def __repr_line(
        self,
        k: "BasicObj",
        v: BasicWrapper,
        is_change_view: bool,
        seps: str,
        max_line_width: int,
        level: int,
        lines: list[str],
    ) -> None:
        if is_change_view:
            _status = v.get_status()
        else:
            if v.is_deleted():
                return
            _status = ""
        if _status == "r":
            self.__repr_line(
                k,
                v.replaced_value(),
                is_change_view,
                seps,
                max_line_width,
                level,
                lines,
            )
            _status = "a"
        _head = lines[-1] if lines else ""
        _key = f"{k!r}: "
        _lenflat, _flat = v.repr_flat(is_change_view)
        if lines and (len(_head) + len(_key) + _lenflat + 2 <= max_line_width):
            lines[-1] += colorful_console(f" {_key}{_flat},", _status)
        elif len(seps) + len(_key) + _lenflat < max_line_width:
            lines.append(colorful_console(f"{seps}{_key}{_flat},", _status))
        else:
            _child = v.repr(level + 1, is_change_view)
            lines.append(colorful_console(f"{seps}{_key}{_child},", _status))

    def repr_flat(self, is_change_view: bool = False, /) -> tuple[int, str]:
        if not is_change_view:
            string = repr(self.unwrap())
            return len(string), string
        lines: list[str] = []
        maxi = len(self.__obj)
        length = 0
        for i, item in enumerate(self.__obj.items()):
            k, v = item
            _status = v.get_status()
            _lenr, _r = v.replaced_value().repr_flat() if _status == "r" else (0, "")
            _key = f"{k!r}: "
            _lenflat, _flat = v.repr_flat(True)
            if _status == "r":
                _lenflat += len(_key) + _lenr + 2
            if maxi <= 1:
                lines.append(
                    colorful_console(f"{_key}{_flat}", _status, f"{_key}{_r}, ")
                )
                length += len(_key) + _lenflat
            elif i == 0:
                lines.append(
                    colorful_console(f"{_key}{_flat},", _status, f"{_key}{_r}, ")
                )
                length += len(_key) + _lenflat + 1
            elif i < maxi - 1:
                lines.append(
                    colorful_console(f" {_key}{_flat},", _status, f" {_key}{_r},")
                )
                length += len(_key) + _lenflat + 2
            else:
                lines.append(
                    colorful_console(f" {_key}{_flat}", _status, f" {_key}{_r},")
                )
                length += len(_key) + _lenflat + 1
        string = "{" + "".join(lines) + "}"
        return length, string

    def keys(self) -> Iterable["BasicObj"]:
        return self.unwrap_top_level().keys()

    def values(self) -> Iterable[Self]:
        return self.unwrap_top_level().values()

    def items(self) -> Iterable[tuple["BasicObj", Self]]:
        return self.unwrap_top_level().items()

    def unwrap(self) -> "UnwrappedDataObj":
        return {k: v.unwrap() for k, v in self.__obj.items() if v.is_present()}

    def unwrap_top_level(self) -> "DataObj":
        return {k: v for k, v in self.__obj.items() if v.is_present()}

    def isinstance(self, cls: type) -> bool:
        return isinstance(self.__obj, cls)

    def get_type(self) -> type:
        return self.__obj.__class__

    def asdict(self) -> dict["BasicObj", "UnwrappedDataObj"]:
        return self.unwrap()

    def get_html_node(self) -> HTMLTreeMaker:
        if len(flat := repr(self.unwrap())) <= self.get_max_line_width():
            return HTMLTreeMaker(flat)
        maker = HTMLTreeMaker('{<span class="closed"> ... }</span>')
        for k, v in self.items():
            node = v.get_html_node()
            if node.has_child():
                node.setval(f"{k!r}: {node.getval()}")
                tail = node.get(-1)
                tail.setval(f"{tail.getval()},")
            else:
                node.setval(f"{k!r}: {node.getval()},")
            maker.add(node)
        maker.add("}", "t")
        return maker

    def recover(self) -> None:
        super().recover()
        for k, v in self.__obj.items():
            match v.get_status():
                case "a":
                    del self.__obj[k]
                case "r":
                    self.__obj[k] = v.replaced_value()
                    self.__obj[k].recover()
                case _:
                    v.recover()

    def has_flag(self, flag: Flag, /) -> bool:
        return any(k == flag or v.has_flag(flag) for k, v in self.items())

    def replace_flags(
        self, recorder: dict[str, "DataObj"] | None = None, /
    ) -> dict[str, "DataObj"]:
        if recorder is None:
            recorder = {}

        for v in self.values():
            v.replace_flags(recorder)

        return recorder


class ListBasicWrapper(BasicWrapper):
    """Wrapper of list."""

    constructor = BasicWrapper
    sub_constructors = {}

    def __init__(self, obj: "DataObj", *args, **kwargs) -> None:
        super().__init__(obj, *args, **kwargs)
        new_obj: list[BasicWrapper] = []
        for x in obj:
            if isinstance(x, self.constructor):
                new_obj.append(x)
            else:
                new_obj.append(self.constructor(x))
        self.__obj = new_obj

    def __getitem__(self, key: int, /) -> Self:
        value = self.__obj[key]
        if value.is_deleted():
            raise KeyError(f"{key!r}")
        return value

    def __setitem__(self, key: int, value: "DataObj", /) -> None:
        if not isinstance(value, self.constructor):
            value = self.constructor(value)
        if r := self.__obj[key].replaced_value():
            value.mark_as_replaced(r)
        else:
            value.mark_as_replaced(self.__obj[key])
        self.__obj[key] = value

    def __delitem__(self, key: int, /) -> None:
        self.__obj[key].delete()

    def __len__(self) -> int:
        return len(self.unwrap_top_level())

    def __contains__(self, value: "BasicObj", /) -> bool:
        return value in self.unwrap_top_level()

    def __iter__(self) -> Iterator[Self]:
        return iter(self.unwrap_top_level())

    def repr(self, level: int = 0, is_change_view: bool = False, /) -> str:
        if level == 0:
            lenflat, flat = self.repr_flat(is_change_view)
            if lenflat <= self.get_max_line_width():
                return flat
        seps = _sep(level + 1)
        lines: list[str] = []
        max_line_width = self.get_max_line_width()
        for x in self.__obj:
            self.__repr_line(x, is_change_view, seps, max_line_width, level, lines)
        string = "[\n" + "\n".join(lines) + f"\n{_sep(level)}" + "]"
        return string

    def __repr_line(
        self,
        x: BasicWrapper,
        is_change_view: bool,
        seps: str,
        max_line_width: int,
        level: int,
        lines: list[str],
    ) -> None:
        if is_change_view:
            _status = x.get_status()
        else:
            if x.is_deleted():
                return
            _status = ""
        if _status == "r":
            self.__repr_line(
                x.replaced_value(), is_change_view, seps, max_line_width, level, lines
            )
            _status = "a"
        _head = lines[-1] if lines else ""
        _lenflat, _flat = x.repr_flat(is_change_view)
        if lines and (len(_head) + _lenflat + 2 <= max_line_width):
            lines[-1] += colorful_console(f" {_flat},", _status)
        elif len(seps) + _lenflat < max_line_width:
            lines.append(colorful_console(f"{seps}{_flat},", _status))
        else:
            _child = x.repr(level + 1, is_change_view)
            lines.append(colorful_console(f"{seps}{_child},", _status))

    def repr_flat(self, is_change_view: bool = False, /) -> tuple[int, str]:
        if not is_change_view:
            string = repr(self.unwrap())
            return len(string), string
        lines: list[str] = []
        maxi = len(self.__obj)
        length = 0
        for i, x in enumerate(self.__obj):
            _status = x.get_status()
            _lenr, _r = x.replaced_value().repr_flat() if _status == "r" else (0, "")
            _lenflat, _flat = x.repr_flat(True)
            if _status == "r":
                _lenflat += _lenr + 2
            if maxi <= 1:
                lines.append(colorful_console(_flat, _status, f"{_r}, "))
                length += _lenflat
            elif i == 0:
                lines.append(colorful_console(f"{_flat},", _status, f"{_r}, "))
                length += _lenflat + 1
            elif i < maxi - 1:
                lines.append(colorful_console(f" {_flat},", _status, f" {_r},"))
                length += _lenflat + 2
            else:
                lines.append(colorful_console(f" {_flat}", _status, f" {_r},"))
                length += _lenflat + 1
        string = "[" + "".join(lines) + "]"
        return length, string

    def append(self, obj: "DataObj", /) -> None:
        if not isinstance(obj, self.constructor):
            obj = self.constructor(obj)
        obj.mark_as_added()
        self.__obj.append(obj)

    def extend(self, iterable: Iterable["DataObj"], /) -> None:
        if not isinstance(iterable, self.__class__):
            iterable = self.constructor(list(iterable))
        for x in iterable:
            x.mark_as_added()
        self.__obj.extend(list(iterable))

    def unwrap(self) -> "UnwrappedDataObj":
        return [x.unwrap() for x in self.__obj if x.is_present()]

    def unwrap_top_level(self) -> "DataObj":
        return [x for x in self.__obj if x.is_present()]

    def isinstance(self, cls: type) -> bool:
        return isinstance(self.__obj, cls)

    def get_type(self) -> type:
        return self.__obj.__class__

    def aslist(self) -> list["UnwrappedDataObj"]:
        return self.unwrap()

    def get_html_node(self) -> HTMLTreeMaker:
        if len(flat := repr(self.unwrap())) <= self.get_max_line_width():
            return HTMLTreeMaker(flat)
        maker = HTMLTreeMaker('[<span class="closed"> ... ]</span>')
        for x in self:
            node = x.get_html_node()
            if node.has_child():
                node.setval(f"{node.getval()}")
                tail = node.get(-1)
                tail.setval(f"{tail.getval()},")
            else:
                node.setval(f"{node.getval()},")
            maker.add(node)
        maker.add("]", "t")
        return maker

    def recover(self) -> None:
        super().recover()
        for i, x in enumerate(self.__obj):
            match x.get_status():
                case "a":
                    del self.__obj[i]
                case "r":
                    self.__obj[i] = x.replaced_value()
                    self.__obj[i].recover()
                case _:
                    x.recover()

    def has_flag(self, flag: Flag, /) -> bool:
        return any(x.has_flag() for x in self)

    def replace_flags(
        self, recorder: dict[str, "DataObj"] | None = None, /
    ) -> dict[str, "DataObj"]:
        if recorder is None:
            recorder = {}

        for x in self:
            x.replace_flags(recorder)

        return recorder


class ChangeView:
    """Views change."""

    def __init__(self, repr_str: str, htmlmaker: HTMLTreeMaker) -> str:
        self.repr_str = repr_str
        self.htmlmaker = htmlmaker

    def __repr__(self) -> str:
        return self.repr_str

    # def _repr_mimebundle_(self, *_, **__) -> dict[str, str]:
    #     return {"text/html": self.htmlmaker.make()}

    def __str__(self) -> str:
        return self.repr_str


def get_bg_colors(color_scheme: "ColorScheme") -> tuple[str, str, str]:
    """Get background colors."""
    match color_scheme:
        case "dark":
            return ["#505050", "#4d2f2f", "#2f4d2f"]
        case "modern":
            return ["#505050", "#701414", "#4e5d2d"]
        case "high-intensty":
            return ["#505050", "#701414", "#147014"]
        case _:
            raise ValueError(f"invalid color scheme: {color_scheme!r}")


def colorful_console(string: str, status: "WrapperStatus", replaced: str = ""):
    """Make string colorful in console."""
    match status:
        case "":
            return string
        case "a":
            return f"\033[48;5;028m{string}\033[0m"
        case "r":
            return f"\033[48;5;088m{replaced}\033[0m\033[48;5;028m{string}\033[0m"
        case "d":
            return f"\033[48;5;088m{string}\033[0m"
        case _:
            raise ValueError(f"invalid status: {status!r}")


def _sep(level: int) -> str:
    return "    " * level
