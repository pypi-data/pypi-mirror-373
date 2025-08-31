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


from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, TYPE_CHECKING

from mkdocs_macros.plugin import MacrosPlugin



from ...exceptions import PmtConfigurationError, PmtMacrosDeprecationError
from ...pyodide_logger import logger
from ...tools_and_constants import PmtPyMacrosName
from ..tools.maestro_tools import ConfigExtractor
from .config_option_src import ConfigOptionSrc
from .sub_config_src import SubConfigSrc
from .macro_config_src import MacroConfigSrc
from .dumpers import AccessorsDumper


if TYPE_CHECKING:
    from ..pyodide_macros_plugin import PyodideMacrosPlugin





SRC_MACROS_CONF = dict(MacrosPlugin.config_scheme)



@dataclass
class PluginConfigSrc(SubConfigSrc):
    """
    Top level element defining the plugin's config.
    It also holds various data helpers, to access some ConfigOptionSrc, or trigger proper
    initializations of various sub elements.


    # Lifetime of this object/tree:


    * Created  _BEFORE_ mkdocs even starts running (because created when the modules are imported)

    * Lives throughout the entire build/serve.

    * Values depending on the serve/build should most likely be updated during `on_config` (lang
      stuff, deprecation reassignments, ...).
      NOTE: code updates are done through `mkdocs_hooks.on_config`, which is triggered before any
            other `on_config` method (priority 3000)

    * _NONE OF THE VALUES REPRESENT ANYTHING TRUSTABLE AT RUNTIME:_ the live config of the plugin
      must be used to get them :
        - either through env.ConfigExtractor getters,
        - or using ConfigOption.get_current_value(env), which will extract the live value
          automatically.
    """


    is_plugin_config: bool = True
    """ Override parent value """

    is_first_build: bool = True
    """ Used to apply some actions only on the first build (for serve operations). """

    __all_options: List[ConfigOptionSrc] = field(default_factory=list)
    """ List of all the ConfigOptionSrc instances. """

    __all_macros_configs: Dict[str, MacroConfigSrc] = field(default_factory=dict)
    """ Dict of all the MacroConfigSrc instances, wih the macro name as key. """


    PLUGIN_NAME: ClassVar[str] = 'pyodide_macros'


    def __post_init__(self):
        if self.name:
            raise PmtConfigurationError('PluginConfigSrc: no name argument should be given.')

        self.name = 'config'
        super().__post_init__()

        AccessorsDumper.apply(self, self.__all_options, self.__all_macros_configs)


    def validate_macros_plugin_config_once(self, env:'PyodideMacrosPlugin'):
        """
        Verify that the config of the MacroPlugin class is still the expected one.
        """
        logger.debug("Check that the original MacrosPlugin implementation didn't change.")

        current_props = {
            prop for prop,obj in self.subs_dct.items()
                 if isinstance(obj, ConfigOptionSrc) and prop!='_dev_mode'
        }

        src_macros_props     = set(SRC_MACROS_CONF)
        missing_macros_props = current_props - src_macros_props
        removed_macros_props = src_macros_props - current_props

        missing_props = "" if not missing_macros_props else ("\nDisappeared from MacrosPlugin:"
            + ''.join(f'\n\t{name}' for name in missing_macros_props)
        )
        removed_props = "" if not removed_macros_props else ("\nNew config in MacrosPlugin:"
            + ''.join(f'\n\t{name}' for name in removed_macros_props)
        )

        if not missing_props and not removed_props:
            return

        if env.ignore_macros_plugin_diffs:
            logger.error(
                "Inconsistent MacrosPlugin properties. `build.ignore_macros_plugin_diffs` "
                "is set to true."
            )
        else:
            raise PmtConfigurationError(f"""
Cannot configure PyodideMacrosPlugin: the basic configuration of MacrosPlugin changed:
{ missing_props }{ removed_props }"""
"\n\nIf you absolutely need to run mkdocs before any fix is done, you can try the option "
"`ignore_macros_plugin_diffs: true` in the `plugin_macros` section of `mkdocs.yml`, "
"but there are no guarantees the build will succeed, depending on what the changes were.\n")



    def to_config(self):
        """ Create the Config plugin's class, with strict options validation process. """

        def validate(self):
            """ Transform all warnings to errors. """
            errors, warns = src_validate(self)
            return errors + warns, []

        conf = super().to_config()
        src_validate = conf.validate
        conf.validate = validate
        return conf




    def get_plugin_path(self, option_path:str, no_deprecated:bool=False):
        """
        Validate the given `option_path` (not including "config") and return the equivalent
        `py_yaml_path`.
        """
        attrs = option_path.split('.')
        obj = self
        if no_deprecated:
            for key in attrs:
                obj = obj.subs_dct[key]
                if obj.is_deprecated:
                    raise PmtMacrosDeprecationError(f"{ option_path } is deprecated")
        else:
            for key in attrs:
                obj = obj.subs_dct[key]
        return obj.py_macros_path



    def update_lang_defaults_with_current_lang(self, env:'PyodideMacrosPlugin'):
        """
        Update The default values onc env.lang has been assigned.
        """
        assert env.lang, "env.lang should already be assigned."
        for arg in self.__all_options:
            arg.assign_lang_default_if_needed(env)



    def handle_deprecated_options_and_conversions(self, env:'PyodideMacrosPlugin'):
        """
        Reassign values set on deprecated options, and/or convert old settings to new ones.
        """

        ConfigExtractor.RAISE_DEPRECATION_ACCESS = False

        used = []
        for option in self.__all_options:
            msg = option.handle_deprecation_or_changes(env)
            if msg:
                used.append(msg)

        try:
            if self.is_first_build and used:
                self.is_first_build = False
                env.warn_unmaintained( msg=
                    "The following options should be removed or updated according to the given "
                +"information.\nIf you absolutely need to pass the build right now, you can "
                +"change the plugin option build.deprecation_level to 'warn'.\nNote these "
                +"options will be removed in near future .\n\n"
                +'\n---\n'.join(used)
                )

        finally:
            # Reactivate PMT defensive programming against deprecated properties usage:
            ConfigExtractor.RAISE_DEPRECATION_ACCESS = True




    def assign_defaults_to_args_and_macro_data(
        self, name:str, args:tuple, kwargs:dict, env:'PyodideMacrosPlugin'
    ):
        """
        If the given macro matches a macro of the theme, modify the args and/or kwargs
        to add the missing arguments, using the current global config (MaestroMeta having
        swapped the config already, if needed).
        """
        src_name, in_macros_data = PmtPyMacrosName.get_macro_data_config_for(name)

        if src_name not in self.__all_macros_configs:
            return args, kwargs

        macro_src = self.__all_macros_configs[src_name]
        new_args, new_kwargs = macro_src.add_defaults_to_macro_call(args, kwargs, env)
        if in_macros_data:
            macro_src.build_macro_data_and_store_in_env(new_args, new_kwargs, env)
        return new_args, new_kwargs




    def get_base_config_option_classname(self, _=None):
        return 'PyodideMacroConfig'
