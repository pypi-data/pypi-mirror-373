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
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional, Tuple, Union



from ...exceptions import *
from ...tools_and_constants import ScriptData, ScriptDataWithRemPaths, ScriptSection, SiblingFile
from ...paths_utils import read_file
from .root_extractors import RootFilesExtractor



CWD = Path.cwd()
















@dataclass(eq=False)
class BaseIdeFilesExtractor(RootFilesExtractor):
    """
    ENTRY POINT: takes a py_name (IDE macro first argument) and extract from that all the
    necessary data from the different files.

    With `py_name` being denoted {X} and {F} being the stem of the current .md source file,
    the extracted files may be:

        1.  {X}.py
            {X}_REM.md
            {X}_VIS_REM.md
            Where the py file contains all the needed python code/sections, separated by the
            pyodide python tokens: `# --- PYODIDE:{kind} --- #`

        2.  {X}.py
            {X}_text.py
            {X}_corr.py
            {X}_REM.md
            {X}_VIS_REM.md

        3.  scripts/{F}/{X}.py
            scripts/{F}/{X}_REM.md
            scripts/{F}/{X}_VIS_REM.md
            Where the py file contains all the needed python code/sections, separated by the
            pyodide python tokens: `# --- PYODIDE:{kind} --- #`

        4.  scripts/{F}/{X}.py
            scripts/{F}/{X}_test.py
            scripts/{F}/{X}_corr.py
            scripts/{F}/{X}_REM.md
            scripts/{F}/{X}_VIS_REM.md

    The order gives the precedence. Way "1" is excluding the others (except for the REM file)
    """


    DATA_TO_PROPS: ClassVar[Dict[str,str]] = ScriptDataWithRemPaths.check_all_member_defined({
        ScriptSection.env:          "env_content",
        ScriptSection.env_term:     "env_term_content",
        ScriptSection.code:         "user_content",
        ScriptSection.corr:         "corr_content",
        ScriptSection.tests:        "public_tests",
        ScriptSection.secrets:      "secret_tests",
        ScriptSection.post_term:    "post_term_content",
        ScriptSection.post:         "post_content",

        ScriptData.REM:             'rem_content',
        ScriptData.VIS_REM:         'vis_rem_content',

        ScriptDataWithRemPaths.REM_PATH:     'rem_rel_path',
        ScriptDataWithRemPaths.VIS_REM_PATH: 'vis_rem_rel_path',
    })


    file_max_attempts: str = ""
    """ [deprecated] """

    test_rel_path: Optional[Path] = None
    """
    Relative path to the ..._test.py file. Always generated if a python file exists.
    Use self.has_xxx to know if the file/content actually exists
    """

    corr_rel_path: Optional[Path] = None
    """
    Relative path to the ..._corr.py file. Always generated if a python file exists.
    Use self.has_xxx to know if the file/content actually exists
    """

    rem_rel_path: Optional[Path] = None
    """
    Relative path to the ...REM.md file. Always generated if a python file exists.
    Use self.has_xxx to know if the file/content actually exists
    """

    vis_rem_rel_path: Optional[Path] = None
    """
    Relative path to the ..._VIS_REM.md file. Always generated if a python file exists.
    Use self.has_xxx to know if the file/content actually exists
    """

    # vvvvvvvvv
    # GENERATED
    @property
    def env_content(self): return self.contents["env"] if "env" in self.contents else ""
    @env_content.setter
    def env_content(self, s:str): self.contents["env"] = s
    @property
    def env_term_content(self): return self.contents["env_term"] if "env_term" in self.contents else ""
    @env_term_content.setter
    def env_term_content(self, s:str): self.contents["env_term"] = s
    @property
    def code_content(self): return self.contents["code"] if "code" in self.contents else ""
    @code_content.setter
    def code_content(self, s:str): self.contents["code"] = s
    @property
    def corr_content(self): return self.contents["corr"] if "corr" in self.contents else ""
    @corr_content.setter
    def corr_content(self, s:str): self.contents["corr"] = s
    @property
    def tests_content(self): return self.contents["tests"] if "tests" in self.contents else ""
    @tests_content.setter
    def tests_content(self, s:str): self.contents["tests"] = s
    @property
    def secrets_content(self): return self.contents["secrets"] if "secrets" in self.contents else ""
    @secrets_content.setter
    def secrets_content(self, s:str): self.contents["secrets"] = s
    @property
    def post_term_content(self): return self.contents["post_term"] if "post_term" in self.contents else ""
    @post_term_content.setter
    def post_term_content(self, s:str): self.contents["post_term"] = s
    @property
    def post_content(self): return self.contents["post"] if "post" in self.contents else ""
    @post_content.setter
    def post_content(self, s:str): self.contents["post"] = s
    @property
    def rem_content(self): return self.contents["REM"] if "REM" in self.contents else ""
    @rem_content.setter
    def rem_content(self, s:str): self.contents["REM"] = s
    @property
    def vis_rem_content(self): return self.contents["VIS_REM"] if "VIS_REM" in self.contents else ""
    @vis_rem_content.setter
    def vis_rem_content(self, s:str): self.contents["VIS_REM"] = s
    @property
    def has_env(self): return "env" in self.contents
    @property
    def has_env_term(self): return "env_term" in self.contents
    @property
    def has_code(self): return "code" in self.contents
    @property
    def has_corr(self): return "corr" in self.contents
    @property
    def has_tests(self): return "tests" in self.contents
    @property
    def has_secrets(self): return "secrets" in self.contents
    @property
    def has_post_term(self): return "post_term" in self.contents
    @property
    def has_post(self): return "post" in self.contents
    @property
    def has_rem(self): return "REM" in self.contents
    @property
    def has_vis_rem(self): return "VIS_REM" in self.contents
    # GENERATED
    # ^^^^^^^^^

    # Properties aliases for backward compatibility:
    public_tests = tests_content
    secret_tests = secrets_content
    user_content = code_content


    @property
    def corr_rems_bit_mask(self):
        """
        Bit mask giving the configuration for correction and/or remark data:
            - mask & 1 -> presence of correction
            - mask & 2 -> presence of REM(s).

        Note: As property because the data are not available yet for `CompositeFilesDataExtractor`
        instances.
        """
        return self.has_corr + (self.has_rem or self.has_vis_rem) * 2


    def get_sections_data(self, with_corr=True, as_sections=False, with_rems=False):
        """
        Returns an generator of tuples (property_name, content) for all sections, or
        (section_name, content) if @as_sections is True.

        @with_corr=True:    Yield or not the corr related information.
        @as_sections=False: If true, yield the section names (as in the python files), instead
                            of the property name on the IdeFilesExtractor object.
        """
        return (
            (
                (section if as_sections else self.DATA_TO_PROPS[section]),
                getattr(self, self.DATA_TO_PROPS[section]),
            )
            for section in (ScriptData.VALUES if with_rems else ScriptSection.VALUES)
            if section!=ScriptSection.corr or with_corr
        )


    def get_all_data(self):
        """
        Iterator of items, `(section name, data_or_content)`, extracting the data or its
        representation for all kind of data for the current instance:
            - sections -> code contents
            - REMs -> absolute paths and contents
        """
        return (
            (section, val.resolve())
                if isinstance( val:=getattr(self,prop), Path) else
            (section, val)
            for section, prop in self.DATA_TO_PROPS.items()
        )


    def get_section(self, section:ScriptData) -> str:
        """
        Extract the given section, verifying its name validity.
        """
        if ScriptData.has_member(section) or section in self.contents:
            return "" if section not in self.contents else self.contents[section]
        else:
            self.raise_invalid_section(section)


    @classmethod
    def get_section_property_from_cls(cls, section:ScriptData):
        # Still needed because going though self.contents only would require a full code
        # base update on the JS side as well...
        return cls.DATA_TO_PROPS[section]


    def iter_on_files(self):
        return (
            self.exo_py,
            self.rem_rel_path,
            self.vis_rem_rel_path,
            self.corr_rel_path,
            self.test_rel_path,
        )
















@dataclass(eq=False)
class _IdeFilesExtractor(BaseIdeFilesExtractor):

    def __post_init__(self):
        super().__post_init__()

        if self.exo_py is not None:
            exo_py = Path(self.exo_py).resolve().relative_to(CWD)
            name   = exo_py.stem
            (
                self.test_rel_path,
                self.corr_rel_path,
                self.rem_rel_path,
                self.vis_rem_rel_path,
            )=(
                exo_py.with_name(f"{ name }{ ending }")
                for ending in SiblingFile.VALUES
            )


    def extract_files_content(self):
        script_content = read_file(self.exo_py) if self.exo_py  else ""

        # Remove any old content, to allow spotting double sources error, even on re-serve
        self.contents.pop("REM", None)
        self.contents.pop("VIS_REM", None)

        if self.SECTION_TOKEN.search(script_content):
            self.extract_multi_sections(script_content)
        else:
            self.extract_multi_files(script_content)
        self._validate_not_tabs_in_REMs()


    def _validate_not_tabs_in_REMs(self):
        for prop in ('rem_content', 'vis_rem_content'):
            rem: str = getattr(self, prop)
            if '\t' not in rem:
                continue
            elif self.env.tab_to_spaces > -1:
                rem = rem.replace('\t', ' '*self.env.tab_to_spaces)
                setattr(self, prop, rem)
            else:
                raise PmtTabulationError(
                    "Found a tabulation character in a rem or vis_rem content. They should be "
                    f"replaced with spaces.{ self.env.log() }"
                )



    def get_content_if_exists(self, tail:str=None, using:Optional[Path]=None):
        """
        Return the content of the given file, or empty string if the file doesn't exist.

        If @using is an actual Path, use this path instead of searching the appropriated
        file on the disk.

        @throws: PmtMacrosInvalidPyFileError if a file is found but it's empty.
        """
        content = ''
        path: Union[Path,None] = using or self.env.get_sibling_of_current_page(self.py_name, tail=tail)

        if path and path.is_file():
            path = path.relative_to(CWD)

            # Also checks that the file exists and contains something:
            if not path.is_file():
                path = None
            else:
                content = read_file(path).strip()
                if not content:
                    raise PmtMacrosInvalidPyFileError(f"{path} is an empty file and should be removed.")
        return content



    #--------------------------------------------------------------------------
    #                      MONOLITHIC WAY (= theme way)
    #--------------------------------------------------------------------------


    def check_pmt_potential_sections(
        self,
        script_content: str,
        headers: List[Tuple[str,str]],
        headers_and_matches: List[Tuple[str,str]],
    ):
        header_pattern = ScriptData.get_sections_pattern(self.env)
        potential_sections = [ (m[0],m[1]) for m in header_pattern.finditer(script_content)]
        if(len(potential_sections) != len(headers)):
            wrong = [
                "\n\t" + token for token,header in potential_sections
                               if header not in headers
            ]+[
                "\n\t" + section for section,header in headers_and_matches
                                 if not header_pattern.search(section)
            ]
            valid_names =  "\n\t".join(ScriptData.gen_values(keep=True))
            raise PmtMacrosInvalidPyFileError(
                f"Potential mistake in { self.exo_py }.\n\nThe following string(s) could match PMT "
                 "tokens, but weren't identified as such. Please check there are no formatting "
                 f"mistakes:{ ''.join(wrong) }\n\nA valid section token should match this pattern: "
                 f"{ self.SECTION_TOKEN.pattern !r}\n\nAllowed section names are:\n\t{ valid_names }"
            )

    def extract_multi_sections(self, script_content:str):
        """
        Extract all the python content from one unique file with different sections:
            - env: header content (optional)
            - user: starting code for the user (optional)
            - corr: ... (optional - must be defined before the tests...?)
            - tests: public tests (optional)
            - secrets: secrets tests (optional)
        Note that the REM content has to stay in a markdown file, so that it can contain macros
        and mkdocs will still interpret those (if it were containing only markdown, it could be
        inserted on the fly by a macro, but an "inner macro call" would be ignored).
        """
        super().extract_multi_sections(script_content)

        # Extract REMs checking that only one source of data is used:
        rems_siblings: List[Tuple[str,str]] = [
            (ScriptData.REM,     SiblingFile.rem),
            (ScriptData.VIS_REM, SiblingFile.vis_rem),
        ]
        for section,sibling in rems_siblings:
            existent = section in self.contents
            content  = self.get_content_if_exists(sibling)
            if existent and content:
                prop_path = section.lower() + '_rel_path'
                raise PmtMultiRemSourcesError(
                    f"Found both sources for { section } content:\n"
                    f"   - File: { getattr(self, prop_path) }\n"
                    f"   - `#--PYODIDE:{ section }--#` section in { self.exo_py }."
                )
            elif content:
                self.contents[section] = self.strip_section(content)



    #--------------------------------------------------------------------------
    #                            OLD FASHION WAY
    #--------------------------------------------------------------------------


    def extract_multi_files(self, script_content:str):
        """
        "Old fashion way" extractions, with:
            - user code + public tests (+ possibly HDR) in the base script file (optional)
            - secret tests in "{script}_test.py" (optional)
            - Correction in "{script}_corr.py" (optional, but secret tests have to exist)
            - Remarks in "{script}_REM.md" (optional, but secret tests have to exist)
        """
        exo_py = self.exo_py and Path(self.exo_py).resolve().relative_to(CWD)

        self.env.outdated_PM_files.append(
            (exo_py, self.env.file_location())
        )

        if script_content.startswith('#MAX'):
            self.env.warn_unmaintained(
                partial_msg = "Setting IDE MAX value through the file is deprecated. Move this "
                             f"to the IDE macro argument.\nFile: { exo_py }"
            )
            script = script_content
            first_line, script = script.split("\n", 1) if "\n" in script else (script,'')
            script_content = script.strip()
            self.file_max_attempts = first_line.split("=")[1].strip()

        (
            self.env_content,
            self.user_content,
            self.public_tests,
        ) = self.env.get_hdr_and_public_contents_from(script_content, apply_strip=False)
        (
            self.secret_tests,
            self.corr_content,
            self.rem_content,
            self.vis_rem_content,
        ) = map(self.get_content_if_exists, SiblingFile.VALUES)

        # Apply common sections stripping/formatting:
        (
            self.env_content,
            self.user_content,
            self.public_tests,
            self.secret_tests,
            self.corr_content,
        ) = map(self.strip_section, (
            self.env_content,
            self.user_content,
            self.public_tests,
            self.secret_tests,
            self.corr_content,
        ))

        self.secret_tests = "" if not self.secret_tests else read_file(self.test_rel_path)


    def validate_section(self, target:str, src_file:Path, src_section:str):
        is_pmt = ScriptData.has_member(target)
        is_extra = not is_pmt and target in self.env.extra_pyodide_sections
        if not is_pmt and not is_extra:
            self.raise_invalid_section(target, src_file, src_section)
