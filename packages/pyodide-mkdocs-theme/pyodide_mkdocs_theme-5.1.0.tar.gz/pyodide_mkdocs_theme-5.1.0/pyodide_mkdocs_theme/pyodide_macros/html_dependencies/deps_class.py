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
from typing import ClassVar, Dict, List, Optional, Set, Union, TYPE_CHECKING


from ..tools_and_constants import AutoDescriptor

if TYPE_CHECKING:
    from ..plugin.pyodide_macros_plugin import PyodideMacrosPlugin







class Block:
    """
    StrEnum-like object, giving all the jinja blocks usable in the main.html file.
    """
    libs    = AutoDescriptor()
    content = AutoDescriptor()
    scripts = AutoDescriptor()

    @classmethod
    def get_blocks(cls):
        return (cls.libs, cls.content, cls.scripts)





class DepKind:
    """
    StrEnum-like object, identifying the key components to build the "dependencies graph"
    of scripts and css injections in main.html.
    """
    always      = AutoDescriptor()

    pyodide     = AutoDescriptor()
    py_btn      = AutoDescriptor()
    run_macro   = AutoDescriptor()
    term        = AutoDescriptor()
    runners     = AutoDescriptor()
    ide         = AutoDescriptor()
    ides_test   = AutoDescriptor()
    playground  = AutoDescriptor()
    qcm         = AutoDescriptor()
    qcm_encrypt = AutoDescriptor()
    mermaid     = AutoDescriptor()


    @classmethod
    def resolve_deps_needs(cls, kind:'DepKind', needs:Set['DepKind']):
        """
        Gather the whole "chain" of dependencies according to the dependencies graph,
        sorting from the given @kind, which is already present in @needs.
        Keep adding kinds as long as they are not present in @needs.
        """
        # NOTE: this is almost useless, for PMT 4^ because of automatic resolution of imported
        # modules, BUT there are still some needs for non modules, so keep everything as is...

        # Keep in mind DepKind _values_ are actually SIMPLE STRINGS!
        if kind in _DEP_KINDS_GRAPH:
            next_kind = _DEP_KINDS_GRAPH[kind]
            if next_kind not in needs:
                needs.add(next_kind)
                cls.resolve_deps_needs(next_kind, needs)



# Ignoring the systematic DepKind.always final dependency.
_DEP_KINDS_GRAPH = {
    DepKind.playground: DepKind.ide,
    DepKind.ides_test:  DepKind.ide,
    DepKind.ide:        DepKind.term,
    DepKind.term:       DepKind.pyodide,
    DepKind.run_macro:  DepKind.py_btn,
    DepKind.py_btn:     DepKind.pyodide,
    DepKind.pyodide:    DepKind.runners,
}







class Dep:
    """
    An html dependency, knowing, what to insert, where and if it's needed in the page depending
    on the macros calls done in it.
    """

    name: str
    """ Dep identifier (must be unique. """

    data: Dict[str,str]
    """ Key-value pairs of information to put in the final html tag. """

    block: str
    """ Identify the jinja block using this dependency (see main.html). """

    kind: DepKind
    """ Kind of dependency (used to build the "kinda dependencies graph"). """

    extra_dump: Optional[str]
    """
    If defined, this is the name of a PyodideMacrosPlugin method to call after the html tag for
    the current dependency has been built: the string returned by this method will be concatenated
    after the tag declaration.
    """

    pool_requirement: Optional[str]
    """
    If defined, this is the (or "one of") name of the CONFIG.CLASSES_POOL property that will
    be assigned in this JS file. This is used to build the overlordClasses array from python,
    depending on the DepKinds of the file.
    """


    ATTR: ClassVar[str]
    """ Key to use if the data argument is a simple string (shortcut declaration). """

    DUMP_TEMPLATE: ClassVar[str]
    """ Template string to build the html tag for the considered child class. """

    EXTENSION: ClassVar[str] = None
    """ File extension (as Path.suffix) for the given Dep instance/subclass. """

    #-------------------------------------------------------------------------

    EXTENSION_TO_CLASS: ClassVar[Dict[str,'Dep']] = {}
    """ Static property: associates a Dep subclass to it's file extension. """

    DEPS_DECLARATION_ORDER: ClassVar[List['Dep']] = []
    """ Static property: keep track of the HtmlDependencies properties declaration order. """

    DEPS_DECLARATION_VALIDATION: ClassVar[Set[str]] = set()
    """ Static property: Store HtmlDependencies property names, to make sure they are unique. """



    def __init_subclass__(cls):
        Dep.EXTENSION_TO_CLASS[cls.EXTENSION] = cls


    @staticmethod
    def auto_ordering():
        Dep.DEPS_DECLARATION_VALIDATION = set()
        Dep.DEPS_DECLARATION_ORDER = []
        return Dep.DEPS_DECLARATION_ORDER


    def __init__(
        self,
        block:      Block,
        kind:       DepKind,
        data:       Union[dict,str],
        extra_dump: str = None,
        pool:       str = None,
        **kwargs:   dict
    ):
        self.DEPS_DECLARATION_ORDER.append(self)

        self.block = block
        self.kind  = kind
        self.extra_dump = extra_dump
        self.pool_requirement = pool

        if isinstance(data, str):
            data = {self.ATTR: data}
        data.update({
            'crossorigin':"anonymous",
            'referrerpolicy':"no-referrer",
            'charset':"utf-8"
        })
        data.update(kwargs)
        self.data = data


    def __set_name__(self, _, prop:str):
        self.name = prop
        if prop in self.DEPS_DECLARATION_VALIDATION:
            raise ValueError(f'{prop!r} Dep instance already exists!')
        self.DEPS_DECLARATION_VALIDATION.add(prop)


    def __get__(self, _obj, _kls):
        return self


    def to_template(self, extras:List[str]):
        template = self.get_html_tag()
        if self.extra_dump is not None:
            extras.append(self.extra_dump)
            template += "\n{" + self.extra_dump + "}"
        return template


    def get_html_tag(self):
        return self.DUMP_TEMPLATE.format(
            data=' '.join(f'{k}="{v}"' for k,v in self.data.items())
        )

    def gen_import_map(self):
        return ()





class Css(Dep):
    EXTENSION     = '.css'
    ATTR          = 'href'
    DUMP_TEMPLATE = '<link {data} rel="stylesheet"/>\n'



class Cdn(Dep):
    EXTENSION     = '.js'
    ATTR          = 'src'
    DUMP_TEMPLATE = '<script {data}></script>\n'

    def __init__(self, *a,**kw):
        super().__init__(*a, **kw)

        if 'type' not in self.data:
            self.data['type'] = 'text/javascript'
            # https://stackoverflow.com/questions/876561/when-serving-javascript-files-is-it-better-to-use-the-application-javascript-or

        if self.data.get('type')=='module':
            base_path = self.data[self.ATTR]
            self.import_name = Path(base_path).stem


    def gen_import_map(self):
        if self.data.get('type')=='module':
            yield self.import_name, self.data[self.ATTR]
