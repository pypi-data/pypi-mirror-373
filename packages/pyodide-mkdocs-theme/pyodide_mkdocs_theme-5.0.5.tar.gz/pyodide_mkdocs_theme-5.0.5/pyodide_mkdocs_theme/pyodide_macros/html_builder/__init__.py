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

"""
Objects to facilitate building html elements.

Usage:
    Import the module as a namespace and use the functions. This allows to keep the type
    hints, the docstrings and the function signature when coding.
"""
# Using a package to control what functions/elements are seen through autocompletion
# suggestions when coding.

# pylint: disable=all

from ._html_builder import (
    bi_tag,
    mono_tag,

    input,
    img,

    a,
    button,
    code,
    div,
    script,
    style,
    span,
    svg,
    td,
    tooltip,
    checkbox,
)