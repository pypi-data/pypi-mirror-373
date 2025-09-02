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

# pylint: disable=all

from typing import Dict, Optional

from ..tools_and_constants import HtmlClass






def html_builder_factory(template:str, allow_content):
    def tagger(tag:str, **props):
        def html_builder(
            content:str="",
            *,
            id:str='', kls:str="", attrs: Dict[str, str]=None,
            **kwargs
        ) -> str:
            """
            Build a the code for the given tag element.
            The id and kls named arguments, and also all keyword arguments have precedence over the
            content of the attrs dict. This dict allow to define hyphen separated attributes (like
            "data-max_size" and so on).

            NOTE: Using the @content argument on "mono tags" will raise ValueError.
            """
            if not allow_content and content:
                raise ValueError(f"Cannot use content on {tag!r} tags ({content=!r})")

            attrs = attrs or {}
            attrs.update(props)
            attrs.update(kwargs)
            if id:  attrs['id'] = id
            if kls: attrs['class'] = kls

            disabled = attrs.pop('disabled', None)

            attributes = " ".join(
                f'{ name }="{ value }"' #if name!='onclick' else f'{ name }={ value }'
                for name,value in attrs.items()
            )
            if disabled is not None:
                attributes += ' disabled'

            code = template.format(tag=tag, content=content, attributes=attributes)
            return code

        return html_builder
    return tagger



mono_tag = html_builder_factory("<{tag} {attributes} />", False)
bi_tag   = html_builder_factory("<{tag} {attributes}>{content}</{tag}>", True)




input   = mono_tag('input')
img     = mono_tag('img')

a       = bi_tag('a')
button  = bi_tag('button', type='button') # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#notes
code    = bi_tag('code')
div     = bi_tag('div')
script  = bi_tag('script')
style   = bi_tag('style')
span    = bi_tag('span')
svg     = bi_tag('svg')
td      = bi_tag('td')




def tooltip(txt:str, width_em:Optional[int]=None, shift:Optional[int]=None):
    """
    Generic PMT tooltip builder. If width_em is falsy, use automatic width.
    Th @shift argument is the % to use for the translation, 0% means the tooltip will got on the
    right, 100% means it will go on the left. With 50 (default), it's centered below the original element
    """
    if shift is None:
        shift = 50
    dct = {
        'kls': 'tooltiptext bottom',
        'style': f'--tool_shift: {shift}%;',
    }
    if width_em:
        dct['style'] += f"width:{ width_em }em;"

    return span(txt, **dct)



def checkbox(
    checked:bool,
    *,
    label:str="",
    id:str = "none",
    kls:str = "",
    kls_box:str = "",
    tip_txt:str = "",
    width_em:Optional[int]=None,
    tip_shift:Optional[int]=None
):
    """

    """
    checked = {'checked':""} if checked else {}
    box = input('', type='checkbox', disabled=True, id=id, kls=kls_box, **checked)
    txt = label and span(label)
    tip = tooltip(tip_txt, width_em, shift=tip_shift)
    out = div( box+txt+tip, kls=f'{ HtmlClass.tooltip } {kls}'.strip())
    return out
