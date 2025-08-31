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
# pylint: disable=multiple-statements



from collections import defaultdict
from dataclasses import dataclass
from operator import attrgetter
import shutil
from typing import Dict, List, Optional, Set, Type, TYPE_CHECKING
from pathlib import Path

from mkdocs.structure.files import Files, File, InclusionLevel
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.nav import Navigation

import pyodide_mkdocs_theme.PMT_tools as PMT_tools

from ..pyodide_logger import logger
from ..exceptions import PmtIdesTestingError, PmtMacrosPyLibsError
from ..tools_and_constants import ZIP_EXTENSION, PageInclusion
from ..macros.ide_term_ide import CommonGeneratedIde
from ..macros.ide_tester import IdeTester
from ..macros.ide_playground import IdePlayground
from .tools.maestro_tools import PythonLib
from .maestro_base import BaseMaestro


if TYPE_CHECKING:
    from pyodide_mkdocs_theme.pyodide_macros import PyodideMacrosPlugin





class MaestroPyLibs(BaseMaestro):
    """
    Handles anything related to files managed on the fly, including python_libs management.
    """


    libs: List[PythonLib] = None        # added on the fly
    """
    List of PythonLib objects, representing all the available custom python libs.
    """

    base_py_libs: Set[str] = None       # added on the fly
    """
    Set of all the python_libs paths strings, as declared in the plugins config (meta or not).
    """

    python_libs_in_pyodide: List[str] = None
    """
    Names of the each python_lib, as it will be imported from pyodide.
    """


    def on_config(self, config: MkDocsConfig):

        super().on_config(config)

        logger.info("Prepare python_libs.")
        self._conf.watch.extend(
            str(py_lib.absolute()) for py_lib in map(Path, self.python_libs)
                                   if py_lib.exists()
        )

        self.libs: List[PythonLib] = sorted(
            filter(None, map(PythonLib, self.python_libs)),
            key=attrgetter('abs_slash')
        )
        self._check_libs()
        self.base_py_libs = set(p.lib for p in self.libs)
        self.python_libs_in_pyodide = [lib.lib_name for lib in self.libs]




    def on_files(self, files: Files, /, *, config: MkDocsConfig):
        """
        If python libs directories are registered, create one archive for each of them.
        It's the user's responsibility to work with them correctly...
        """

        logger.info("Create python_libs archives.")
        for lib in self.libs:
            # Remove any cached files to make the archive lighter (the version won't match
            # pyodide compiler anyway!):
            for cached in lib.path.rglob("*.pyc"):
                cached.unlink()
            file = lib.create_archive_and_get_file(self)
            files.append(file)


        logger.info("Create PMT tools archives (p5, ...).")
        folder = Path(PMT_tools.__path__[0])
        for tool_dir in folder.iterdir():
            if tool_dir.stem.startswith('_'): continue  # __init__ and __pycache__

            archive  = Path( shutil.make_archive(tool_dir.name, ZIP_EXTENSION, tool_dir) )
            dest_zip = Path(self.site_dir) / "assets" / "javascripts" / archive.name
            content  = archive.read_bytes()
            archive.unlink()

            file = File.generated(
                config, dest_zip,
                content=content,
                inclusion=InclusionLevel.NOT_IN_NAV
            )
            files.append(file)

        return super().on_files(files, config=config)




    # Override
    def on_post_build(self, config: MkDocsConfig) -> None:
        """
        Suppress the python archives from the CWD.
        """
        logger.info("Remove python_libs archives.")
        for lib in self.libs:
            lib.unlink()

        super().on_post_build(config)





    def _check_libs(self):
        """
        Add the python_libs directory to the watch list, create the internal PythonLib objects,
        and check python_libs validity:
            1. No python_lib inside another.
            2. If not a root level, must not be importable.
            3. No two python libs with the same name (if registered at different levels)
        """

        libs_by_name: Dict[str, List[PythonLib]] = defaultdict(list)
        for lib in self.libs:
            libs_by_name[lib.lib_name].append(lib)


        same_names = ''.join(
            f"\nLibraries that would be imported as {name!r}:" + ''.join(
                f'\n\t{ lib.lib }' for lib in libs
            )
            for name,libs in libs_by_name.items() if len(libs)>1
        )
        if same_names:
            raise PmtMacrosPyLibsError(
                "Several custom python_libs ending with the same final name are not allowed."
                + same_names
            )

        parenting = ''.join(
            f"\n\t{ self.libs[i-1].lib } contains at least { lib.lib }"
                for i,lib in enumerate(self.libs)
                if i and self.libs[i-1].is_parent_of(lib)
        )
        if parenting:
            raise PmtMacrosPyLibsError(
                "Custom python libs defined in the project cannot contain others:" + parenting
            )












class MaestroGeneratedPages(BaseMaestro):


    is_mermaid_available: bool = False

    _generated_pages: List['PageGenerator'] = None



    def on_config(self, config: MkDocsConfig):
        super().on_config(config)

        self.is_mermaid_available = self._is_mermaid_available()

        self._generated_pages = [
            PageGenerator(self, 'testing', IdeTester),
            PageGenerator(self, 'playground', IdePlayground),
        ]


    def _is_mermaid_available(self):
        mdx_conf      = self._conf.mdx_configs
        custom_fences = mdx_conf.get('pymdownx.superfences', {}).get('custom_fences', [])
        return any( fences['name']=='mermaid' for fences in custom_fences)



    def on_files(self, files: Files, /, *, config: MkDocsConfig):
        """
        If python libs directories are registered, create one archive for each of them.
        It's on the responsibility of the user to work with them correctly...
        """
        for generator in self._generated_pages:
            if generator.is_built:
                file = generator.generate_file(config)
                files.append(file)
        return files



    def on_nav(self, nav: Navigation, /, *, config: MkDocsConfig, files: Files):
        for generator in self._generated_pages:
            generator.handle_nav(nav)
        return nav










class MaestroFiles(
    MaestroPyLibs,
    MaestroGeneratedPages,
):
    """
    Handles anything related to files managed on the fly, including python_libs management.
    """







@dataclass
class PageGenerator:

    env: 'PyodideMacrosPlugin'

    kind:str

    kls: Type[CommonGeneratedIde]

    file: Optional[File] = None
    """
    MkDocs File instance of the test_ides page, if used (allows to "transfer" data/logic from
    `on_files` to `on_nav`).
    """

    is_built: bool = False
    """ Define if the page is generated or not. """

    is_in_nav: bool = False
    """ Define if the page is added to the navigation or not. """



    def __post_init__(self):
        inclusion      = getattr(self.env, f"{ self.kind }_include")
        self.is_built  = PageInclusion.is_built(inclusion, self.env)
        self.is_in_nav = PageInclusion.is_in_nav(inclusion, self.env)


    def generate_file(self, config:MkDocsConfig):
        name      = getattr(self.env, f"{ self.kind }_page")
        page_name = self._build_and_validate_generated_page_name(name, self.kind)

        logger.info(f"Add IDE { page_name } page to documentation.")

        content   = self.kls.get_markdown(self.env.is_mermaid_available)
        self.file = File.generated(config, page_name, content=content, inclusion=InclusionLevel.NOT_IN_NAV)
            # To avoid any waring about the generated file being in the rendered docs but not in the nav,
            # the inclusion level HAS to always be NOT_IN_NAV, then overridden in the on_nav event...

        return self.file


    def _build_and_validate_generated_page_name(self, name:str, kind:str):

        if not name.endswith('.md'):
            name += '.md'

        file_path = Path(name)

        if name != file_path.name:
            raise PmtIdesTestingError(
                f'The { kind } page should be at the top level of the documentation '
                f'but was: { name }'
            )
        if file_path.exists():
            raise PmtIdesTestingError(
                f'Cannot create the { kind } page: a file with the target name already '
                f'exists: { name }.'
            )
        return name


    def handle_nav(self, nav: Navigation):
        """
        Automatically add OR REMOVE the page from the navigation, depending on the plugins' config
        (awesome page could put it automatically in the nav if used with regexp, while it's might
        not be the desired behavior).
        """
        if not self.file:
            return

        page = self.file.page

        # Make sure the title will stay the short version in the navigation
        # (because, awesome-pages plugin):
        page.title = page.file.name

        # Awesome-pages plugin _MIGHT_ add the page to the nav automatically if the author
        # is using patterns to find pages, so need to check if that happened already:
        i_page = next((i for i,p in enumerate(nav.items) if p is page), None)
        already_in_nav = i_page is not None
        is_not_last = already_in_nav and i_page != len(nav.items)-1

        if self.is_in_nav:
            logger.info(f"Add { self.kind } page to navigation.")
            self.file.inclusion = InclusionLevel.INCLUDED

            if not already_in_nav:
                nav.items.append(page)
                # Note: it seems useless to add it to the nav.pages list.

            elif is_not_last:
                # Awesome page might have ordered the test page in whatever way it wants, so
                # push it again at the very end...
                nav.items.pop(i_page)
                nav.items.append(page)

        elif already_in_nav:
            logger.info(f"Remove { self.kind } page from navigation")

            # Never leave the test_ides page in the nav on the built site (awesome-pages plugin
            # might have already added it to the nav if the author is using patterns):
            nav.items.pop(i_page)