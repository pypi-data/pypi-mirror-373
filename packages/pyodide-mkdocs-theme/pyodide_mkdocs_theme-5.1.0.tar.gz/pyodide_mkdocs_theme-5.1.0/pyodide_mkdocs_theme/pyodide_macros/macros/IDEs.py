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

# pylint: disable=invalid-name, missing-module-docstring


from typing import Optional, Type

from ..tools_and_constants import MACROS_WITH_INDENTS
from ..plugin.maestro_macros import MaestroMacros
from .ide_manager import IdeManager
from .ide_ide import Ide, IdeV
from .ide_tester import IdeTester
from .ide_playground import IdePlayground
from .ide_terminal import Terminal
from .ide_py_btn import PyBtn
from .ide_run_macro import AutoRun





def _element_maker(env:MaestroMacros, kls:Type[IdeManager]):

    # REMINDER:
    #   1) No argument will be left to None at runtime (MaestroMeta), except for the ID argument.
    #   2) The arguments below are there for backward compatibility and also allow to not put
    #      generic arguments (aka, needed for all macros) in the extra_kq dict. this simplifies
    #      the implementation of the various subclasses.
    def wrapped(
        *py_name:  str,
        ID:        Optional[int] = None,
        SANS:      str = None,
        WHITE:     str = None,
        REC_LIMIT: int = None,
        MERMAID:   bool = None,
        AUTO_RUN:  bool = None,
        SHOW:      str = None,
        RUN_GROUP: str = None,
        **kw
    ) -> str:
        return kls(
            env, py_name, ID, SANS, WHITE, REC_LIMIT, MERMAID, AUTO_RUN, SHOW, RUN_GROUP,
            extra_kw=kw     # Arguments sink... (see IdeManager contract)
        ).make_element()

    wrapped.__name__ = wrapped.__qualname__ = kls.MACRO_NAME
    return wrapped




def IDE(env:MaestroMacros):
    """ Build editor+terminal on 2 rows """
    MACROS_WITH_INDENTS.add('IDEv?')
    return _element_maker(env, Ide)


def IDEv(env:MaestroMacros):
    """ Build editor+terminal on 2 columns """
    return _element_maker(env, IdeV)


def IDE_tester(env:MaestroMacros):
    """ Build editor+terminal on 2 columns """
    MACROS_WITH_INDENTS.add(IdeTester.MACRO_NAME)
    return _element_maker(env, IdeTester)


def IDE_playground(env:MaestroMacros):
    """ Build editor+terminal on 2 columns """
    MACROS_WITH_INDENTS.add(IdePlayground.MACRO_NAME)
    return _element_maker(env, IdePlayground)


def terminal(env:MaestroMacros):
    """ Build an isolated terminal """
    return _element_maker(env, Terminal)


def py_btn(env:MaestroMacros):
    """ Build an isolated button, to run python `env` sections """
    return _element_maker(env, PyBtn)


def run(env:MaestroMacros):
    """ Insert an element automatically running `env` sections """
    return _element_maker(env, AutoRun)


