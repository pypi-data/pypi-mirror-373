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
# pylint: disable=unused-argument

from functools import wraps
from textwrap import dedent
from typing import Any, Dict, List, Tuple

from mkdocs.exceptions import BuildError


from ..pyodide_logger import logger
from ..tools_and_constants import MACROS_WITH_INDENTS, HtmlClass, IdeConstants
from ..exceptions import PmtMacrosInvalidArgumentError
from ..html_dependencies.deps_class import DepKind
from ..plugin.maestro_macros import MaestroMacros









FIX_P = '</p KEEP>'



def multi_qcm(env:MaestroMacros):
    """
    @inputs:          lists of data for one question, aka:
                        - question title
                        - list of choices
                        - list of correct answers
                        - kwargs, for single=Optional[bool]  >>>  spec not fixed yet...
    @shuffle=False:   Questions and their items are shuffled on each refresh/retry
    @hide=False:      Correct answers will stay hidden if True after checking the user's answers
    @multi=None:      Set the default behavior for unique correct answers, at qcm level.
    @admo_kind="!!!": Control the kind of admonition used for the QCM
    @admo_type='tip': Category of admonition to use
    @qcm_title=None:  Title for the admonition. If not given "Question" (possibly plural) is used.

    @DEBUG=False:     If True, md output will be printed to the console
    """

    MACROS_WITH_INDENTS.add('multi_qcm')

    @wraps(multi_qcm)
    def wrapped(
        *questions,
        # REMINDER: _NOTHING_ should ever be left to None at runtime (MaestroMeta)
        description:str = None,
        hide:       bool = None,
        multi:      bool = None,
        shuffle:    bool = None,
        shuffle_questions: bool = None,
        shuffle_items: bool = None,
        admo_kind:  str = None,
        admo_class: str = None,
        qcm_title:  str = None,
        tag_list_of_qs: str = None,
        DEBUG:      bool = None,
        SHOW:       str = None,         # sink (not needed here!)
        ID=None,                        # sink (deprecated)
    ):
        """
        WARNING:    Extra closing </p> tags needed here and there to guarantee the final
                    html structure!

        Reasons:
        1. THE MD RENDERER GENERATES INVALID HTML, WHEN MIXING html+md, PERIOD!
        2. The md renderer will automatically open a <p> tag when starting the admo content.
        3. If _ever_ the user defines a multiline content anywhere in the qcm, a new <p>
            tag will be started, leaving the previous one hanging in the air...

        So far, so good...: the html is invalid, but rendered correctly/usable in a browser.

        4. CATACLYSM: use another plugin that will pass that html through BSoup...:
            Depending on the html parser used, Beautif(o)ulSoup _WILL_ generate the missing
            closing tags, and this will entirely mess up the rendered page.

        So, to avoid this, the extra closing `</p>` are added. They _LOOK_ like they are hanging,
        but they _will_ actually produce valid html!
        """


        def qcm_start():
            nonlocal qcm_title

            qcm_id       = env.get_qcm_id()
            shuffled     = shuffle or shuffle_questions
            xtra_classes = ' '.join(filter(None, (
                HtmlClass.py_mk_admonition_qcm,
                HtmlClass.qcm_shuffle * shuffled,
                HtmlClass.qcm_hidden * hide,
                HtmlClass.qcm_multi if multi else HtmlClass.qcm_single,
                HtmlClass.qcm_no_admo * (not admo_kind),
                qcm_id,
            )))

            is_default_title = qcm_title == env.lang.qcm_title.msg
            if is_default_title:
                # If using default, pick plural when appropriate:
                qcm_title = env.lang.qcm_title.one_or_many( len(questions_data) > 1 )

            elif not admo_kind:
                # But forbid title when the admonition will be removed later (JS)
                raise PmtMacrosInvalidArgumentError(
                    "A multi_qcm with a `qcm_title` argument cannot use `admo_kind=None` "
                    "or the title would be lost."
                )

            admo_qcm    = f'{ admo_kind or "!!!" } { admo_class } { xtra_classes } "{ qcm_title }"'
            ol_ul_class = f'{ HtmlClass.py_mk_questions_list_qcm } { HtmlClass.py_mk_question_qcm }'

            return [
                indent + admo_qcm,
                '',                 # ALWAYS KEEP THIS ONE!
                *(
                    () if not description else (auto_indent(qcm_format(description)), '')
                ),
                auto_indent( f'\n{ FIX_P }<{ tag_list_of_qs } class="{ ol_ul_class }">\n' ),
            ]

        def qcm_close():
            admonition_lst.append(auto_indent(f"{ FIX_P }</{ tag_list_of_qs }>"))



        def question_open(question:str, n:int, lst_answers:List[int], default_multi, shuffled):
            is_multi  = len(lst_answers) > 1
            multi_kls = HtmlClass.qcm_multi if is_multi or default_multi else HtmlClass.qcm_single
            item_kls  = f'class="{ HtmlClass.py_mk_question_qcm } { multi_kls } { shuffled * HtmlClass.qcm_shuffle}"'
            answers   = ','.join( map(str, lst_answers) )
            tag_open  = f'{ FIX_P }<li { item_kls } correct="{ answers }" markdown>\n{ question }'

            admonition_lst.append(auto_indent(tag_open))


        def question_options(items):
            """
            Always use "md_in_html" approach, to simplify the construction. It is required anyway
            when the first item starts with a code block...
            """
            admonition_lst.append(
                auto_indent(f'{ FIX_P }<ul class="{ HtmlClass.py_mk_item_qcm }">')
            )
            admonition_lst.extend(
                auto_indent(item, wrap_li=True) for item in items
            )
            admonition_lst.append(
                auto_indent("</ul>")
            )

        def add_question_comment(comment:str):
            encrypt_token = ()
            if env.encrypt_comments:
                env.set_current_page_insertion_needs(DepKind.qcm_encrypt)
                encrypt_token = ( indent_comment(IdeConstants.encryption_token)+"\n", )

            classes = ' '.join((
                HtmlClass.py_mk_hidden,
                HtmlClass.py_mk_comment_qcm,
                HtmlClass.py_mk_encrypted_qcm * env.encrypt_comments,
            ))
            admonition_lst.extend((
                auto_indent(f'??? tip { classes } "Remarque"')+"\n",
                *encrypt_token,
                indent_comment(comment)+"\n",
                *encrypt_token,
            ))

        def question_close():
            admonition_lst.append(auto_indent("</li>\n"))
            # Extra linefeed for presentational purpose only



        def validate_question_config(n_question, question, items, lst_correct, multi):

            duplicates  = len(lst_correct) != len(set(lst_correct))
            unknown     = set(lst_correct) - set(range(1,1+len(items)))
            require_ans = env.forbid_no_correct_answers_with_multi

            msg = ""
            if duplicates:
                msg = f"Correct answers contain duplicated values: {lst_correct}"

            elif unknown:
                msg = f"Correct answers contain invalid items number: {unknown}"
                if 0 in unknown:
                    msg += "\n(Note: correct answers are not indices and start at 1, not 0!)"

            elif not lst_correct and (not multi or require_ans):
                msg = ''.join((
                    "The question above has no correct answer specified:\n",
                    "    - This is not allowed for SCQ.\n",
                    "    - This is not allowed for MCQ.\n" * require_ans,
                    "If this is the desired behavior:\n",
                    "    - Set the plugin's option `qcms.forbid_no_correct_answers_with_multi` to false.\n" * require_ans,
                    "    - Define the question as `multi` (one way or another, see documentation).\n",
                ))

            if msg:
                msg = (
                    f"\nFile:       { env.file_location() }"
                    f"\nQCM Title:  { qcm_title }"
                    f"\nQuestion { n_question }:\n"
                    f"\n{ question !r}"
                    f"\n\n{msg}"
                )
                raise PmtMacrosInvalidArgumentError(msg)


        def get_comment_and_options(a=None, b=None):
            """
            Extra appropriately the two last optional values (question options configuration
            and question commentary).
            """
            dct     = a if isinstance(a, dict) else b if isinstance(b, dict) else {}
            comment = a if isinstance(a, str) else b if isinstance(b, str) else ""
            return comment, dct


        #------------------------------------------------------------------


        env.set_current_page_insertion_needs(DepKind.qcm)


        # Unify data, adding/extracting systematically the extra_dct element:
        questions_data: List[ Tuple[str, list, List[int], Dict[str,Any]] ] = [
            [
                qcm_format(q),
                [*map(qcm_format,items)],
                sorted(ans),
                *get_comment_and_options(*extras),
            ]
            for q, items, ans, *extras in questions
        ]

        tag_list_of_qs = tag_list_of_qs or ('ol' if len(questions_data) > 1 else 'ul')
        indent         = env.get_macro_indent()
        auto_indent    = auto_indenter_factory(indent)
        indent_comment = auto_indenter_factory(indent + '    ')
        admonition_lst = qcm_start()

        for n, (question, items, lst_answers, comment, extra_dct) in enumerate(questions_data, 1):

            shuffled = extra_dct.get('shuffle', shuffle or shuffle_items)
            is_multi = extra_dct.get('multi',   multi)
            validate_question_config(n, question, items, lst_answers, is_multi)

            question_open(question, n, lst_answers, is_multi, shuffled)
            question_options(items)
            if comment:
                add_question_comment(comment)
            question_close()

        qcm_close()


        output = '\n'.join(admonition_lst)
        output = f'\n\n{ output }\n\n'    # Enforce empty spaces around in the markdown admonition

        if DEBUG:
            # The user doesn't need to know about the CORRECT_CLOSE_P thing, so remove them first:
            to_print = output.replace(FIX_P, '')
            print('\vCall to multi_qcm in page', env.page.file.src_uri, '\n', to_print)
        return output

    return wrapped








def auto_indenter_factory(indent:str):
    """ Auto-indenter factory, to indent CONTENT of the admonition (hence, one extra level) """

    indent += '    '

    def indenter(content:str, wrap_li=False):
        """
        Takes a @content, possibly multiline, and indent all lines (including the first) with the
        base @indent and an extra @lvl, where each level counts for 4 space characters.

        If @wrap_li is True, handle the "li" element appropriately, meaning:
            - prepend with "* " for simple content
            - surround the item with `<li markdown>...</li>

        @lvl: override the number of indentation levels (default: 1)
        """
        if wrap_li:
            content = f'<li class="{ HtmlClass.py_mk_item_qcm }" markdown="1">\n{ content }\n</li>'
        return indent + content.replace('\n',"\n"+indent)

    return indenter




def qcm_format(msg:str):
    """ Use the natural/minimal indentation and strip spaces on both ends """
    bare = dedent(msg).strip()
    return f"{ bare }\n"
