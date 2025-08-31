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

from mkdocs.exceptions import ConfigurationError, BuildError

# REMINDER: PluginError doesn't show the stack trace, so even if it extends BuilderError,
# this is BAD!!!



class PmtConfigurationError(ConfigurationError):
    """ Something went wrong in the Pyodide theme itself """


class PmtError(BuildError):
    """
    Some top level mkdocs pages related hooks are not decorated with the
    MaestroMeta.meta_config_swap decorator.
    """


#------------------------------------------------------------------------
# Build related errors


class PmtMacrosPyLibsError(PmtError):
    """ Problem related to handling the python custom libraries. """

class PmtMacrosContractError(PmtError):
    """ Any contract that is broken. """

class PmtMacrosDeprecationError(PmtError):
    """ Stuff that shouldn't be used anymore... """

class PmtEncryptionError(PmtError):
    """ REMs+corr of PAGES_DATA encryption failures. """



#------------------------------------------------------------------------


class PmtInternalError(PmtError):
    """
    Error related to internal verifications, defensive programming and such.
    """



#------------------------------------------------------------------------


class PyodideMkdocsError(PmtError):
    """
    Error related to the ancestor project logistic
    """



#------------------------------------------------------------------------
# Markdown & parsing related errors

class PmtMarkdownError(PmtError): pass




class PmtMetadataError(PmtMarkdownError):
    """
    Some top level mkdocs pages related hooks are not decorated with the
    MaestroMeta.meta_config_swap decorator.
    """



class PmtIndentParserError(PmtMarkdownError):
    """
    The stack of indentations has not been consumed entirely after the page markdown
    has been created.
    """

class PmtInvalidSyntaxError(PmtIndentParserError):
    """
    Invalid syntax found while parsing a markdown file, when gathering
    information about macros calls indentations in the page.
    """

class PmtIndentedMacroError(PmtIndentParserError):
    """
    A macro with indent has been called while text is found on its left.
    """

class PmtTabulationError(PmtIndentParserError):
    """
    A tab character has been found in the indentation before a multiline macro call,
    or in a REM content.
    """



class PmtCustomMessagesError(PmtError):
    """ An error encountered while handling custom messages. """



class PmtIdesTestingError(PmtError):
    """ An error related to the test_ides pages """



#------------------------------------------------------------------------
# Marcos calls/arguments related errors



class PmtMacrosError(PmtError): pass


class PmtDuplicateMacroError(PmtMacrosError):
    """
    Different macros functions have been registered with the same name, or the same macro has
    been registered a second time.
    """

class PmtMacrosNonUniqueIdError(PmtMacrosError):
    """
    A non unique id has been generated (for an IDE, terminal, ...)
    """

class PmtMermaidConfigError(PmtMacrosError):
    """
    Attempt at using MERMAID=True while the md extension isn't configured in mkdocs.yml
    """

class PmtCodeFenceTitleQuotesError(PmtMacrosError):
    """
    Found "quotes" in the string used to build code fences titles.
    """


class PmtMacrosInvalidArgumentError(PmtMacrosError):
    """
    Any kind of error related to invalid macros arguments values.
    """


class PmtMultiRemSourcesError(PmtMacrosError):
    """
    REMs contents set both with a md file and through a PYODIDE:section.
    """


class PmtMacrosInvalidPyFileError(PmtMacrosError):
    """
    File missing or with invalid content.
    """

class PmtMacrosComposerError(PmtMacrosError):
    """
    Invalid composition instruction.
    """

class PmtMacrosInvalidSectionError(PmtMacrosInvalidPyFileError):
    """
    Invalid PYODIDE section name.
    """

class PmtPythonPyInclusionError(PmtMacrosInvalidPyFileError):
    """
    Error found while resolving python files inclusions instructions
    (`## {{ py_name:section }}`)
    """

class PmtCircularPyInclusionError(PmtPythonPyInclusionError):
    """
    A cyclic dependency has been found while resolving python files inclusions
    instructions (`## {{ py_name:section }}`)
    """






#---------------------------------------------------------------------------------
# Aliases for backward compatibility

PyodideMacrosError = PmtError
PyodideConfigurationError = PmtConfigurationError
PyodideMacrosPyLibsError = PmtMacrosPyLibsError
PyodideMacrosContractError = PmtMacrosContractError
PyodideMacrosDeprecationError = PmtMacrosDeprecationError
PyodideMacrosParsingError = PmtInvalidSyntaxError
PyodideMacrosIndentError = PmtIndentParserError
PyodideMacrosTabulationError = PmtTabulationError
PyodideMacrosMetaError = PmtMetadataError
