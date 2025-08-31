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
# pylint: disable=invalid-name

from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, Optional, Type, Tuple, TYPE_CHECKING

from pyodide_mkdocs_theme.pyodide_macros.tools_and_constants import MacroShowConfig, ScriptData, ScriptDataWithRemPaths, ScriptSection



if TYPE_CHECKING:
    from ..pyodide_macros_plugin import PyodideMacrosPlugin
    from ...macros.ide_manager import IdeManager
    from ...macros.ide_ide import Ide


# All the classes defined here are there to provide autocompletion to the user.
# They are (almost) all generated automatically (among other things...), from
# python_devops/py_codes_updates/macro_data_code.py, to ensure they are always
# in sync with the actual implementation.




class DataGetter:
    """
    Descriptor automatically "tapping" into the inner _data_dct dict.
    Possibly allow to use default values when the property/key is missing.
    """

    def __init__(self, prop=None, default:Any=None, none_as_default=False, wraps:Callable=None):
        self.key = prop
        self.default = default
        self.allow_default = default is not None or none_as_default
        self.wraps = wraps

    def __set_name__(self, _, name:str):
        if self.key is None:
            self.key = name

    def __get__(self, obj:'ObjectWithDataGetters', _):
        if self.key not in obj._data_dct and self.allow_default:
            value = self.default
        else:
            value = obj._data_dct[self.key]
        return self.wraps(value) if self.wraps else value

    def __set__(self, obj, _value):
        raise ValueError(f"Cannot set { obj.__class__.__name__ } properties ({self.key!r})")





class ObjectWithDataGetters:

    def __init__(self, dct):
        self._data_dct: Dict[str,bool] = dct

    def show_as_list(self):
        ordered_items = sorted(self._data_dct.items(), key=lambda kv: (kv[0]!='py_name', kv[0]))
        return [ f"{ key }={val!r}" for key,val in ordered_items ]




class MacroDataGeneric:
    """
    Generic interface, common to all MacroData objects.
    """
    # All properties declared with a default value to ease the extraction to build the docs...

    macro: str
    """
    Name of the macro that created this object. Notes:

    - `#!py "IDEv"` calls are seen has `#!py "IDE"`.
    - `#!py "IDE_tester"` calls are not gathered.
    """

    args: ObjectWithDataGetters
    """
    All values of arguments, as passed in the macro call
    (overridden by child class with the needed class).
    """

    src_uri: str
    """
    Uri of the source file, relative to cwd.
    """

    page_url: str
    """
    As provided by `page.url` (aka, relative to the site_dir and taking in consideration
    the value of `use_directory_urls`).
    """

    full_page_url: str
    """
    Absolute url of the built page holding this element.
    """

    meta: Dict[str,Any]
    """
    Metadata of the source page (allows to store extra informations there, to add logic later
    when building the content).
    """

    abs_link: str
    """
    Absolute url of the element in the built page (defaults to full_page_url).
    """




class MacroDataSpecific:
    """
    Properties of MacroData objects that are defined only when appropriated (generally, for
    macros involving python files, like `IDE`, `IDEv`, `terminal`, `py_btn`).
    """

    storage_id: Optional[str] = None
    """ Id used as key in the localStorage, if the related entry exists, None otherwise. """

    load_py_name: Optional[str] = None
    """
    Python file name used for the download/export machinery of the IDEs (Will generally differ
    from the macro `py_name` argument).
    """

    has_check_btn: Optional[bool] = None
    """
    True if the related element will have a visible validation button in the GUI.
    <br>_Alternative way to access the information in `self.has.check_btn` or
    `self.content.check_btn`_
    """

    content: Optional['Content'] = None
    """
    Object showing the "content" associated with sections or buttons for the generated object.
    <br>_See the detailed interface of the `Content` objects. Support autocompletion when
    defined._
    """

    has: Optional['HasContent'] = None
    """
    Object indicating what sections, files or buttons are present on the generated object.
    <br>_See the detailed interface of the `HasContent` objects. Support autocompletion when
    defined._
    """





class MacroData(MacroDataGeneric, MacroDataSpecific):
    """
    Object storing data about each macro call found in the documentation.
    They are stored along the way, and allow the user to create pages at build time (through
    on_page_context hooks, for example) with are depending on data
    """

    ENV: ClassVar['PyodideMacrosPlugin']
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]]


    @staticmethod
    def register_config(env:'PyodideMacrosPlugin'):
        """
        Register the current plugin runtime object, so that global data can be built
        according to those.
        """
        MacroData.ENV = env
        MacroData.SITE_URL = env.site_url + '/' * (not env.site_url.endswith('/'))


    def __init__(self, macro_name, args_dict):
        self.macro    = macro_name
        self.args     = self.ARGS_CLASS(args_dict)
        self.meta     = self.ENV.page.meta or {}
        self.src_uri  = f"{ self.ENV.docs_dir_cwd_rel.as_posix() }/{ self.ENV.page.file.src_uri }"
        self.page_url = self.ENV.page.url
        self.full_page_url = self.SITE_URL + self.page_url
        self.abs_link = self.full_page_url



    def build_ide_manager_related_data(self, manager:'IdeManager'):
        """
        Update all the infos related to IdeManager instances, once the current object has been
        created. This also will create `self.has` and `self.content` objects.
        """
        contents = dict(manager.files_data.get_all_data())
        contents['check_btn'] = manager.has_check_btn       # duplicate the way to access the info

        # Fill the Content and HasContent data:
        self.content = Content(contents)
        self.has     = HasContent({ k: bool(v) for k,v in contents.items() })

        self.storage_id    = manager.editor_name
        self.has_check_btn = manager.has_check_btn
        self.abs_link      = f"{ self.full_page_url }#{ self.storage_id }"
        self.load_py_name  = manager.built_py_name
        if self.args.ID is not None:
            self.load_py_name = f'{ self.load_py_name[:-3] }-{ self.args.ID }.py'


    def show_if_needed(self):
        """
        Show the data in the terminal if needed (see SHOW argument), after the actual call to
        the macro has been done (so that the MacroData has been updated).
        """
        show = getattr(self.args, 'SHOW', MacroShowConfig.none)
        if show != MacroShowConfig.none:
            yall = show == MacroShowConfig.all
            lines = [
                f"\n-----------\nShow {'{{'} { self.macro }(...) {'}}'} call in file '{ self.src_uri }':"
            ]
            if yall or show == MacroShowConfig.args:
                lines += self.args.show_as_list()

            has_content = hasattr(self, 'content')
            if has_content:
                lines += self.content.show_as_list(show)

            print('\n    '.join(lines))




# vvvvvvvvvvvvvvvvv
# GENERATED CLASSES


class Content(ObjectWithDataGetters):
    """ Content of each section (or absolute Path on the disk for REMs files). """

    env: str = DataGetter(default="")
    env_term: str = DataGetter(default="")
    code: str = DataGetter(default="")
    corr: str = DataGetter(default="")
    tests: str = DataGetter(default="")
    secrets: str = DataGetter(default="")
    post_term: str = DataGetter(default="")
    post: str = DataGetter(default="")
    REM: str = DataGetter(default="")
    VIS_REM: str = DataGetter(default="")
    REM_PATH: Optional[Path] = DataGetter(none_as_default=True)
    VIS_REM_PATH: Optional[Path] = DataGetter(none_as_default=True)
    check_btn: bool = DataGetter(default=False)

    def show_as_list(self, show:ScriptDataWithRemPaths):
        # GENERATED
        with_rems   = show in (MacroShowConfig.contents, MacroShowConfig.all)
        with_python = with_rems or show==MacroShowConfig.python
        targets = (
            ScriptData.gen_showing() if with_rems else
            ScriptSection.gen_showing() if with_python else
            ()
        )
        header = '# --- '
        tail   = header[::-1]
        return [
            f"\n{ '#' * (2*len(header) + len(section_msg)) }"
          + f"\n{ header }{ section_msg }{ tail }"
          + f"\n\n{ self._data_dct[section] }\n\n"
                for section, section_msg in targets if self._data_dct[section]
        ]




class HasContent(ObjectWithDataGetters):
    """ Flags to know what sections/elements are defined or not. """

    env: bool = DataGetter(default=False, wraps=bool)
    env_term: bool = DataGetter(default=False, wraps=bool)
    code: bool = DataGetter(default=False, wraps=bool)
    corr: bool = DataGetter(default=False, wraps=bool)
    tests: bool = DataGetter(default=False, wraps=bool)
    secrets: bool = DataGetter(default=False, wraps=bool)
    post_term: bool = DataGetter(default=False, wraps=bool)
    post: bool = DataGetter(default=False, wraps=bool)
    REM: bool = DataGetter(default=False, wraps=bool)
    VIS_REM: bool = DataGetter(default=False, wraps=bool)
    check_btn: bool = DataGetter(default=False)



HAS_CONTENT_PROPS = [p for p in dir(HasContent) if not p.startswith('_')]









class MacroArgsDataIDE(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataIDE macro. """

    py_name: Tuple[str] = DataGetter()
    ID: int = DataGetter(none_as_default=True)
    SANS: str = DataGetter()
    WHITE: str = DataGetter()
    REC_LIMIT: int = DataGetter()
    SHOW: str = DataGetter()
    RUN_GROUP: str = DataGetter()
    AUTO_RUN: bool = DataGetter()
    MERMAID: bool = DataGetter()
    MAX: int = DataGetter()
    LOGS: bool = DataGetter()
    MODE: str = DataGetter()
    MIN_SIZE: int = DataGetter()
    MAX_SIZE: int = DataGetter()
    TERM_H: int = DataGetter()
    TEST: str = DataGetter()
    TWO_COLS: bool = DataGetter()
    STD_KEY: str = DataGetter()
    EXPORT: bool = DataGetter()

class MacroDataIDE(MacroData):
    """ Runtime data object for the IDE macro. """

    args: MacroArgsDataIDE
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataIDE





class MacroArgsDataTerminal(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataTerminal macro. """

    py_name: Tuple[str] = DataGetter()
    ID: int = DataGetter(none_as_default=True)
    SANS: str = DataGetter()
    WHITE: str = DataGetter()
    REC_LIMIT: int = DataGetter()
    SHOW: str = DataGetter()
    RUN_GROUP: str = DataGetter()
    AUTO_RUN: bool = DataGetter()
    MERMAID: bool = DataGetter()
    TERM_H: int = DataGetter()
    FILL: str = DataGetter()

class MacroDataTerminal(MacroData):
    """ Runtime data object for the terminal macro. """

    args: MacroArgsDataTerminal
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataTerminal





class MacroArgsDataPy_btn(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataPy_btn macro. """

    py_name: Tuple[str] = DataGetter()
    ID: int = DataGetter(none_as_default=True)
    SANS: str = DataGetter()
    WHITE: str = DataGetter()
    REC_LIMIT: int = DataGetter()
    SHOW: str = DataGetter()
    RUN_GROUP: str = DataGetter()
    AUTO_RUN: bool = DataGetter()
    MERMAID: bool = DataGetter()
    ICON: str = DataGetter()
    HEIGHT: int = DataGetter()
    WIDTH: int = DataGetter()
    SIZE: int = DataGetter()
    TIP: str = DataGetter()
    TIP_SHIFT: int = DataGetter()
    TIP_WIDTH: float = DataGetter()
    WRAPPER: str = DataGetter()

class MacroDataPy_btn(MacroData):
    """ Runtime data object for the py_btn macro. """

    args: MacroArgsDataPy_btn
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataPy_btn





class MacroArgsDataRun(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataRun macro. """

    py_name: Tuple[str] = DataGetter()
    ID: int = DataGetter(none_as_default=True)
    SANS: str = DataGetter()
    WHITE: str = DataGetter()
    REC_LIMIT: int = DataGetter()
    SHOW: str = DataGetter()
    RUN_GROUP: str = DataGetter()
    AUTO_RUN: bool = DataGetter()
    MERMAID: bool = DataGetter()

class MacroDataRun(MacroData):
    """ Runtime data object for the run macro. """

    args: MacroArgsDataRun
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataRun





class MacroArgsDataSection(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataSection macro. """

    py_name: str = DataGetter()
    section: str = DataGetter()

class MacroDataSection(MacroData):
    """ Runtime data object for the section macro. """

    args: MacroArgsDataSection
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataSection





class MacroArgsDataComposed_py(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataComposed_py macro. """

    py_name: Tuple[str] = DataGetter()
    sections: str = DataGetter()
    with_headers: bool = DataGetter()
    auto_title: bool = DataGetter()
    name_only: bool = DataGetter()
    title: str = DataGetter()

class MacroDataComposed_py(MacroData):
    """ Runtime data object for the composed_py macro. """

    args: MacroArgsDataComposed_py
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataComposed_py





class MacroArgsDataPy(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataPy macro. """

    py_name: str = DataGetter()
    auto_title: bool = DataGetter()
    name_only: bool = DataGetter()
    title: str = DataGetter()

class MacroDataPy(MacroData):
    """ Runtime data object for the py macro. """

    args: MacroArgsDataPy
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataPy





class MacroArgsDataMulti_qcm(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataMulti_qcm macro. """

    questions: Any = DataGetter()
    description: str = DataGetter()
    hide: bool = DataGetter()
    multi: bool = DataGetter()
    shuffle: bool = DataGetter()
    shuffle_questions: bool = DataGetter()
    shuffle_items: bool = DataGetter()
    admo_kind: str = DataGetter()
    admo_class: str = DataGetter()
    qcm_title: str = DataGetter()
    tag_list_of_qs: str = DataGetter()
    DEBUG: bool = DataGetter()
    SHOW: str = DataGetter()

class MacroDataMulti_qcm(MacroData):
    """ Runtime data object for the multi_qcm macro. """

    args: MacroArgsDataMulti_qcm
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataMulti_qcm





class MacroArgsDataFigure(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataFigure macro. """

    div_id: str = DataGetter()
    div_class: str = DataGetter()
    inner_text: str = DataGetter()
    admo_kind: str = DataGetter()
    admo_class: str = DataGetter()
    admo_title: str = DataGetter()
    p5_buttons: str = DataGetter()
    SHOW: str = DataGetter()

class MacroDataFigure(MacroData):
    """ Runtime data object for the figure macro. """

    args: MacroArgsDataFigure
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataFigure


# GENERATED CLASSES
# ^^^^^^^^^^^^^^^^^



class MacroArgsDataSqlide(ObjectWithDataGetters):
    """ Runtime arguments object for the MacroDataSqlide macro (from mkdocs-sqlite-console). """

    titre: str = DataGetter(default="Sql")
    sql: str = DataGetter(default="")
    espace: str = DataGetter(none_as_default=True)
    base: str = DataGetter(default="/")
    init: str = DataGetter(default="")
    hide: bool = DataGetter(default=False)
    autoexec: bool = DataGetter(default=False)

class MacroDataSqlide(MacroData) :
    """ Runtime data object for the sqlide macro (from mkdocs-sqlite-console). """

    args: MacroArgsDataFigure
    ARGS_CLASS: ClassVar[Type[ObjectWithDataGetters]] = MacroArgsDataSqlide






class IdeToTest(MacroDataIDE):

    _as_dict: dict

    @property
    def rel_dir_url(self):
        """
        Relative url to the directory containing the initial markdown file
        (typically used to redirect links/fetches during the tests).
        """
        dir_step_up = not self.ENV.use_directory_urls or not self.src_uri.endswith('index.md')
        rel_dir_url = str(Path(self.page_url).parent) if dir_step_up else self.page_url
        return rel_dir_url


    def __init__(self, macro_name, args_dict, ide:'Ide'):
        super().__init__(macro_name, args_dict)
        self.build_ide_manager_related_data(ide)

        # Rebuild an IDE name to show in the center panel of the tests (warning: do not use
        # `test.build_py_name` which covers a different purpose)
        tail     = "" if self.args.ID is None else f', ID={ self.args.ID }'
        ide_name = f"{ self.page_url.rstrip('/') }/{ self.args.py_name[0] }{ tail }"

        self._as_dict = dict(
            **ide.test_config.as_dict(),
            rel_dir_url = self.rel_dir_url,
            page_url    = self.full_page_url,
            ide_link    = self.abs_link,
            ide_name    = ide_name,
            editor_id   = self.storage_id,
        )

    @classmethod
    def from_ide(cls, ide:'Ide'):

        # Extract on the fly the very last MacroData added to the env (using a copy to make sure
        # no one messes up my data :p ):
        args_dct = ide.env.all_macros_data[-1].args._data_dct.copy()        # pylint: disable=protected-access
        test     = cls(ide.MACRO_NAME, args_dct, ide)
        return test


    def as_dict(self):
        return self._as_dict
