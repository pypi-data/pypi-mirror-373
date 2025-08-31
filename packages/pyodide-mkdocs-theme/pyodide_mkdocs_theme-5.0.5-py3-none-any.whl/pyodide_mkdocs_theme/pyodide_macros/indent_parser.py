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

from functools import wraps
import re
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple

from pyodide_mkdocs_theme.pyodide_macros.exceptions import (
    PmtInvalidSyntaxError,
    PmtIndentedMacroError,
    PmtTabulationError,
)
from pyodide_mkdocs_theme.pyodide_macros.pyodide_logger import logger




#----------------------------------------------------------------------------
# Debugging logistic

indent_lvl = 0
target_debug = "42=42" and None     # Comment out the 'and None" to activate debugging logs


def log(method):
    if not target_debug:
        return method

    @wraps(method)
    def wrapper(self:'IndentParser', *a,**kw):
        global indent_lvl

        indent_lvl += 1
        i, tok  = self.i, repr(self.taste())
        current = f"{' ': >{indent_lvl}}{ method.__name__ }, on {tok = }   "
        show(self, f"{ current } i={ i }")

        out = method(self, *a,**kw)

        show(self, f"{ current } (from:{ i } -> to:{ self.i })")
        indent_lvl -= 1

        return out
    return wrapper

def log_reset(method):
    if not target_debug:
        return method

    @wraps(method)
    def wrapper(self:'IndentParser', content, *a,**kw):
        global indent_lvl
        indent_lvl = 0
        if target_debug in content:     # show(...) not usable yet
            print("Parsing:\n", content, "\n")
        out = method(self, content, *a,**kw)
        return out
    return wrapper

def show(parser:'IndentParser', *msg):
    if target_debug in parser.content:
        print(*msg)


#----------------------------------------------------------------------------





NUMBER = r"\d+[.]\d+(?:[Ee][+-]?\d+)?|\d+(?:[Ee][+-]?\d+)?"

def is_factory(pattern):
    """ Method factory "is_...". """
    return lambda self: bool( (tok := self.taste()) and re.fullmatch(pattern, tok))


def to_pattern(s):
    """
    Convert a string to a regex pattern, converting back some escaped characters to something
    more appropriate in the current context.
    """
    return re.escape(s).replace('\\ ',r'\s*').replace('\\#','#')




class JinjaCodeParser:
    """
    Parse Jinja blocks or vars. Simplified grammar is like this:

        maths ::= expr [ math_op maths ]*

        expr ::= number | string | data_struct | id_stuff

        data_struct ::= paired  [ extras ]

        numbers ::=   are like     11  1.1  -1  +1  +1.1e+5  +1.1E+5

        string ::= '"' !'"'* '"' [ string ]* [ extras ]
                    | "'" !"'"* "'" [ string ]* [ extras ]

        paired ::= '(' [comma_sep] ')'  |  '{' [comma_sep] '}'  |  '[' [comma_sep] ']'

        comma_sep ::= [ item [ ',' item ]* ','? ]

        item ::= maths  |  maths ':' maths

        identifier ::= (?=\D)\w+              (broadly :p )

        extras ::= [ call | attr | '[' comma_sep ']' ]*

        id_stuff ::= identifier [ extras ]

        attr ::= '.' id_stuff

        call ::= '(' comma_sep_args ')' [ extras ]

        args ::= maths | identifier '=' maths

        comma_sep_args ::= [ args [ ',' args ]* ','? ]

        math_op ::=   + - * / // ** %     (no bitwise)


    ------------------------------------------------
    NOTES:

    * No comments INSIDE other jinja block.

    * No nested jinja blocks either... BUT var blocks inside strings themselves inside a var
    block work... :rolleyes:
            e.g:    {{ "This works... {{ 42 }}!" }}     ->    "This works... 42!"

    * Numbers with leading or trailing dot are not allowed in Jinja.

    * Multiline strings do not actually exist in jinja: those are concatenations of strings:
            e.g:    '''kljhkjh'''      <=>     ''  'kljhkjh'  ''

    * varargs syntax are forbidden in jinja, so no need to support them.

    ------------------------------------------------

    Implementation wise, the methods of the parser handling one piece of logic are responsible
    for eating the related tokens. Especially, for parsing involving specific head+tail tokens,
    the token has been tasted, but never eaten when entering the function/method.
    """

    _CACHE: ClassVar[Dict[str,List]] = {}

    i: int
    """ Current index in the list of tokens. """

    size: int
    """ Number of tokens """

    content:str
    """ debugging purpose"""

    tokens: List[str]
    """ Tokens extracted from the markdown content. """

    matching_pairs: Dict[str,str]
    """ Dict of associated opening -> closing tokens string, ESCAPED for pattern matching. """

    tokenizer: re.Pattern
    """ 'It's in da name... """

    is_macro_with_indent: Callable[[str],bool] = None
    """
    Predicate to identify macro names whose the indentation on the left of the jinja call
    has to be checked and stored.
    """

    err_info_stack: List[Any] = None
    """
    Stack of information on the currently opened 'paired" elements. Allow for better feedback.
    """


    def __init__(self,
        open_block:    str = None,
        close_block:   str = None,
        open_var:      str = None,
        close_var:     str = None,
        open_comment:  str = None,
        close_comment: str = None,
        is_macro_with_indent: Callable[[str],bool] = None,
        *args, **kwargs,
    ):
        assert not args and not kwargs, f"Extra arguments found:\n   {args=}\n   {kwargs=}"

        # Defined later in self.parse(...):
        self.i = 0
        self.tokens = []
        self.indents = []
        self.matching_pairs = {}
        self.err_info_stack = []

        # Build the delimiters according to the user's config of the MacrosPlugin:
        self.open_block    = open_block    or '{%'
        self.close_block   = close_block   or '%}'
        self.open_var      = open_var      or '{{'
        self.close_var     = close_var     or '}}'
        self.open_comment  = open_comment  or '{#'
        self.close_comment = close_comment or '#}'

        self.open_raw      = rf'{ self.open_block } raw { self.close_block }'
        self.close_raw     = rf'{ self.open_block } endraw { self.close_block }'
            # Spaces will be replaced later with `\s*`

        self.is_macro_with_indent = is_macro_with_indent or (lambda *_: False)

        tokens = []
        open_close_pairs = [
            (self.open_block,    self.close_block),
            (self.open_var,      self.close_var),
            (self.open_comment,  self.close_comment),
            (self.open_raw,      self.close_raw),
            "''", '""',
            '()', '[]', '{}',
        ]
        for o,c in open_close_pairs:
            c = to_pattern(c)
            self.matching_pairs[o] = c
            tokens.extend( (to_pattern(o),c) )

        # Add escaped versions of the quotes (added separately because they are not "matching pairs"!):
        tokens.extend((r"\\'", r'\\"'))

        all_tokens = sorted(set(
            tokens + [
                NUMBER, r'\w+', r'\n', r'[\t ]+', r'\\', r"\*\*", "//", '.',    # '\\"', "\\'",  # These are actually wrong as patterns...
            ]
        ), key=lambda s:(-len(s), s))

        self.tokenizer = re.compile('|'.join(all_tokens), flags=re.DOTALL)



    #-------------------------------------------------------------
    #                    Behaviors injection
    #-------------------------------------------------------------

    def error_info(self, info:str, tok:str):
        raise NotImplementedError()

    def _store_macro_with_indent(self, start:int, name:str):
        raise NotImplementedError()

    def _location_info(self, tok, i:Optional[int]=None):
        raise NotImplementedError()

    def gathered_data_as_str(self):
        raise NotImplementedError()

    def start_parsing(self):
        raise NotImplementedError()


    #-------------------------------------------------------------
    #                     Parsing machinery
    #-------------------------------------------------------------


    def taste(self, di=0) -> Optional[str] :
        token = self.tokens[ self.i+di ] if 0 <= self.i+di < self.size else None
        return token

    def eat(self,regex:str=None) -> str :
        """
        Raises PmtParsingError if there are no tokens left or if @regex is given and the current
        token has to match the @regex.
        Otherwise, consume the current token, then walk through any whitespace tokens.
        """
        tok = self.taste()
        if tok is None or regex is not None and not re.fullmatch(regex, tok):
            tok = 'EOF' if tok is None else repr(tok)
            msg = 'Reached EOF' if not regex else f'Expected pattern was: {regex!r}, but found: {tok}'
            self.fatal(msg, tok)
        self.i += 1
        self.walk()
        return tok

    def walk(self):
        """ consume spaces """
        while (tok := self.taste()) and tok.isspace():
            self.i += 1

    def eat_and_get_matching_closing_token(self):
        tok = self.taste()
        if tok not in self.matching_pairs:
            self.fatal("Expected an opening token 'bracket, parentheses, quote, ...)")
        target = self.matching_pairs[self.eat()]
        return target

    def fatal(self, msg:str, tok:str=...):
        err_msg = self.error_info(msg, tok)
        raise PmtInvalidSyntaxError(err_msg)

    def taste_next(self):
        """ Find the next non space token, or None if... none. """
        i = self.i+1
        while i < self.size and self.tokens[i].isspace():
            i += 1
        return self.tokens[i] if i < self.size else None


    #------------------------------------------------------------------------------

    def err_stack_opening(self):
        """ Register opening pair data (to apply before eating the token) """
        self.err_info_stack.append(self.i)

    def err_stack_closing(self):
        """ remove opening pair data (to apply at the end of the function call) """
        self.err_info_stack.pop()

    #------------------------------------------------------------------------------


    def is_(self, pattern):
        tok = self.taste()
        return bool(tok and re.fullmatch(pattern, tok))

    def is_not(self, pattern):
        return not self.is_(pattern)

    is_math_op           = is_factory(r'\*\*|//|[/*+%-]')
    is_unary_sign        = is_factory(r'[+-]')
    is_number            = is_factory(NUMBER)
    is_string            = is_factory('["\']')
    is_id                = is_factory(r'(?=\D)\w+')
    is_opening           = is_factory(r'[\[{(]')
    is_open_curly        = is_factory(r'\{')
    is_open_bracket      = is_factory(r'\[')
    is_open_parenth      = is_factory(r'\(')
    is_getattr           = is_factory('[.]')
    is_closing_jinja_var = is_factory(r'\}\}')

    def tokens_left(self):
        return self.i < self.size

    #------------------------------------------------------------------------------


    def _eat_until_paired(self):
        """
        Consume the tokens unconditionally until the expected matching token has been reached.
        Useful for paired tokens that do not contain anything meaningful (comments, raw stuff,
        blocks (because we are searching for macro, not jinja blocks!), ...)
        """
        self.err_stack_opening()
        target = self.eat_and_get_matching_closing_token()
        while self.tokens_left() and self.is_not(target):
            tok = self.eat()            # tok declared for debugging purpose
        self.eat(target)                # Matching again is necessary in case end of tokens has been reached
        self.err_stack_closing()



    @log
    def maths(self):
        """
        Cardinality: ONE OR MORE(with maths ops in between)

        Parse elements and mathematical binary operations done with them.
        """
        while True:
            self.expr()
            if not self.is_math_op():
                break
            self.eat()


    @log
    def expr(self):
        """
        Cardinality: ONE

        A number, a string (possibly with "follow up"), a data structure,
        an identifier, e function call, ...

        Unary sign are just swallowed here without any special consideration. Should be enough for
        the task at stake...
        """
        while self.is_unary_sign():
            self.eat()

        if self.is_number():
            self.eat()

        elif self.is_id():
            self.id_stuff()

        elif self.is_string():
            self.string()

        elif self.is_opening():
            self.paired_delimited_and_commas()

        else:
            self.fatal(f"Unexpected token {self.taste()!r}")




    @log
    def string(self):
        """
        Cardinality: ONE OR MORE (strings, not chars... :p )

        Consume consecutive strings, allowing automatic continuations, then try any
        "follow up" after it.
        """
        self.err_stack_opening()
        while self.tokens_left() and self.is_string():
            self._eat_until_paired()
        self.follow_up()
        self.err_stack_closing()



    @log
    def paired_delimited_and_commas(self, allow_empty=True, allow_named_args=False):
        """
        Cardinality: ONE

        Represent one collection of things separated by commas, and surrounded with a pair
        of head+tail matching tokens.
        No constraints on the items here (done in comma_sep)
        """
        self.err_stack_opening()
        is_dict = self.is_open_curly()      # No sets allowed in jinja
        target  = self.eat_and_get_matching_closing_token()
        self.comma_sep(target, is_dict, allow_empty, allow_named_args)
        self.eat(target)        # est closing element
        self.follow_up()        # `dict(call)` should be seen as wrong, but ":rolleyes:"...
        self.err_stack_closing()


    @log
    def comma_sep(self, closing_target:str, is_dict:bool, allow_empty:bool, named_args:bool):
        """
        Cardinality: ZERO OR MORE (depends also on arguments)

        Collection of `maths` elements separated by commas.

        - Collection may be empty, unless @allow_empty is False.
        - May allow matching named arguments if @named_args is True.
        - If `is_dict` is True, validate items as `maths : maths`
        """
        some = False
        while not self.is_(closing_target):
            some = True
            self.item_or_value(is_dict, named_args)
            if self.is_(closing_target):
                break
            self.eat(',')

        if not some and not allow_empty:
            self.fatal("Empty brackets not allowed")


    @log
    def item_or_value(self, is_dict, named_args):
        """
        Cardinality: ONE

        search ont of those, depending on the arguments:
        - `maths`
        - `maths:maths`
        - `id=maths`
        """
        if named_args:
            was_id = self.is_id()
            was:str = self.taste()
            self.maths()
            if self.is_('='):
                if not was_id:
                    if not re.fullmatch(NUMBER, was): was = repr(was)
                    self.fatal(f"A named argument must be an identifier but was: { was }")
                self.eat()
                self.maths()
        else:
            self.maths()
            if is_dict:
                self.eat(':')
                self.maths()

    @log
    def follow_up(self):
        """
        Cardinality: ZERO OR MORE

        Represent various things that could be "chained" behind a value:
        - getitem:          `value[...]`    (one item at least)
        - getattr:          `value.id`
        - function call:    `value(...)`    (may be empty)
        """
        while self.is_(r'[(\[.]'):
            if self.is_open_bracket():
                self.paired_delimited_and_commas(allow_empty=False)

            elif self.is_open_parenth():
                self.paired_delimited_and_commas(allow_named_args=True)

            if self.is_getattr():
                self.eat()
                if not self.is_id():
                    self.fatal("Expected an identifier after an attribute access operator")
                self.id_stuff()

    @log
    def id_stuff(self):
        self.eat()
        self.follow_up()



    @log_reset
    def parse(self, content:str, src_file=None, *, tab_to_spaces=-1):
        """
        Parse the given content and gather any kind of desired data on the way (through override
        of various methods, especially `start_parsing`).

        - Returns a copy of the result.
        - Results are cached in between builds.
        """
        # pylint: disable=attribute-defined-outside-init, multiple-statements
        self.content = content
        self.src_file = src_file
        self.tab_to_spaces = tab_to_spaces

        if content not in self._CACHE:
            self.i = 0
            self.tokens = self.tokenizer.findall(content)
            self.size = len(self.tokens)
            self.err_info_stack.clear()
            self._CACHE[content] = self.start_parsing()

        return self._CACHE[content][:]













class BaseMarkdownIndentParser(JinjaCodeParser):


    jinja_gatherer: Dict[str,Callable[[],None]]
    """ Routines extracting top level jinja blocks/contents """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jinja_gatherer = {
            self.open_var:     self.gather_jinja_var,
            self.open_raw:     self._eat_until_paired,
            self.open_block:   self._eat_until_paired,
            self.open_comment: self._eat_until_paired,
        }


    def start_parsing(self):
        self.indents = []

        # Travel through the content ignoring simple md/html until something jinja related occurs
        while self.i < self.size:
            tok = self.taste()
            if tok in self.jinja_gatherer:
                self.jinja_gatherer[tok]()
            else:
                self.eat()
        return self.indents



    def gather_jinja_var(self):
        start = self.i        # index of the opening '{{' token, to compute indentation later
        closing_target = self.eat_and_get_matching_closing_token()

        if self.is_(closing_target):
            self.fatal("Invalid empty jinja variable expression")

        if self.is_id():
            i_name = self.i                 # index of identifier
            name   = self.taste()
            self.current = i_name, name     # Store "debugging purpose" data:

            is_macro = self.taste_next() == '('
            if is_macro:
                if self.is_macro_with_indent(name):
                    self._store_macro_with_indent(start, name)

        self.maths()
        self.eat(closing_target)














class IndentManager(BaseMarkdownIndentParser):

    indents: List[Tuple[str,str]]
    """ List of tuples, `(macro_name, indent_as_whitespaces)`. """

    tab_to_spaces: int = -1     # Overridden in self.parse(...)
    """
    Determine the behavior when a `\t` character is found in the indentations on the left
    of a macro call:
    * `tab_to_spaces == -1` -> raise an error
    * `tab_to_spaces > 0` -> replace the tabs with this number of whitespaces.
    """

    def _store_macro_with_indent(self, start_var:int, name:str):
        i = start_var-1
        while i>=0 and self.tokens[i].isspace() and self.tokens[i] != '\n':
            i -= 1

        if i>=0 and self.tokens[i] != '\n':
            raise PmtIndentedMacroError( self.error_info(
               f"Invalid macro call:\nThe {name!r} macro is a `macros_with_indents` but a "
                "call to it has been found with characters on its left. This is not possible.\n"
                "This happened",
                self.tokens[i]
            ))

        i += 1
        indent = ''.join(self.tokens[i:start_var])
        if '\t' in indent:
            if self.tab_to_spaces<0:
                raise PmtTabulationError(
                   f"In { self.src_file }:\n"
                    "A tabulation character has been found on the left of a multiline macro call."
                    "This is considered invalid.\nSolutions are:\n"
                    "    - Configure your IDE to automatically convert tabulations into spaces.\n"
                    "    - Replace them with spaces characters manually.\n"
                    "    - Or set the `build.tab_to_spaces: integer` option of the plugin (NOTE:"
                    " depending on how the macros calls have been written, this might not always"
                    " work).\n"
                    "      If done so, warnings will be shown in the console with the locations of"
                    " each of these updates, so that they can be checked and fixed."
                )
            else:
                indent = indent.replace('\t', ' '*self.tab_to_spaces)
                logger.warning(
                    f"Automatic conversion of tabs to spaces in { self.src_file }, for the macro "
                    f"call: { self.current[1] }"
                )
        n_indent = len(indent)
        self.indents.append( (name, n_indent) )



    def gathered_data_as_str(self):
        if self.indents:
            return "\nKnown indents so far: " + ''.join(
                f"\n\t{name}: {n}" for name,n in self.indents
            )+"\n"
        return "No indents collected so far." * bool(self.src_file)














class IndentParserFeedbackManager(BaseMarkdownIndentParser):

    src_file: str = None
    """ If given, the path to the file containing the markdown currently parsed. """

    current: str = None
    """ Name of the macro call currently parsed (if any) """

    LOOK_AROUND: ClassVar[int] = 18
    LOOKING_FOR: str = "macro calls indentation data"



    def error_info(self, info:str, tok:str=...):
        info = info.rstrip('.')                 # In case I forget and put a dot... :p
        macro = ''

        if tok is ...:
            tok = self.taste()

        if self.current:
            i,name = self.current
            macro = f"""
  Macro being parsed during the error (token index:{ i }/{ self.size }):  \033[31m>>{ name }<<\033[0m
"""
        gathered_data = self.gathered_data_as_str()

        if self.src_file:
            # Line numbers might be off because the md content is stripped and the headers got removed.
            line_number = 1 + ''.join(self.tokens[:self.i]).count('\n')
            error_location = f"{ self.src_file }, line { line_number }"
        else:
            error_location = '<unknown file>'

        source = ""
        if self.err_info_stack:
            i_src = self.err_info_stack[-1]
            source = f"""
  Currently parsed structure/element (token index: { i_src }/{ self.size }):
      { self._location_info(None, i_src) }
"""

        return f"""\
Parsing error while looking for { self.LOOKING_FOR }.\n
\033[34m  ERROR: { info } (in: { error_location })\033[0m\n
With the \033[31m>>tokens<<\033[0m of interest highlighted in red:{ macro }
{ source }
  Tokens where the error has been found (token index: { self.i }/{ self.size }):
      { self._location_info(tok) }
{ gathered_data }
If the error message looks sibyllin, this is most likely because the error comes from invalid
syntaxes earlier inside the parsed content, like:
    - unbalanced parentheses (normal, curly, squared, ...)
    - nested string delimitation characters that are not properly escaped
            Example:    {"{{"} macro('it\\'s correct') {"}}"}
                        {"{{"} macro('it's wrong') {"}}"}
    - unclosed strings inside macros calls , the error might be found anywhere lower in the file
            Example:    {"{{"} macro('it is wrong) {"}}"}, with the error found here -> ' <-

"""


    def _location_info(self, tok:Optional[str], i:Optional[int]=None):
        i = self.i if i is None else i
        if tok is None:
            tok = self.tokens[i] if i<len(self.tokens) else "EOF"
        heads = self.__extract(i, -self.LOOK_AROUND)
        tails = self.__extract(i,  self.LOOK_AROUND)
        return f"{ heads }\033[31m>>{ tok }<<\033[0m{ tails }"


    def __extract(self, i_src, di):
        i,j = (max(0,i_src+di), i_src) if di<0 else  (i_src+1, i_src+1+di)
        return ''.join(self.tokens[i:j])






class IndentParser(
    IndentParserFeedbackManager,
    IndentManager,
    BaseMarkdownIndentParser,
):
    """
    Build a markdown parser class, extracting the indentations of macros calls requiring
    indentation, and taking in consideration jinja markups (skip {% raw %}...{% endraw %},
    properly parse complex macro calls, ignore macro variables).

    The result of the method `IndentParser(content).parse()` is a list of `Tuple[str,int]`:
    `(macro_name, indent)`, in the order they showed up in the content.
    """
