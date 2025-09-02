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


from .classes import (
    Tr,
    TestsToken,
    Msg,
    MsgPlural,
    Tip,
    LangBase,
)

from .fr_lang import Lang



def __enforce_definitions_but_hidden_classes():
    from .de_lang import LangDe
    from .en_lang import LangEn

__enforce_definitions_but_hidden_classes()
