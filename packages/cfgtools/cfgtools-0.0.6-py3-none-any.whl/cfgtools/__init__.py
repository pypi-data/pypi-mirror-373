"""
# cfgtools
Provides tools for managing config files.

## Usage
### Save to a config file

```py
>>> import cfgtools as cfg
>>> f = cfg.config({"foo": "bar", "this": ["is", "an", "example"]})
>>> f.save("test.cfg", "yaml") # or: f.to_yaml("test.cfg")
```
If not specifeid, the format of the file will be automatically detected according to the
file suffix. Valid formats include `ini`, `json`, `yaml`, `pickle`, `toml`, etc. For
example:
```py
>>> f.save("test.yaml") # a yaml file is created
>>> f.save("test.pkl") # a pickle file is created
>>> f.save("unspecified.cfg") # by default a json file is created
```

### Read from a config file
```py
>>> cfg.read("test.cfg")
cfgtools.config({'foo': 'bar', 'this': ['is', 'an', 'example']})
```
The encoding and format of the file will be automatically detected if not specified.

### Modify configs
```py
>>> f["foo"] = None
>>> f["that"] = {"is": ["also", "an", "example"]}
>>> f
cfgtools.config({
    'foo': None, 'this': ['is', 'an', 'example'],
    'that': {'is': ['also', 'an', 'example']},
})
```
If user wants to check the changed items, run:
```py
>>> f.view_change()
```

## See Also
### Github repository
* https://github.com/Chitaoji/cfgtools/

### PyPI project
* https://pypi.org/project/cfgtools/

## License
This project falls under the BSD 3-Clause License.

"""

import lazyr

lazyr.VERBOSE = 0
lazyr.register("yaml")
lazyr.register(".test_case")

# pylint: disable=wrong-import-position
from . import basic, core, iowrapper, reader, test_case
from ._version import __version__
from .basic import *
from .core import *
from .iowrapper import *
from .reader import *

__all__: list[str] = ["test_case"]
__all__.extend(core.__all__)
__all__.extend(iowrapper.__all__)
__all__.extend(reader.__all__)
__all__.extend(basic.__all__)
