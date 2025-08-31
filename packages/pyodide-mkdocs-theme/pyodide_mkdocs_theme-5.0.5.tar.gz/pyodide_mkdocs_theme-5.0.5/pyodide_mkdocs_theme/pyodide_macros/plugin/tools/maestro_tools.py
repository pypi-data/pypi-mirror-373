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


import re
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Optional, TYPE_CHECKING, Tuple

from mkdocs.structure.files import File
from mkdocs.config.base import Config

from pyodide_mkdocs_theme.pyodide_macros.exceptions import PmtMacrosPyLibsError
from pyodide_mkdocs_theme.pyodide_macros.tools_and_constants import PY_LIBS, ZIP_EXTENSION

from ...parsing import camel


if TYPE_CHECKING:
    from ..pyodide_macros_plugin import PyodideMacrosPlugin










class CopyableConfig(Config):
    """
    CopyableConfig instances can copy themselves, merging them with a given dict-like object
    (potentially another mkdocs Config object) and return a brand new object.
    """

    def copy(self):
        """ Recursively create a copy of self """
        other = self.__class__()
        for k,v in self.items():
            other[k] = v.copy() if isinstance(v, CopyableConfig) else v
        return other



    def copy_with(self, yml_nested_dct:dict, consume_dict=False):
        """
        Create a copy of self, overriding any of its property with the matching content of
        the @yml_nested_dct argument.
        The original object is used as "tree hierarchy source", so anything in the dict
        object that doesn't already exist in the source structure will be ignored.

        @consume_dict: If True, the dict object to merge will be recursively mutated,
                       removing the data from it as they are used. This allows to know
                       if something has not been used from the @yml_nested_dct if some
                       kind of validation of its content is needed.
        """
        def merge_dfs(new_config, yml_nested_dct:dict):
            for k in [*yml_nested_dct]:
                if not hasattr(new_config, k):
                    continue

                obj = getattr(new_config, k)
                val = yml_nested_dct.pop(k) if consume_dict else yml_nested_dct[k]
                if isinstance(obj, CopyableConfig):
                    merge_dfs(obj, val)
                else:
                    new_config[k] = val

            return new_config

        return merge_dfs(self.copy(), yml_nested_dct)









class ConfigExtractor:
    """
    Data descriptor extracting automatically the matching property name from the mkdocs config.
    An additional path (dot separated keys/properties) can be provided, that will be prepended
    to the property name.
    """

    RAISE_DEPRECATION_ACCESS: ClassVar[bool] = False
    """
    Accessing the value on getters marked as deprecated will raise an error if this flag is True.
    This is defensive programming, to make sure PMT code isn't using those anymore.

    Note: Start at False because during on_config, the theme will check if the user set some values
          for deprecated options, so the access should work the first time.
          See PluginConfigSrc.spot_usage_of_deprecated_features(env)
    """

    def __init__(self, path='', *, prop=None, deprecated=False, alteration=None):
        self.prop = prop
        self.path = path
        self._getter = lambda _: None
        self.deprecated = deprecated
        self.alteration = alteration


    def __set_name__(self, _kls, over_prop:str):
        path = self.path
        if not self.prop:
            self.prop = over_prop if not self.deprecated else over_prop.lstrip('_')

        # Using an evaluated function gives perfs equivalent to the previous version using a
        # cache, while keeping everything fully dynamic (=> prepare the way for meta.pmt.yml)
        props = 'env.' + '.'.join((path, self.prop)).strip('.').replace('..','.')

        if not re.fullmatch(r'\w([\w.]*\w)?', props):
            raise ValueError(
                "Invalid code. Cannot build ConfigExtractor getter with:\n" + props
            )

        value_getter = self._getter = eval("lambda env: " + props)         # pylint: disable=eval-used
        if self.alteration:
            self._getter = lambda env: self.alteration(value_getter(env))


    def __get__(self, env:'PyodideMacrosPlugin', kls=None):
        if self.deprecated and self.RAISE_DEPRECATION_ACCESS:
            env.warn_unmaintained(f'The option {self.prop}')
        return self._getter(env)


    def __set__(self, *a, **kw):
        raise ValueError(f"The {self.prop} property should never be reassigned")











class AutoCounter:
    """
    Counter with automatic increment. The internal value can be updated/rested by assignment.
    @warn: if True, the user will see a notification in the console about that counter being
    unmaintained so far (displayed once only).

    WARNING: this is a class level-based counter.
    """

    def __init__(self, warn=False):
        self.cnt = 0
        self.warn_once = warn

    def __set_name__(self, _, prop:str):
        self.prop = prop        # pylint: disable=attribute-defined-outside-init

    def __set__(self, _:'PyodideMacrosPlugin', value:int):
        self.cnt = value

    def __get__(self, obj:'PyodideMacrosPlugin', _=None):
        if self.warn_once:
            self.warn_once = False
            obj.warn_unmaintained(f'The property {self.prop!r}')
        self.cnt += 1
        return self.cnt

    def inc(self):
        """ when not used as descriptor... """
        self.cnt += 1
        return self.cnt










def dump_and_dumper(props, obj:Optional[Any]=None, converter:Optional[Callable]=None):
    """
    Convert the given properties of an object to a dict where:
    * Keys are camelCased property names
    * Values are converted through the converter function. If @obj is `None`, send `None` as value.
    """
    return {
        camel(prop): converter( getattr(obj, prop) if obj else None )
        for prop in props
    }









@dataclass
class PythonLib:
    """ Represent one python_lib with all its related info/logic. """

    lib: str          # String from the mkdocs plugin config
    """ python_libs yaml declaration string """

    path: Path = None  # self.libs as Path
    """ python_libs declaration as relative path to CWD """

    exist: bool = None
    """ True if self.path directory exists """

    lib_name: str  = None  # last element
    """ Import name, in pyodide (aka, last segment of the path). """

    archive:   Path = None  # zip filename
    """ Archive filename. """

    abs_slash: str  = ""
    """
    Absolute posix path as string, with a terminal slash (used to spot directories containing
    others quickly, the slash is there to avoid lib matching libXx).
    """



    def __post_init__(self):
        self.path  = Path(self.lib)
        self.exist = self.path.is_dir()

        if not self.exist and self.lib != PY_LIBS:
            raise PmtMacrosPyLibsError(
                f"Python libraries used for `python_lib` must be packages but found: { self.lib }."
                "\n(a package is a directory with at least an __init__.py file, and possibly other"
                " files or packages)"
            )

        segments = self.path.parent.parts
        if segments:
            loc = Path.cwd()
            for segment in segments:
                loc /= segment
                if not (loc/'__init__.py').exists():
                    break
            else:
                raise PmtMacrosPyLibsError(
                   f"The { self.lib } python_lib is not directly at the project root directory "
                    "so it should not be importable from the CWD at build time:\n"
                   f"Remove the `__init__.py` file from the top level directory."
                )

        self.lib_name  = self.path.name
        self.archive   = Path(f"{ self.lib_name }.{ ZIP_EXTENSION }")
        self.abs_slash = f"{ self.path.resolve().as_posix() }/"


    def __bool__(self):
        return self.exist


    def is_parent_of(self, other:'PythonLib'):
        """
        Check if the current instance is a parent directory of the @other PythonLib.
        """
        # Working with strings because it makes the logic easier than with Path.relative_to
        # (requires checking both ways, and handling common higher parents => boring...)
        return other.abs_slash.startswith(self.abs_slash)


    def create_archive_and_get_file(self, env:'PyodideMacrosPlugin'):
        """
        Create the archive for the given PythonLib object
        """
        shutil.make_archive(self.lib_name, ZIP_EXTENSION, self.path)
        return File(self.archive.name, '.', Path(env.site_dir), False)


    def unlink(self):
        """
        Suppress the archive from the cwd (on_post_build)
        """
        self.archive.unlink(missing_ok=True)
