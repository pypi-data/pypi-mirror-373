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
# pylint: disable=multiple-statements, missing-function-docstring


import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from pyodide_mkdocs_theme.pyodide_macros.macros.ide_files_data.root_extractors import RootFilesExtractor



from ...exceptions import PmtMacrosInvalidPyFileError, PmtPythonPyInclusionError
from ...tools_and_constants import ScriptData
from ...parsing import add_indent
from ...indent_parser import IndentParser
from ...plugin.config import PLUGIN_CONFIG_SRC

if TYPE_CHECKING:
    from .generic_extractors import FileExtractorWithInclusions


InclusionNode = Tuple['FileExtractorWithInclusions', ScriptData]
""" (obj, section) """

CWD = Path.cwd()











@dataclass
class ExtractorGatherer(Set[InclusionNode]):

    _cache: Dict[Optional[Path], 'FileExtractorWithInclusions'] = field(default_factory=dict)
    """
    Resolutions of the inclusions REQUIRE kind of a cache, so that one avoid infinite loops when
    a file includes a part of himself.

    Thing is: this is different from the generic cache, because the latter could be deactivated
    by the user, and then the cache of the ExplorerTrace becomes mandatory.
    """

    def store(self, file:'FileExtractorWithInclusions'):
        key = file.get_key_cache(file.exo_py)
        self._cache[key] = file

    def get_cached(self, exo_py: Optional[Path]):
        key  = RootFilesExtractor.get_key_cache(exo_py)
        file = self._cache.get(key)
        return file













class InclusionParser(IndentParser):

    _CACHE: ClassVar[Dict[str,List]] = {}

    LOOKING_FOR: ClassVar[str] = "python inclusions informations"

    targets: List[ScriptData]
    replacements: List[Tuple[str,str]]


    def gathered_data_as_str(self):
        replacements = ''.join(
            f"\n               {src!r} -> {repl!r}" for src,repl in self.replacements
        ) or "\n               ()"
        return f"""\
Content parsed:     {self.content!r}
Targeted sections:
               { ', '.join(self.targets) or () }
Replacements:{ replacements }"""


    def start_parsing(self):
        self.targets = []
        self.replacements = []

        while self.is_(':'):
            self.eat_section()

        if '*' in self.targets and len(self.targets) > 1:
            self.fatal("Cannot sue '*' in combination with other section names.")

        while self.is_('[|]'):
            self.eat_replacement()

        if self.tokens_left():
            got_repl = bool(self.replacements)
            self.eat('[|]'if got_repl else '[:|]')

        return self.targets, self.replacements


    def eat_section(self):
        self.eat()
        is_all  = self.is_('[*]')
        section = self.eat() if is_all else self.eat_id()
        self.targets.append(section)

    def eat_replacement(self):
        self.eat()
        src = self.eat_repl_segment()
        self.eat_arrow()
        repl = self.eat_repl_segment()
        self.replacements.append((src,repl))

    def eat_arrow(self):
        i = self.i
        arrow = ''.join( self.tokens[i:i+2] )
        if arrow != "->":
            show = repr(arrow) if arrow else 'EOF'
            self.fatal(
                f"Expected an arrow `->` to specify the replacement to use, but found { show }"
            )
        self.eat()
        self.eat()

    def eat_repl_segment(self):
        if self.is_string():
            return self.eat_string()
        else:
            return self.eat_id()


    def eat_id(self):
        return self.eat(r'\w+')

    def eat_string(self):
        i = self.i
        self.err_stack_opening()
        self._eat_until_paired()
        self.err_stack_closing()
        j = self.i
        str_repr = ''.join(self.tokens[i:j])
        return eval(str_repr)



INCLUSION_PARSER = InclusionParser()

















@dataclass
class InclusionConfig:

    parent: 'FileExtractorWithInclusions'
    parent_section: ScriptData

    child: 'FileExtractorWithInclusions'

    targets_as_str: str

    inclusion_string: str

    indent: str

    targets: List[ScriptData] = None
    replacements: Dict[str,str] = None


    INCLUSION_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"(?P<indent>[ \t]*)##\s*\{\{\s*(?P<src>\[\w+\])?(?P<rel_path>[^:\s]*)(?P<targets>[^\}]+?)\s*\}\}"
    )


    @classmethod
    def build_inclusions(
        cls,
        file: 'FileExtractorWithInclusions',
        section: ScriptData,
        content: str,
        to_resolve: ExtractorGatherer,
    ):
        for m in cls.INCLUSION_PATTERN.finditer(content):
            i = m.start(0)
            if i and content[i-1] != '\n':
                raise PmtPythonPyInclusionError(
                    "Inclusion instructions should always be at the beginning of a line.\n"
                    f"    Found this misplaced instruction: { m[0] }\n"
                    f"    File: { file.exo_py }\n"
                )

            src, rel_path, targets, indent = m['src'], m['rel_path'], m['targets'], m['indent']

            child = file
            if rel_path or src:
                exo_py = cls._get_child_exo_py(file, src, rel_path)
                child  = to_resolve.get_cached(exo_py)
                if not child:
                    _,child = file.get_file_extractor_and_exo_py_for(
                        file.env, rel_path, exo_py=exo_py, to_resolve=to_resolve,
                        extract = False,
                    )
                    to_resolve.store(child)
                    child.extract_contents(to_resolve)
                if child is not file:
                    child.register_parent(file)

            inclusion = cls(file, section, child, targets, m[0], indent)
            file.add_inclusion(section, inclusion)
            to_resolve.add( (file, section) )           # Add only if a match exists (hence the set to avoid duplicates)


    @classmethod
    def _get_child_exo_py(cls, file:'FileExtractorWithInclusions', src:str, rel_path:str):

        if src=='[md]':
            source = Path(file.env.page.file.abs_src_path)
        elif src=='[py]':
            source, py_name = cls._rebuild_src_py_and_py_name_rel_path(file)
            if not rel_path:
                rel_path = py_name
        elif src=='[cwd]':
            name = Path(file.env.page.file.abs_src_path).name
            source = CWD / name
        else:
            source = file.exo_py

        if not rel_path:
            raise PmtMacrosInvalidPyFileError(
                "Inclusions using `[md]` or `[cwd]` require to specify a relative path information (aka, `py_name`)"
            )

        exo_py = file.env._get_sibling(source, rel_path, tail='.py')

        if not exo_py:
            raise PmtMacrosInvalidPyFileError(
                f"No file matching {(src or '')+rel_path!r} could be found, starting from "
                f"the { source.parent.relative_to(CWD) } directory."
            )
        return exo_py

    @classmethod
    def _rebuild_src_py_and_py_name_rel_path(cls, file:'FileExtractorWithInclusions'):
        """ Rebuild the path matching the original python file. """
        md      = Path(file.env.page.file.abs_src_path)
        py_name = file.env.current_macro_data.args.py_name[0]
        source = file.env._get_sibling(md, py_name, tail='.py')
        return source, py_name


    def __post_init__(self):
        self.targets, self.replacements = INCLUSION_PARSER.parse(
            self.targets_as_str.strip(), self.parent.exo_py
        )

        if self.targets != ['*']:
            for target in self.targets:
                self.child.validate_section(target, self.parent.docs_py, self.parent_section)

        if self.replacements and self.parent.env.activate_cache:
            yaml_path = PLUGIN_CONFIG_SRC.build.activate_cache.py_macros_path
            pmt_meta  = self.parent.env._pmt_meta_filename
            raise PmtPythonPyInclusionError(
                "Sections inclusions with string replacements are not compatible with the use "
                f"of the cache.\nYou need to deactivate the `{yaml_path}` option either from a "
                f"`{ pmt_meta }` file, or from the markdown page header."
            )


    def get_children_sections(self):
        if self.targets != ['*']:
            return self.targets
        return [section for section in ScriptData.VALUES if section in self.child.contents]


    def apply(self):
        content = self.parent.get_section(self.parent_section)
        targets = self.get_children_sections()
        to_use  = "\n\n".join(
            self.child.get_section(child_section) for child_section in targets
        )
        for src,repl in self.replacements:
            to_use = to_use.replace(src,repl)
        indented = add_indent(to_use, self.indent, leading=True)
        content  = content.replace(self.inclusion_string, indented)
        self.parent.update_content(self.parent_section, content)
