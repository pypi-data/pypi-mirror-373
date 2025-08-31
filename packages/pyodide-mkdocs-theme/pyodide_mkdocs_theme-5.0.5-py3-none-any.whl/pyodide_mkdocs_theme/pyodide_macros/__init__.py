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


from .plugin.pyodide_macros_plugin import PyodideMacrosPlugin
from .plugin.config.dumpers import *
from .plugin.tools.macros_data import (
    MacroData,

    MacroDataIDE,
    MacroDataTerminal,
    MacroDataPy_btn,
    MacroDataSection,
    MacroDataMulti_qcm,
    MacroDataPy,
    MacroDataFigure,

    Content,
    HasContent,
    MacroArgsDataIDE,
    MacroArgsDataTerminal,
    MacroArgsDataPy_btn,
    MacroArgsDataSection,
    MacroArgsDataMulti_qcm,
    MacroArgsDataPy,
    MacroArgsDataFigure,

)

from .messages import Msg, MsgPlural, TestsToken, Tip
