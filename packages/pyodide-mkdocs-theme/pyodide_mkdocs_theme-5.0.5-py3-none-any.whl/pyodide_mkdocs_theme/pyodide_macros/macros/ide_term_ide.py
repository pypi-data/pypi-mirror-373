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


from abc import ABCMeta
from typing import Optional


from .. import html_builder as Html
from ..parsing import admonition_safe_html
from ..tools_and_constants import HtmlClass
from .ide_manager import IdeManager






_BTN_STDOUT_SVG = admonition_safe_html('''
<svg viewBox="0 0 24 24" fill="none"
    stroke="var(--md-default-fg-color)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"
    xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
<g>
  <path d="M 4,21.4 V 2.6 C 4,2.3 4.3,2 4.6,2 h 11.65 c 0.16,0 0.31,0.06 0.42,0.18 l 3.15,3.15 C 19.94,5.44 20,5.59 20,5.75 V 21.4 C 20,21.73 19.73,22 19.4,22 H 4.6 C 4.3,22 4,21.73 4,21.4 Z" ></path>
  <path d="M 16,5.4 V 2.35 C 16,2.16 16.16,2 16.35,2 c 0.09,0 0.18,0.03 0.25,0.10 l 3.29,3.29 C 19.96,5.46 20,5.55 20,5.65 20,5.84 19.84,6 19.65,6 H 16.6 C 16.27,6 16,5.73 16,5.4 Z" ></path>
  <path d="m 8,9.25 h 8" ></path>
  <path d="M 7.9,13.25 H 15.9"></path>
  <path d="M 7.9,11.25 H 14.4" ></path>
  <path d="M 7.9,19.25 H 14.4" ></path>
  <path d="m 7.9,15.25 h 8" ></path>
  <path d="M 7.9,17.25 H 11.9" ></path>
  <path d="m 8,5.25 h 4" ></path>
  <path d="m 8,7.25 h 4" ></path>
</g>
<g><path class="stdout-x-ray-svg" d="M 3,11.4 v 6 L 21,13.8 V 7.7 Z" style="fill:var(--md-default-bg-color);stroke-width:0;" ></path></g>
</svg>
''')




# Cannot use the `:material-overflow:` syntax, because not rendered when the terminal is not
# inside an admonition or tab... DX (markdown attributes missing, but putting them in IDE makes a whole mess of them...)
_BTN_MATERIAL_OVERFLOW = admonition_safe_html('''
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<path d="M7 21H5V3h2v18m7-18h-2v6h2V3m0 12h-2v6h2v-6m5-3-3-3v2H9v2h7v2l3-3Z">
</path></svg>''')




class CommonGeneratedIde(IdeManager, metaclass=ABCMeta):

    @classmethod
    def get_markdown(cls, use_mermaid:bool):
        raise NotImplementedError()






class CommonTermIde(IdeManager, metaclass=ABCMeta):
    """ Behaviors and data common to bth IDEs and isolated terminals. """


    term_height: Optional[int] = None
    """
    Number of lines to define the height of the terminal (unless it's vertical)
    """


    def exported_items(self):
        """
        Generate all the items of data that must be exported to JS.
        """
        yield from super().exported_items()
        yield from [
            ("stdout_cut_off", self.env.stdout_cut_off),
            ("cut_feedback",   self.env.cut_feedback),
        ]



    def make_terminal(self, term_id:str, kls:str, n_lines_h:int, **kw):
        """
        Build a terminal div with its button. If n_lines_h is falsy, the height of the div isn't
        handled. Otherwise, it's the mac of n_lines_h and 5.
        """
        n_buttons = 0
        shift = 97

        # Build buttons:
        tip = Html.tooltip(self.env.lang.feedback, width_em=self.env.lang.feedback.em, shift=shift)
        feed_div = Html.div(
            _BTN_STDOUT_SVG + tip,
            kls = f"twemoji { HtmlClass.stdout_ctrl } { HtmlClass.tooltip }"
        )
        n_buttons += 1

        tip_wrap = Html.tooltip(self.env.lang.wrap_term, width_em=self.env.lang.wrap_term.em, shift=shift)
        wrap_div = Html.div(
            _BTN_MATERIAL_OVERFLOW + tip_wrap,
            kls=f"{ HtmlClass.stdout_wrap_btn } {HtmlClass.tooltip } { HtmlClass.svg_switch_btn } twemoji deactivated",
        )
        n_buttons += 1

        # Group buttons:
        btns_div = Html.div(
            feed_div + wrap_div,
            kls=f"{ HtmlClass.term_btns_wrapper }",
        )

        # Build main div:
        if n_lines_h:
            n_lines_h = max(n_lines_h, 5)
            kw['style'] = f"--n-lines:{ n_lines_h };" + kw.get('style','')
        kw['style'] = 'line-height:24px;' + kw.get('style','')

        term_div = Html.div(id=term_id, kls=f"{kls} { HtmlClass.py_mk_terminal }", **kw)

        global_div = Html.div(
            term_div+btns_div,
            kls=HtmlClass.term_wrapper,
            style=f'--n-buttons:{ n_buttons }'
        )
        return global_div
