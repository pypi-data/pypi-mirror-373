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

# pylint: disable=unused-argument


from abc import ABCMeta
import re
import hashlib
from typing import Any, ClassVar, Dict, List, Literal, Optional, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass
from pathlib import Path

from pyodide_mkdocs_theme.pyodide_macros.parsing import items_comma_joiner


from .. import html_builder as Html
from ..exceptions import (
    PmtInternalError,
    PmtMacrosError,
    PmtMacrosInvalidArgumentError,
    PmtMacrosNonUniqueIdError,
    PmtMermaidConfigError
)
from ..tools_and_constants import (
    KEYWORDS_SEPARATOR,
    PYTHON_KEYWORDS,
    HashPathMode,
    HtmlClass,
    IdeConstants,
    PmtPyMacrosName,
    SequentialFilter,
)
from ..messages import Tip
from ..paths_utils import get_ide_button_png_path
from ..html_dependencies.deps_class import DepKind
from ..plugin.tools.pages_and_macros_py_configs import MacroPyConfig
from ..plugin.config.definitions.plugin_config import PLUGIN_CONFIG_SRC
from .ide_files_data import CompositeFilesDataExtractor

if TYPE_CHECKING:
    from ..plugin import PyodideMacrosPlugin












@dataclass
class IdeManagerMacroArguments:
    """
    Handle the creation of the underlying object, articulating the inner state with the macros
    actual arguments and performing validation of those.

    Also defines all the instance properties for the object (whatever the inheritance chain).
    """


    KEEP_CORR_ON_EXPORT_TO_JS: ClassVar[bool] = False
    """ Define if the corr section must be exported to the JS layer. """


    KW_TO_TRANSFER: ClassVar[Tuple[ Union[str, Tuple[str,str]]] ]  = ()
    """
    Configuration of the keywords that should be extracted if given in the constructor.
    This makes the "link" between the macros arguments and the actual properties in the python
    object, which often differ (legacy in action...).

    KW_TO_TRANSFER is an iterable of (argument_name, property_name) pairs of strings, or if
    an element is a simple string instead, it will be used as (value, value.lower()).
    """


    MACRO_NAME: ClassVar[PmtPyMacrosName] = None
    """ Origin of the macro call (for __str__) """


    ID_PREFIX: ClassVar[str] = None
    """ Must be overridden in the child class """

    NEED_INDENTS: ClassVar[bool] = False
    """
    Specify the macro had adding multiline content (so it _will_ consume one indentation data).
    """

    DEPS_KIND: ClassVar[DepKind] = DepKind.pyodide
    """
    Register the kind of js scripts that must be added to the page, for the current object.
    """

    IDE_VERT: ClassVar[ Literal["","_v"] ] = ""
    """ For IDEs only, but defined here to allow better html id generation """


    # Defined on instantiation:
    #--------------------------


    env: 'PyodideMacrosPlugin'
    """ The MaestroEnv singleton """

    py_names: Tuple[str]
    """
    Base names for the files to use (first argument passed to the macros), possibly with
    combinations instructions.
    Partial path from the directory holding the sujet.md file, to the one holding all the
    other required files, ending with the common prefix for the exercice.
    Ex:     "exo" to extract:   "exo.py", "exo_corr.py", "exo_test.py", ...
            "sub_exA/exo" for:  "sub_exA/exo.py", "sub_exA/exo_corr.py", ...
    """

    id: Optional[int]
    """ Used to disambiguate the ids of two IDEs, if the same file is used several times
        in the document.
    """

    excluded: str
    """ String of spaces or coma separated python functions or modules/packages that are forbidden
        at runtime. By default, nothing is forbidden.
            - Every string section that matches a builtin callable forbid that function by
              replacing it with another function which will raise an error if called.
            - Every string section prefixed with a fot forbids a method call. Here a simple
              string containment check is done opn the user's code, to check it does not
              contain the desired method name with the dot before it.
            - Any other string section is considered as a module name and doing an import (in
              any way/syntax) involving that name will raise an error.

        Note that the restrictions are rather strict, and may have unexpected side effects, such
        as, forbidding `exec` will also forbid to import numpy, because the package relies on exec
        for some operations at import time.
        To circumvent such a kind of problems, use the white_list argument.
    """

    white_list: str
    """ String of spaces or coma separated python modules/packages names the have to be
        preloaded before the code restrictions are enforced on the user's side.
    """

    rec_limit: int
    """ If used, the recursion limit of the pyodide runtime will be updated before the user's
        code or the tests are run.
        Note that this also forbids the use of the `sys.setrecurionlimit` at runtime.
    """

    with_mermaid: bool
    """ If True, a mermaid graph will be generated by this IDE/terminal/py_btn, so the general
        setup for mermaid must be put in place.
    """

    auto_run: bool
    """ If True, the underlying python file is executed just after the page has loaded. """

    show: str       # Sink (not needed here! / kept for debugging purpose...)
    """ Allow to print all the arguments of the current macro call to the console. """

    run_group: Optional[str]
    """
    Allow to identify groups of elements and their global ordering in the page, for sequential
    executions: only one element of a group will be automatically run when the "sequential"
    runs are activated.
    """

    extra_kw: Optional[Dict[str,Any]] = None
    """
    Any kw left in the original call.
    Should be always be None when reaching IdeManager.__post_init__. This allows subclasses
    to handle the extra (legacy) keywords on their side.
    """


    # defined during post_init or in child class
    #-------------------------------------------

    exo_py: Optional[Path] = None
    """
    Unresolved absolute path to the target python file.
    As for PMT 5+, this has to be stored in the IdeManager to be allowed to build the editor html id
    while the CompositeFilesDataExtractor instances are now cached and unique considering the resolved path.
    """

    py_name: str = ""
    """
    If some python files are given through py_names, this is the stem of the file.
    Warning: not usable in __post_init__ yet (especially in handle_extra_args).
    """

    built_py_name: str = ""
    """
    Extended python file name, prepending with page url data and stuff, to make the name
    more explicit.
    """

    indentation: str = ""
    """ Indentation on the left of the macro call, as str """



    def __post_init__(self):

        if self.MACRO_NAME is None:
            raise NotImplementedError("Subclasses should override the MACRO_NAME class property.")

        if self.ID_PREFIX is None:
            raise NotImplementedError("Subclasses should override the ID_PREFIX class property.")

        # Archive the indentation level for the current IDE:
        if self.NEED_INDENTS:
            self.indentation = self.env.get_macro_indent()

        self.handle_extra_args()        # may be overridden by subclasses.

        self.env.set_current_page_insertion_needs(self.DEPS_KIND)

        if self.with_mermaid:
            self.env.set_current_page_insertion_needs(DepKind.mermaid)

            if not self.env.is_mermaid_available:
                raise PmtMermaidConfigError(
                    "\nCannot use MERMAID=True because the superfences markdown extension is not "
                    "configured to accept mermaid code blocks.\n"
                    "Please add the following in your mkdocs.yml file, in the markdown_extension "
                    "section:\n\n"
                    "  - pymdownx.superfences:\n"
                    "      custom_fences:\n"
                    "        - name: mermaid\n"
                    "          class: mermaid\n"
                    "          format: !!python/name:pymdownx.superfences.fence_code_format\n"
                )



    def __str__(self):
        return self.env.file_location(all_in=True)



    def handle_extra_args(self):
        """
        Assign the extra arguments provided through other keyword arguments, handling only those
        actually required for the child class.
        Also extract default values for properties that are still set to None after handling the
        keyword arguments.
        If some are remaining, after this in self.extra_kw, an error will be raised.
        """
        to_transfer = [
            data if isinstance(data,tuple) else (data, data.lower())
            for data in self.KW_TO_TRANSFER
        ]
        for kw, prop in to_transfer:
            if kw in self.extra_kw:
                value = self.extra_kw.pop(kw)
                setattr(self, prop, value)

        if self.extra_kw:
            raise PmtMacrosInvalidArgumentError(
                f"Found forbidden arguments:\n" + "".join(
                    f"    {k} = {v!r}\n" for k,v in self.extra_kw.items()
                ) + f"\n{ self.env.log() }"
            )
















@dataclass
class IdeSectionsManager(IdeManagerMacroArguments):
    """
    Generic logistic related to sections data.

    Implement __getattr__ so that all undefined `has_xxx` properties are automatically
    relayed to the files_data object.
    """

    files_data: CompositeFilesDataExtractor = None

    # vvvvvvvvv
    # GENERATED
    @property
    def has_env(self): return "env" in self.files_data.contents
    @property
    def has_env_term(self): return "env_term" in self.files_data.contents
    @property
    def has_code(self): return "code" in self.files_data.contents
    @property
    def has_corr(self): return "corr" in self.files_data.contents
    @property
    def has_tests(self): return "tests" in self.files_data.contents
    @property
    def has_secrets(self): return "secrets" in self.files_data.contents
    @property
    def has_post_term(self): return "post_term" in self.files_data.contents
    @property
    def has_post(self): return "post" in self.files_data.contents
    @property
    def has_rem(self): return "REM" in self.files_data.contents
    @property
    def has_vis_rem(self): return "VIS_REM" in self.files_data.contents
    # GENERATED
    # ^^^^^^^^^

    @property               # pylint: disable-next=all
    def has_any_corr_rems(self):
        return self.has_corr or self.has_rem or self.has_vis_rem

    @property               # pylint: disable-next=all
    def has_check_btn(self): return False


    def __post_init__(self):
        super().__post_init__()

        self.exo_py, self.files_data = CompositeFilesDataExtractor.get_file_extractor_and_exo_py_for(self.env, self.py_names)
        self.py_name = self.exo_py.stem if self.exo_py else ""

        self._define_max_attempts_symbols_and_value()       # To do before files validation: MAX

        self._validate_files_config()

        if self.rec_limit < -1:         # standardization
            self.rec_limit = -1

        if -1 < self.rec_limit < IdeConstants.min_recursion_limit:
            raise PmtMacrosInvalidArgumentError(
                f"The recursion limit is set too low and may causes runtime troubles. "
                f"Please set it to at least { IdeConstants.min_recursion_limit }.{ self.env.log() }"
            )


    def _define_max_attempts_symbols_and_value(self):
        """ Placeholder, to insert (very...) specific logic for IDEs... """


    def _validate_files_config(self):
        raise NotImplementedError()

    def _check_forbidden_sections(self, sections:str, err_header:str):
        forbidden = [
            section for section in sections.split() if getattr(self, f"has_{ section.lower() }")
        ]
        if forbidden:
            self._validation_outcome(
                f"{ err_header }, but found:\n"
                f"    { items_comma_joiner(forbidden, 'and') }"
            )


    def _build_error_msg_with_option(self, msg:Optional[str], config_opt:Optional[str]=None):
        msg = f"\nInvalid configuration with:\n{ msg }\n{ self.env.log() }"
        if config_opt:
            msg += (
                f"\n    You can deactivate this check by setting `mkdocs.yml:plugins.{config_opt}:"
                f" false`, or the equivalent in a `{ self.env._pmt_meta_filename }` file, or as "
                "metadata of a markdown documentation page."
            )
        return msg


    def _validation_outcome(self, msg:Optional[str]):
        """
        Routine that can be called from the _validate_files_config implementation, raising if given
        an error message as argument.
        """
        if msg:
            raise PmtMacrosError(msg)

















@dataclass
class IdeManagerMdHtmlGenerator(IdeSectionsManager):
    """
    Generic html handling (ids, buttons, ...)
    """

    editor_name: str = ''
    """ tail part of most html elements' ids, in the shape of 'editor_{32 bits hexadecimal}' """


    def __post_init__(self):
        super().__post_init__()
        self.editor_name = self.generate_id()



    def make_element(self) -> str:
        """
        Create the actual element template (html and/or md content).
        """
        raise NotImplementedError("Subclasses should implement the make_element method.")



    def generate_id(self):
        """
        Generate an id number for the current element, in the form:

            "{ self.PREFIX_ }{ 32 chars hex value }"

        <br><br>

        ## CONSTRAINTS:

        - Unique to every runner used throughout the whole website.
        - Stable, so that it can be used to identify what IDE goes with what file or what
        localStorage data.
        - For IDEs:
            * It must be possible to differentiate IDEs from different pages using the same
            base python file
            * It must be possible to identify unambiguously IDEs in different pages that do
            not use any python file.

        <br><br>

        ## STRATEGIES:

        The string to hash is built in the following ways:
        - For elements with python file(s):
            * use the absolute path (unresolved) to the main side fail (first argument if
              `py_names` is a varargs).
            * non IDE macros see the macro name added to the string (to differentiate them
              from IDEs, while keeping backward compatibility for IDEs' ids)
            * the ID argument _will_ often be needed to differentiate the runners/macros,
              while allowing cache capabilities without much ambiguity when the user is
              adding, deleting or moving macro calls around in the md page.
              This can be turned down with `build.activate_cache: false`: then all non IDE
              macros fall back to the behavior below.
            * IDEs specific: the "mode" (/_v) is appended to the string before hashing (legacy).

        - For elements without a python file, or for non IDEs with `build.activate_cache: false`:
            * use the page url, with the macro name, then a counter of that kind of macro calls.

        Uniqueness of the resulting hash is verified and BuildError is raised if two identical
        hashes are encountered.
        """
        is_ide = PmtPyMacrosName.is_ide(self.MACRO_NAME)

        if self.exo_py and (is_ide or self.env.activate_cache):
            # IDE ids have to stay consistent with previous implementations.
            # But add the macron name in the string generating the hash for non IDE elements, so
            # that there using the same source file for different kind of macros won't generate
            # equivalent hashes (ease the way for the users, _and_ more consistent with previous
            # behaviors... Even if that is probably a breaking change).
            less_ID_needs = "" if is_ide else ':'+self.MACRO_NAME

            runner_path   = self.exo_py
            if is_ide and not HashPathMode.is_legacy(self.env):
                # Avoid any dependency on the domain/site name, if needed:
                runner_path = Path(self.exo_py).relative_to(self.env.docs_dir_path)

            to_hash = f"{ runner_path }{ self.IDE_VERT }{ less_ID_needs }"

        else:
            count   = self.env.macros_counters[ self.MACRO_NAME ].inc()
            to_hash = f"{ self.env.page.url }-{ self.MACRO_NAME }-{ count }"
                    # DO NOT lstrip, even if it looks ugly on the home page (nobody but me can see
                    # it anyway... :rolleyes:), to keep implementation consistent for users...

        hashed = self.id_to_hash(to_hash)
        # print(hashed, to_hash)
        return hashed



    def id_to_hash(self, id_path:str, *_):
        """
        Hash the "clear version of it" to add as html id tail, prefix it, and check the uniqueness
        of the hash across the whole website.

        @*_: used for backward compatibility only.
        """
        to_hash = id_path if self.id is None else f"{ id_path }{ self.id }"
        hashed  = hashlib.sha1(to_hash.encode("utf-8")).hexdigest()
        html_id = f"{ self.ID_PREFIX }{ hashed }"

        if not self.env.is_unique_then_register(html_id, id_path, self.id):
            cache_option = PLUGIN_CONFIG_SRC.get_plugin_path('build.activate_cache', no_deprecated=True)
            msg = (
                "The same html id got generated twice.\nIf you are trying to use the same "
                "set of files for different macros calls, use their ID argument (int >= 0) "
                "to disambiguate them.\n\n"
                "If you are encountering this problem with macros other than IDE or IDEv and you "
                "do not need some extra speed rendering-wise, you also can deactivate the PMT "
               f"cache, using `{ cache_option }: false`.\n\n"
               f"ID values already in use:   { self.env.get_registered_ids_for(id_path) }\n"
               f"Id generated with:          { to_hash }\n{ self.env.log() }"
            )
            raise PmtMacrosNonUniqueIdError(msg)
        return html_id



    def create_button(
        self,
        btn_kind: str,
        *,
        margin_left:   float = 0.2,
        margin_right:  float = 0.2,
        extra_btn_kls: str   = "",
        **kwargs
    ) -> str:
        """
        Build one button
        @btn_kind:      The name of the JS function to bind the button click event to.
                        If none given, use the lowercase version of @button_name.
        @margin_...:    CSS formatting as floats (default: 0.2em on each side).
        @extra_btn_kls: Additional html class for the button element.
        @**kwargs:      All the remaining kwargs are attributes added to the button tag.
        """
        return self.cls_create_button(
            self.env,
            btn_kind,
            margin_left   = margin_left,
            margin_right  = margin_right,
            extra_btn_kls = extra_btn_kls,
            **kwargs
        )


    @classmethod
    def cls_create_button(
        cls,
        env:           'PyodideMacrosPlugin',
        btn_kind:       str,
        *,
        margin_left:    float = 0.2,
        margin_right:   float = 0.2,
        extra_btn_kls:  str   = "",
        **kwargs
    ) -> str:
        """
        Build one button
        @btn_kind:      The name of the JS function to bind the button click event to.
                        If none given, use the lowercase version of @button_name.
        @margin_...:    CSS formatting as floats (default: 0.2em on each side).
        @extra_btn_kls: Additional html class for the button element.
        @**kwargs:      All the remaining kwargs are attributes added to the button tag.
        """
        png_name, lang_prop, bgd_color = get_button_fields_data(btn_kind)

        lvl_up    = env.level_up_from_current_page()
        img_link  = get_ide_button_png_path(lvl_up, png_name)
        img_style = {}
        if bgd_color is not None:
            img_style = {'style': f'--ide-btn-color:{ bgd_color };'}

        img = Html.img(src=img_link, kls=HtmlClass.skip_light_box, **img_style)

        tip: Tip = getattr(env.lang, lang_prop)
        tip_span = Html.tooltip(tip, tip.em)

        btn_style = f"margin-left:{margin_left}em; margin-right:{ margin_right }em;"
        if 'style' in kwargs:
            btn_style += kwargs.pop('style')

        button_html = Html.button(
            f'{ img }{ tip_span }',
            btn_kind = btn_kind,
            kls = ' '.join([HtmlClass.tooltip, extra_btn_kls]),
            style = btn_style,
            **kwargs,
        )
        return button_html





def get_button_fields_data(btn_kind:str):
    """
    Return the various property names to use for each kind of element (tooltip, image, ...),
    for the given initial button_name.

    @returns:   png_name, lang_prop, js_method, color
    """
    if btn_kind in BTNS_KINDS_CONFIG:
        return BTNS_KINDS_CONFIG[btn_kind]
    return (btn_kind, btn_kind, None)


# btn_kind:       (png,          lang,           color)  (if color is None: apply default)
BTNS_KINDS_CONFIG = {
    'corr_btn':   ('check',      'corr_btn',     'green'),
    'show':       ('check',      'show',         'gray'),

    'test_ides':  ('play',       'test_ides',    'orange'),
    'test_stop':  ('stop',       'test_stop',    'orange'),
    'test_1_ide': ('play',       'test_1_ide',   'orange'),
    'load_ide':   ('download',   'load_ide',     None),

    'p5_start':   ('play',       'p5_start',     None),
    'p5_stop':    ('stop',       'p5_stop',      None),
    'p5_step':    ('step',       'p5_step',      None),
}

















@dataclass
class IdeManagerExporter(IdeManagerMdHtmlGenerator, metaclass=ABCMeta):
    """
    Handle data exportations to JS, through the MacroPyConfig objects (compute only values
    that are not stored on the instance itself).
    """


    def __post_init__(self):
        super().__post_init__()
        self.built_py_name = self._build_py_filename_for_uploads()
        (
            self._excluded,
            self._excluded_methods,
            self._excluded_kws,
            self._white_list
        ) = self._compute_exclusions_and_white_lists()

        registered = dict(self.exported_items())
        self.env.set_current_page_js_macro_config(
            self.editor_name, MacroPyConfig(**registered)
        )

        macro_data_name, in_macros_data = PmtPyMacrosName.get_macro_data_config_for(self.MACRO_NAME)

        # IDE_tester or playground macro is not exported, so exit directly:
        if not in_macros_data:
            return

        if not self.env.all_macros_data:            # Defensive programming
            if self.env.is_dirty: return
            raise PmtInternalError(
                "No MacroData instance registered yet! Seeking for "+self.MACRO_NAME
            )

        macro_data = self.env.all_macros_data[-1]
        if macro_data.macro != macro_data_name:     # Defensive programming
            raise PmtInternalError(
                f"Wrong MacroData object: Expected {macro_data_name} but was {macro_data.macro}"
            )
        macro_data.build_ide_manager_related_data(self)


    def exported_items(self):
        """
        Generate all the items of data that must be exported to JS.
        """
        yield from [
            ('py_name',          self.built_py_name),
            ("excluded",         self._excluded),
            ("excluded_methods", self._excluded_methods),
            ("excluded_kws",     self._excluded_kws),
            ("rec_limit",        self.rec_limit),
            ("white_list",       self._white_list),
            ("auto_run",         self.auto_run),
            ('python_libs',      [ p.name for p in map(Path,self.env.python_libs) ]),
            ('pypi_white',       self.env.limit_pypi_install_to),
            ('seq_run',          self.env.sequential_run),

            *zip(
                ('run_group', 'order_in_group'),
                self.get_page_group_and_order()
            ),
        ]
        # All data related to files (python, REMs):
        yield from self.files_data.get_sections_data( with_corr=self.KEEP_CORR_ON_EXPORT_TO_JS )



    #-----------------------------------------------------------------------------


    def get_page_group_and_order(self):
        """
        Build sequential runs related data.

        The overall "state" of the runner, considering sequential runs, ios determined here:
            - Check the RUN_GROUP argument validity
            - what is its group ID (RUN_GROUP cleaned up)
            - is it in a sequential run group or not ?
            - does it have priority or not ?

        The actual encoding of these states are left to determine by the current PageConfiguration:
            self.env.current_page_config.get_run_group_data(...) -> [int, int]
        """
        group_id = self.run_group and self.run_group.strip('*')
        is_skip  = group_id == 'SKIP'
        has_priority = group_id and (self.run_group.startswith('*') or self.run_group.endswith('*'))

        if isinstance(group_id, str) and is_skip and has_priority:
            raise PmtMacrosInvalidArgumentError(
                f"Invalid RUN_GROUP={self.run_group!r} argument: a skipped element cannot get priority."
                f"{ self.env.log() }"
            )

        in_sequential_run = not is_skip and SequentialFilter.is_allowed(self, self.env)
        run_config = self.env.current_page_config.get_run_group_data(
            in_sequential_run, bool(has_priority), group_id
        )

        return run_config




    def _build_py_filename_for_uploads(self):
        """
        Guess an explicative enough py_name (when downloading the IDE content)
        """
        root_name = Path(self.env.page.url).stem
        py_name   = f"{ root_name }-{ self.py_name }".strip('-') or 'unknown'
        return py_name + '.py'



    def _compute_exclusions_and_white_lists(self):
        """
        Compute all code exclusions and white list of imports
        """

        non_kws, kws, *_ = self.excluded.split(KEYWORDS_SEPARATOR) + ['']
        # print((non_kws, kws))

        all_excluded   = self._exclusion_string_to_list(string_prop=non_kws)
        kws_candidates = self._exclusion_string_to_list(string_prop=kws)
        white_list     = self._exclusion_string_to_list("white_list")

        exclusions = excluded, excluded_methods, excluded_kws = [
            self._get_exclusions_prefixed_with(lst, pattern, slice)
            for lst, pattern, slice in (
                (all_excluded,   r'(?!\d)\w+', 0),
                (all_excluded,   r'[.](?!\d)\w+', 1),
                (kws_candidates, '.+', 0),
            )
        ]
        # print(*exclusions,sep='\n')

        if excluded_kws and any(kw for kw in excluded_kws if kw not in PYTHON_KEYWORDS):
            wrongs=', '.join(sorted(repr(kw) for kw in excluded_kws if kw not in PYTHON_KEYWORDS))
            raise PmtMacrosInvalidArgumentError(
                f"Invalid python keywords for the `SANS` argument: { wrongs }.{ self.env.log() }"
            )

        if 'globals' in excluded:
            raise PmtMacrosInvalidArgumentError(
                "It's not possible to use `SANS='globals`, because it would break pyodide "
               f"itself.{ self.env.log() }"
            )

        # Check nothing missing (would mean invalid syntax):
        all_done_check = all_excluded + kws_candidates
        if all_done_check and len(all_done_check) != sum(map(len, exclusions)):
            all_done_check = { arg.lstrip('.') for arg in all_done_check }
            for lst in exclusions:
                all_done_check.difference_update(lst)
            wrongs = ', '.join( map(repr, sorted(all_done_check)) )
            raise PmtMacrosInvalidArgumentError(
                f"Invalid `SANS` argument, containing: { wrongs }{ self.env.log() }"
            )

        return excluded, excluded_methods, excluded_kws, white_list



    def _exclusion_string_to_list(self, prop:str=None, *, string_prop:str=""):
        """
        Convert a string argument (exclusions or white list) tot he equivalent list of data.
        """
        string_prop = getattr(self, prop) if prop else string_prop
        rule = (
            string_prop or ""       # Never allow None
        ).strip().strip(';,')       # 2 steps, to make sure any kind of whitespaces are stripped
        lst = re.split(r'[\s;,]+', rule) if rule else []
        return lst


    def _get_exclusions_prefixed_with(self, exclusions_lst:List[str], pattern:str, slice_on:int=None):
        if not exclusions_lst:
            return exclusions_lst
        reg = re.compile(pattern)
        return [
            kw[slice_on:] if slice_on else kw
            for kw in exclusions_lst if reg.fullmatch(kw)
        ]














@dataclass
class IdeManager(
    IdeManagerExporter,
    IdeManagerMdHtmlGenerator,
    IdeSectionsManager,
    IdeManagerMacroArguments,
    metaclass=ABCMeta,
):
    """
    Base class managing the information for the underlying environment.
    To be extended by a concrete implementation, providing the actual logistic to
    build the html hierarchy (see self.make_element).
    """
