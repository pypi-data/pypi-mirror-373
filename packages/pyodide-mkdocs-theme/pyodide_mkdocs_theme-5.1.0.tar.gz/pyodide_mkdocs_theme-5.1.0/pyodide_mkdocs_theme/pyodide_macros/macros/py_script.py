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
# pylint: disable=unused-argument, invalid-name, missing-module-docstring


import re
from pathlib import Path
from functools import wraps
from typing import Any, Tuple

from ..tools_and_constants import MACROS_WITH_INDENTS, ScriptData
from ..parsing import build_code_fence
from ..plugin.maestro_macros import MaestroMacros
from .ide_files_data import SourceFilesExtractor, CompositeFilesDataExtractor




def section(env:MaestroMacros):
    """
    Insert the given section from the python file.

    Notes:
    * To use only on python scripts holding all the sections for the IDE macros. For regular
    files, use the `py` macro or regular code fences with file inclusions (for performances
    reasons).
    * This macro DOES NOT WORK with content built from different python files. Use the
    `composed_py` macro for this purpose.
    """
    MACROS_WITH_INDENTS.add('section')

    @wraps(section)
    def _section(
        py_name:str,
        section_name:ScriptData,
        ID: Any=None # sink (deprecated)             # pylint: disable=unused-argument
    ):
        _, file_data = SourceFilesExtractor.get_file_extractor_and_exo_py_for(env, py_name)
        content   = file_data.get_section(section_name)
        indent    = env.get_macro_indent()
        out       = build_code_fence(content, indent, lang='python')
        return out

    return _section





def composed_py(env:MaestroMacros):
    """
    Generalization of the `section` macro, when using combination instructions with
    different files.

    * By default, only the code section is displayed.
    *if @full is True, all existing sections are displayed
    """
    MACROS_WITH_INDENTS.add('composed_py')

    @wraps(composed_py)
    def _composed_py(
        *py_names:    str,
        sections:     str = None,               # ""
        with_headers: bool = None,              # True
        auto_title:   bool = None,              # False
        name_only:    bool = None,
        title:        str = None,
    ):
        _, composite = CompositeFilesDataExtractor.get_file_extractor_and_exo_py_for(env, py_names)
        targets = re.split(r"[\s,;]+", sections) if sections else ScriptData.VALUES
        content = composite.get_sections(targets, with_headers)
        indent  = env.get_macro_indent()

        if not title and auto_title:
            title = composite.exo_py.name if name_only else py_names[0]
        out = build_code_fence(content, indent, lang='python', title=(title or ""))
        return out

    return _composed_py






def py(env:MaestroMacros):
    """
    Macro python rapide, pour insérer le contenu d'un fichier python. Les parties HDR sont
    automatiquement supprimées, de même que les tests publics (cf. Pyodide-Mkdocs).
    Pour tout autre fichier python, tout le contenu est inséré automatiquement (notamment,
    pour les fichiers du thème !).

    Si l'argument @stop est fourni, ce doit être une chaîne de caractères compatible avec
    `re.split`, SANS matching groupes. Tout contenu après ce token sera ignoré (token compris)
    et "strippé".
    """
    MACROS_WITH_INDENTS.add('py')

    @wraps(py)
    def wrapped(
        py_name: str,
        stop:str=None,
        *,
        auto_title:bool=None,       # default: False
        name_only:bool=None,
        title: str = None,
        **_
    ) -> str:
        return script(env, py_name, stop=stop, auto_title=auto_title, name_only=name_only)
    return wrapped




def script(
    env: MaestroMacros,
    nom: str,
    *,
    lang: str='python',
    auto_title: bool = False,
    title: str="",
    stop= None,
    name_only=None,
) -> str:
    """
    Renvoie le script dans une balise bloc avec langage spécifié

    - lang: le nom du lexer pour la coloration syntaxique
    - nom: le chemin du script relativement au .md d'appel
    - stop: si ce motif est rencontré, il n'est pas affichée, ni la suite.
    """
    target = env.get_sibling_of_current_page(nom, tail='.py')
    _,content,public_tests = env.get_hdr_and_public_contents_from(target)

    # Split again if another token is provided
    if stop is not None:
        # rebuild "original" if another token is provided
        if public_tests:
            content = f"{ content }{ env.lang.tests.msg }{ public_tests }"
        content = re.split(stop, content)[0]

    if not title and auto_title:
        nom += '.py'
        title = Path(nom).name if name_only else nom

    indent = env.get_macro_indent()
    out = build_code_fence(content, indent, lang=lang, title=(title or ""))
    return out
