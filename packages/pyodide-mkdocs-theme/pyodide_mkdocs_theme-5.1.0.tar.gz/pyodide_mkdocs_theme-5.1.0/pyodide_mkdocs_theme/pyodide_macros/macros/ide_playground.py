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
from typing import ClassVar




from ..tools_and_constants import PmtPyMacrosName, Prefix, ScriptSection
from ..html_dependencies.deps_class import DepKind
from ..plugin.config.definitions.docs_dirs_config import GIT_LAB_PAGES
from .ide_files_data import IdeFilesExtractor
from .ide_term_ide import CommonGeneratedIde
from .ide_ide import Ide




@dataclass
class IdePlayground(CommonGeneratedIde, Ide):

    MACRO_NAME: ClassVar[PmtPyMacrosName] = PmtPyMacrosName.IDE_playground

    ID_PREFIX: ClassVar[str] = Prefix.playground_

    DEPS_KIND: ClassVar[DepKind] = DepKind.playground


    @property
    def has_check_btn(self):
        """ The IdeTester always has one... """
        return True

    @property
    def has_corr_btn(self):
        """ The IdeTester always has one... """
        return True

    @property
    def has_reveal_btn(self):
        """ The IdeTester always has one... """
        return False

    @property
    def has_counter(self):
        """ The IdeTester always has one... """
        return False



    def register_ide_for_tests(self):
        """ IdeTester instances are never registered for testing... """


    # def list_of_buttons(self):
    #     """ Keep only public tests, validations and restart. """
    #     btns    = super().list_of_buttons()
    #     restart = next(btn_html for btn_html in btns if "icons8-restart-64.png" in btn_html)
    #     return btns[:2] + [restart]



    #-----------------------------------------------------------------------------------


    @classmethod
    def _get_sections_editors(cls):
        """
        Build the divs that will hold the various sections when using the page (except for the
        `code` section, that will be the IDE itself).
        """
        sections = "\n\n".join(
            f"""
???+ tip "{ section }"

    <div class="dev-sandbox" id="{ IdeFilesExtractor.get_section_property_from_cls(section) }"></div>
"""
            for section in ScriptSection.VALUES if section != 'code'
        )
        return sections



    @classmethod
    def get_markdown(cls, use_mermaid:bool):
        """
        Build the code generating the IdeTester object. Insert the MERMAID logistic only if
        the `mkdocs.yml` holds the custom fences code configuration.
        """

        return f"""
# Playground  {'{'} data-search-exclude {'}'}


Cette page permet de développer dynamiquement dans un contexte où les différentes sections sont modifiables et exécutables à volonté: Lorsque l'IDE est exécuté, les contenus de tous les autres éditeurs de la page sont utilisés en lieu et place des sections de l'IDE.

* Le contenu de la section `tests` est automatiquement exécuté après le contenu de l'IDE : il n'est pas nécessaire d'en rajouter le code dans celui-ci pour retrouver le comportement habituel des IDEs normaux.
* Mermaid est utilisable dans cette page, ainsi que les autres outils complémentaires (p5, matplotlib, ...).
* Le bouton de téléchargement sous l'IDE permet de récupérer un fichier PMT avec toutes les sections, correctement formé.
* Le bouton de téléversement permet d'importer un fichier existant pour ensuite en modifier les différentes sections.
* Les raccourcis ++ctrl+s++ et ++ctrl+enter++ sont actifs depuis n'importe quel éditeur dans la page.

<br>

??? help "Aide..."
    - [Configuration]({ GIT_LAB_PAGES }custom/config/#pyodide_macros.playground) de la page Playground.
    - Informations sur les différentes [`sections`]({ GIT_LAB_PAGES }redactors/IDE-details/#ide-sections) et leurs comportements

<br>

---

<br>

{'{{'} IDE_playground(MERMAID={ use_mermaid }, TERM_H=15) {'}}'}

{'{{'} figure() {'}}'}

<br>

---

<br>

{ cls._get_sections_editors() }
"""
