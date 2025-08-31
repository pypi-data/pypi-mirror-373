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
from textwrap import dedent
from typing import Tuple, TYPE_CHECKING

from mkdocs.exceptions import BuildError


from ...exceptions import PmtInternalError, PmtMacrosInvalidArgumentError
from .sub_config_src import SubConfigSrc, ConfigOptionSrc
from ..tools import macros_data

if TYPE_CHECKING:
    from ..pyodide_macros_plugin import PyodideMacrosPlugin












@dataclass
class BaseMacroConfigSrc(SubConfigSrc):

    is_macro: bool = True
    """ Override parent value """

    force_kwargs_index: int = None     # Failure if not properly computed
    """
    Index of the first kwarg in the macro call (= where to insert a `*,` when
    building the signature).
    """


    def __post_init__(self):

        super().__post_init__()
        elements: Tuple['ConfigOptionSrc'] = self.elements      # linting purpose

        positionals = tuple(
            arg for arg in elements if not arg.is_config and arg.is_positional()
        )
        start_args = elements[:len(positionals)]
        if start_args != positionals:
            raise PmtMacrosInvalidArgumentError(dedent(f"""
                Positional arguments in { self } definition should come first:
                    Positional args found: {', '.join(arg.name for arg in positionals)}
                    Order of declaration:  {', '.join(arg.name for arg in elements)}
            """))

        if positionals and not positionals[-1].is_varargs and len(positionals)!=len(elements):
            self.force_kwargs_index = len(positionals)



    def as_docs_table(self):
        """
        Converts all arguments to a 3 columns table (data rows only!):  name + type + help.
        No indentation logic is added here.
        """
        return '\n'.join(
            arg.as_table_row(False) for arg in self.subs_dct.values() if arg.is_in_args_tables
        )


    def signature_for_docs(self):
        """
        Converts the SubConfigSrc to a python signature for the docs.
        """
        args = [arg for arg in self.subs_dct.values() if arg.is_in_signature]
        size = max( arg.doc_name_type_min_length for arg in args )
        lst  = [ arg.signature(size) for arg in args ]

        if self.force_kwargs_index is not None:
            lst.insert(self.force_kwargs_index, "\n    *,")

        return f"""
```python
{ '{{' } { self.name }({ ''.join(lst) }
) { '}}' }
```
"""



    def add_defaults_to_macro_call(self, args:tuple, kwargs:dict, env:'PyodideMacrosPlugin'):
        """
        Modify the args and/or kwargs to add the missing arguments, using the current global
        config (MaestroMeta having swapped the config already, if needed).
        """
        for arg_name, arg in self.subs_dct.items():

            if not arg.is_in_config:                            # not handled
                continue

            is_positional = arg.is_positional()
            if is_positional and arg.index >= len(args):        # Add missing args or varargs
                current_default = arg.get_current_value(env)
                args += tuple(current_default) if arg.is_varargs else (current_default,)

            elif not is_positional and arg_name not in kwargs:  # Add missing kwargs
                kwargs[arg_name] = arg.get_current_value(env)

        return args, kwargs







class MacroConfigSrcToArgsData(BaseMacroConfigSrc):


    _cached_macro_data_class_names: Tuple[str,str] = None

    def get_macro_data_class_names(self):
        """
        Rebuild the names of the classes needed to build the kind of MacroData related to the
        current object (to build the python code).
        """
        if not self._cached_macro_data_class_names:
            kls_tail_name       = self.name.capitalize() if self.name.islower() else self.name
            macro_data_kls_name = f'MacroData{ kls_tail_name }'
            macro_args_kls_name = macro_data_kls_name.replace('Macro', 'MacroArgs')

            self._cached_macro_data_class_names = macro_data_kls_name, macro_args_kls_name

        return self._cached_macro_data_class_names


    def build_macro_data_and_store_in_env(self, args:tuple, kwargs:dict, env:'PyodideMacrosPlugin'):
        """
        Convert the given args and kwargs (related to the current macro config source, for the
        current macro call at runtime) to the equivalent MacroData object.
        """
        args_dct   = self._args_to_dict(args, kwargs, env)
        kls_name,_ = self.get_macro_data_class_names()
        data_kls   = getattr(macros_data, kls_name)

        macro_obj: macros_data.MacroData = data_kls(self.name, args_dct)
        env.push_macro_data(macro_obj)



    def _args_to_dict(self, src_args:tuple, kwargs:dict, env:'PyodideMacrosPlugin'):
        """
        Regroup all the arguments with the kwargs, retrieving the actual argument name as key.
        """
        dct = {}
        kwargs = kwargs.copy()
        args: list = [*reversed(src_args)]

        for elt in self.elements:
            if elt.is_varargs:
                args, value = [], tuple(reversed(args))
            elif elt.is_positional():
                value = args.pop()
            elif not elt.is_in_config and elt.name not in kwargs:
                continue
            else:
                value = kwargs.pop(elt.name)

            dct[elt.name] = value

        # Skip validations in production (relying on the IdeManager validation only), and
        # let SIZE go through, to use the warn_unmaintained logistic (proper error message)
        if env._dev_mode and (args or kwargs and 'SIZE' not in kwargs):
            raise PmtInternalError(
                f"Couldn't generate a valid argument dict for the macro {'{{'}{self.name}(...)"
                f"{'}}'}. Remaining:\n\targs: { args }\n\tkwargs: { kwargs }\n{ env.log() }"
            )

        return dct







@dataclass
class MacroConfigSrc(
    MacroConfigSrcToArgsData,
    BaseMacroConfigSrc,
):
    """
    Specific class that represents the config of a macro call, with it's arguments and
    specific behaviors (see pmt_macros, for example).
    """

    long_accessor: bool = True




@dataclass
class MultiQcmConfigSrc(MacroConfigSrc):
    """ Special class handling the json files data for the multi_qcm macro """


    def add_defaults_to_macro_call(
        self, args:tuple, kwargs:dict, env:'PyodideMacrosPlugin'
    ):
        if len(args)==1 and isinstance(args[0],str):
            qcm_file = args[0]
            if not args[0].endswith('.json'):
                qcm_file += '.json'
            args, kwargs = self._extract_json_qcm(qcm_file, kwargs, env)
        return super().add_defaults_to_macro_call(args, kwargs, env)



    def _extract_json_qcm(self, file:str, kwargs:dict, env:'PyodideMacrosPlugin'):

        target = env.get_sibling_of_current_page(file)
        if not target or not target.is_file() or target.suffix!='.json':
            raise PmtMacrosInvalidArgumentError(
                f"Couldn't find the json file \"{file}\" for the `multi_qcm` macro call.{ env.file_location(all_in=True) }"
            )

        dct: dict = json.loads(target.read_text(encoding='utf-8'))
        args = dct.pop('questions', None)

        if args is None:
            raise PmtMacrosInvalidArgumentError(
                f"No questions array found in json data, for `multi_qcm`.{ env.file_location(all_in=True) }"
            )

        for k,v in dct.items():
            if k not in kwargs:
                kwargs[k] = v

        return args, kwargs
