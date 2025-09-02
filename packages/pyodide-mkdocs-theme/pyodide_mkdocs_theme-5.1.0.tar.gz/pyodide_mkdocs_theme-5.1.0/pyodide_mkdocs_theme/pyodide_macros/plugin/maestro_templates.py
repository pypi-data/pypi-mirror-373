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
# pylint: disable=invalid-name, attribute-defined-outside-init, unused-argument





import json
from contextlib import contextmanager
from typing import Any, Dict, Optional, TYPE_CHECKING


from jinja2 import Environment
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files


from ..pyodide_logger import logger
from ..tools_and_constants import ICONS_IN_TEMPLATES_DIR #, JS_CONFIG_TEMPLATES
from ..messages.fr_lang import Lang
from ..html_dependencies import HtmlDependencies, Block
from .tools.maestro_tools import dump_and_dumper
from .maestro_base import TO_DUMP_TO_CONFIG
from .maestro_meta import MaestroMeta
from .maestro_macros import MaestroMacros

if TYPE_CHECKING:
    from .pyodide_macros_plugin import PyodideMacrosPlugin




class MaestroTemplates(MaestroMacros, MaestroMeta):
    """
    Manage everything related to functions used in the Jinja/html templates.
    """


    def on_env(self, env:Environment, config:MkDocsConfig, files:Files):

        logger.info("Build templates and update Jinja environment for rendering.")
        super().on_env(env, config, files)

        HtmlDependencies.build_scripts_pages_templates(self, self._pages_configs)
        HtmlDependencies.build_import_map_template()
        HtmlDependencies.build_overlord_data()

        for method in [
            self.pyodide_imports_map,
            self.link_palette_to_ace_theme,
            self._template_renderer_factory(Block.libs),        # Generate: pyodide_libs()
            # self._template_renderer_factory(Block.content),   # (applied from python layer)
            self._template_renderer_factory(Block.scripts),     # Generate: pyodide_scripts()
        ]:
            env.globals[method.__name__] = method



    def _template_renderer_factory(self, block:Block):

        @MaestroMeta.meta_config_swap(self)
        def wrapper(page:Page):
            """
            WARNING: the page argument is NOT useless: it's used in the meta_config_swap decorator.
            """
            # NOTE: SOMETIMES `page` is None (once, actually, for the 404 default page).
            #       With the current implementation, everything works even with self._page = None
            #       below...
            #       BUT, when picking the tag template in the cache, one cannot rely on self.page
            #       when page is None, because self.page isn't actually up to date. So explicitly
            #       pass the correct cache_key value
            cache_key = page and self.page and self.page.url
            return HtmlDependencies.render_tags_for(block, self, cache_key)

        wrapper.__doc__ = f"Jinja environment routine building dependencies for the {block} block."
        wrapper.__name__ = wrapper.__qualname__ = f"pyodide_{block}"

        return wrapper



    #---------------------------------------------------------------

    @MaestroMeta.meta_config_swap
    def pyodide_imports_map(self, page:Page):   # page argument used in the config swap decorator
        """
        Called from jinja html templates. Has to see the local config.
        """
        return HtmlDependencies.render_import_map(self, page)


    def link_palette_to_ace_theme(self, config:MkDocsConfig):
        """
        Set ace themes for each palette color.
        """
        dark  = self.ace_style_dark
        light = self.ace_style_light

        if 'ace_style' in config.extra:
            if 'slate' in config.extra['ace_style']:
                dark = config.extra['ace_style']['slate']
            if 'default' in config.extra['ace_style']:
                light = config.extra['ace_style']['default']

        return (
            '<input type="checkbox" id="ace_palette" autocomplete="off" class="md-toggle"'
           f' data-ace-dark-mode="{ dark }" data-ace-light-mode="{ light }">'
        )



    #----------------------------------------------------------------------------



    def dump_to_js_config(self):
        """
        Create the <script> tag that will add all the CONFIG properties needed in the
        JS global config file.

        !!! WARNING !!!
            1. This method is called from the main.html template, through jinja logistic, so
               self.page HAS NO MEANING here!
            2. It is also called from devops hooks to generate the placeholders in the
               `0_config-libs.js` file, hacking the call directly on the class, with
               None in place of self.
        """

        # The Lang dump requires a slightly different logic, so it is handled separately.
        # WARNING: the below call HAS to be a static method, because self _may_ be None, here...
        with MaestroTemplates._to_dumpable_state(self):
            dump_dct         = dump_and_dumper(TO_DUMP_TO_CONFIG, self, json.dumps)
            dump_dct['lang'] = Lang.dump_as_str(self and self.lang)

        if self:
            dump_dct['pythonLibs'] = self.python_libs_in_pyodide   # Fix JS dump as names only
            dumped = MaestroTemplates._dump_script_config_for_page(dump_dct)
        else:
            dumped = MaestroTemplates._dump_config_partial_json_obj_placeholders(dump_dct)
        return dumped



    @staticmethod
    def _dump_script_config_for_page(dump_dct: Dict[str,Any]):
        """
        Create a script tag updating the CONFIG data with the global values coming from the plugin.
        """
        js_code = "\n".join([
            "if(!window.CONFIG) window.CONFIG={}",     # handle 404 -like pages (less errors...)
            *(
                f"CONFIG.{ prop }={ val }" for prop,val in dump_dct.items()
            )
        ])
        return f'<script type="text/javascript">\n{ js_code }\n</script>'

# JS module version (but causing more problems than anything else... Mostly because of mathjax):
#
#         return f'''\
# <script type="module">
# import {'{'} CONFIG {'}'} from '{ JS_CONFIG_TEMPLATES.stem }';{ "".join(dumping) }
# </script>'''


    @staticmethod
    def _dump_config_partial_json_obj_placeholders(dump_dct: Dict[str,Any]):
        dumping = [ f"\n    { prop }: { val }," for prop,val in dump_dct.items() ]
        return ''.join(dumping)



    @staticmethod
    @contextmanager
    def _to_dumpable_state(maestro: Optional['PyodideMacrosPlugin']):
        """
        If maestro is None, the dump is done to update the placeholders in 0_config-libs.js and
        nothing special needs to be done.
        Otherwise, some data of the MaestroTemplates instance need to be updated to prepare the
        actual dump, with setup + teardown logic (teardown enforced in a finally clause).
        """
        # pylint: disable=protected-access
        if not maestro:
            yield   # Used from in python_devops hooks file, to create the JS config file

        else:
            maestro.button_icons_directory = f"{ maestro.base_url }/{ ICONS_IN_TEMPLATES_DIR }"
            if maestro._dev_mode:
                TO_DUMP_TO_CONFIG.append('_dev_mode')
            try:
                yield
            finally:
                # Make absolutely sure the original state of python_libs will be restored
                if maestro._dev_mode:
                    TO_DUMP_TO_CONFIG.pop()
