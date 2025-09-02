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


import re
from collections import defaultdict
from typing import Callable, ClassVar, Dict, List, Set, Tuple

from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple, TYPE_CHECKING



from ...exceptions import PmtMacrosComposerError, PmtMacrosInvalidPyFileError
from ...tools_and_constants import ScriptData, ScriptSection
from ...pyodide_logger import logger
from ...plugin.config.definitions.macros_configs import ACTIVATE_COMPOSITION_INFOS
from ._inclusions import ExtractorGatherer
from .generic_extractors import CachedIdeFilesExtractor
from .common_extractors import IdeFilesExtractor, SourceFilesExtractor
from .runners_extractors import BaseIdeFilesExtractor


if TYPE_CHECKING:
    from pyodide_mkdocs_theme.pyodide_macros import PyodideMacrosPlugin


CWD = Path.cwd()










@dataclass(eq=False)
class BaseCompositeFilesDataExtractor(BaseIdeFilesExtractor):
    """
    Master chief, to compose IDEs/runners contents from various "main side files",
    with various combination options:

        xxx:code:env:post       -> use env, code and post from xxx
        yyy:+code               -> add yyy.code to xxx.code content
        bbb:+REM                -> add bbb.REM to the current REM
        zzz:!code               -> replace all the sections with the available content in zzz, except for code
        aaa                     -> use the sections existing in aaa
        ccc:+                   -> add any section of ccc to existing ones

    - Combinations are done in order (line per line).
    - The order of the sections/instructions within a line doesn't matter.
    - No sections/instructions means "use any content related to that file(s) that is not empty".

    About the syntaxes:

        py_name:env::code       -> "::" not allowed
        py_name:env:!code       -> mix inclusion+exclusion not allowed
        py_name:+env:!code      -> mix inclusion+exclusion not allowed
        :[!+]?xxx               -> sections without file: not allowed
        '', 'py_name:xxx",..    -> not allowed (aka: impossible to combine non existant py files)

        py_name:+env            -> means "concat only the env section from py_name (if exist)"
        py_name:+env:code       -> means "concat env, replace code (if they exist)"
        py_name:!a:!b           -> means "replace with all existing sections in py_name, except a & b"
        py_name:+:!a:!b         -> means "concat with all existing sections in py_name, except a & b"

    When contents are concatenated, `\n\n` is added in between them.
    """

    src_uri: Optional[str] = None
    """
    Uri of the md file containing the runner related to the current object, relative to the CWD
    """


    composers: List['Composer'] = None
    """
    Instructions saying how to combine the different python files.
    """


    def __post_init__(self):
        src = self.env.page.file.abs_src_path
        self.src_uri = src and Path(src).relative_to(CWD).as_posix()
        for c in self.composers:
            c.prepare(self)



    def extract_contents(self, to_resolve: ExtractorGatherer=None):

        # Override the one that will be passed as argument (always, actually), so that the
        # Composite instance is not showing up inside its `_cache`:
        to_resolve = ExtractorGatherer()

        for c in self.composers:                # Pass 1
            to_resolve.store(c.file_data)
            c.file_data.extract_contents(to_resolve)

        self.resolve_inclusions(to_resolve)     # Pass 2

        for c in self.composers:                # Pass 3
            c.combine(self)

        super().extract_contents(to_resolve)     # will trigger mark_refreshed


    def extract_files_content(self):
        pass        # nothing to do here...


    def resolve_inclusions(self, to_resolve:ExtractorGatherer):
        """
        Resolve all python inclusions, in any order, but raising if ever a cyclic dependency
        is found.
        """
        # Error messages could be enhanced by making sure all the nodes are explored in
        # topological order, so that the feedback message always starts with an ancestor/root
        # node. But that's the only bonus of the topological sort.

        while to_resolve:
            extractor, section = to_resolve.pop()
            extractor.resolve_inclusions(section, [], set(), to_resolve)



    def get_sections(self, sections:Tuple[ScriptSection], with_headers:bool):
        """
        Compose the needed content, possibly adding headers in-between the sections.
        Empty sections are always ignored.
        (related to the macro `composed_py`)
        """
        ScriptData.check_all_members_valid(sections)

        def push_if_needed(section, content=None):
            if content or section in sections and (content := self.get_section(section)):
                contents.append( template.format(section, content) )

        template = with_headers * "# --- PYODIDE:{0} --- #\n" + "{1}"
        contents = []

        for section in ScriptSection.VALUES:
            push_if_needed(section)

        with_rems = self.has_rem or self.has_vis_rem
        if with_rems:
            push_if_needed('ignore', '"""')
            for section in (ScriptData.REM, ScriptData.VIS_REM):
                push_if_needed(section)
            push_if_needed('ignore', '"""')

        return "\n\n".join(contents)












@dataclass(eq=False)
class CompositeFilesDataExtractor(CachedIdeFilesExtractor, BaseCompositeFilesDataExtractor):

    # OVERRIDE
    _CACHED_EXTRACTORS: ClassVar[Dict[Path, '(IdeFilesExtractor)']] = {}


    @classmethod
    def _get_key_cache_and_instance_builder(
        cls,
        env: 'PyodideMacrosPlugin',
        py_names: Tuple[str],
        exo_py: Optional[Path]=...,
    ):
        key, composers = cls._get_key_cache_and_instructions(env, py_names)
        exo_py  = composers[0].exo_py if composers else None
        builder = lambda: cls(env, py_name=key, exo_py=exo_py, composers=composers, key_cache=key)
        return key, exo_py, builder


    @classmethod
    def _get_key_cache_and_instructions(cls, env:'PyodideMacrosPlugin', py_names:Tuple[str]):
        """
        Parse the content of the py_names strings and extract the desired configuration from it.
        """
        if not py_names:
            py_names = ('')

        if py_names[0] == env.py_snippets_stem:
            raise PmtMacrosInvalidPyFileError(
                f"{ env.py_snippets_stem }.py files can only be used for snippets inclusion inside "
                f"other python files. They cannot be used as {ACTIVATE_COMPOSITION_INFOS*'first '}"
                f"argument for the theme's macros.\n{ env.file_location(all_in=True) }"
            )

        composers: List[Composer] = []
        for segment in py_names:

            py_name, *composite = re.sub(r'\s+', '', segment).split(':')
            exo_py = env.get_sibling_of_current_page(py_name, tail='.py')

            # Existing files are required except if none used at all:
            if not exo_py and (composers or len(py_names) > 1):
                loc_info = env.file_location(all_in=True)
                raise PmtMacrosInvalidPyFileError(
                    f"Invalid py_name argument: file { py_name } does not exist.\n{ loc_info }"
                )

            composers.append(Composer(py_name, composite, exo_py))

        key = ' '.join( c.key_element for c in composers ) or "None:"
        return key, composers


    def show_refresh(self):
        file = self.env.page.file.src_uri
        macro = self.env.current_macro_data.macro
        py_name = self.env.current_macro_data.args.py_name[0]
        logger.info(
            f'\033[32;1mBuilding data\033[0m for macro call in { file }:{ macro }({py_name!r})'
        )














@dataclass
class Composer:

    py_name: str
    instructions: List[List[str]]
    exo_py: Optional[Path]

    #------------------------------

    key_element: str = None
    file_data: IdeFilesExtractor = None
    actions: List[Tuple[Callable, List[str]]] = None

    #------------------------------

    SECTIONS: ClassVar[Tuple[ScriptData]] = ScriptData.VALUES

    PROPS: ClassVar[Dict[ScriptData,str]] = {
        section: IdeFilesExtractor.DATA_TO_PROPS[section] for section in SECTIONS
    }

    MATCHER: ClassVar[re.Pattern] = re.compile(
        f"(?P<mode>[+!]?)(?P<src>{ '|'.join(SECTIONS) })?(?:>(?P<to>{ '|'.join(SECTIONS) }))?"
    )

    #------------------------------


    def __post_init__(self):
        self.instructions.sort()
        self.key_element = f'{ self.exo_py }:{ ":".join(self.instructions) }'


    def prepare(self, master:CompositeFilesDataExtractor):
        _, self.file_data = SourceFilesExtractor.get_file_extractor_and_exo_py_for(
            master.env, self.py_name, exo_py=self.exo_py, extract=False,
        )

        self.file_data.register_parent(master)
        all_sections =  {(s,s) for s in self.SECTIONS}

        actions = []
        if not self.instructions:
            actions = [(self.replace, all_sections)]

        else:
            bad = []
            dct = defaultdict(set)
            for s in self.instructions:
                m = self.MATCHER.fullmatch(s)
                if not m or not m['mode'] and not m['src']:
                    bad.append(s)
                elif m['mode']=='!' and m['to']:
                    bad.append(s+' (cannot use destination)')
                elif not m['src'] and m['to']:
                    bad.append(s+' (unknown source)')
                else:
                    dct[m['mode'] or ''].add( (m['src'], m['to'] or m['src']) )

            concat, repl, nope = dct['+'], dct[''], dct['!']

            msg = ""
            if bad:
                lines = '\n    '.join(map(repr,s))
                msg = f"Invalid instructions for python file combinations:\n    { lines }"

            elif '' in concat and len(concat) > 1:
                msg = "Invalid instructions for python file combinations: cannot contain \"+\" and \"+SECTION\""

            elif nope and (repl or concat and concat != {''}):
                msg = (
                    "Invalid instructions for python file combinations: cannot contain \"!\" with "
                    "either \"SECTION\" or \"+SECTION\""
                )

            if msg:
                raise PmtMacrosComposerError(
                    f"{ msg } for { self.py_name }.\n{ master.env.file_location(all_in=True) }"
                )

            BARE_PLUS = {(None,None)}
            if concat == BARE_PLUS or nope:
                concat = all_sections
            if not repl and not concat:
                repl = all_sections

            concat -= nope
            repl -= nope

            if concat: actions.append( (self.concat,  concat) )
            if repl:   actions.append( (self.replace, repl)   )

        self.actions = [
            (method, [ (self.PROPS[src], self.PROPS[to]) for src,to in sections])
            for method,sections in actions
        ]


    def concat(self, master:CompositeFilesDataExtractor, section_props:Set[str]):
        for src, to in section_props:
            content = getattr(self.file_data, src)
            if not content: continue

            current = getattr(master, to)
            concat  = f'{ current }\n\n{ content }' if current else content
            setattr(master, to, concat)


    def replace(self, master:CompositeFilesDataExtractor, section_props:Set[str]):
        for src, to in section_props:
            content = getattr(self.file_data, src)
            if content:
                setattr(master, to, content)


    def combine(self, master:CompositeFilesDataExtractor):
        for todo, section_prop in self.actions:
            todo(master, section_prop)
