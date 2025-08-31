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
# from pathlib import Path
from typing import List, TYPE_CHECKING
from random import shuffle
from functools import lru_cache

from mkdocs.exceptions import BuildError


from .tools_and_constants import LZW_DELIMITER, DebugConfig
from .exceptions import PmtEncryptionError, PmtInternalError, PmtCodeFenceTitleQuotesError

if TYPE_CHECKING:
    from .plugin import PyodideMacrosPlugin




def replace_chunk(source:str, start:str, end:str, repl:str, *, at=0, keep_limiters=False):
    """ Given a @source and two delimiters/tokens, @start and @end, find those two tokens in
        @source, then replace the content of source between those two tokens with @repl.

        @at=0:                  Starting point for the search of @start in @source.
        @keep_limiters=False:   If True, the @start and @end tokens are kept and @repl is
                                placed in between them instead.
    """
    i,j = eat(source, start, at)
    _,j = eat(source, end,   j)
    if keep_limiters:
        repl = start + repl + end
    return source[:i] + repl + source[j:]


def eat(source:str, token:str, start=0, *, skip_error=False):
    """ Given a @source text, search for the given @token and returns the indexes locations
        of it, i and j (i: starting index, j: ending index, exclusive, as for slicing).

        @start=0:           Starting index for the search
        @skip_error=False:  Raises ValueError if False and the token isn't found.
                            If True and the token isn't found, returns i=j=len(source).
    """
    i = source.find(token, start)
    if i>=0:
        return i, i+len(token)

    if skip_error:
        return len(source), len(source)

    # handle error message:
    end  = min(1000, len(source)-start)
    tail = "" if end != 1000 else ' [...]'
    raise ValueError(f"Couldn't find {token=} in:\n\t[...] {source[start:end]}{ tail }")





def admonition_safe_html(s:str):
    """
    Replace all the new lines character from html/svg content, so that it van be inserted safely
    in admonitions, without breaking markdown rendering.
    """
    return s.strip().replace('\n',' ')



def camel(snake:str):
    """ Transform a snake_case python property to a JS camelCase one. """
    snake = re.sub(r'_{2,}', '_', snake)
    return re.sub(r'(?<=[a-zA-Z\d])_([a-z\d])', _camelize, snake)

def _camelize(m:re.Match):
    return m[1].upper()


def items_comma_joiner(lst:List[str], join:str='et'):
    """ ['1','2','3','4']  -> '1, 2, 3 {join} 4' """
    elements = [ v or "''" for v in map(str,lst)]
    if len(elements)>1:
        last = elements.pop()
        elements[-1] += f" {join} {last}"
    elements = ', '.join(elements)
    return elements



def add_indent(content:str, indent:str, leading=False):
    """
    Add the given indentation to all lines containing non space characters (hence, leave
    empty lines as they are: this is compliant with the md rendering engine).

    If @leading is True, also add the indent at the beginning.
    """
    out = re.sub(r"(\n *)(?=\S)", lambda m:m[0]+indent, content)
    return indent * leading + out




def build_code_fence(
    content:str,
    indent:str="",
    line_nums=1,
    lang:str='python',
    title:str=""
) -> str :
    """
    Build a markdown code fence for the given content and the given language.
    If a title is given, it is inserted automatically.
    If linenums is falsy, no line numbers are included.
    If @indent is given each line is automatically indented.

    @content (str): code content of the code block
    @indent (str): extra left indentation to add on each line
    @line_nums (=1): if falsy, no line numbers will be added to the code block. Otherwise, use
                     the given int value as starting line number.
    @lang (="python"): language to use to format the resulting code block.
    @title: title for the code block, if given. Note: the title cannot contain quotes `"`
    """
    line_nums = f'linenums="{ line_nums }"' if line_nums else ""
    if title:
        if '"' in title:
            raise PmtCodeFenceTitleQuotesError(
                f'Cannot create a code fence template with a title containing quotes:\n'
                f"  {lang=}, {title=!r}\n{content}"
            )
        title = f'title="{ title }"'

    lst = [
        '',
        f"```{ lang } { title } { line_nums }",
        *content.strip('\n').splitlines(),
        "```",
        '',
    ]
    out = '\n'.join( indent+line for line in lst )
    return out







# MEAN = []

NO_HTML   = '\'"&#><\n\t\r\\'
"""
Characters that shouldn't be present in a random text in the DOM, because they may generate html
constructs the server _will_ interpret, and this will break the decompression.

(this string is automatically transferred in the JS code).
"""

# pylint: disable-next=line-too-long
TOME_BASE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%()*+,-./:;=?@^_`{|}~ "
"""
Removed:
    - "<>" because could generate tags
    - "&" because of &lt; stuff
    - "[]" because could be seen as md links syntaxe by mkdocs-addresses
    - anything close to escaping... (otherwise, the encoded stuff is unusable through requests.)

(this string is automatically transferred in the JS code).
"""

BASE_TOME = {c:i for i,c in enumerate(TOME_BASE)}
BASE      = len(TOME_BASE)


@lru_cache(None)
def i_to_base(n, size):
    """
    Convert an index in the table to the TOME_BASE encoded string, using size characters.
    """
    out = ''.join(
        TOME_BASE[ n // BASE**p % BASE ]
        for p in reversed(range(size))
    )
    return out



def compress_LZW(txt:str, env:'PyodideMacrosPlugin'):
    """ string Compression """

    tome  = set(txt) - set(NO_HTML)                  # remove tags tokens
    if LZW_DELIMITER in tome:
        raise PmtEncryptionError(
            "Cannot encrypt data because the text already contains the delimiter used to "
            "identify sections in the encoded content. Solutions to this problem are:\n"
           f"    1. Don't use {LZW_DELIMITER!r} in the content.\n"
            "    2. Deactivate the encryption by setting the ides.encrypt_corrections_and_rems "
            "option to false."
        )
    big   = list(filter(chr(255).__lt__, tome))     # might be problematic for python->JS transfer
    small = list(filter(chr(255).__ge__, tome))     # easy ones (python->JS)

    if env.encrypt_alpha_mode=='shuffle':
        shuffle(small)                              # 'cause, why not... :p
    elif env.encrypt_alpha_mode=='sort':
        small.sort()

    alpha = list(NO_HTML) + big + small             # Will always be added afterward

    def grab(j):
        i,j = j,j+1
        while j<len(txt) and txt[i:j] in dct: j+=1
        token = txt[i:j]

        if token not in dct:
            # tokens.append(token)
            dct[token] = len(dct)
            return j-1, dct[token[:-1]]

        return len(txt), dct[token]

    out, i, size, limit = [], 0, 2, BASE**2
    dct = {c: i for i,c in enumerate(alpha)}

    while i < len(txt):
        i,idx = grab(i)
        out.append(i_to_base(idx,size))
        if len(dct)==limit:     # Reached x**base-1 => increase the chunk size
            out.append(LZW_DELIMITER)
            size += 1
            limit = BASE**size

    # Version to put in the encoded tag, WITHOUT any character form NO_HTML string:
    encoded_bigs   = '.'.join( str(ord(c)) for c in big )
    encoded_smalls = ''.join(small)

    # Leading and trailing dots to allow unconditional trim in JS, later:
    output_with_table = (
        f".{ encoded_bigs }{ LZW_DELIMITER }{ encoded_smalls }{ LZW_DELIMITER }{ ''.join(out) }."
    )

    if DebugConfig.check_decode:
        _check_decode_LZW(txt, dct, size, output_with_table)

    # MEAN.append((len(txt),len(out)))
    return output_with_table







def _check_decode_LZW(txt, dct, size, output_with_table):
    try:
        decoded = _decode_LZW(output_with_table)
    except Exception as e:
        decoded = str(e)
    if decoded != txt:
        alpha = ''.join(sorted(set(txt)))
        i = next(
            (i for i,(a,b) in enumerate(zip(txt,decoded)) if a!=b),
            min(len(txt), len(decoded))
        )
        # (Path.cwd() / "encoded").write_text(output_with_table.replace('\x1e', '\n'), encoding='utf-8')
        raise PmtInternalError(f'''
Failed to decode...

Alpha: ]]{ alpha }[[ (len={len(alpha)})
        { [*map(ord,alpha)] }

table: len={len(dct)}
{size=} | BASE**size = {BASE**size}

source: len={len(txt)}
back:   len={len(decoded)}
Differ: {i=}

source[i-50:i]:
{ txt[i-50:i] }

source[i:i+200]:
{ txt[i:i+200]}

back[i:i+200]:
{decoded[i:i+200]}

''')

def un_i_to_base(s:str):
    """ Debugging purpose only """
    v = 0
    for c in s:
        v = BASE*v + BASE_TOME[c]
    return v

def _decode_LZW(compressed:str):
    """ Debugging purpose only """

    big,small,*chunks = compressed.strip().split(LZW_DELIMITER)
    big = big[1:]
    tome = [*NO_HTML] + [chr(int(s)) for s in big and big.split('.')] + [*small]

    txt,size = [],1
    for chunk in chunks:
        size += 1
        assert not len(chunk)%size, (len(chunk), size, len(chunk)%size)
        txt.extend( un_i_to_base(chunk[i:i+size]) for i in range(0, len(chunk), size) )

    out = []
    for i,idx in enumerate(txt):
        w = tome[idx]
        fresh = '' if i+1==len(txt) else w + ( w if txt[i+1]==len(tome) else tome[txt[i+1]] )[0]
        # https://mooc-forums.inria.fr/moocnsi/t/question-lzw-cas-particulier-decompression/11491/2
        out.append(w)
        tome.append(fresh)

    return ''.join(out)
