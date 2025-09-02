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


from urllib.parse import unquote
from pathlib import Path
from typing import Union

from pyodide_mkdocs_theme.pyodide_macros.tools_and_constants import IdeConstants




PathOrStr = Union[str,Path]




def to_uri(path:Union[Path,str], *segments:str):
    """ Take a path string, potentially os dependent, and rebuild a slash separated
        version of it.
        If additional segments are given, they'll be considered new directories, up
        to a final segment that will be considered a file (hence, no trailing slash).

        Behavior for trailing separators on @path:
            - If @segments is not given, trailing separators on @path are kept (to keep
              behaviors consistent with "hidden" index.html files in mkdocs addresses
              when url_directories is True).
            - If any @segments is given, trailing separators on @path are removed
              before joining @path and @segments.
    """
    if isinstance(path,str):
        path = Path(path)
    joined = "/".join(path.parts + segments)
    joined = joined.replace('\\','/')
        # Because windows path behave weirdly when given a "root-like" path, which is
        # starting with a slash in the original string...

    if joined.startswith('//'):      # may happen on absolute paths (Linux)
        joined = '/' + joined.lstrip('/')
    return joined




def convert_url_to_utf8(nom: str) -> str:
    return unquote(nom, encoding="utf-8")




def read_file(target:Path) -> str:
    """
    Read the content of the given target filepath (absolute or relative to the cwd),
    NOTE: return an empty string if the path is not valid.

    Throws AssertionError if the target isn't a Path instance.
    """
    assert isinstance(target,Path), f"target should be a Path object, but was: {target!r}"
    if not target.is_file():
        return ""

    content = target.read_text(encoding="utf-8")
    return content




def get_ide_button_png_path(lvl_up:str, button_name:str):
    path = IdeConstants.ide_buttons_path_template.format(
        lvl_up = lvl_up,
        button_name = button_name
    )
    return path
