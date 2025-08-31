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
from typing import ClassVar, List, Optional, Tuple


from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.exceptions import BuildError

from pyodide_mkdocs_theme.pyodide_macros.parsing import add_indent


from ..exceptions import PmtConfigurationError, PmtIndentParserError
from ..indent_parser import IndentParser
from ..tools_and_constants import MACROS_WITH_INDENTS
from ..pyodide_logger import logger
from .maestro_base import BaseMaestro
from .config import PLUGIN_CONFIG_SRC



# pylint: disable-next=pointless-string-statement, line-too-long
'''
- Macros are run in "reading order" of the original document, included content also being used
  this way => fully predictable
- WARNING with md_include, which interleaves other calls in the "current context"... => needs
  an external md page parser
- Process:
    1. remove raw markers. NOTE: nested raw markups aren't allowed => easy
    2. tokenize (longest tokens first)
    3. _carefully parse the thing_, keeping in mind that the input is md text, not actual python...
       and store the indents of the calls to multiline macros in a reversed stack (store a pair
       indent/macro name, to enforce validity of executions on usage).
    4. Each time a macro starts running (spotted through the custom macro decorator), pop the
       current indent to use, AND STACK IT, because of potential nested macro calls: A(BCD)
       => when going back to A, there is no way to know if the macro will reach for the
       indentation value of A, for example, so the value must be accessible.
       Each time the macro returns, pop the current indent from the current stack.
    5. For nested macros, add the included indentation data on top of the current reversed stack.
'''







class MaestroIndent(BaseMaestro):
    """ Manage Indentation logistic """


    _parser: 'IndentParser'

    _indents_store: List[Tuple[str,int]]
    """
    List of all indentations for the "macro with indents" calls throughout the page, in
    reading order (=dfs).
    Data are stored in reversed fashion, because consumed using `list.pop()`.
    """

    _indents_stack: ClassVar[List[str]] = []
    """
    Stack the current indentation level to use, the last element being the current one.
    This allows the use of macros through multi layered inclusions (see `md_include`),
    getting back the correct indentations when "stepping out" of the included content.
    """

    _macros_calls_stack: ClassVar[List[str]] = []
    """ Same as before, but for the macro currently applied... """

    @property
    def _running_macro_name(self) -> Optional[str]:
        """
        Name of the macro currently running. None if no macro running.
        """
        return self._macros_calls_stack[-1] if self._macros_calls_stack else None



    def on_config(self, config:MkDocsConfig):
        logger.info("Configure the IndentParser for multiline macros with the user settings.")

        nope = [ w for w in self.macros_with_indents if not w.isidentifier() ]
        if nope:
            raise PmtConfigurationError(
                "Invalid macros_with_indents option: should be a list of identifiers, but found: "
                f"{ ', '.join(map(repr,nope)) }"
            )

        self._parser = IndentParser(
            self.j2_block_start_string,
            self.j2_block_end_string,
            self.j2_variable_start_string,
            self.j2_variable_end_string,
            self.j2_comment_start_string,
            self.j2_comment_end_string,
            self.is_macro_with_indent,
        )

        super().on_config(config)   # MacrosPlugin is actually "next in line" and has this method

        # After the super call, all macros have been registered, so MACROS_WITH_INDENTS isn't
        # empty anymore:
        macros = [*MACROS_WITH_INDENTS] + self.macros_with_indents
        self._macro_with_indent_pattern = re.compile('|'.join(macros))



    def on_page_markdown(
        self,
        markdown:str,
        page:Page,
        config:MkDocsConfig,
        site_navigation=None,
        **kwargs
    ):

        file_loc     = self.file_location(page)
        indentations = self._parser.parse(markdown, file_loc, tab_to_spaces=self.tab_to_spaces)

        self._indents_store = [*reversed(indentations)]
        self._indents_stack.clear()
        self._macros_calls_stack.clear()

        out = super().on_page_markdown(
            markdown, page, config, site_navigation=site_navigation, **kwargs
        )
        self._ensure_clean_outcome(file_loc)
        return out



    def _ensure_clean_outcome(self, file_loc):
        """
        Make sure all indentation data have been properly consumed.
        """
        if not self.on_error_fail:
            self._indents_store.clear()
            self._indents_stack.clear()
            self._macros_calls_stack.clear()
            return

        if self._indents_store:
            content = ''.join( f"\n    {name}: {n}" for name,n in reversed(self._indents_store) )
            raise PmtIndentParserError(
                "Registered macros calls with indents have not been entirely consumed for "
                f"{ file_loc }. The remaining store content is:{ content }"
            )

        if self._indents_stack:
            raise PmtIndentParserError(
                "Indentations stack inconsistency when rendering the markdown page for "
                f"{ file_loc }. The remaining stack content is:\n    {self._indents_stack!r}"
            )

        if self._macros_calls_stack:
            raise PmtIndentParserError(
                "Macros calls stack inconsistency when rendering the markdown page for "
                f"{ file_loc }. The remaining stack content is:\n    {self._macros_calls_stack!r}"
            )



    #----------------------------------------------------------------------------



    def apply_macro(self, name, func, *a, **kw):
        """
        Gathers automatically the name of the macro currently running (for better error
        messages). Also validate the call config for macros with indents
        """
        need_indent = self.is_macro_with_indent(name)

        self._macros_calls_stack.append(name)
        if need_indent:
            call,indent = self._indents_store.pop()
            if call != name:
                raise PmtIndentParserError(
                    f"Invalid indentation data: expected a call to `{call}`, but was `{name}`"
                )
            self._indents_stack.append(indent * ' ')

        out = super().apply_macro(name, func, *a, **kw)

        if need_indent:
            self._indents_stack.pop()
        self._macros_calls_stack.pop()
        return out



    def is_macro_with_indent(self, macro_call:str=None) -> bool:
        """
        Return True if the given macro call requires to register indentation data.
        This is using a white list, so that user defined macro cannot cause troubles.

        If no argument, check against the currently running macro
        """
        return bool(self._macro_with_indent_pattern.fullmatch(
            macro_call or self._running_macro_name
        ))


    def get_macro_indent(self):
        """
        Extract the indentation level for the current macro call.
        """
        if not self._indents_stack:
            macros_with_indents = PLUGIN_CONFIG_SRC.build.macros_with_indents.py_macros_path
            raise PmtIndentParserError(
                f"No indentation data available while building the page {self.file_location()}.\n"
                "This means a macro calling `env.indent_macro(text)` or `env.get_macro_indent()`"
                f" has not been registered in:\n    `mkdocs.yml:plugins.{ macros_with_indents }`."
            )
        return self._indents_stack[-1]


    def indent_macro(self, code:str):
        """
        Automatically indent appropriately the given macro output markdown, leaving empty
        lines untouched.
        """
        indent   = self.get_macro_indent()
        out_code = add_indent(code, indent)
        return out_code
