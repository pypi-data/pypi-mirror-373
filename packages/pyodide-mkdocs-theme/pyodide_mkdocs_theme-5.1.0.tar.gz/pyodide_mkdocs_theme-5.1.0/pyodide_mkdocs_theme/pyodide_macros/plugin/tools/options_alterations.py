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


from typing import Any
from pyodide_mkdocs_theme.pyodide_macros.pyodide_logger import logger



def sanitize_decrease_attempts_on_user_code_failure(val:Any):
    """ Backward compatibility change, going from bool to enum of strings. """

    if isinstance(val, bool):
        correct = 'editor' if val else 'secrets'
        logger.warning(
            "Deprecated use of a boolean value for the `ides.decrease_attempts_on_user_code"
            f"_failure` options. Replace {val} with {correct!r}."
        )
        val = correct
    return val
