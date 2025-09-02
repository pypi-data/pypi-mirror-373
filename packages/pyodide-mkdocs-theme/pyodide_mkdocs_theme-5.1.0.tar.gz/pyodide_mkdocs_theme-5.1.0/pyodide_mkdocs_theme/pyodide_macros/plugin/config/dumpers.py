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

# pylint: disable=signature-differs, multiple-statements


from abc import ABCMeta
from typing import Any, Dict, List, TYPE_CHECKING, Union
from dataclasses import dataclass, field
from functools import wraps


if TYPE_CHECKING:
    from .sub_config_src import ConfOrOptSrc






@dataclass
class Dumper(metaclass=ABCMeta):
    """
    Generic interface to transform a SubConfigSrc tree into... something else.
    Generally, something like a linearized version of the tree content.
    """

    was_option: bool
    """ The last exited element was... """


    @classmethod
    def apply(cls, start:'ConfOrOptSrc', *extra_init:Any, **kw_init):
        """
        Entry point, to apply the given logic to the source config hierarchy tree.
        """
        dumper = cls(False, *extra_init, **kw_init)

        travel_out = dumper.travel_with_dumper(start)
        return dumper.finalize(travel_out)




    def travel_with_dumper(self, obj:'ConfOrOptSrc') -> Union[None, Any] :
        """
        Generic routine to transform a config tree into something else.
        Useful to convert the tree to something that is essentially "linear" 'code, text, ...)

        If it returns something, the output of the top level call will be passed to the finalize
        method, but it's generally not necessary (useful only for recursive outputs).
        """
        raise NotImplementedError()

    def finalize(self, travel_out: Any=None):
        """ Return the actual output at the end of executions """
        raise NotImplementedError()


    #---------------------------------------------------------------------------------------
    # Generic iteration ordering methods:


    def _ordered_iter(self, obj: 'ConfOrOptSrc', sort_all=False):
        """ Generic ordering tool. """

        is_in_args = obj.name=='args' or 'args' in obj.config_setter_path
        children   = obj.elements
        if children and not is_in_args or sort_all:
            children = sorted(children, key=self.ordering)

        return children


    @staticmethod
    def ordering(obj:'ConfOrOptSrc'):
        """ Sub config first, deprecated last, then lexicographic. """
        return not obj.is_config, obj.is_deprecated, obj.name


    #---------------------------------------------------------------------------------------
    # Generic observers/mutators to know when the recursion exits a leaf SubConfigSrc:
    # (Interesting to build flatten content from the tree)


    @staticmethod
    def spot_exiting_leaf_config(method:callable):
        """
        Decorator taking in charge the evolution of `self.was_option`.
        Use it to decorate the `travel_with_dumper(obj) -> None` method of the child class where
        you need to use `is_closing_leaf_config(obj)`.
        """
        @wraps(method)
        def wrapper(self:Dumper, obj:'ConfOrOptSrc') -> None:
            method(self, obj)
            self.was_option = not obj.is_config
        return wrapper


    def is_closing_leaf_config(self, obj:'ConfOrOptSrc'):
        """
        Return True if, when exiting the current object, it is a "leaf SubConfigSrc", meaning
        the previously exited element was a ConfigOptionSrc.

        WARNING: relies on the SubConfigSrc being first in the iteration process.
        """
        return obj.is_config and self.was_option







@dataclass
class AccessorsDumper(Dumper):
    """
    Mutate the plugin config source tree to build all the accessors (config_setter_path, depth,
    maestro_extractor_getter_name), and store the needed data in the `options` list and `macros`
    dict (references held by the PluginConfigSrc object)
    """

    all_options: List['ConfOrOptSrc']           # Mutate a property of PluginConfigSrc
    all_macros_configs:  Dict[str,'ConfOrOptSrc']       # Mutate a property of PluginConfigSrc

    path: List[str] = field(default_factory=list)


    def finalize(self, _):  pass

    def travel_with_dumper(self, obj:'ConfOrOptSrc'):

        # Enter:
        self.path.append(obj.name)

        obj.build_accessor(self.path)
        if not obj.is_config:  self.all_options.append(obj)
        if obj.is_macro:       self.all_macros_configs[obj.name] = obj

        # Recurse:
        for child in obj.elements:
            self.travel_with_dumper(child)

        # Exit:
        self.path.pop()
