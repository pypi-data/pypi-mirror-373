"""
Contains template class: ConfigIOWrapper.

NOTE: this module is private. All functions and objects are available in the main
`cfgtools` namespace - use that instead.

"""

from typing import TYPE_CHECKING, Callable

from .basic import BasicWrapper, DictBasicWrapper, Flag, ListBasicWrapper

if TYPE_CHECKING:
    from .iowrapper import ConfigIOWrapper

__all__ = []


class ConfigTemplate(BasicWrapper):
    """
    A template for matching config objects.

    Parameters
    ----------
    data : DataObj
        Template data.

    Raises
    ------
    TypeError
        Raised if the template data has invalid type.

    """

    valid_types = (
        str,
        int,
        float,
        bool,
        type(None),
        type,
        Callable,
        Flag,
        type(Ellipsis),
    )
    constructor = object
    sub_constructors = {
        dict: lambda: DictConfigTemplate,
        list: lambda: ListConfigTemplate,
    }

    def __repr__(self) -> str:
        return f"cfgtools.template({self.repr()})"

    def fill(
        self,
        constructor: type["ConfigIOWrapper"],
        wrapper: "ConfigIOWrapper | None" = None,
    ) -> "ConfigIOWrapper":
        """Fill the template with an iowrapper."""
        obj = self.unwrap_top_level()
        if self.isinstance(type):
            if wrapper is not None and wrapper.isinstance(obj):
                return wrapper.copy()
            return constructor(obj())
        if self.isinstance(Callable):
            if wrapper is not None and obj(wrapper):
                return wrapper.copy()
            return constructor(None)
        if wrapper is None:
            return constructor(obj)
        return wrapper.copy()

    def delete(self) -> None:
        raise TypeError("cannot modify a template")

    def mark_as_added(self) -> None:
        raise TypeError("cannot modify a template")

    def mark_as_replaced(self, value: "BasicWrapper", /) -> None:
        raise TypeError("cannot modify a template")


class DictConfigTemplate(ConfigTemplate, DictBasicWrapper):
    """Dict template."""

    constructor = ConfigTemplate
    sub_constructors = {}

    def fill(
        self,
        constructor: type["ConfigIOWrapper"],
        wrapper: "ConfigIOWrapper | None" = None,
    ) -> "ConfigIOWrapper":
        if wrapper is None or not wrapper.isinstance(dict):
            return constructor({k: v.fill(constructor) for k, v in self.items()})

        new_data = {}
        for kt, vt in self.items():
            for k, v in wrapper.items():
                if constructor(k).match(kt):
                    new_data[k] = vt.fill(constructor, v)
                    break
            else:
                new_data[self.constructor(kt).fill(constructor).unwrap()] = vt.fill(
                    constructor
                )

        return constructor(new_data)


class ListConfigTemplate(ConfigTemplate, ListBasicWrapper):
    """List template."""

    constructor = ConfigTemplate
    sub_constructors = {}

    def fill(
        self,
        constructor: type["ConfigIOWrapper"],
        wrapper: "ConfigIOWrapper | None" = None,
    ) -> "ConfigIOWrapper":
        if wrapper is None or not wrapper.isinstance(list):
            return constructor([x.fill(constructor) for x in self])

        new_data = []
        len_wrapper = len(wrapper)
        for i, xt in enumerate(self):
            if i < len_wrapper:
                new_data.append(xt.fill(constructor, wrapper[i]))
            else:
                new_data.append(xt.fill(constructor))

        return constructor(new_data)
