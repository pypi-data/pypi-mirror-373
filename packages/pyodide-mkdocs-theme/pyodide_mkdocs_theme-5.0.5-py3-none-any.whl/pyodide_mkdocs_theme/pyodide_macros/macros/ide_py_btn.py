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


import re
from typing import ClassVar, Optional, Tuple, Union
from dataclasses import dataclass

from pyodide_mkdocs_theme.pyodide_macros.html_dependencies.deps_class import DepKind
from pyodide_mkdocs_theme.pyodide_macros.paths_utils import get_ide_button_png_path


from ..html_builder import _html_builder as Html
from ..tools_and_constants import HtmlClass, PmtPyMacrosName, Prefix
from ..messages import Tip
from .ide_manager import IdeManager





@dataclass
class PyBtn(IdeManager):
    """
    Builds a button + a terminal + the buttons and extra logistic needed for them.
    """
    MACRO_NAME: ClassVar[PmtPyMacrosName] = PmtPyMacrosName.py_btn

    ID_PREFIX: ClassVar[str] = Prefix.btn_only_

    DEPS_KIND: ClassVar[DepKind] = DepKind.py_btn

    KW_TO_TRANSFER: ClassVar[Tuple[ Union[str, Tuple[str,str]]] ] = (
        'WRAPPER',
        'HEIGHT', 'SIZE', 'WIDTH', 'ICON',
        'TIP', 'TIP_SHIFT', 'TIP_WIDTH',
    )


    wrapper: str = 'div'
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None
    icon: str = ""
    tip: Optional[Tip] = None
    tip_shift: int = 50
    tip_width: int = 0


    def _validate_files_config(self):
        self._check_forbidden_sections(
            "env_term code corr tests secrets post_term post REM VIS_REM",
            f"Only the `env` section should be used, for { self.MACRO_NAME } macros"
        )



    def make_element(self) -> str:

        span_tooltip  = self._build_tooltip()
        img, img_size = self._build_icon()

        button_html   = Html.button(
            f'{ img }{ span_tooltip }',
            kls = HtmlClass.tooltip,
            btn_kind = 'py_btn',
            style = img_size,
            markdown = 1,       # in case material icon reference is used
        )
        wrapper = getattr(Html, self.wrapper)(
            button_html,
            id = self.editor_name,
            kls = HtmlClass.py_mk_py_btn,
            markdown = 1,       # in case material icon reference is used
        )
        return wrapper



    def _build_tooltip(self):
        tip: Tip = Tip(self.tip_width, self.tip) if self.tip else self.env.lang.py_btn
        span_tooltip = Html.tooltip(str(tip), tip.em, self.tip_shift)
        return span_tooltip


    def _build_img(self, img_style:str, *, docs_path:Optional[str]=None, link:Optional[str]=None):
        lvl_up   = self.env.level_up_from_current_page()
        img_link = (
            f"{lvl_up}/{docs_path}"
                if docs_path else
            link or get_ide_button_png_path(lvl_up,'play')
        )
        return Html.img(
            src = img_link,
            kls = HtmlClass.skip_light_box,
            style = img_style
        )


    def _build_icon(self):
        if self.size:
            self.width = self.height = self.size

        img_size = ""
        for prop in ('width', 'height'):
            val = getattr(self,prop)
            if val is not None:
                img_size += f"{prop}:{val}px;"

        self.icon    = self.icon.strip()
        is_link      = re.match(r"http|ftp|www.", self.icon)
        is_docs_path = re.fullmatch(r"(?!https?\W)(?!ftps?\W)(?!www\.).+[.]\w{2,7}", self.icon)
                       # Relative + does not start with link + ends with extension (2-7 chars)

        if not self.icon:                       # Default image
            img = self._build_img(img_size)

        elif is_link:
            img = self._build_img(img_size, link=self.icon)

        elif is_docs_path:                      # relative to "docs to be"
            img = self._build_img(img_size, docs_path=self.icon)

        else:                                   # Assume svg raw code or material icon
            img = self.icon

        return img, img_size
