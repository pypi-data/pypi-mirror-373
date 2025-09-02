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
# pylint: disable=line-too-long


import json
from typing import Dict, FrozenSet, List, TYPE_CHECKING, Optional, Set, Tuple

from mkdocs.structure.pages import Page

from ..tools_and_constants import PageUrl
from ..plugin.tools.pages_and_macros_py_configs import PageConfiguration
from .deps_class import Block, Cdn, Css, Dep, DepKind

if TYPE_CHECKING:
    from ..plugin.pyodide_macros_plugin import PyodideMacrosPlugin





Template = MethodExtraFormatArg = str
BlocksTemplatesData = Dict[Block, Tuple[Template, Tuple[MethodExtraFormatArg, ...]]]



class HtmlDependencies:

    __DEPS_IN_ORDER: List[Dep] = Dep.auto_ordering()
    __URL_TO_TEMPLATE_CACHE: Dict[PageUrl, BlocksTemplatesData] = {}
    __IMPORT_MAP = ""
    __DEP_KINDS_TO_POOL_NAME: Dict[PageUrl, List[str]]


    @classmethod
    def build_scripts_pages_templates(
        cls,
        env:'PyodideMacrosPlugin',
        pages_configs:Dict[PageUrl, PageConfiguration]
    ):
        """
        Build all the templates needed for any page of the documentation, caching the different
        versions of them.
        """
        needs_to_templates: Dict[FrozenSet[DepKind], BlocksTemplatesData] = {}
        base_needs_to_all_needs: Dict[FrozenSet[DepKind], Set[DepKind]] = {}

        # (covers the weird case where page is None... Might also become useful one day, if ever
        # pages_configs do not reference anymore all the possible pages of the documentation.
        # It currently works because of MaestroMacros.on_page_markdown, where the
        # `if self.does_current_page_need(DepKind.mermaid)` actually inserts all pages on the fly,
        # even when they don't contain macros calls...).
        default = PageConfiguration(env)
        default.needs.add(DepKind.always)
        all_kinds_of_pages = {None: default, **pages_configs}

        for url, page_config in all_kinds_of_pages.items():

            base_needs = frozenset(page_config.needs)
            if base_needs not in needs_to_templates:

                # Build the complete set of dependencies:
                all_needs = set(base_needs)
                all_needs.add(DepKind.always)
                for need in base_needs:
                    DepKind.resolve_deps_needs(need, all_needs)
                base_needs_to_all_needs[base_needs] = all_needs

                # Separate the wheat from the chaff... :p
                blocks_dct: Dict[Block,List[Dep]] = {b:[] for b in Block.get_blocks()}
                for dep in cls.__DEPS_IN_ORDER:
                    if dep.kind in all_needs:
                        blocks_dct[dep.block].append(dep)

                # Mutate the wheat to templates and extra method calls needed:
                for block, lst_deps in blocks_dct.items():
                    extras_dump_calls = []
                    template = '\n'.join( dep.to_template(extras_dump_calls) for dep in lst_deps )
                    blocks_dct[block] = template, tuple(extras_dump_calls)


                # Register templates and cbks
                needs_to_templates[base_needs] = blocks_dct

            cls.__URL_TO_TEMPLATE_CACHE[url] = needs_to_templates[base_needs]

            # Reassign the page needs with the complete set so that the proper info is
            # available "later" if needed.
            page_config.needs = base_needs_to_all_needs[base_needs]


    @classmethod
    def render_tags_for(cls, block:Block, env:'PyodideMacrosPlugin', cache_key:Optional[str]=...):
        """
        Build all the `<script>` html code to include all the required dependencies
        in the current page.
        """
        # None IS a valid key in the templates cache, so need to use ellipsis for default calls
        # without cache_key argument:
        if cache_key is ...:
            cache_key = env.page and env.page.url
        template, extras_dump_calls = cls.__URL_TO_TEMPLATE_CACHE[cache_key][block]
        extras = { method: getattr(env, method)() for method in extras_dump_calls}
        html   = template.format(base_url=env.base_url, **extras)
        return html



    @classmethod
    def build_import_map_template(cls):
        """ Build the importmap script template (done in on_env hook). """
        imports = {
            name: target
                for dep in cls.__DEPS_IN_ORDER
                for name,target in dep.gen_import_map()
        }
        cls.__IMPORT_MAP = f'''
<script type="importmap">{'{'}"imports": { json.dumps(imports) }{'}'}</script>
'''

    @classmethod
    def render_import_map(cls, env:'PyodideMacrosPlugin', page:Optional[Page]):
        """
        Build the importmap script for the current page (used through jinja routines, around
        `on_page_context`).
        """
        return cls.__IMPORT_MAP.replace("{base_url}", env.base_url if page else '.')




    @classmethod
    def build_overlord_data(cls):
        cls.__DEP_KINDS_TO_POOL_NAME = {
            dep.kind: dep.pool_requirement
                for dep in cls.__DEPS_IN_ORDER if dep.pool_requirement
        }


    @classmethod
    def get_overlord_classes(cls, page_configs: PageConfiguration):
        overlord_classes = [
            cls.__DEP_KINDS_TO_POOL_NAME[dep_kind]
                for dep_kind in page_configs.needs
                if dep_kind in cls.__DEP_KINDS_TO_POOL_NAME
        ]
        return overlord_classes


    #---------------------------------------------------------
    # NOTE: some scripts are loaded the "sync" way (text/javascript) for the following reasons:
    #   1) Makes backward compatibility with previous hooks and mathjax overrides easier
    #   2) Getting mathjax to work with the config loaded async from a module is a nightmare...
    #      ('couldn't find the proper way to get it to work...)
    #   3) Easier to transmit data from mkdocs through inlined scripts if the CONFIG parts are
    #      actually loaded sync (this avoids the need for yet another global async flag...)


    lodash         = Cdn(Block.libs, DepKind.always, "https://cdn.jsdelivr.net/npm/lodash@4.17.20/lodash.min.js")
    jQuery         = Cdn(Block.libs, DepKind.always, "https://cdn.jsdelivr.net/npm/jquery@3.7.1")

    jQuery_css     = Css(Block.libs, DepKind.always, "https://cdn.jsdelivr.net/npm/jquery.terminal@2.43.1/css/jquery.terminal.min.css")
    awesome_font   = Css(Block.libs, DepKind.always, {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css",
        "integrity": "sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A==",
    })

    jQterm         = Cdn(Block.libs, DepKind.term,   "https://cdn.jsdelivr.net/npm/jquery.terminal@2.43.1/js/jquery.terminal.min.js")
    ace            = Cdn(Block.libs, DepKind.ide, {
        'src': "https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ace.min.js",
        'integrity': "sha512-GQpIYSKNIPIC763JKTNALj+t18/nfLdzw5gITgFGa31aK/4NmjyPKsfqrjh7CuzpJaG3nqEleeVcWUhHad9Axg==",
    })
    ace_tools      = Cdn(Block.libs, DepKind.ide, {
        'src': "https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ext-language_tools.min.js",
        'integrity': "sha512-iK7yTkCkv7MbFwTqRgHTbmIqoiiLq6BsyNjymnFyB5a7pEQwYThj9QIgqBy9+XPPwj7+hAEHyR2npOHL1bz4Qg==",
    })
    pyodide        = Cdn(Block.libs, DepKind.pyodide, "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js")

    #vvvvvvvvvvvvvvv
    # GENERATED-libs
    config          = Cdn(Block.libs, DepKind.always, "{base_url}/js-libs/0-config.js", type="text/javascript", extra_dump="dump_to_js_config")
    subscriber      = Cdn(Block.libs, DepKind.always, "{base_url}/js-libs/0-legacy-subscriber.js", type="text/javascript")
    functools       = Cdn(Block.libs, DepKind.always, "{base_url}/js-libs/functools.js", type="module")
    jsLogger        = Cdn(Block.libs, DepKind.always, "{base_url}/js-libs/jsLogger.js", type="module")
    mathjax         = Cdn(Block.libs, DepKind.always, "{base_url}/js-libs/mathjax-libs.js", type="text/javascript")
    process_and_gui = Cdn(Block.libs, DepKind.always, "{base_url}/js-libs/process_and_gui.js", type="module")
    generic         = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/0-generic.css")
    header          = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/btns-header.css")
    history         = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/history.css")
    hourglass       = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/hourglass.css")
    ide             = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/ide.css")
    qcm             = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/qcm.css")
    terminal        = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/terminal.css")
    testing         = Css(Block.libs, DepKind.always, "{base_url}/pyodide-css/testing.css")
    # GENERATED-libs
    #^^^^^^^^^^^^^^^

    # Always _after_ the js mathjax-libs.js file (SYNC!)
    mathjax_tex    = Cdn(Block.libs, DepKind.always, "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js")


    #---------------------------------------------------


    #vvvvvvvvvvvvvvvv
    # GENERATED-pages
    snippets        = Cdn(Block.content, DepKind.pyodide,   "{base_url}/js-per-pages/0-generic-python-snippets-pyodide.js", type="module")
    error_logs      = Cdn(Block.content, DepKind.pyodide,   "{base_url}/js-per-pages/1-error_logs-pyodide.js", type="module")
    install         = Cdn(Block.content, DepKind.pyodide,   "{base_url}/js-per-pages/1-packagesInstaller-install-pyodide.js", type="module")
    runtime         = Cdn(Block.content, DepKind.pyodide,   "{base_url}/js-per-pages/1-runtimeManager-runtime-pyodide.js", type="module")
    runnersManager  = Cdn(Block.content, DepKind.runners,   "{base_url}/js-per-pages/2-0-runnersManager-runners.js", type="module", pool="GlobalRunnersManager")
    runner          = Cdn(Block.content, DepKind.pyodide,   "{base_url}/js-per-pages/2-pyodideSectionsRunner-runner-pyodide.js", type="module")
    btnRunner       = Cdn(Block.content, DepKind.py_btn,    "{base_url}/js-per-pages/3-btnRunner-py_btn.js", type="module", pool="PyBtn")
    terminalRunner  = Cdn(Block.content, DepKind.term,      "{base_url}/js-per-pages/3-terminalRunner-term.js", type="module", pool="Terminal")
    idesManager     = Cdn(Block.content, DepKind.ide,       "{base_url}/js-per-pages/4-0-idesManager-ide.js", type="module")
    ideLogistic     = Cdn(Block.content, DepKind.ide,       "{base_url}/js-per-pages/4-ideLogistic-ide.js", type="module")
    ideRunner       = Cdn(Block.content, DepKind.ide,       "{base_url}/js-per-pages/4-ideRunner-ide.js", type="module", pool="Ide")
    ideTester       = Cdn(Block.content, DepKind.ides_test, "{base_url}/js-per-pages/5-ideTester-ides_test.js", type="module", pool="IdeTester")
    init            = Cdn(Block.content, DepKind.playground, "{base_url}/js-per-pages/6-2-init-playground.js", type="module")
    idePlayground   = Cdn(Block.content, DepKind.playground, "{base_url}/js-per-pages/6-idePlayground-playground.js", type="module", pool="IdePlayground")
    qcms            = Cdn(Block.content, DepKind.qcm,       "{base_url}/js-per-pages/qcms-qcm.js", type="module", pool="Qcm")
    start           = Cdn(Block.content, DepKind.pyodide,   "{base_url}/js-per-pages/start-pyodide.js", type="module")
    # GENERATED-pages
    #^^^^^^^^^^^^^^^^


    #---------------------------------------------------


    #vvvvvvvvvvvvvvvvvv
    # GENERATED-scripts
    overlord        = Cdn(Block.scripts, DepKind.always, "{base_url}/js-scripts/overlord.js", type="module")
    subscriptions   = Cdn(Block.scripts, DepKind.always, "{base_url}/js-scripts/subscriptions.js", type="module")
    # GENERATED-scripts
    #^^^^^^^^^^^^^^^^^^
