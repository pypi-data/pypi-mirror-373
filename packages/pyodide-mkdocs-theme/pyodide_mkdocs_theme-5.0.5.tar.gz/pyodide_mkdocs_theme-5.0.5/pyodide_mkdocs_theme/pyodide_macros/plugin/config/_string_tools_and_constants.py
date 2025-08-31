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

from operator import or_
from functools import reduce
import json
import re
from textwrap import dedent
from argparse import Namespace
from typing import Any, Callable, Dict, Iterable, List, Tuple, TYPE_CHECKING


from pyodide_mkdocs_theme.pyodide_macros.tools_and_constants import AutoDescriptor
from pyodide_mkdocs_theme.pyodide_macros.indent_parser import IndentParser
    # not relative, to be able to run the file alone (see tests at the bottom)



if TYPE_CHECKING:
    from pyodide_mkdocs_theme.pyodide_macros.plugin.config.config_option_src import ConfigOptionSrc



PARSER_VALIDATOR = IndentParser()



PMT_PM_PREFIX_SIZE = 15  # Length of "pyodide_macros."



def gen_pow2():
    p = 1
    while True:
        yield p
        p *= 2
POWS = gen_pow2()
def pow2():
    return next(POWS)


class InclusionProfile:
    """ All possible inclusions constants """

    config = pow2()
    """ In the plugins Config object (at runtime) """

    yaml_schema = pow2()
    """ In the yaml validation schema """

    yaml_docs_tree = pow2()
    """ In the yaml tree showing the entire options in the configuration page """

    docs_signature = pow2()
    """ In the generated function/macro signature """

    docs_args_table = pow2()
    """ in the generated tables ("only" or with all rows) """

    docs_config_page = pow2()
    """ In the detailed config page of the docs """

    everywhere = pow2() - 1

    all_but_config = everywhere - config
    all_but_yaml_stuff = everywhere - yaml_schema - yaml_docs_tree


    @classmethod
    def combine(cls, *args: 'InclusionProfile'):
        return sum(args)

    @classmethod
    def not_in(cls, *args: 'InclusionProfile'):
        return cls.everywhere ^ reduce(or_, args, 0)

    @classmethod
    def deactivate(cls, src:'ConfigOptionSrc', *args: 'InclusionProfile'):
        flag = cls.not_in(*args)
        src.inclusion_profile &= flag






class DeprecationStatus:
    """ All possible deprecation types """

    moved       = AutoDescriptor()
    removed     = AutoDescriptor()
    unsupported = AutoDescriptor()


class DeprecationTemplate(Namespace):
    """ Messages template for all DeprecationStatus """

    moved = "The option {src} is deprecated. It's equivalent is now: {moved_to}."

    removed = "The option {src} is deprecated: it will be removed in near future."

    unsupported = (
        "Macros using {src} may not work anymore and will be removed in the future. Please contact "
        "the author of the theme if you need this macro/tool."
    )



PARAGRAPHS_SEP  = r"\n\n\s*"
""" One empty line """

BULLET_OR_TABLE = r"\n\s*(?:[|*+-]|\d[.] )"
""" New line then bullet point (`*` or `-`), tables definition lines.
    NOTE: doesn't match for a docstring STARTING with bullet points (but this doesn't need
    to be handled, so it's ok)
"""

MD_IN_HTML = r"\n\s*\{(?![%{])"
""" Spot § md attributes (must not be "inlined") """


INLINE_MD_SPLITTER: re.Pattern = re.compile( '(```|' + '|'.join(
    [PARAGRAPHS_SEP, BULLET_OR_TABLE, MD_IN_HTML]
) + ')')
"""
Pattern extracting blocks of markdown content from dedented strings, keeping their
individual indentation. Beginning of blocks considered:
    * Paragraphs: \\n\\n\\s*
    * Bullet points: \\n\\s*+*-   or \\n\\s*+*-
    * Table rows: \\n\\s*|
    * paragraphs attributes but not macros or jinja: \\n\\s*{(?![%{])
    * Starting or ending code blocks: ```. When those are found, the content in between
      stays unchanged after the initial dedent operation.
"""


def inline_md(msg:str, in_cell:bool=False, validate=False) -> str:
    """
    Most/some docs strings will be used inside cells of tables, so the md cannot be "multiline"
    in the source content. But because it's boring AF to write those and still have something
    readable in the declaring code, the following logic is always applied:

    1. Consider the declaration is done with python multiline strings in the python code.
    2. `dedent` the content.
    3. Strip the message from leading and trailing new lines.
    4. Inline every "paragraph" by removing all "\\n\\s*" except when they are preceded by
        another "\\n" (which means it's the beginning of a new §, potentially with indentation).

    If @in_cell is True, replaces automatically any remaining new line character with `"<br>"`,
    to avoid breaking markdown tables.

    If @validate is True, the resulting markdown, is parsed by an IndentParser object, to get
    some level of insurance that there are no quotes syntaxes troubles or so (otherwise, mistakes
    are almost impossible to spot in the config...).
    """
    clean = dedent(msg).strip('\r\n')
    chunks_with_seps_on_odds = INLINE_MD_SPLITTER.split(clean)

    inlines = []
    in_code_block = False
    for i,chunk in enumerate(chunks_with_seps_on_odds):
        is_separator = i&1
        if not in_code_block and not is_separator:
            chunk = re.sub(r'\n\s*', ' ', chunk)
        inlines.append(chunk)
        if chunk == "```":
            in_code_block = not in_code_block

    out = ''.join(inlines).lstrip()
        # Never add leading/trailing new lines here: inlined single § should _ACTUALLY_
        # be on one single line.

    if in_cell:
        out = out.replace("\n","<br>")

    # Validate the jinja syntax for the config's docs, otherwise it's a damn hell to spot
    # were the error are...
    if validate:
        PARSER_VALIDATOR.parse(out)


    return out













def __unicode_converter() -> Callable[[str], str] :
    replacements = {
        "\\u00e9": "é",
    }
    pattern = re.compile('|'.join(replacements).replace('\\','\\\\'))   #... x/

    def replacer(s:str):
        # print(s)          # To spot missing conversions (german!!)
        return re.sub(pattern, lambda m: replacements[m[0]], s)
    return replacer

unicode_to_nicer = __unicode_converter()




def to_nice_yml_value_for_docs(value:Any):
    """
    Convert a value to a "json nicer representation" for docs.
    """
    json_value  = json.dumps( value )
    nicer_value = unicode_to_nicer(json_value)
    return nicer_value




def get_python_type_as_code(typ:Any):
    """
    Transform self.py_type in it's string code declaration, taking various type declarations
    in consideration:

    - basics:   int, str, ...
    - typing:   Set[str], ...
    - 3.9+:     set[str], ...
    """
    is_from_typing = hasattr(typ,'_name')
    is_simple_type = not is_from_typing and (typ is str or not issubclass(typ, Iterable))
                     # issubclass raises with typing types...

    if is_simple_type:
        py_type = typ.__name__
    elif is_from_typing:
        py_type = str(typ).replace('typing.','')
    else:
        py_type = str(typ)

    return py_type
