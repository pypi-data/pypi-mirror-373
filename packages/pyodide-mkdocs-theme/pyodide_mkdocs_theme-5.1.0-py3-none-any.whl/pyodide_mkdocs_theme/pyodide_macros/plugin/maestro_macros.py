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
# pylint: disable=invalid-name, attribute-defined-outside-init, unused-argument





import re
from textwrap import dedent
from typing import Dict, List, Set, Tuple, Optional, Union
from collections import defaultdict
from pathlib import Path


from jinja2 import Environment
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation
from mkdocs.plugins import event_priority


from ..exceptions import PmtInternalError, PyodideMkdocsError
from ..tools_and_constants import (
    HIDDEN_MERMAID_MD,
    HtmlClass,
    IdeConstants,
    PageUrl,
    Prefix,
)
from ..parsing import eat, compress_LZW
from ..paths_utils import PathOrStr
from ..pyodide_logger import logger
from ..html_dependencies import HtmlDependencies, Block, DepKind
from ..macros.ide_files_data import IdeFilesExtractor
from .tools.maestro_tools import AutoCounter
from .tools.macros_data import MacroData, IdeToTest, MacroDataRun
from .tools.pages_and_macros_py_configs import MacroPyConfig, PageConfiguration
from .config import PLUGIN_CONFIG_SRC, GIT_LAB_PAGES
from .maestro_meta import MaestroMeta
from .maestro_indent import MaestroIndent



DEV_TESTS = {
    'dev_docs/tests_feedback__globals__meta/': (15, ['py_libs','other_py_libs/libxyz']),
    'dev_docs/tests_feedback__globals__meta/config_tests/headers/': (12, ['py_libs']),
    'dev_docs/tests_feedback__globals__meta/config_tests/meta/': (20, ['py_libs']),
    'dev_docs/tests_feedback__globals__meta/config_tests/deep_meta/meta/': (15, ['other_py_libs/libxyz']),
}






class MaestroMacroManager(MaestroIndent):
    """
    Holds the global logic related to generation and data tracking for Ide, terminals, ...
    """


    compteur_qcms: int = AutoCounter()
    """ Number of qcm or qcs in the docs """

    _editors_ids: Set[str]
    """
    Store the ids of all the created IDEs, to enforce their uniqueness.
    """

    _editors_paths_to_ids: Dict[str,Set[int]]
    """
    Informational purpose only: store all the ID values already used for a given "base
    path without ID".
    """


    def on_config(self, config:MkDocsConfig):

        self.compteur_qcms = 0
        self._editors_ids  = set()
        self._editors_paths_to_ids = defaultdict(set)

        super().on_config(config)   # pylint: disable=no-member

        IdeFilesExtractor.propagate_any_refresh_needs()


    def get_qcm_id(self):
        return f"{ Prefix.py_mk_qcm_id_ }{ self.compteur_qcms :0>5}"


    def is_unique_then_register(self, id_ide:str, no_id_path:str, ID:Optional[str]) -> bool :
        """
        Check if the given id has already been used.
        If so, return False. If not, register it and return True.
        """
        if id_ide in self._editors_ids:
            return False
        self._editors_ids.add(id_ide)
        if ID is not None:
            self._editors_paths_to_ids[no_id_path].add(ID)
        return True


    def get_registered_ids_for(self, no_id_path:str):
        """
        Return a sorted list giving all the IDs already used for the given "IDE source".
        """
        return sorted(self._editors_paths_to_ids[no_id_path])



    def get_hdr_and_public_contents_from(
        self, opt_path_or_content: Union[ Optional[Path], str ], apply_strip:bool=True,
    ) -> Tuple[str,str,str]:
        """
        Extract the header code and the public content from the given file (assuming it's a
        python file or possibly None, if @path is coming from get_sibling_of_current_page).

        @returns: (header, user_content, public_tests) where header and content may be an
                  empty string.
        """
        if isinstance(opt_path_or_content,str):
            content = opt_path_or_content
        else:
            if opt_path_or_content is None or not opt_path_or_content.is_file():
                return '','',''
            content = opt_path_or_content.read_text(encoding="utf-8")

        lst = IdeConstants.hdr_pattern.split(content)
        # NOTE: If HDR tokens are present, split will return an empty string as first element, so:
        #   - len == 1 : [content]
        #   - len == 3 : ['', hdr, content]

        if len(lst) not in (1,3):
            raise PyodideMkdocsError(
                f"Wrong number of HDR/ENV tokens (found { len(lst)-1 }) in:\n"
                f"{opt_path_or_content!s}"
            )

        hdr     = "" if len(lst)==1 else lst[1]
        content = lst[-1].strip()

        # Make sure the old version of the pattern separating `code` from public `tests` is
        # still accepted (...or something close... :p ):
        pm_pattern = f"^# ?tests(?: ?:)?|{ self.lang.tests.as_pattern.pattern }"
        tests_cuts = re.split(pm_pattern, content, flags=re.I|re.M)

        if len(tests_cuts)>2:
            pattern = self.lang.tests.as_pattern.pattern
            raise PyodideMkdocsError(
                f'Found more than one time the token {pattern!r} (case insensitive) in:'
                f"\n{ opt_path_or_content }"
            )

        tests_cuts.append('')       # ensure always at least 2 elements
        user_code, public_tests, *_ = map(str.strip, tests_cuts) if apply_strip else tests_cuts

        return hdr, user_code, public_tests



    def get_sibling_of_current_page(
        self, partial_path: PathOrStr, *, tail:str="",
    ) -> Optional[Path] :
        """
        Extract the current page from the env, then build a path name toward a file using
        the @partial_path (string name of slash separated string, or relative Path), starting
        from the same parent directory.

        If @tail is given, it is added to the name of the last segment of of the built path.

        If @partial_path is an empty string or a Path without name, return None

        WARNING:
            * This function returns an absolute path, BUT...
            * ...the output path is not normalized, meaning...
            * identical target files using "back and forth" moves will return different output...
            * And this kind of path is controlling the need for ID arguments or not

        CCL: DON'T EVER NORMALIZE THE PATH HERE!! (huge breaking change)
        """
        path: Path = self.docs_dir_path / self.page.file.src_uri
        out_path = self._get_sibling(path, partial_path, tail=tail)
        return out_path


    @staticmethod
    def _get_sibling(src:Path, rel:PathOrStr, *, tail:str="") -> Optional[Path] :
        """
        Build a sibling of the given path file, replacing the current `Path.name` with the given
        @rel element (path or str), and using the different kinds of logic allowed by the theme
        to find the files:
        1. Relative to "{src.parent}/" (priority)
        2. Relative to "{src.parent}/scripts/{src.stem}/"

        `@tail`: suffix to add to the file stem (if given).

        Return None if:
        - `@src` has no explicit parent (using '.' on the cwd will cause troubles)
        - `@rel` is an empty string or is a Path without name property (empty IDE)
        """
        # NOTE: the docstring might be  outdated... (-> @rel info!?)

        if not src.name or not rel or isinstance(rel,Path) and not rel.name:
            return None

        possible_paths = [
            src.parent / rel,
            src.parent / 'scripts' / src.stem / rel
        ]
        for path in possible_paths:
            if tail:
                path = path.with_name( path.stem + tail )
            if path.is_file():
                return path
        return None















class MaestroMacros(MaestroMacroManager):
    """ Holds the global logic related data management for IDE-like elements. """


    _scripts_or_link_tags_to_insert: Dict[DepKind,str]
    """
    UI formatting scripts to insert only in pages containing IDEs, terminals, ...
    Note that the values are all the scripts and/or css tags needed for the key kind,
    all joined together already, as a template string expecting the variable `to_base`.

    Defined once per build, through a call to register_js_and_css_tags in on_config.
    """

    _pages_configs: Dict[PageUrl, 'PageConfiguration']
    """
    Represent the configurations of the "needs" (JS + css) in every Page of the documentation,
    as well as the complete configuration of arguments for every single macro/element in the
    page (see MacroPyConfig).
    """

    _pages_with_ides_to_test: Dict[PageUrl, List[IdeToTest]]
    """
    Holds all the pages url of pages containing IDE that will be tested, with the related
    test config.
    """                     # (note: used on CodEx)

    all_macros_data: List[MacroData]
    """
    Contains all the objects tracking the various states of the PMT macros calls.
    """

    current_macro_data: Optional[MacroData] = None
    """
    MacroData potentially defined during/for the current macro run. May be None (IdeTester,
    non PMT macros calls, ...)
    """

    outdated_PM_files: List[Tuple[Path,str]] = []
    """
    Store Python files info that should be updated (from PM to PMT format).
    """

    macros_counters: Dict[str,AutoCounter] = None
    """
    Per page-wise counter of runners that are not linked to any python file.
        Dict[ MACRO_NAME -> AutoCounter ]
    """


    @property
    def current_page_config(self) -> PageConfiguration :
        """ Note: usable only once on_page_markdown has been called """
        if self.page.url not in self._pages_configs:
            raise PmtInternalError(
                f"PageConfiguration object for { self.file_location() } has not been created yet."
            )
        return self._pages_configs[self.page.url]



    def on_config(self, config:MkDocsConfig):
        self.all_macros_data = []
        self._pages_configs  = {}
        self._scripts_or_link_tags_to_insert = {}
        self._pages_with_ides_to_test = defaultdict(list)
        self.outdated_PM_files.clear()

        super().on_config(config)   # pylint: disable=no-member



    @MaestroMeta.meta_config_swap
    def on_page_markdown(
        self,
        markdown:str,
        page:Page,
        config:MkDocsConfig,
        site_navigation=None,
        **kwargs
    ):
        """
        Automatically add the mermaid code (hidden figure) at the end of the page, if it got
        marked as needing some.
        """
        self._pages_configs[self.page.url] = PageConfiguration(self)
        self.macros_counters = defaultdict(AutoCounter)

        markdown_out = super().on_page_markdown(
            markdown, page, config, site_navigation=site_navigation, **kwargs
        )

        if self.does_current_page_need(DepKind.mermaid):
            markdown_out += HIDDEN_MERMAID_MD

        return markdown_out



    def push_macro_data(self, macro_data:MacroData):
        self.current_macro_data = macro_data
        self.all_macros_data.append(macro_data)



    def apply_macro(self, name, func, *args, **kwargs):            # pylint: disable=unused-argument
        """
        Apply all default arguments from the current config, register the related MacroData objects
        and manage them when needed.
        """
        self.current_macro_data: Optional[MacroData] = None  # reset

        args, kwargs = PLUGIN_CONFIG_SRC.assign_defaults_to_args_and_macro_data(
            name, args, kwargs, self
        )
        out = super().apply_macro(name, func, *args, **kwargs)

        if self.current_macro_data is not None:
            self.current_macro_data.show_if_needed()

        return out


    def file_location(self, page:Optional[Page]=None, *, full_macro=False, intro=False, all_in=False):
        """
        String info about to the current file, relative to the cwd, including the current running
        macro if any.

        @full_macro: if True and this is a PMT macro currently running, add the complete arguments
        values to the message.

        @intro: if True, prepend the message with the sentence

        @all_in: set both flags to True.
        """
        out = super().file_location(page)
        if self.current_macro_data:
            if all_in:
                full_macro = intro = True
            config = intro + 2* full_macro
            if not config:
                out += f" (in macro: { self._running_macro_name })"
            if config&1:
                out  = f"\nHappened in file { out } in macro: \033[31m{ self._running_macro_name }\033[0m."
            if config&2:
                lines = "\n\t".join(self.current_macro_data.args.show_as_list())
                out += f"\nMacro arguments:\n\t{ lines }"
        return out


    def log(self):
        """ Shorthand for `self.file_location(all_in=True)`. """
        return self.file_location(all_in=True)


    def on_env(self, env:Environment, config:MkDocsConfig, files:Files):
        from ..macros.ide_run_macro import AutoRun      # pylint: disable=C0415

        logger.debug("Build the mapping {page.url: list of MacroData}.")
        self._pages_with_run_macro: Dict[str,List[MacroDataRun]] = defaultdict(list)
        for m in self.all_macros_data:
            if m.macro == AutoRun.MACRO_NAME:
                self._pages_with_run_macro[m.page_url].append(m)

        if self.outdated_PM_files:
            files = ''.join(
                f'\n    { path } -> used in: { md }' for path,md in self.outdated_PM_files
            )
            logger.info(
                'You are currently using the outdated "multi-python files" setup of the original '
                'pyodide-mkdocs prototype. You should update these files to match PMT requirements:'
               f'{ files }\n(For more information, see { GIT_LAB_PAGES }redactors/IDE-quick-guide/ ).'
            )



    @MaestroMeta.meta_config_swap
    @event_priority(9001)
    def on_page_context(self, _ctx, page:Page, *, config:MkDocsConfig, nav:Navigation):
        """
        Spot pages in which corrections and remarks have been inserted, and encrypt them.

        This hook uses high priority because the html content must be modified before the
        search plugin starts indexing stuff in the related plugin (which precisely happens
        in the on_page_context hook).
        """
        # pylint: disable=pointless-string-statement

        # Log AFTER the call to `get_page_config_and_set_base_url`, because self.file_location
        # needs the current page object:
        logger.debug(f"Add scripts + encrypt solutions and remarks in {self.file_location()}")

        chunks       = []
        page_config  = self._pages_configs[page and page.url]
        is_tester    = page_config.has_need(DepKind.ides_test)
        need_encrypt = (
            page_config.has_need(DepKind.ide) and self.encrypt_corrections_and_rems
            or page_config.has_need(DepKind.qcm_encrypt)
        )

        if is_tester:
            from ..macros.ide_tester import IdeTester   # pylint: disable=import-outside-toplevel

            logger.info("Create the tests for all the IDEs in the test page.")
            tests_content = IdeTester.build_html_for_tester(self, self._pages_with_ides_to_test)
            chunks = [page.content, tests_content]

        elif need_encrypt:
            self.chunk_and_encrypt_contents(page.content, chunks)

        else:
            chunks.append(page.content)

        # Insert hidden spans to trigger the `{{ run(...) }}` related codes on JS subscriptions:
        chunks.extend(
            f'<span id="{ run_macro.storage_id }" class="{ HtmlClass.py_mk_hidden }"></span>'
            for run_macro in self._pages_with_run_macro[page.url]
        )

        # Add all the pyodide related config data + mermaid related stuff
        overlord_classes = HtmlDependencies.get_overlord_classes(page_config)
        script_tag = page_config.build_page_script_tag_with_ides_configs_mermaid_and_pool_data(overlord_classes)
        chunks.append(script_tag)

        # Add all JS/CSS dependencies + drop config values on the way:
        content_tags = HtmlDependencies.render_tags_for(Block.content, self)
        chunks.append(content_tags)

        page.content = ''.join(chunks)


        if self._dev_mode and page.url in DEV_TESTS:
            expected = DEV_TESTS[page.url]
            actual   = self.editor_font_size, self.python_libs
            if actual != expected:
                raise PmtInternalError(dedent(f"""
                    Wrong implementation of the CONFIG dumps: on_page_context(...)
                        Page: { page.url }
                        Tested: ides.editor_font_size, self.python_libs
                        { actual } should have been { expected }
                    """)
                )



        # If ever the MacrosPlugin gets the super method implemented:
        if hasattr(super(), 'on_page_context'):
            super().on_page_context(_ctx, page, config=config, nav=nav)






    #-----------------------------------------------------------------------
    #     Manage scripts and css to include only in some specific pages
    #-----------------------------------------------------------------------



    def set_current_page_insertion_needs(self, *kind:DepKind):
        """ Mark a page url as needing some specific kinds of scripts (depending on the macro
            triggering the call). """
        self._pages_configs[self.page.url].needs.update(kind)



    def does_current_page_need(self, kind:DepKind):
        """ Check if the current page needs this kind of data. """
        return kind in self._pages_configs[self.page.url].needs



    def archive_ide_to_tests(self, conf:IdeToTest):
        """
        Store data for an IDE in the current Page. @prop must be a property of the
        MacroPyConfig class.
        """
        self._pages_with_ides_to_test[self.page.url].append(conf)



    def set_current_page_js_macro_config(self, editor_name:str, conf:MacroPyConfig):
        """
        Store data for an IDE in the current Page. @prop must be a property of the
        MacroPyConfig class.
        """
        self._pages_configs[self.page.url][editor_name] = conf


    def is_page_with_something_to_insert(self, page:Optional[Page]=None):
        """
        Check if the current page is marked as holding at least one thing needing a script,
        insertion or ide content.
        If @page is given, use this instance instead of the one from self.page (useful for hooks)
        """
        url = page.url if page else self.page.url
        return url in self._pages_configs





    #--------------------------------------------------------------------
    #                    Solution & remarks encryption
    #--------------------------------------------------------------------



    def chunk_and_encrypt_contents(self, html:str, chunks:List[str]):
        """
        Assuming it's known that the @page holds corrections and/or remarks:
            - Search for the encryption tokens
            - Encrypt the content in between two consecutive tokens in the page html content.
            - Once done for the whole page, replace the page content with the updated version.
        Encryption tokens are removed on the way.
        """

        entering = 0
        while entering < len(html):
            i,j = eat(html, IdeConstants.encryption_token, start=entering, skip_error=True)
            i,j = self._cleanup_p_tags_around_encryption_tokens(html, i, j)

            chunks.append( html[entering:i] )

            if i==len(html):
                break

            ii,entering = eat(html, IdeConstants.encryption_token, start=j)     # raise if not found
            ii,entering = self._cleanup_p_tags_around_encryption_tokens(html, ii, entering)

            solution_and_rem = html[j:ii].strip()
            encrypted_content = compress_LZW(solution_and_rem, self)
            chunks.append(encrypted_content)



    def _cleanup_p_tags_around_encryption_tokens(self, html:str, i:int, j:int):
        """
        mkdocs automatically surrounds the encryption token with <p> tag, so they must be removed.
        Note: Including the tags in the ENCRYPTION_TOKEN doesn't change the problem: you'd just
              get another <p> tag surrounding the token... sometimes... x/
        """
        while html[i-3:i]=='<p>' and html[j:j+4]=='</p>':
            i -= 3
            j += 4
        return i,j
