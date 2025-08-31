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


from pathlib import Path

# ************************************************
# GENERATED FILE: DO NOT MODIFY
# source: python_devops/docs_dirs_config_source.py
# ************************************************

GIT_LAB_PAGES        = "https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/"
DOCS                 = Path('docs')

DOCS_INDEX           = DOCS / 'index.md'
DEV_DOCS_INDEX       = DOCS / "dev_docs" / "index.md"
DOCS_CUSTOM          = DOCS / 'custom'
DOCS_CONFIG          = DOCS_CUSTOM / 'config.md'
DOCS_MESSAGES        = DOCS_CUSTOM / 'messages.md'
DOCS_MACRO_DATA      = DOCS_CUSTOM / 'generic_pages.md'

REDACTORS            = DOCS / 'redactors'
DOCS_RESUME          = REDACTORS / 'resume.md'
DOCS_IDE_DETAILS     = REDACTORS / 'IDE-details.md'
DOCS_TERMINALS       = REDACTORS / 'terminaux.md'
DOCS_PY_BTNS         = REDACTORS / 'py_btns.md'
DOCS_RUN_MACRO       = REDACTORS / 'run_macro.md'
DOCS_QCMS            = REDACTORS / 'qcms.md'
DOCS_FIGURES         = REDACTORS / 'figures.md'


def to_page(docs_path:Path):
    """
    Transform the fox path of an md file into the equivalent relative page address
    on the built site .
    """
    return docs_path.relative_to(DOCS).with_suffix('')
