"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""


from abc import ABCMeta
from dataclasses import dataclass
from itertools import takewhile
from typing import ClassVar, Tuple, Type, Union

from mkdocs.config import config_options as C



from ..tools.maestro_tools import CopyableConfig
from ._string_tools_and_constants import PMT_PM_PREFIX_SIZE
from .common_tree_src import CommonTreeSrc
from .config_option_src import ConfigOptionSrc








@dataclass
class SubConfigSrc(CommonTreeSrc, metaclass=ABCMeta):
    """
    Class making the link between:
        - The actual python implementation
        - The docs content (avoiding out of synch docs)
        - The Config used for the .meta.pmt.yml features. Note that optional stuff "there" is
          different from an optionality (or it's absence) in the running macro/python layer.

    Those instances represent the config "starting point", so all defaults are applied here,
    for the Config implementation.
    When extracting meta files or meta headers, the CopyableConfig instances will receive dicts
    from the yaml content, and those will be merged in the current config. This means the dict
    itself can contain only partial configs, it's not a problem.
    The corollary of this, is that _only_ values that could be None at runtime as an actual/useful
    value should be declared as `C.Optional`.
    """

    is_config: bool = True
    """ Override parent value. """

    is_varargs: bool = False
    """ Override parent value. """

    BASES: ClassVar[Tuple[Type]] = (CopyableConfig,)
    """ Extensions for the Mkdcos Config object to create from the current instance. """

    DOCS_MRO_BASES: ClassVar[str] = ', '.join(
        takewhile(
            'UserDict'.__ne__,
            dict.fromkeys( kls.__name__ for base in BASES for kls in base.mro() )
        )
    )



    def __post_init__(self):
        super().__post_init__()
        self.subs_dct = {arg.name: arg for arg in self.elements}

        if len(self.subs_dct) != len(self.elements):
            raise ValueError(
                f"{ self }: duplicated name for sub config elements." + ''.join(
                    f"\n    {elt}" for elt in self.elements
                )
            )

        if self.long_accessor:
            for elt in self.elements:
                elt.long_accessor = True


    def __getattr__(self, prop):
        if not self.has(prop):
            raise AttributeError(f"{ self }: no { prop } attribute")
        return self.subs_dct[prop]


    def to_config(self):
        """ Convert recursively to the equivalent CopyableConfig object. """

        class_name = self.get_base_config_option_classname()
        body = {
            name: below.to_config()
                for name,below in self.subs_dct.items()
                if below.is_in_config
        }
        body['__docs__'] = self.docs

        kls = type(class_name, self.BASES, body)
        return kls if self.is_plugin_config else C.SubConfig(kls)


    def yield_invalid_yaml_paths(self, meta_dct:dict):
        """
        Check that the given property name, in the given meta_dct, is actually an option
        or a subconfig of the current instance, and yield an error message when an invalid
        property is found.
        """
        for prop,value in meta_dct.items():
            if not self.has(prop):
                path = f"`{ self.py_macros_path[PMT_PM_PREFIX_SIZE:] }.{prop}`".lstrip('.')
                yield f"{ path } is not a valid configuration option for pyodide_macros."
            else:
                sub = self.subs_dct[prop]
                yield from sub.yield_invalid_yaml_paths(value)








ConfOrOptSrc = Union[ConfigOptionSrc, SubConfigSrc]
"""
Union type: regroup instances of ConfigOptionSrc and SubConfigSrc (basically,
revolves around the behaviors of CommonTreeSrc).
"""
