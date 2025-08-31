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


import json
from dataclasses import dataclass
from itertools import count
from textwrap import dedent
from typing import Callable, ClassVar, Dict, Iterator, List, TYPE_CHECKING


from ..exceptions import PmtMacrosInvalidArgumentError
from .. import html_builder as Html
from ..tools_and_constants import HtmlClass, PageUrl, PmtPyMacrosName, PageInclusion, Prefix, Qcm, ScriptSection
from ..html_dependencies.deps_class import DepKind
from ..plugin.tools.macros_data import IdeToTest
from .ide_term_ide import CommonGeneratedIde
from .ide_ide import Ide


if TYPE_CHECKING:
    from ..plugin.pyodide_macros_plugin import PyodideMacrosPlugin




@dataclass
class IdeTester(CommonGeneratedIde, Ide):

    MACRO_NAME: ClassVar[PmtPyMacrosName] = PmtPyMacrosName.IDE_tester

    ID_PREFIX: ClassVar[str] = Prefix.tester_

    DEPS_KIND: ClassVar[DepKind] = DepKind.ides_test

    nth_item:  ClassVar[str] = ""
    nth_style: ClassVar[str] = ""


    @property
    def has_check_btn(self):
        """ The IdeTester always has one... """
        return True

    @property
    def has_counter(self):
        """ The IdeTester always has one... """
        return True



    def register_ide_for_tests(self):
        """ IdeTester instances are never registered for testing... """


    def list_of_buttons(self):
        """ Keep only public tests, validations and restart. """
        btns    = super().list_of_buttons()
        restart = next(btn_html for btn_html in btns if "icons8-restart-64.png" in btn_html)
        return btns[:2] + [restart]



    def counter_txt_spans(self):
        """ No counter below the IDE, unless run in `_dev_mode`. """
        if self.env._dev_mode:                  # pylint: disable=protected-access
            return super().counter_txt_spans()
        return ''



    #-----------------------------------------------------------------------------------



    @classmethod
    def get_markdown(cls, use_mermaid:bool):
        """
        Build the code generating the IdeTester object. Insert the MERMAID logistic only if
        the `mkdocs.yml` holds the custom fences code configuration.
        """
        return dedent(f"""
            # Testing all IDEs in the documentation {'{'} data-search-exclude {'}'}

            <br>

            {'{{'} IDE_tester(MAX='+', MERMAID={ use_mermaid }, TERM_H=15) {'}}'}

        """)




    @classmethod
    def build_filters(cls):
        """
        Div with the status filter toggle buttons/checkboxes.
        """
        return Html.div(
            "".join(
                "".join((
                    f'<button type="button" class="filter-btn" id="filter-{ kind }" state=1>',
                    Html.div("Show", kls="filter-show"),
                    Html.div('', kls=f'{ kind } { HtmlClass.status_filter }')
                        if kind != Qcm.ok else
                    Html.div(
                        Html.span('', kls=f'{ Qcm.ok } { HtmlClass.status_filter }')
                        +
                        Html.span('', kls=f'{ Qcm.ok } { Qcm.fail_ok } { HtmlClass.status_filter }')
                    ),
                    '</button>',
                ))
                for kind in Qcm.show_tests_buttons
            ),
            id = HtmlClass.py_mk_tests_filters
        )


    @classmethod
    def build_global_controller(cls, env:'PyodideMacrosPlugin'):
        """
        Div containing the buttons and counters to control the tests (class contains "inline").
        """
        btn_start = cls.cls_create_button(env, 'test_ides')
        btn_stop  = cls.cls_create_button(env, 'test_stop')
        return f'''
<div class="inline" id="py_mk_tests_controllers">{ btn_start }{ btn_stop }
  <ul>
    <li>IDEs found : <span id="cnt-all"></span></li>
    <li>Skip :       <span id="cnt-skip" style="color:gray;"></span></li>
    <li>To do :      <span id="cnt-remaining"></span></li>
    <li>Success :    <span id="cnt-success" style="color:green;"></span></li>
    <li>Error :      <span id="cnt-failed" style="color:red;"></span></li>
  </ul>
  <button type="button" class="cases-btn" id="select-all">Select all</button>
  <br><button type="button" class="cases-btn" id="unselect-all">Unselect all</button>
  <br><button type="button" class="cases-btn" id="toggle-human">Toggle human</button>
</div>
'''





    @classmethod
    def build_html_for_tester(
        cls,
        env:'PyodideMacrosPlugin',
        pages_with_ides: Dict[PageUrl, List[IdeToTest]],
    ) -> str :
        """
        Build all the html base elements holding the results/information for each IDE to test.
        """
        filters    = cls.build_filters()
        controller = cls.build_global_controller(env)

        use_load_button = env.testing_include == PageInclusion.serve
        if env.testing_load_buttons is not None:
            use_load_button = env.testing_load_buttons

        def item_generator():
            for n in count(1):
                cls.nth_item, cls.nth_style = f'--item-{n}', f"display:var(--item-{n}, unset);"
                yield

        item_style  = item_generator()
        script_data = {}
        table_like  = ''.join(
            row for lst in pages_with_ides.values()
                for item in lst
                for row in cls._build_one_ide_items(
                    env, item, use_load_button, script_data, item_style
                )
        )
        div_table    = Html.div(table_like, id=HtmlClass.py_mk_tests_results)
        cases_script = f"<script>const CASES_DATA={ json.dumps(script_data) }</script>"

        inner = controller + filters + Html.div(div_table, id=HtmlClass.py_mk_tests_table)

        return Html.div(inner + cases_script, id=HtmlClass.py_mk_test_global_wrapper)




    @classmethod
    def _build_one_ide_items(
        cls,
        env:'PyodideMacrosPlugin',
        item:IdeToTest,
        use_load_button:bool,
        script_data: List[str],
        item_style: Iterator[str],
    ):
        """
        Build the entire html data for the given IDE/item.
        Might generate several subtests if Case.subcases is used.
        """
        dive    = cls._diver(item)
        js_dump = item.as_dict()

        # Store for dump so script tag:
        script_data[ js_dump['editor_id'] ] = js_dump

        # Build main test/item row:
        next(item_style)
        yield cls._build_main_item_row(env, dive, js_dump, use_load_button, item)

        # Now generate all the subtests, if they exist:
        sub_cases = js_dump.get('subcases',())
        for i,sub_case in enumerate(sub_cases, 1):
            is_last = i == len(sub_cases)

            if 'subcases' in sub_case:
                raise PmtMacrosInvalidArgumentError("Case.subcases should go down one level at most.")

            next(item_style)

            # Only the div holding the final svg element is given the itemVar value:
            div_svg  = dive('', id=HtmlClass.status+str(i), kls=HtmlClass.status, itemVar=cls.nth_item)
            load_btn = cls._button(env, 'load_ide',   "testing") if use_load_button else ""
            lone_btn = cls._button(env, 'test_1_ide', "testing")
            sub_btns = dive(load_btn+lone_btn, id=f"play{i}")

            yield dive(cls.description(sub_case, is_last=is_last)) + div_svg + sub_btns + dive('')




    @classmethod
    def _build_main_item_row(
        cls,
        env,
        dive:Callable,
        js_dump:dict,
        use_load_button:bool,
        item: IdeToTest,
    ):
        ide_name = js_dump['ide_name']

        # Link + main test description
        a_href = Html.a(ide_name, href=js_dump['ide_link'], target="_blank")
        link   = dive( a_href + cls.description(js_dump, True) )

        # Empty div that WILL hold the test's status svg indicator (filled in JS):
        svg_status = dive( '', id=HtmlClass.status, kls=HtmlClass.status+' top_test', itemVar=cls.nth_item)

        # Buttons
        load_btn  = cls._button(env, 'load_ide') if use_load_button else ""
        play_1    = cls._button(env, 'test_1_ide')
        main_btns = dive( load_btn + play_1, id="test-btns")

        # sections indicators:
        def boxer(section):
            use_orange = (
                section=='code' and js_dump.get('code')
                or section=='corr' and not js_dump.get('code')
            )
            return Html.checkbox(
                getattr(item.has, section),
                id  = f"box_{ section }_{ item.storage_id }",
                kls = "section-box",
                kls_box = 'orange-box' * use_orange,
                tip_txt = section+"?",
                tip_shift=90,
            )

        row1 = []
        row2 = []
        for section in ScriptSection.VALUES:
            box = boxer(section)
            if ScriptSection.env_term == section:
                row2.append(box)
            elif ScriptSection.corr == section:
                row2.extend(map(boxer, (section,'REM','VIS_REM') ))
            elif ScriptSection.post_term == section:
                row2.append(box)
            else:
                row1.append(box)
        sections = dive(Html.div(''.join(row1+row2), kls='sections'))

        return link + svg_status + main_btns + sections




    @classmethod
    def _diver(cls, item:IdeToTest) -> Callable :

        def dive(*a, id=None, kls=None,**kw):
            return Html.div(
                *a,
                id = id and f"{ id }-{ item.storage_id }",
                kls = f"{ HtmlClass.py_mk_test_element } { kls or '' }".strip(),
                style = cls.nth_style,
                **kw
            )
        return dive


    @classmethod
    def _button(cls, env, kind:str, xtra_class="") -> str :
        return cls.cls_create_button(env, kind, extra_btn_kls=xtra_class, style=cls.nth_style)



    @staticmethod
    def description(dump:dict, is_top=False, *, is_last=False):
        """
        Build one test description html, with proper classes/ids/format.
        """
        desc = 'description' in dump and dump['description'] or ""
        if is_top and not desc:
            return ""

        desc = Html.div(desc, kls="pmt_note_tests" + ' top_test'*is_top + ' last'*is_last)
        return desc
