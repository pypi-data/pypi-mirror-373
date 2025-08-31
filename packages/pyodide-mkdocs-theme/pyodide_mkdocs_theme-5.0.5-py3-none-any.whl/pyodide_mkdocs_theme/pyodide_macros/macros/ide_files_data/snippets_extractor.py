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


from dataclasses import dataclass

from ...paths_utils import read_file
from .root_extractors import RootFilesExtractor





@dataclass(eq=False)
class _SnippetsExtractor(RootFilesExtractor):

    def extract_files_content(self):
        script_content = read_file(self.exo_py) if self.exo_py else ""
        self.extract_multi_sections(script_content)

    def iter_on_files(self):
        return (self.exo_py,)