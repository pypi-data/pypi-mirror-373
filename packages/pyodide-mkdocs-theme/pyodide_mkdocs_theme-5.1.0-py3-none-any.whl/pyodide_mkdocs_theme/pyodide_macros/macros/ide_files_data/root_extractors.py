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
from collections import Counter
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Optional, Set, Tuple, Union, TYPE_CHECKING





from ...exceptions import (
    PmtInternalError,
    PmtMacrosInvalidPyFileError,
    PmtMacrosInvalidSectionError,
)
from ...tools_and_constants import ScriptData
from ...parsing import add_indent, items_comma_joiner


if TYPE_CHECKING:
    from ... import PyodideMacrosPlugin
    from ...plugin.maestro_macros import MaestroMacros
    from ._inclusions import ExtractorGatherer
    from .generic_extractors import CachedIdeFilesExtractor



CWD = Path.cwd()






@dataclass
class RootFilesExtractor:

    env: 'MaestroMacros'
    py_name: str

    key_cache: str = None

    exo_py: Optional[Path] = None
    """
    Path to the master python file (if any).

    WARNING: This path is absolute AND normalized, while an IDE actually needs the absolute
             UNnormalized path when generating its html id (for backward compatibility, when
             checking their uniqueness).
    """

    docs_py: Optional[Path] = None
    """
    Same as self.exo_py, but relative to the CWD (logging purpose).
    """

    #-----------------------------

    contents: Dict[str, str] = field(default_factory=dict)
    """
    Dict[section_name, section_content]
    """

    SECTION_TOKEN: ClassVar[re.Pattern] = re.compile(
        r'^(#[\t ]*-+[\t ]*PYODIDE[\t ]*:[\t ]*\w+[\t ]*-+[\t ]*#[\t ]*)$', flags=re.MULTILINE
    )
    """ Used to split the python files content. """


    def __post_init__(self):
        if self.exo_py:
            self.docs_py = Path(self.exo_py).relative_to(CWD)

        if not self.exo_py and self.py_name:
            raise PmtMacrosInvalidPyFileError(
                f"No python file could be found for py_name='{ self.py_name }'."
                f"{ self.env.log() }"
            )


    def extract_contents(self, to_resolve: 'ExtractorGatherer'=None, **_) -> bool :
        if self.exo_py:
            self.extract_files_content()
        # Must be done way down the MRO hierarchy, before the interpreter starts bubbling up
        # the callstack.
        self.mark_refreshed()


    def __hash__(self):
        return hash(self.key_cache)


    @staticmethod
    def extract_section_name(header:str):
        return header.strip(' #-').split(':')[-1].strip()


    def strip_section(self, content:str):
        """
        Strip linefeed from a section to remove empty lines, but not the indentation.

        NOTE: starting from PMT 5.0, DO NOT just "...".strip(), in case someone starts to concatenate
        partial codes already containing indented code.
        """
        return content.strip('\n')


    def get_section(self, section:str) -> str:
        """
        Extract the given section, verifying its name validity (the section has to exist).
        """
        self.validate_section(section)
        return self.contents[section]


    def validate_section(self, section:str, src_file:Path=None, src_section:str=None):
        if section not in self.contents:
            self.raise_invalid_section(section, src_file, src_section)


    def raise_invalid_section(
        self,
        section: str,
        src_file: Optional[Path]=None,
        src_section: Optional[str]=None
    ):
        header      = "Unknown" if src_file is None else "Invalid inclusion"
        src_file    = src_file or self.docs_py
        src_section = src_section and ':'+src_section
        raise PmtMacrosInvalidSectionError(
            f'{ header } section name {section!r} in { src_file }{ src_section }'
        )


    def check_pmt_potential_sections(
        self,
        script_content: str,
        headers: List[Tuple[str,str]],
        headers_and_matches: List[Tuple[str,str]],
    ):
        """ Check that some misformed PMT headers are not present i the file. """
        # All valid by default!


    def extract_multi_sections(self, script_content:str):
        """
        Extract all the python content from one unique file with different sections.
        """

        # WARNING: at this point chunks MUST NOT be stripped yet, because headers and contents need
        # two different logics (PMT 5.0+ -> to allow concatenation of already indented codes):
        chunks  = self.SECTION_TOKEN.split(script_content)
        chunks  = [*filter(lambda s:bool(s.strip()), chunks)]   # remove sections with only spaces
        pairs   = [*zip(*[iter(chunks)]*2)]
        tic_toc = [ bool(self.SECTION_TOKEN.match(header.strip())) for header,_ in pairs ]
                    # Why strip the header, tho...??? ( because of the condition bellow: `not tic_toc[0]` )

        # File structure validations:
        headers_and_matches = [
            ( chunk, self.extract_section_name(chunk) )
                for chunk in map(str.strip,chunks) if self.SECTION_TOKEN.match((chunk))
        ]
        headers = [ section for _,section in headers_and_matches]
        odds_sections = len(chunks) & 1
        wrong_tic_toc = len(headers) != sum(tic_toc)

        self.check_pmt_potential_sections(script_content, headers, headers_and_matches)

        if tic_toc and not tic_toc[0]:
            raise PmtMacrosInvalidPyFileError(
                f"Invalid file structure for { self.exo_py }: no section header at the beginning of the file."
            )

        if odds_sections or wrong_tic_toc:
            raise PmtMacrosInvalidPyFileError(
                f"Invalid file structure for { self.exo_py }: no empty sections allowed."
            )

        without_ignores_headers = [ h for h in headers if h != ScriptData.ignore ]
        headers_counter = Counter(without_ignores_headers)
        dups = sorted(name for name,n in headers_counter.items() if n>1)
        if dups:
            dups = items_comma_joiner(dups)
            raise PmtMacrosInvalidPyFileError(
                f"Invalid file structure for { self.exo_py }: Duplicate sections are not "
                f"allowed (except for the `ignore` section). Found several { dups }."
            )


        # Codes registrations:
        for section,content in pairs:
            section_name = self.extract_section_name(section)
            if section_name == ScriptData.ignore:
                continue
            self.contents[section_name] = self.strip_section(content)


    @classmethod
    def get_key_cache(cls, exo_py:Optional[Path]):
        return exo_py and Path(exo_py).resolve()  # `Path(...).resolve()` because mutation! :rolleyes:


    def _setup_to_extract_again(self):
        self.contents.clear()

    #------------------------------------------------------------------------------

    def extract_files_content(self):
        """
        Extraction of a concrete/existing single file.
        """
        raise NotImplementedError()

    def mark_refreshed(self):
        raise NotImplementedError()


    def register_parent(self, parent: 'CachedIdeFilesExtractor'):
        raise NotImplementedError()


    @classmethod
    def get_file_extractor_and_exo_py_for(
        cls,
        env: 'PyodideMacrosPlugin',
        py_name: Union[str,Tuple[str]],
        exo_py: Optional[Path]=...,
        *,
        extract: bool = True,
        to_resolve: 'ExtractorGatherer' = None,
    ) -> Tuple[ Optional[Path], 'CachedIdeFilesExtractor'] :
        raise NotImplementedError()


    def iter_on_files(self):
        raise NotImplementedError()
