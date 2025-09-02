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

from mkdocs.config.base import Config

from .definitions.docs_dirs_config import GIT_LAB_PAGES
from .common_tree_src import CommonTreeSrc, DeprecationStatus
from .config_option_src import ConfigOptionSrc
from .sub_config_src import SubConfigSrc, ConfOrOptSrc
from .dumpers import *

from .definitions.macros_configs import MacroConfigSrc, ARGS_MACRO_CONFIG
from .definitions.plugin_config import PluginConfigSrc, PLUGIN_CONFIG_SRC, TESTING_CONFIG, SEQUENTIAL_CONFIG


PyodideMacrosConfig: Config = PLUGIN_CONFIG_SRC.to_config()
"""
The MkDocs actual plugin's Config (inheriting from BasePluginConfig)
"""
