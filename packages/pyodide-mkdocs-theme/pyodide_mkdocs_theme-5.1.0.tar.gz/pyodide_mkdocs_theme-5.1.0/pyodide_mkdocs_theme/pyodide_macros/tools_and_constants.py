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

# pylint: disable=too-few-public-methods, missing-module-docstring

import re
from argparse import Namespace
from dataclasses import dataclass, fields
from pathlib import Path
from typing import ClassVar, Dict, Iterable, Set, Tuple, Type, TypeVar, TYPE_CHECKING

from .exceptions import PmtInternalError, PmtMacrosInvalidArgumentError


if TYPE_CHECKING:
    from .macros.ide_manager import IdeManager
    from . import PyodideMacrosPlugin




class AutoDescriptor:
    """ StrEnum-like property for py3.11-
        If the item string doesn't match the name anymore, one can set the wanted name
        through the constructor, without changing the property name (but F2 will most
        likely also do the trick... Unless string version is actually used somewhere...)
    """

    def __init__(self, prop:str=None):      # allow to override the property name,
        self._prop = prop

    def __set_name__(self, _, prop:str):
        self._prop = prop if self._prop is None else self._prop

    def __get__(self, _, __):
        return self._prop






# --------------------------------------------------------------------
# Various types aliasing, to disambiguate some arguments or constants
# --------------------------------------------------------------------


ZIP_EXTENSION: str = 'zip'

MACROS_WITH_INDENTS = set()
""" Set of identifiers of macro needing indentation logic. They are to register themselves at declaration time """

ICONS_IN_TEMPLATES_DIR = Path("assets/images")
""" Relative location of the icons/pictures for the buttons, in the templates directory """

JS_CONFIG_TEMPLATES = Path(__file__).parent.parent / 'templates' / 'js-libs' / '0-config.js'

PY_LIBS = 'py_libs' # If you change this, don't forget to update config.build.python_libs default
""" Default name for python libraries """

LZW_DELIMITER = "\x1e"    # Unambiguous separator
""" Separator used to structure de compressed strings, with custom LZW algorithm """

HIDDEN_MERMAID_MD = """

!!! tip py_mk_hidden ""
    ```mermaid
    graph TB
        a
    ```
"""


PageUrl = str
""" Page url, as obtained through page.url """

EditorName = str
""" String reference in the form `editor_xxx` """


KEYWORDS_SEPARATOR = 'AST:'

# GENERATED:
PYTHON_KEYWORDS = {

  "and":      ["And"],
  "assert":   ["Assert"],
  "async":    ["AsyncFor","AsyncWhile","AsyncWith","AsyncFunctionDef","comprehension"],
  "async_def":["AsyncFunctionDef"],
  "async_for":["AsyncFor","comprehension"],
  "async_with": ["AsyncWith"],
  "await":    ["Await"],
  "break":    ["Break"],
  "case":     ["match_case"],
  "class":    ["ClassDef"],
  "continue": ["Continue"],
  "def":      ["FunctionDef","AsyncFunctionDef"],
  "del":      ["Delete"],
  "elif":     ["If"],
  "else":     ["For","AsyncFor","While","AsyncWhile","If","IfExp","Try"],
  "except":   ["ExceptHandler"],
  "f_str":    ["JoinedStr"],
  "f_string": ["JoinedStr"],
  "False":    ["Constant"],
  "finally":  ["Try", "TryStar"],
  "for":      ["For","AsyncFor","comprehension"],
  "for_else": ["For","AsyncFor"],
  "for_comp": ["comprehension"],
  "for_inline": ["For"],
  "from":     ["ImportFrom","YieldFrom","Raise"],
  "from_import": ["ImportFrom"],
  "global":   ["Global"],
  "if":       ["comprehension","If","IfExp"],
  "import":   ["Import","ImportFrom"],
  "is":       ["Is","IsNot"],
  "is_not":   ["IsNot"],
  "in":       ["In","NotIn"],
  "lambda":   ["Lambda"],
  "match":    ["Match"],
  "None":     ["Constant"],
  "nonlocal": ["Nonlocal"],
  "not":      ["Not","NotIn","IsNot"],
  "not_in":   ["NotIn"],
  "or":       ["Or"],
  "pass":     ["Pass"],
  "raise":    ["Raise"],
  "raise_from": ["Raise"],
  "return":   ["Return"],
  "True":     ["Constant"],
  "try":      ["Try", "TryStar"],
  "try_else": ["Try", "TryStar"],
  "while":    ["While"],
  "while_else": ["While"],
  "with":     ["With","AsyncWith"],
  "yield":    ["Yield","YieldFrom"],
  "yield_from": ["YieldFrom"],
  "+":        ["UAdd","Add"],
  "-":        ["USub","Sub"],
  "*":        ["Mult"],
  "/":        ["Div"],
  "//":       ["FloorDiv"],
  "%":        ["Mod"],
  "**":       ["Pow"],
  "~":        ["Invert"],
  "<<":       ["LShift"],
  ">>":       ["RShift"],
  "|":        ["BitOr"],
  "^":        ["BitXor"],
  "&":        ["BitAnd"],
  "@":        ["MatMult"],
  "==":       ["Eq"],
  "!=":       ["NotEq"],
  "<":        ["Lt"],
  "<=":       ["LtE"],
  ">":        ["Gt"],
  ">=":       ["GtE"],
  ":=":       ["NamedExpr"],
  "=":        ["Assign","AnnAssign","AugAssign"],
}




class IdeConstants(Namespace):
    """
    Global configuration and data for Ide related elements/values.
    """

    min_ide_id_digits: int = 8
    """ Id numbers (before hashing) will be 0 right padded """

    infinity_symbol: str = "∞"

    ide_buttons_path_template: str = str(
        "{lvl_up}" / ICONS_IN_TEMPLATES_DIR / "icons8-{button_name}-64.png"
    )
    """
    Template to reach the buttons png files from the current IDE.
    Template variables:   lvl_up, button_name
    """

    encryption_token: str = "ENCRYPTION_TOKEN"
    """
    Denote the start and end point of the content of the div tag holding correction and/or remark.
    (only used in the python layer: it is either removed in the on_page_context hook, or it's just
    not inserted at all if the encrypt_corrections_and_rems is False)
    """

    min_recursion_limit: int = 20
    """ Minimum recursion depth allowed. """

    hdr_pattern: re.Pattern = re.compile(r"#\s*-+\s*(?:HDR|ENV)\s*-+\s*#", flags=re.IGNORECASE)
    """ Old fashion way of defining the `env` code in the python source file (still supported). """








class Prefix:
    """ Enum like, holding the prefixes used to build html classes or ids in the project """

    editor_  = AutoDescriptor()
    """ To build the editor name id """

    global_ = AutoDescriptor()
    """ Extra prefix to build the id of the div holding the complete IDE thing """

    comment_ = AutoDescriptor()
    """ Extra prefix for the "toggle assertions button" """

    term_ = AutoDescriptor()
    """ Extra prefix for ids of IDE terminals """

    tester_ = AutoDescriptor()
    """ Extra prefix for ids of the tester IDE """

    playground_ = AutoDescriptor()
    """ Extra prefix for ids of the playground IDE """

    solution_ = AutoDescriptor()
    """ Extra prefix for the div holding the correction + REM """

    input_ = AutoDescriptor()
    """ Extra prefix for the hidden input (type=file) managing the code upload part """

    compteur_ = AutoDescriptor()
    """ Extra id prefix for the span holding the counter of an IDE """

    term_only_ = AutoDescriptor()
    """ Prefix for the id of a div holding an isolated terminal """

    btn_only_ = AutoDescriptor()
    """ Prefix for the id of an isolated 'ide button" """

    auto_run_ = AutoDescriptor()
    """ Prefix for the id of hidden auto running elements (derived of py_btn) """

    solo_term_ = AutoDescriptor()
    """ [OUTDATED] Prefix for the id of the fak div associated to an isolated terminal """

    py_mk_pin_scroll_input = AutoDescriptor()     # Used in the JS part only
    """ Id input, used to mark the current the view port top value when pyodide got ready """

    py_mk_qcm_id_ = AutoDescriptor()
    """ This is actually a CLASS prefix (because it's not possible to register an html id
        on admonitions)
    """







class HtmlClass:
    """ Enum like, holding html classes used here and there in the project. """

    py_mk_py_btn = AutoDescriptor()
    """ Wrapper (div, but not only!) around isolated PyBtn elements """

    py_mk_hidden = AutoDescriptor()    # Was "py_mk_hide"
    """ Things that will have display:none """

    py_mk_ide = AutoDescriptor()       # But "py_mk_ide"... Lost 3 hours because of that 'h'...
    """ Identify div tags holding IDEs """

    terminal = AutoDescriptor()
    """ Identify jQuery terminals. Note: also used by them => do not change it """

    term_solo = AutoDescriptor()
    """ Identify the divs that will hold isolated jQuery terminals, once they are initialized """

    py_mk_terminal_ide = AutoDescriptor()
    """ Identify divs that hold jQuery terminals under an editor, once they are initialized """

    rem_fake_h3 = AutoDescriptor()
    """ To make the "Remarques:" span in the solution admonitions look like a h3 """

    term_editor = AutoDescriptor()
    """ Prefix for the class mode of a terminal (horizontal or vertical) """


    py_mk_terminal = AutoDescriptor()
    """ Generic class for pyodide terminals (put on the div holding the jQuery terminal) """

    py_mk_wrapper = AutoDescriptor()
    """ Prefix for the class mode of the div holding an IDE """

    ide_separator = AutoDescriptor()
    """ might be used with the _v suffix """

    skip_light_box = AutoDescriptor()
    """ Img tab with this class won't be touched by glightbox """

    comment = AutoDescriptor()

    ide_display_btns = AutoDescriptor()

    tooltip = AutoDescriptor()

    compteur = AutoDescriptor()

    compteur_wrapper = AutoDescriptor()

    compteur_txt = AutoDescriptor()

    ide_buttons_div = AutoDescriptor()

    ide_buttons_div_wrapper = AutoDescriptor()

    stdout_ctrl = AutoDescriptor("stdout-ctrl")

    stdout_wrap_btn = AutoDescriptor("stdout-wraps-btn")

    svg_switch_btn = AutoDescriptor("svg-switch-btn")

    term_wrapper = AutoDescriptor()
    """ Prefix for the div holding a terminal and its buttons """

    term_btns_wrapper = AutoDescriptor()
    """ Prefix for the div holding a terminal and its buttons """

    py_mk_figure = AutoDescriptor()
    """ Class for the div added through the figure() macro """

    p5_wrapper = AutoDescriptor()
    """ Class for the divs added through the figure() macro, about p5 related elements """

    p5_btns_wrapper = AutoDescriptor()
    """ Specific class wrapping the p5 buttons in figures elements. """



    py_mk_test_global_wrapper = AutoDescriptor()
    """ Html class for the div holding the whole tests machinery tree """

    py_mk_tests_filters = AutoDescriptor()
    """ Html class for the div holding the filters for the tests """

    py_mk_tests_controllers = AutoDescriptor()
    """ Html class for the div holding the buttons managing the tests """

    py_mk_tests_results = AutoDescriptor()
    """ Html class for the div holding all the tests results """

    py_mk_tests_table = AutoDescriptor()
    """ Html class for the div wrapping the py_mk_tests_results one """

    py_mk_test_element = AutoDescriptor()
    """ Html class for the div holding one test """

    status = AutoDescriptor()
    """ Class name and id prefix used to identify svg status for IDEs tests outcomes. """

    status_filter = AutoDescriptor()
    """ Class name and id prefix used to identify svg status for IDEs tests outcomes. """



    py_mk_admonition_qcm = AutoDescriptor()
    """ Admonition containing a QCM """

    py_mk_questions_list_qcm = AutoDescriptor()
    """ Class identifying the ul or ol wrapping questions """

    py_mk_question_qcm = AutoDescriptor()
    """ Common class identifying the ol, ul and li for the questions """

    py_mk_item_qcm = AutoDescriptor()
    """ Class identifying the ul and li items for one question """

    py_mk_comment_qcm = AutoDescriptor()
    """ Class identifying "details" admonition containing comments for one question. """

    py_mk_encrypted_qcm = AutoDescriptor()
    """ Class identifying encrypted content in the "details" admonition containing comments for one question. """

    qcm_shuffle = AutoDescriptor()
    """ The questions and items must be shuffled if present """

    qcm_hidden = AutoDescriptor()
    """ The answers will be revealed if present """

    qcm_multi = AutoDescriptor()
    """ The user can select several answers """

    qcm_single = AutoDescriptor()
    """ The user can select only one answer """

    qcm_no_admo = AutoDescriptor()
    """ Flag a qcm so that the inner div (generated in JS) will be extracted and will replace
        the whole outer admonition.
    """











@dataclass
class MyEnum:

    SKIPPED_FIELDS: ClassVar[Tuple[str]] = ()
    """ Field names that will be skipped when using cls.gen_values(keep=False) """

    VALUES: ClassVar[Tuple[str]] = ()
    """ Automatically store all the values of the given "enum" as a tuple. """

    _MEMBERS: ClassVar[Set[str]] = set()
    """
    List of all the values in the current Enum (see `is_member`. Ignored fields aren't seen).
    """

    @classmethod
    def gen_values(cls, keep=False):
        """
        Yields the property names associated to each item of the "enum", unless their property
        name is in the class level SKIPPED_FIELD tuple.

        (Note : ClassVar attributes are not listed through `fields`)
        """
        return (
            getattr(cls, field.name)
               for field in fields(cls)
               if keep or field.name not in cls.SKIPPED_FIELDS
        )

    @classmethod
    def has_member(cls, value:str) -> bool :
        """ Return True if the given value is a member of the "Enum" """
        return value in cls._MEMBERS

    @classmethod
    def check_all_members_valid(cls, iterable:Iterable['T']) -> bool :
        """
        Return True if the given iterable only contains existing members.
        DO NOT send in generators!
        """
        actual = set(iterable)
        if set(iterable) <= cls._MEMBERS:
            return

        raise PmtMacrosInvalidArgumentError(
            f"Unknown members for { cls.__name__ }:\n"
            f"  Invalid members: { ', '.join( actual - cls._MEMBERS ) }\n"
            f"\n  Valid members are: { ', '.join( sorted(cls._MEMBERS) ) }"
        )


    @classmethod
    def check_all_member_defined(cls, iterable:Iterable['T']) -> bool :
        """
        Check that all members are defined in iterable then return it.
        DO NOT send in generators!
        """
        actual = set(iterable)
        if cls._MEMBERS != actual:
            missing = cls._MEMBERS - actual
            extra   = actual - cls._MEMBERS
            msg = [
                f"Invalid data structure déclaration based on { cls.__name__ }.\n",
                f"  Missing members: { ', '.join(missing) }\n" * bool(missing),
                f"  Invalid members: { ', '.join(extra) }\n" * bool(extra),
                f"\n  Valid members are: { ', '.join(sorted(cls._MEMBERS)) }"
            ]
            raise PmtInternalError(''.join(msg))
        return iterable






T = TypeVar("T", bound=Type[MyEnum])

def dataclass_with_VALUES(cls:Type[T]) -> Type[T]:
    cls = dataclass(cls)
    cls.VALUES = tuple(cls.gen_values())
    cls._MEMBERS = set(cls.VALUES)
    return cls






@dataclass_with_VALUES
class SiblingFile(MyEnum):
    """
    Suffixes to use to get the names of the different files related to one problem/python file.
    """
    test:    'SiblingFile' = AutoDescriptor('_test.py')
    corr:    'SiblingFile' = AutoDescriptor('_corr.py')
    rem:     'SiblingFile' = AutoDescriptor('_REM.md')
    vis_rem: 'SiblingFile' = AutoDescriptor('_VIS_REM.md')






@dataclass_with_VALUES
class ScriptSection(MyEnum):
    """ Name of each possible section used in a "monolithic" python file """

    SKIPPED_FIELDS: ClassVar[Tuple[str]] = ('ignore',)
    ignore:    'ScriptSection' = AutoDescriptor()

    # WARNING: keep the declaration order -> that's specification for `## {{ py_name:* }}` inclusions
    env:       'ScriptSection' = AutoDescriptor()
    env_term:  'ScriptSection' = AutoDescriptor()
    code:      'ScriptSection' = AutoDescriptor()
    corr:      'ScriptSection' = AutoDescriptor()
    tests:     'ScriptSection' = AutoDescriptor()
    secrets:   'ScriptSection' = AutoDescriptor()
    post_term: 'ScriptSection' = AutoDescriptor()
    post:      'ScriptSection' = AutoDescriptor()

    @classmethod
    def gen_showing(cls):
        yield from ( (section, f'PYODIDE:{ section }') for section in ScriptSection.VALUES)

    @classmethod
    def get_sections_pattern(cls, env:'PyodideMacrosPlugin', with_ignore:bool=True, with_extras:bool=True):
        names = (
            *cls.gen_values(keep=with_ignore),
            *env.extra_pyodide_sections
        ) if with_extras else cls.gen_values(keep=with_ignore)
        return re.compile(rf'PYODIDE[\t ]*:[\t ]*({ "|".join(names) })\b')





@dataclass_with_VALUES
class ScriptData(ScriptSection):
    """
    Python sections & REM contents.
    """

    REM:     'ScriptData' = AutoDescriptor()
    VIS_REM: 'ScriptData' = AutoDescriptor()

    @classmethod
    def gen_showing(cls):
        yield from super().gen_showing()
        yield from ( (section, f'{ section } content') for section in (cls.REM, cls.VIS_REM))


@dataclass_with_VALUES
class ScriptDataWithRemPaths(ScriptData):
    """
    Python sections, REM contents & REM paths.
    """

    REM_PATH:     'ScriptDataWithRemPaths' = AutoDescriptor()
    VIS_REM_PATH: 'ScriptDataWithRemPaths' = AutoDescriptor()

    @classmethod
    def gen_showing(cls):
        yield from super().gen_showing()
        yield from ( (section, f'{ section } path') for section in (cls.REM_PATH, cls.VIS_REM_PATH))








@dataclass_with_VALUES
class IdeMode(MyEnum):
    """
    Runtime profiles, to tweak the default behaviors of the executions in pyodide.
    (IDEs only!)
    """

    delayed_reveal: 'IdeMode' = AutoDescriptor()
    """
    Usable only with IDEs that have neither `tests` nor `secrets` sections, and the number
    of attempts has to be finite. All the attempts must be consumed before the revelation
    is actually done, even without tests (typically useful for turtle exercices, or so).
    """

    no_reveal: 'IdeMode' = AutoDescriptor()
    """
    Keep normal behaviors, except that:
        * The IDE counter is hidden (and infinite, under the hood)
        * On success, the corr/REMs are not revealed: the user only gets the final
          "success" message.
        * This doesn't apply to the corr_btn.
    """

    no_valid: 'IdeMode' = AutoDescriptor()
    """
    The validation button never shows up (neither the related kbd shortcuts), even if secrets
    and/or tests exist:
        * The IDE counter is hidden (and infinite, under the hood)
        * No validation button, no Ctrl+Enter
        * This doesn't apply to the corr_btn.
    """

    revealed: 'IdeMode' = AutoDescriptor()
    """
    The solution, REM and VIS_REM contents are revealed automatically when loading the page.
    """






@dataclass_with_VALUES
class PmtPyMacrosName(MyEnum):
    """
    StrEnum-like object, referencing the possible options for the testing plugin's sub-config.
    """
    IDE:        'PmtPyMacrosName' = AutoDescriptor()
    IDEv:       'PmtPyMacrosName' = AutoDescriptor()
    terminal:   'PmtPyMacrosName' = AutoDescriptor()
    py_btn:     'PmtPyMacrosName' = AutoDescriptor()
    run:        'PmtPyMacrosName' = AutoDescriptor()

    IDE_tester: 'PmtPyMacrosName' = AutoDescriptor()
    IDE_playground: 'PmtPyMacrosName' = AutoDescriptor()
    SKIPPED_FIELDS: ClassVar[Tuple[str]] = 'IDE_tester', 'IDE_playground'

    @classmethod
    def is_ide(cls, name:str):
        """
        Tells if the macro involved matches the IDE_tester one or not.

        NOTES:
            - The method could get names from any macros, also containing IDE in their name
              (like... IDE_py!) so the check must be strict.
            - Not implemented on the IdeManager hierarchy, because this is also needed elsewhere
              in the code base.
        """
        return name in (cls.IDE, cls.IDEv, cls.IDE_tester, cls.IDE_playground)

    @classmethod
    def get_macro_data_config_for(cls, name:str):
        """
        Transform any PMT macro name into its most generic version, and tells if the macro
        involved matches the IDE_tester one or not.
        """
        name = cls.IDE if cls.is_ide(name) else name
        in_macros_data = name not in (cls.IDE_tester, cls.IDE_playground)
        return name, in_macros_data





@dataclass_with_VALUES
class HashPathMode(MyEnum):
    """
    Define how the IDEs html id hashes are computed from their python file location (when
    they have one).
    """

    legacy: 'HashPathMode' = AutoDescriptor()
    """ Use the absolute (unresolved) file path as base for the string to hash """

    relative: 'HashPathMode' = AutoDescriptor()
    """
    Use the path relative to the docs_dir, to avoid any impact of a change of "location" of
    the files on the machine building the site (local, pipeline, ...).
    """

    @classmethod
    def is_legacy(cls, env:'PyodideMacrosPlugin'):
        return env.ides_id_hash_mode == cls.legacy




@dataclass_with_VALUES
class SequentialFilter(MyEnum):
    """
    StrEnum-like object, regrouping the possible options for running automatically some elements
    in page, depending on executions of other elements lower in the page.
    """

    IDE:      'SequentialFilter' = PmtPyMacrosName.IDE
    terminal: 'SequentialFilter' = PmtPyMacrosName.terminal
    py_btn:   'SequentialFilter' = PmtPyMacrosName.py_btn
    run:      'SequentialFilter' = PmtPyMacrosName.run

    EQUIVALENCES: ClassVar[ Dict[PmtPyMacrosName,AutoDescriptor]] = {
        PmtPyMacrosName.IDEv: IDE,
    }

    @classmethod
    def is_allowed(cls, element:'IdeManager', plugin:'PyodideMacrosPlugin'):
        name = element.MACRO_NAME
        if name in cls.EQUIVALENCES:
            name = cls.EQUIVALENCES[name],
        return name in plugin.sequential_only





@dataclass_with_VALUES
class NamedTestCase(MyEnum):
    """
    Identifiers for the default Case objects/configs.
    """
    none:     'NamedTestCase' = AutoDescriptor("")
    skip:     'NamedTestCase' = AutoDescriptor()
    fail:     'NamedTestCase' = AutoDescriptor()
    code:     'NamedTestCase' = AutoDescriptor()
    corr:     'NamedTestCase' = AutoDescriptor()
    human:    'NamedTestCase' = AutoDescriptor()
    no_clear: 'NamedTestCase' = AutoDescriptor()




@dataclass_with_VALUES
class SequentialRun(MyEnum):
    """
    StrEnum-like object, regrouping the possible options for running automatically some elements
    in page, depending on executions of other elements lower in the page.
    """
    none: 'SequentialRun' = AutoDescriptor("")
    dirty: 'SequentialRun' = AutoDescriptor()
    all: 'SequentialRun' = AutoDescriptor()




@dataclass_with_VALUES
class MacroShowConfig(MyEnum):
    """ Possible values for the SHOW argument of the various macros. """

    none: 'MacroShowConfig' = AutoDescriptor("")
    """ Default value: show nothing"""

    args: 'MacroShowConfig' = AutoDescriptor()
    """ Value arguments' values """

    #-----------------------------------------------------------

    python: 'MacroShowConfig' = AutoDescriptor()
    """ Show python code sections (ONLY for runners related macros) """

    contents: 'MacroShowConfig' = AutoDescriptor()
    """ Show python code sections and REMs content (ONLY for runners related macros) """

    all: 'MacroShowConfig' = AutoDescriptor()
    """ Show args and python code sections (ONLY for runners related macros) """


    SKIPPED_FIELDS: ClassVar[Tuple[str]] = ('python', 'contents', 'all')
    # Skipping values specific to runners macros







@dataclass_with_VALUES
class P5BtnLocation(MyEnum):
    """
    Possible HTML classes and arguments names for p5 animations buttons (in figure macros)
    """
    left:   'P5BtnLocation' = AutoDescriptor()
    right:  'P5BtnLocation' = AutoDescriptor()
    top:    'P5BtnLocation' = AutoDescriptor()
    bottom: 'P5BtnLocation' = AutoDescriptor()








@dataclass_with_VALUES
class PageInclusion(MyEnum):
    """
    StrEnum-like object, referencing the possible options for the testing plugin's sub-config.
    """
    none:          'PageInclusion' = AutoDescriptor()
    serve:         'PageInclusion' = AutoDescriptor()
    site:          'PageInclusion' = AutoDescriptor()
    site_with_nav: 'PageInclusion' = AutoDescriptor()


    @classmethod
    def is_built(cls, value:'PageInclusion', env:'PyodideMacrosPlugin'):
        return value != PageInclusion.none and (
            env.in_serve or value != PageInclusion.serve
        )

    @classmethod
    def is_in_nav(cls, value:'PageInclusion', env:'PyodideMacrosPlugin'):
        return value != PageInclusion.none and (
            env.in_serve or value == PageInclusion.site_with_nav
        )





@dataclass_with_VALUES
class Qcm(MyEnum):
    """ Html classes used for the various states of the MCQs. """

    checked:   'Qcm' = AutoDescriptor()
    unchecked: 'Qcm' = AutoDescriptor()
    ok:        'Qcm' = AutoDescriptor('correct')
    wrong:     'Qcm' = AutoDescriptor('incorrect')
    missed:    'Qcm' = AutoDescriptor()
    fail_ok:   'Qcm' = AutoDescriptor('must-fail')

    multi:     'Qcm' = AutoDescriptor()
    single:    'Qcm' = AutoDescriptor()

    show_tests_buttons = ('checked', 'unchecked', 'correct', 'incorrect')







@dataclass_with_VALUES
class DebugConfig(MyEnum):
    """ (Internal dev_mode options...) """

    check_decode: bool = False
    """ If True, decode any LZW encoded string to check consistency """

    check_global_json_dump: bool = False
    """ If True, check that the JSON dump for PAGE_IDES_CONFIG is valid """
