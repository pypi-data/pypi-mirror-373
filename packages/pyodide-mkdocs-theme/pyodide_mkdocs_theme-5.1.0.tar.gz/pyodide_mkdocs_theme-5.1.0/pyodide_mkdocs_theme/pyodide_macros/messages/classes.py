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


import re
import json
from argparse import Namespace
from typing import Any, ClassVar, Dict, Optional, Type, Union, TYPE_CHECKING
from dataclasses import dataclass, fields


from ..exceptions import PmtCustomMessagesError, PmtInternalError
from ..plugin.tools.maestro_tools import dump_and_dumper

if TYPE_CHECKING:
    from ..plugin import PyodideMacrosPlugin
    from .fr_lang import Lang



Tr       = Union['Msg', 'MsgPlural', 'Tip', 'TestsToken']
LangProp = str
TMP_PATTERN  = re.compile('')       # done this way for linting and mkdocstrings... :/





@dataclass
class JsDumper:
    """ Base class to automatically transfer "lang" messages from python to JS """
    # pylint: disable=no-member,missing-function-docstring


    ENV_EXTRACTIONS: ClassVar[Dict[str,Any]] = None
    """
    Used to register messages that should go at some point from the Maestro/plugin object
    to the content of some Lang message before it is dumped to JS.
    """

    def __str__(self):
        return self.msg

    def dump_as_dct(self):
        dct = {
            field.name: v  for field in fields(self)
                           if (v := self.get_prop(field.name)) is not None
        }
        return dct


    def get_prop(self,prop):
        return str(self) if prop=='msg' else getattr(self, prop, None)


    @staticmethod
    def register_env_with_lang(env:'PyodideMacrosPlugin'):
        JsDumper.ENV_EXTRACTIONS = {
            name: getattr(env,name) for name in "site_name".split()
        }
        JsDumper.ENV_EXTRACTIONS['tests'] = str(env.lang.tests) # pylint: disable=unsupported-assignment-operation




@dataclass
class Message(JsDumper):
    """
    Intermediate class so that Msg and MsgPlural are sharing a specific class in their mro.
    """


@dataclass
class Msg(Message):
    """
    A simple message to display in the application.

    Parameters:
        msg:    Message to use
        format: Formatting to use in the terminal. See lower.
    """
    msg: str
    format: Optional[str] = None





@dataclass
class MsgPlural(Message):
    """
    A message that could be used in singular or plural version at runtime.

    Parameters:
        msg:    Message to use
        plural: If not given, `msg+"s"` is used as plural.
        format: Formatting to use in the terminal. See lower.
    """
    msg:    str
    plural: str = ''
    format: Optional[str] = None

    def __post_init__(self):
        self.plural = self.plural or self.msg+'s'

    def one_or_many(self, many:bool):
        return self.plural if many else self.msg





@dataclass
class TestsToken(JsDumper):
    """
    Specific delimiter used to separate the user's code from the public tests in an editor.
    Leading and trailing new lines used here will reflect on the editor content and will
    match the number of additional empty lines before or after the token itself.

    Because this token is also be converted to a regex used in various places, it has to
    follow some conventions. ___Ignoring leading and trailing new lines:___

    - The string must begin with `#`.
    - The string must not contain new line characters anymore.
    - Ignoring inner spaces, the token string must be at least 6 characters long.

    Parameters:
        msg:  Separator to use (with leading and trailing new lines).

    Raises:
        PMTPmtMkdocsLegacyError: If one of the above conditions is not fulfilled.
    """
    msg: str
    as_pattern: re.Pattern = TMP_PATTERN    # Overridden in post_init. Needed for types in 3.8

    def __post_init__(self):
        self.msg = f"\n{ self.msg }\n"
        s = self.msg.strip()
        short = s.replace(' ','').lower()

        if not s.startswith('#'):
            raise PmtCustomMessagesError(
                "The public tests token must start with '#'"
            )
        if '\n' in s:
            raise PmtCustomMessagesError(
                "The public tests token should use a single line"
                " (ignoring leading or trailing new lines)"
            )
        if short=='#test' or len(short)<6:
            raise PmtCustomMessagesError(
                "The public tests token is too short/simple and could cause false positives."
                " Use at least something like '# Tests', or something longer."
            )

        pattern = re.sub(r'\s+', r"\\s*", s)
        self.as_pattern = re.compile('^'+pattern, flags=re.I)

    def __str__(self):
        return self.msg.strip()

    def get_prop(self,prop):
        return (
            self.as_pattern.pattern if prop=='as_pattern' else
            self.msg if prop=='msg' else
            super().get_prop(prop)
        )




@dataclass
class Tip(JsDumper):
    """
    Data for tooltips.

    Parameters:
        em:     Width of the tooltip element, in em units (if 0, use automatic width).
        msg:    Tooltip message.
        kbd:    Keyboard shortcut (as "Ctrl+I", for example). Informational only (no
                impact on the behaviors)

    If a `kbd` combination is present, it will be automatically added in a new line
    after the tooltip `msg`.
    """
    em: int         # Width, in em. If 0, use automatic width
    msg: str        # tooltip message
    kbd: str = ""   # ex: "Ctrl+I" / WARNING: DO NOT MODIFY DEFAULTS!

    def __str__(self):
        msg = self.msg.format(**self.ENV_EXTRACTIONS)       # pylint: disable=not-a-mapping
        if self.kbd:
            kbd = re.sub(r"(\w+)", r"<kbd>\1</kbd>", self.kbd)
            msg = f"{ msg }<br>({ kbd })"
        return msg












class LangBase(Namespace):
    """ Generic behaviors for Lang classes """


    __LANG_CLASSES: ClassVar[ Dict[str,Type['Lang']] ] = {}
    """
    Automatically registered subclasses.
    """

    def __init_subclass__(cls) -> None:
        if not cls.__name__.startswith('Lang'):
            raise PmtInternalError(
                "All LangBase subclasses should be named `LangX`, starting with `Lang`, "
                f"but found: { cls.__name__ }"
            )
        name = cls.__name__[4:].lower() or 'fr'
        LangBase.__LANG_CLASSES[name] = cls
        super().__init_subclass__()



    @staticmethod
    def get_langs_dct():
        """
        Return a fresh dict of fresh Lang instances (to make sure no side effects are possible,
        especially because of overloads).
        """
        dct = { name: kls() for name,kls in LangBase.__LANG_CLASSES.items() }
        return dct



    def overload(self, dct: Dict[LangProp,Tr]):
        """
        Overloads the defaults with any available user config data.
        This has to be done at macro registration time (= in a `define_env(env)` function).

        @throws BuildError if the name isn't formatted as expected: LangXx
        """
        for k,v in dct.items():
            current = getattr(self,k, None)

            if current is None:
                raise PmtCustomMessagesError(f"Invalid Lang property: {k!r}")
            if not isinstance(v, current.__class__):
                kls = current.__class__.__name__
                raise PmtCustomMessagesError(f"Invalid Translation type: {v!r} should be an instance of {kls}")
            setattr(self,k,v)



    @classmethod
    def dump_as_str(cls, obj=None):
        """
        Create a complete json object with all the string representations of all the messages.
        - Takes potential overloads in consideration
        - WARNING: js dumps are simple str conversions, so far, so some messages might be
                   missing some information... (specifically, plurals)
        - If obj is None, use null for all values.
        """
        #pylint: disable=no-member
        dct = dump_and_dumper(cls.__annotations__, obj, lambda v: v.dump_as_dct() if v else "null")

        if obj:
            return json.dumps(dct)
        return json.dumps(dct, indent=8).replace('"','')
