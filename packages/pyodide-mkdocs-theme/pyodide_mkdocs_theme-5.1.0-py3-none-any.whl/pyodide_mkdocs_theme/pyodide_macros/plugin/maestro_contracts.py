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
# pylint: disable=multiple-statements



import os
from pathlib import Path
import re
from typing import ClassVar, Iterable, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict

from mkdocs.config.defaults import MkDocsConfig


from ...__version__ import __version__
from ..exceptions import PmtMacrosContractError
from ..pyodide_logger import logger
from .config import PLUGIN_CONFIG_SRC, GIT_LAB_PAGES
from .maestro_base import BaseMaestro









class MaestroContracts(BaseMaestro):
    """
    Mixin enforcing various contracts on PMT usage within mkdocs.
    """


    is_dirty: bool

    __mkdocs_checked = False
    """ Flag to check the mkdocs.yml config once only """


                                                            # pylint: disable-next=all
    def on_startup(self, command:str, dirty:bool):
        # pylint: disable=attribute-defined-outside-init
        self.is_dirty = dirty


    # Override
    def on_config(self, config:MkDocsConfig):
        logger.info("Validate PMT contracts.")

        if not self.__mkdocs_checked:
            logger.debug("Check Mkdocs-Material's plugins registration in mkdocs.yml.")
            self._check_material_prefixes_plugins_config_once(config)

            logger.debug("Check usage of the old PMT hooks html files.")
            self._check_pmt_hooks_files_usage(config)

            logger.debug("Check the PluginConfig of the original MacrosPlugin didn't change.")
            PLUGIN_CONFIG_SRC.validate_macros_plugin_config_once(self)

            self.__mkdocs_checked = True # pylint: disable=attribute-defined-outside-init

        logger.debug("Markdown and python paths names validation.")
        self._check_docs_paths_validity()

        logger.debug("Handle PMT plugin's deprecated configuration options.")
        PLUGIN_CONFIG_SRC.handle_deprecated_options_and_conversions(self)

        logger.debug("Done with contracts verifications.")
        super().on_config(config)





    def _check_docs_paths_validity(self) -> None :
        """
        Travel through all paths in the docs_dir and raises an BuildError if "special characters"
        are found in directory, py, or md file names (accepted characters are: r'[\\w.-]+' )

        NOTE: Why done here and not in `_on_files`?
                => because on_files is subject to files exclusions, and most python files SHOULD
                have been excluded from the build. So `on_files` could make more sense considering
                the kind of task, but is not technically appropriate/relevant anyway...
        """
        if self.skip_py_md_paths_names_validation:
            logger.warning("The build.skip_py_md_paths_names_validation option is activated.")
            return

        invalid_chars = re.compile(r'[^A-Za-z0-9_.-]+')
        wrongs = defaultdict(list)

        # Validation is done on the individual/current segments of the paths, so that an invalid
        # directory name is not affecting the validation of its children:
        for path,dirs,files in os.walk(self.docs_dir):

            files_to_check = [ file for file in files if re.search(r'\.(py|md)$', file)]

            for segment in dirs + files_to_check:
                invalids = frozenset(invalid_chars.findall(segment))
                if invalids:
                    wrongs[invalids].append( os.path.join(path,segment) )

        if wrongs:
            msg = ''.join(
                f"\nInvalid characters {repr(''.join(sorted(invalids)))} found in these filepaths:"
                + "".join(f"\n\t{ path }" for path in sorted(lst))
                for invalids,lst in wrongs.items()
            )
            raise PmtMacrosContractError(
                f"{ msg }\nPython and markdown files, and their parent directories' names "
                'should only contain alphanumerical characters (no accents or special chars), '
                "dots, underscores, and/or hyphens."
            )



    def _check_pmt_hooks_files_usage(self, config:MkDocsConfig):
        """
        From 3.2.0, hooks files defined in the custom_dir are still working, but should be
        replaced using the extension of `main.html` of the theme (making things easier).
        """
        custom_dir_name = getattr(config.theme, 'custom_dir', None)
        if not custom_dir_name:
            return

        cwd = Path.cwd()
        hooks: Path = cwd / custom_dir_name / 'hooks'
        if hooks.is_dir():
            files = ''.join( f"\n    { file.relative_to(cwd) }" for file in hooks.iterdir() )
            logger.warning(
                "Some PMT html hook files are present in Your custom_dir. From PMT 3.2.0, the "
                'extension of `main.html` (extending `"base_pmt.html"`) should be preferred.\n'
                'Please see this page of the documentation for more information: '
                f'{ GIT_LAB_PAGES }custom/custom_dir/\nRelated files:{ files }'
            )




    def _check_material_prefixes_plugins_config_once(self, config:MkDocsConfig):
        """
        Following 2.2.0 breaking change: material plugins' do not _need_ to be prefixed
        anymore, but the json schema validation expects non prefixed plugin names, so:

            if config.theme.name is material:
                error + how to fix it (mismatched config)
            if "material/plugin":
                error + how to fix it (pmt/...)
            if config.theme.name is something else (theme extension):
                if not "pmt/plugin":  error + how to fix it (pmt/...)


        HOW TO SPOT VALUES:
            Access plugins (dict):  `config.plugins`

                Containing keys (behavior of material's plugins only!):
                * `{theme.name}/search`  <-  `mkdocs.yml:plugins: - search`
                * `{some}/search`        <-  `mkdocs.yml:plugins: - {some}/search`
                => The theme prefix IS ALWAYS THERE in the config!
        """
        errors       = []
        material     = 'material'
        pmt          = 'pyodide-mkdocs-theme'
        theme        = config.theme.name
        is_extension = theme and theme not in (material, pmt, None)
        registered   = RegisteredPlugin.convert(config.plugins)


        if not theme or theme==material:
            errors.append(
                f"The { pmt }'s plugin is registered, so `theme.name` should be set "
                f"to `{ pmt }` instead of `{ theme }`."
            )

        features = config.theme.get('features', ())
        if 'navigation.instant' in features:
            errors.append(
                "Remove `navigation.instant` from `mkdocs.yml:theme.features`. "
                "It is not compatible with the pyodide-mkdocs-theme."
            )

        for plug in registered:
            if plug.prefix != theme:
                errors.append(
                    f"The `{ plug.qualname }` plugin should be registered " + (
                        f"with `pyodide-mkdocs-theme/{ plug.name }`."
                            if is_extension else
                        f"using `{ plug.name }` only{ ' (PMT >= 2.2.0)' * (theme==pmt) }."
                    )
                )

        if errors:
            str_errors = ''.join(map( '\n  {}'.format, errors ))
            raise PmtMacrosContractError(
                f"Invalid theme or material's plugins configuration(s):{ str_errors }"
            )









@dataclass
class RegisteredPlugin:
    """
    Represents an mkdocs plugin name, with information about how it's built.
    """

    qualname: str
    """ Fully qualified name: 'pyodide-mkdocs-theme/search' """

    name: str
    """ Plugin's name: 'search' """

    prefix: Optional[str]
    """ Plugin's prefix: 'pyodide-mkdocs-theme' or None """



    MATERIAL_PLUGINS: ClassVar[Set[str]] = set('''
        blog group info offline privacy search social tags
    '''.split())
    """
    All existing mkdocs-material plugins.
    See: https://github.com/squidfunk/mkdocs-material/tree/master/src/plugins
    """


    @classmethod
    def convert(cls, plugins:Iterable[str]) -> List['RegisteredPlugin'] :
        pattern = re.compile(
            f"(?:(?P<prefix>\\w*)/)?(?P<name>{ '|'.join(cls.MATERIAL_PLUGINS) })"
        )
        registered = [
            RegisteredPlugin(m[0], m['name'], m['prefix'])
                for m in map(pattern.fullmatch, plugins)
                if m
        ]
        return registered
