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

# pylint: disable=multiple-statements, line-too-long, protected-access



import re
from typing import  Dict, List, Optional, Tuple
from functools import wraps
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import BuildError
from mkdocs.structure.pages import Page
from mkdocs.plugins import BasePlugin


from ...__version__ import __version__
from ..exceptions import PmtInternalError, PmtMacrosDeprecationError, PmtMacrosError
from ..messages import LangBase, Lang
from ..messages.classes import JsDumper
from ..pyodide_logger import logger
from .tools.maestro_tools import ConfigExtractor
from .config import PyodideMacrosConfig, PLUGIN_CONFIG_SRC
from .tools.options_alterations import sanitize_decrease_attempts_on_user_code_failure





# Do NOT declare these as class level attributes (see `dump_to_js_config` hack, using None as self)
TO_DUMP_TO_CONFIG = """
    args_figure_div_id
    export_zip_with_names
    export_zip_prefix

    base_url
    button_icons_directory
    editor_font_family
    editor_font_size
    in_serve
    language
    pmt_url
    python_libs
    site_url
    version
""".split()





class BaseMaestro(BasePlugin[PyodideMacrosConfig]):
    """
    Main class, regrouping the basic configurations, properties, getters and/or constants
    for the different children classes: each of them will inherit from MaestroConfig.
    It is also used as "sink" for the super calls of other classes that are not implemented
    on the MacrosPlugin class.

    Note that, for the ConfigExtractor for to properly work, the class hierarchy has to
    extend MacrosPlugin at some point.
    """

    # global mkdocs config data:
    docs_dir:  str = ConfigExtractor('_conf')
    repo_url:  str = ConfigExtractor('_conf')
    site_name: str = ConfigExtractor('_conf')
    site_url:  str = ConfigExtractor('_conf')
    site_dir:  str = ConfigExtractor('_conf')
    use_directory_urls: str = ConfigExtractor('_conf')

    # ARGS EXTRACTOR TOKEN
    args_IDE_AUTO_RUN:      bool = ConfigExtractor('config.args.IDE', prop='AUTO_RUN')
    args_IDE_EXPORT:        bool = ConfigExtractor('config.args.IDE', prop='EXPORT')
    args_IDE_ID:             int = ConfigExtractor('config.args.IDE', prop='ID')
    args_IDE_LOGS:          bool = ConfigExtractor('config.args.IDE', prop='LOGS')
    args_IDE_MAX:            int = ConfigExtractor('config.args.IDE', prop='MAX')
    args_IDE_MAX_SIZE:       int = ConfigExtractor('config.args.IDE', prop='MAX_SIZE')
    args_IDE_MERMAID:       bool = ConfigExtractor('config.args.IDE', prop='MERMAID')
    args_IDE_MIN_SIZE:       int = ConfigExtractor('config.args.IDE', prop='MIN_SIZE')
    args_IDE_MODE:           str = ConfigExtractor('config.args.IDE', prop='MODE')
    args_IDE_REC_LIMIT:      int = ConfigExtractor('config.args.IDE', prop='REC_LIMIT')
    args_IDE_RUN_GROUP:      str = ConfigExtractor('config.args.IDE', prop='RUN_GROUP')
    args_IDE_SANS:           str = ConfigExtractor('config.args.IDE', prop='SANS')
    args_IDE_SHOW:           str = ConfigExtractor('config.args.IDE', prop='SHOW')
    args_IDE_STD_KEY:        str = ConfigExtractor('config.args.IDE', prop='STD_KEY')
    args_IDE_TERM_H:         int = ConfigExtractor('config.args.IDE', prop='TERM_H')
    args_IDE_TEST:           str = ConfigExtractor('config.args.IDE', prop='TEST')
    args_IDE_TWO_COLS:      bool = ConfigExtractor('config.args.IDE', prop='TWO_COLS')
    args_IDE_WHITE:          str = ConfigExtractor('config.args.IDE', prop='WHITE')
    args_IDE_py_name: Tuple[str] = ConfigExtractor('config.args.IDE', prop='py_name')

    args_composed_py_auto_title:    bool = ConfigExtractor('config.args.composed_py', prop='auto_title')
    args_composed_py_name_only:     bool = ConfigExtractor('config.args.composed_py', prop='name_only')
    args_composed_py_py_name: Tuple[str] = ConfigExtractor('config.args.composed_py', prop='py_name')
    args_composed_py_sections:       str = ConfigExtractor('config.args.composed_py', prop='sections')
    args_composed_py_title:          str = ConfigExtractor('config.args.composed_py', prop='title')
    args_composed_py_with_headers:  bool = ConfigExtractor('config.args.composed_py', prop='with_headers')

    args_figure_SHOW:       str = ConfigExtractor('config.args.figure', prop='SHOW')
    args_figure_admo_class: str = ConfigExtractor('config.args.figure', prop='admo_class')
    args_figure_admo_kind:  str = ConfigExtractor('config.args.figure', prop='admo_kind')
    args_figure_admo_title: str = ConfigExtractor('config.args.figure', prop='admo_title')
    args_figure_div_class:  str = ConfigExtractor('config.args.figure', prop='div_class')
    args_figure_div_id:     str = ConfigExtractor('config.args.figure', prop='div_id')
    args_figure_inner_text: str = ConfigExtractor('config.args.figure', prop='inner_text')
    args_figure_p5_buttons: str = ConfigExtractor('config.args.figure', prop='p5_buttons')

    args_multi_qcm_DEBUG:             bool = ConfigExtractor('config.args.multi_qcm', prop='DEBUG')
    args_multi_qcm_SHOW:               str = ConfigExtractor('config.args.multi_qcm', prop='SHOW')
    args_multi_qcm_admo_class:         str = ConfigExtractor('config.args.multi_qcm', prop='admo_class')
    args_multi_qcm_admo_kind:          str = ConfigExtractor('config.args.multi_qcm', prop='admo_kind')
    args_multi_qcm_description:        str = ConfigExtractor('config.args.multi_qcm', prop='description')
    args_multi_qcm_hide:              bool = ConfigExtractor('config.args.multi_qcm', prop='hide')
    args_multi_qcm_multi:             bool = ConfigExtractor('config.args.multi_qcm', prop='multi')
    args_multi_qcm_qcm_title:          str = ConfigExtractor('config.args.multi_qcm', prop='qcm_title')
    args_multi_qcm_shuffle:           bool = ConfigExtractor('config.args.multi_qcm', prop='shuffle')
    args_multi_qcm_shuffle_items:     bool = ConfigExtractor('config.args.multi_qcm', prop='shuffle_items')
    args_multi_qcm_shuffle_questions: bool = ConfigExtractor('config.args.multi_qcm', prop='shuffle_questions')
    args_multi_qcm_tag_list_of_qs:     str = ConfigExtractor('config.args.multi_qcm', prop='tag_list_of_qs')

    args_py_auto_title: bool = ConfigExtractor('config.args.py', prop='auto_title')
    args_py_name_only:  bool = ConfigExtractor('config.args.py', prop='name_only')
    args_py_py_name:     str = ConfigExtractor('config.args.py', prop='py_name')
    args_py_title:       str = ConfigExtractor('config.args.py', prop='title')

    args_py_btn_AUTO_RUN:      bool = ConfigExtractor('config.args.py_btn', prop='AUTO_RUN')
    args_py_btn_HEIGHT:         int = ConfigExtractor('config.args.py_btn', prop='HEIGHT')
    args_py_btn_ICON:           str = ConfigExtractor('config.args.py_btn', prop='ICON')
    args_py_btn_ID:             int = ConfigExtractor('config.args.py_btn', prop='ID')
    args_py_btn_MERMAID:       bool = ConfigExtractor('config.args.py_btn', prop='MERMAID')
    args_py_btn_REC_LIMIT:      int = ConfigExtractor('config.args.py_btn', prop='REC_LIMIT')
    args_py_btn_RUN_GROUP:      str = ConfigExtractor('config.args.py_btn', prop='RUN_GROUP')
    args_py_btn_SANS:           str = ConfigExtractor('config.args.py_btn', prop='SANS')
    args_py_btn_SHOW:           str = ConfigExtractor('config.args.py_btn', prop='SHOW')
    args_py_btn_SIZE:           int = ConfigExtractor('config.args.py_btn', prop='SIZE')
    args_py_btn_TIP:            str = ConfigExtractor('config.args.py_btn', prop='TIP')
    args_py_btn_TIP_SHIFT:      int = ConfigExtractor('config.args.py_btn', prop='TIP_SHIFT')
    args_py_btn_TIP_WIDTH:    float = ConfigExtractor('config.args.py_btn', prop='TIP_WIDTH')
    args_py_btn_WHITE:          str = ConfigExtractor('config.args.py_btn', prop='WHITE')
    args_py_btn_WIDTH:          int = ConfigExtractor('config.args.py_btn', prop='WIDTH')
    args_py_btn_WRAPPER:        str = ConfigExtractor('config.args.py_btn', prop='WRAPPER')
    args_py_btn_py_name: Tuple[str] = ConfigExtractor('config.args.py_btn', prop='py_name')

    args_run_AUTO_RUN:      bool = ConfigExtractor('config.args.run', prop='AUTO_RUN')
    args_run_ID:             int = ConfigExtractor('config.args.run', prop='ID')
    args_run_MERMAID:       bool = ConfigExtractor('config.args.run', prop='MERMAID')
    args_run_REC_LIMIT:      int = ConfigExtractor('config.args.run', prop='REC_LIMIT')
    args_run_RUN_GROUP:      str = ConfigExtractor('config.args.run', prop='RUN_GROUP')
    args_run_SANS:           str = ConfigExtractor('config.args.run', prop='SANS')
    args_run_SHOW:           str = ConfigExtractor('config.args.run', prop='SHOW')
    args_run_WHITE:          str = ConfigExtractor('config.args.run', prop='WHITE')
    args_run_py_name: Tuple[str] = ConfigExtractor('config.args.run', prop='py_name')

    args_section_py_name: str = ConfigExtractor('config.args.section', prop='py_name')
    args_section_section: str = ConfigExtractor('config.args.section', prop='section')

    args_terminal_AUTO_RUN:      bool = ConfigExtractor('config.args.terminal', prop='AUTO_RUN')
    args_terminal_FILL:           str = ConfigExtractor('config.args.terminal', prop='FILL')
    args_terminal_ID:             int = ConfigExtractor('config.args.terminal', prop='ID')
    args_terminal_MERMAID:       bool = ConfigExtractor('config.args.terminal', prop='MERMAID')
    args_terminal_REC_LIMIT:      int = ConfigExtractor('config.args.terminal', prop='REC_LIMIT')
    args_terminal_RUN_GROUP:      str = ConfigExtractor('config.args.terminal', prop='RUN_GROUP')
    args_terminal_SANS:           str = ConfigExtractor('config.args.terminal', prop='SANS')
    args_terminal_SHOW:           str = ConfigExtractor('config.args.terminal', prop='SHOW')
    args_terminal_TERM_H:         int = ConfigExtractor('config.args.terminal', prop='TERM_H')
    args_terminal_WHITE:          str = ConfigExtractor('config.args.terminal', prop='WHITE')
    args_terminal_py_name: Tuple[str] = ConfigExtractor('config.args.terminal', prop='py_name')

    _pmt_meta_filename:                 str = ConfigExtractor('config.build')
    activate_cache:                    bool = ConfigExtractor('config.build')
    deprecation_level:                  str = ConfigExtractor('config.build')
    encrypted_js_data:                 bool = ConfigExtractor('config.build')
    extra_pyodide_sections:       List[str] = ConfigExtractor('config.build')
    forbid_macros_override:            bool = ConfigExtractor('config.build')
    ides_id_hash_mode:                  str = ConfigExtractor('config.build')
    ignore_macros_plugin_diffs:        bool = ConfigExtractor('config.build')
    limit_pypi_install_to:        List[str] = ConfigExtractor('config.build')
    load_yaml_encoding:                 str = ConfigExtractor('config.build')
    macros_with_indents:          List[str] = ConfigExtractor('config.build')
    meta_yaml_allow_extras:            bool = ConfigExtractor('config.build')
    meta_yaml_encoding:                 str = ConfigExtractor('config.build')
    python_libs:                  List[str] = ConfigExtractor('config.build')
    show_cache_refresh:                bool = ConfigExtractor('config.build')
    skip_py_md_paths_names_validation: bool = ConfigExtractor('config.build')
    tab_to_spaces:                      int = ConfigExtractor('config.build')

    ace_style_dark:                               str = ConfigExtractor('config.ides')
    ace_style_light:                              str = ConfigExtractor('config.ides')
    deactivate_stdout_for_secrets:               bool = ConfigExtractor('config.ides')
    decrease_attempts_on_user_code_failure:      bool = ConfigExtractor('config.ides', alteration=sanitize_decrease_attempts_on_user_code_failure)
    editor_font_family:                           str = ConfigExtractor('config.ides')
    editor_font_size:                             int = ConfigExtractor('config.ides')
    encrypt_alpha_mode:                           str = ConfigExtractor('config.ides')
    encrypt_corrections_and_rems:                bool = ConfigExtractor('config.ides')
    export_zip_prefix:                            str = ConfigExtractor('config.ides')
    export_zip_with_names:                       bool = ConfigExtractor('config.ides')
    forbid_corr_and_REMs_with_infinite_attempts: bool = ConfigExtractor('config.ides')
    forbid_hidden_corr_and_REMs_without_secrets: bool = ConfigExtractor('config.ides')
    forbid_secrets_without_corr_or_REMs:         bool = ConfigExtractor('config.ides')
    show_only_assertion_errors_for_secrets:      bool = ConfigExtractor('config.ides')

    playground_include: str = ConfigExtractor('config.playground', prop='include')
    playground_page:    str = ConfigExtractor('config.playground', prop='page')

    encrypt_comments:                     bool = ConfigExtractor('config.qcms')
    forbid_no_correct_answers_with_multi: bool = ConfigExtractor('config.qcms')

    sequential_only: List[str] = ConfigExtractor('config.sequential', prop='only')
    sequential_run:        str = ConfigExtractor('config.sequential', prop='run')

    cut_feedback:  bool = ConfigExtractor('config.terms')
    stdout_cut_off: int = ConfigExtractor('config.terms')

    testing_empty_section_fallback: str = ConfigExtractor('config.testing', prop='empty_section_fallback')
    testing_include:                str = ConfigExtractor('config.testing', prop='include')
    testing_load_buttons:          bool = ConfigExtractor('config.testing', prop='load_buttons')
    testing_page:                   str = ConfigExtractor('config.testing', prop='page')

    _dev_mode:               bool = ConfigExtractor('config')
    force_render_paths:       str = ConfigExtractor('config')
    include_dir:              str = ConfigExtractor('config')
    include_yaml:       List[str] = ConfigExtractor('config')
    j2_block_end_string:      str = ConfigExtractor('config')
    j2_block_start_string:    str = ConfigExtractor('config')
    j2_comment_end_string:    str = ConfigExtractor('config')
    j2_comment_start_string:  str = ConfigExtractor('config')
    j2_variable_end_string:   str = ConfigExtractor('config')
    j2_variable_start_string: str = ConfigExtractor('config')
    module_name:              str = ConfigExtractor('config')
    modules:            List[str] = ConfigExtractor('config')
    on_error_fail:           bool = ConfigExtractor('config')
    on_undefined:             str = ConfigExtractor('config')
    render_by_default:       bool = ConfigExtractor('config')
    verbose:                 bool = ConfigExtractor('config')
    # ARGS EXTRACTOR TOKEN



    #----------------------------------------------------------------------------
    # WARNING: the following properties are assigned from "other places":
    #   - page:   from the original MacrosPlugin
    #   - _conf: from PyodideMacrosPlugin.on_config

    page: Page  # just as a reminder: defined by MacrosPlugin

    _conf: MkDocsConfig

    docs_dir_path: Path
    """ Current docs_dir of the project as a Path object (ABSOLUTE path) """

    docs_dir_cwd_rel: Path
    """ docs_dir Path object, but relative to the CWD, at runtime """

    _macro_with_indent_pattern:re.Pattern = None
    """
    Pattern to re.match macro calls that will need to handle indentation levels.
    Built at runtime (depends on `macro_with_indents`)
    """

    __lvl_up_url_cache: Dict[str,str]


    #----------------------------------------------------------------------------
    # Also transferred to JS CONFIG:

    base_url:str = ""
    button_icons_directory:str = ""
    pmt_url:str = 'https://gitlab.com/frederic-zinelli/pyodide-mkdocs-theme'
    version:str = __version__
    in_serve:bool = False
    lang:Lang = None
    language:str = 'fr'

    py_snippets_stem: str = ".snippets"


    @property
    def directory_urls_is_false(self):
        """ Return True if config.use_directory_urls is false. """
        return not self._conf.use_directory_urls



    # Override MacroPlugin
    def on_config(self, config:MkDocsConfig):       # pylint: disable=missing-function-docstring
        self.__lvl_up_url_cache = {}
        dct       = LangBase.get_langs_dct()
        self.lang = dct[self.language]
        PLUGIN_CONFIG_SRC.update_lang_defaults_with_current_lang(self)
        JsDumper.register_env_with_lang(self)

        super().on_config(config)   # pylint: disable-next=no-member
                                    # MacrosPlugin is actually "next in line" and has the method


    # Override MacroPlugin
    def macro(self, func, name=""):     # pylint: disable=arguments-renamed
        """
        Add an extra wrapper around the macro, so that the different classes can inject
        their logic around the macros calls themselves, when needed.
        """
        name = name or func.__name__

        @wraps(func)
        def wrapper(*a,**kw):
            """ Delegate the macro execution to the instance method : allow each Maestro level to
                apply its own/dedicated logic, keeping everything perfectly self contained and
                consistent.
                (This is complex, but this is a beautiful piece of logic... XD )
            """
            return self.apply_macro(name, func, *a, **kw)


        # Raise if different macros are registered with the same name (unless allowed).
        # Note: the macro plugin creates a fresh dict on each on_config hook.
        if self.forbid_macros_override and name in self.macros:
            raise PmtMacrosError(
                f'A macro named "{name}" has already been registered, possibly by the theme '
                f'itself.\nPlease remove or rename the { name } macro is in the module: '
                f'{ func.__module__ }'
            )

        wrapper.__name__ = wrapper.__qualname__ = name
        return super().macro(wrapper, name)



    def apply_macro(self, name, func, *a, **kw):            # pylint: disable=unused-argument
        """ Root method: just call the macro... """
        return func(*a, **kw)



    #----------------------------------------------------------------------------



    def file_location(self, page:Optional[Page]=None, **_):
        """
        Path to the current file, relative to the cwd.
        """
        page = page or getattr(self, 'page', None)
        if not page:
            raise PmtInternalError("No page defined yet")
        return f"{ self.docs_dir_cwd_rel }/{ page.file.src_uri }"


    def level_up_from_current_page(self, url:str=None) -> str:
        """
        Return the appropriate number of ".." steps needed to build a relative url to go from the
        current page url back to the root directory.

        Note there are no trailing backslash.

        @url: relative to the docs_dir (ex: "exercices/ ..."). If None, use self.page.url instead.
        """
        url = self.page.url if url is None else url
        if url not in self.__lvl_up_url_cache:
            page_loc:Path = self.docs_dir_path / url
            segments      = page_loc.relative_to(self.docs_dir_path).parts
            out           = ['..'] * ( len(segments) - self.directory_urls_is_false )
            self.__lvl_up_url_cache[url] = '/'.join(out) or '.'
        return self.__lvl_up_url_cache[url]


    def setup_ctx(self, page:Optional[Page], base_url:Optional[str]=None):
        """
        Update self._page (see MacrosPlugin base class) and self.base_url.
        If base_url is None, compute automatically the value.

        This might be required for events or function calls that are not done from the
        on_page_markdown event (only place where the original plugin handle this for us).
        """
        if page:
            self._page = page        # pylint: disable=attribute-defined-outside-init
            # This is for backward compatibility:
            #   - page may be None when building the 404 page
            #   - base_url must be defined for the 404 page
            #   - page may also be None in other cases (typically, for dev_ops operations when
            #     mkdocs is not running!), then self._page must NOT be updated, but base_url
            #     doesn't matter
        self.base_url = self.level_up_from_current_page(page.url) if base_url is None and page else '.'



    #----------------------------------------------------------------------------



    def _omg_they_killed_keanu(self,page_name:str, page_on_context:Page=None):
        """ Debugging purpose only. Use as breakpoint utility.
            @page_on_context argument used when called "outside" of the macro logic (for example,
            in external hooks)
        """
        page = page_on_context or self.page
        if page_name == page.url:
            logger.error("Breakpoint! (the CALL to this method should be removed)")



    def warn_unmaintained(self, that:str=None, *, msg:str=None, partial_msg:str=None):
        """
        Generic warning message for people trying to used untested/unmaintained macros.
        """
        if not msg:
            msg = partial_msg or (
                f"{ that.capitalize() } has not been maintained since the original pyodide-mkdocs "
                "project, may not currently work, and will be removed in the future.\n"
                "Please open an issue on the pyodide-mkdocs-theme repository, if you need it.\n\n"
                f"\t{ self.pmt_url }."
            )
            msg += (
                "\nIf you absolutely need to pass the build right now, you can change the plugin option "
                "build.deprecation_level to 'warn'."
            )

        if self.deprecation_level == 'error':
            raise PmtMacrosDeprecationError(msg)

        logger.error(msg)
