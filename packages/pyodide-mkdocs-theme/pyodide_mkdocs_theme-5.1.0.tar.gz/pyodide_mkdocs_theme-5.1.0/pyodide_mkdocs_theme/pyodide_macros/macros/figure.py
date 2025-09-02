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
from typing import Optional

from mkdocs.exceptions import BuildError



from ..tools_and_constants import MACROS_WITH_INDENTS, HtmlClass, P5BtnLocation
from ..exceptions import PmtMacrosInvalidArgumentError
from .. import html_builder as Html
from ..plugin.maestro_macros import MaestroMacros
from .ide_manager import IdeManager





def figure(env:MaestroMacros):
    """
    Macro pour insérer une <div> qui devra contenir une figure dessinée ensuite via matplotlib,
    par exemple(ou autre!).
    """
    MACROS_WITH_INDENTS.add('figure')

    def p5_btn(kind:str, div_id:str):
        return IdeManager.cls_create_button(
            env,
            f'p5_{ kind }',
            id=f"{ kind }-btn-{ div_id }",
            extra_btn_kls='p5-btn'
        )

    @wraps(figure)
    def wrapped(
        div_id:      Optional[str] = None, # "figure1",
        *,
        div_class:   Optional[str] = None, # '',
        inner_text:  Optional[str] = None, # 'Votre tracé sera ici',
        admo_kind:   Optional[str] = None, # '!!!',
        admo_class:  Optional[str] = None, # 'tip',
        admo_title:  Optional[str] = None, # 'Votre Figure',
        p5_buttons:  Optional[str] = None, # None,
        SHOW:        Optional[str] = None, # sink (not needed here!)
    ):
        code = Html.div(inner_text, id=div_id, kls=f"{ HtmlClass.py_mk_figure } { div_class }")

        if p5_buttons:
            if not P5BtnLocation.has_member(p5_buttons):
                raise PmtMacrosInvalidArgumentError(f"Invalid value for `p5_buttons`: {p5_buttons!r}")

            buttons_order = 'stop', 'start', 'step'
            buttons = Html.div(
                ''.join( p5_btn(kind, div_id) for kind in buttons_order ),
                kls=f"{ HtmlClass.p5_wrapper } { HtmlClass.p5_btns_wrapper } p5_{ p5_buttons }"
            )
            code = Html.div(buttons+code, kls=f"{ HtmlClass.p5_wrapper } p5_{ p5_buttons }")

        if admo_kind:
            code = f"""\n
{admo_kind} {admo_class} "{admo_title}"
    {code}
\n"""

        out_code = env.indent_macro(code)
        return out_code

    return wrapped
