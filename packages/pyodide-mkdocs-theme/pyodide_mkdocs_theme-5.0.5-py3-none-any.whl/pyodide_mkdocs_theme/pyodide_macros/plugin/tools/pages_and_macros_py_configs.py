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
# pylint: disable=multiple-statements, line-too-long



import json
from textwrap import dedent
from typing import Dict, List, Optional, Set, Tuple, Type, TYPE_CHECKING
from itertools import starmap
from dataclasses import dataclass, fields
from collections import defaultdict
from math import inf


from ...exceptions import PmtInternalError, PmtMacrosInvalidArgumentError
from ... import html_builder as Html
from ...tools_and_constants import DebugConfig, EditorName
from ...parsing import compress_LZW
from ...html_dependencies.deps_class import DepKind
from .maestro_tools import AutoCounter


if TYPE_CHECKING:
    from ..pyodide_macros_plugin import PyodideMacrosPlugin
    from ...macros.ide_ide import Ide










@dataclass
class MacroPyConfig:
    """
    Configuration of one IDE in one page of the documentation. Convertible to JS, to define the
    global variable specific to each page.

    Always instantiated without arguments, and items are updated when needed.
    """
    # WARNING: this declaration is used to generate the getters in the PyodideSectionRunner class.

    py_name:      str = ""          # name to use for downloaded file
    env_content:  str = ""          # HDR part of "exo.py"
    env_term_content:  str = ""     # HDR part for terminal commands only
    user_content: str = ""          # Non-HDR part of "exo.py" (initial code)
    corr_content: str = ""          # not exported to JS!
    public_tests: str = ""          # test part of "exo.py" (initial code)
    secret_tests: str = ""          # Content of "exo_test.py" (validation tests)
    post_term_content: str = ""     # Content to run after for terminal commands only
    post_content: str = ""          # Content to run after executions are done

    excluded: List[str] = None      # List of forbidden instructions (functions or packages)
    excluded_methods: List[str] = None # List of forbidden methods accesses
    excluded_kws: List[str] = None  # List of forbidden python keywords
    python_libs: List[str] = None
    pypi_white: List[str] = None
    rec_limit: int = None           # recursion depth to use at runtime, if defined (-1 otherwise).
    white_list: List[str] = None    # White list of packages to preload at runtime
    auto_run: bool = None           # Auto execute the python content on page load.
    run_group: int = None           # -1 if skipped or not involved in a sequential run, an int otherwise
    order_in_group: int = None      # -1 if skipped or not involved in a sequential run, 0 if priority, a unique int otherwise.
    seq_run: str = None             # '', 'all', 'dirty' (added as IDE property to avoid the user accessing it through CONFIG)

    profile: str = None             # IDE execution profile ("no_valid", "no_reveal" or "")
    attempts_left: int = None       # Not overwriting this means there is no counter displayed
    auto_log_assert: bool = None    # Build automatically missing assertion messages during validations
    corr_rems_mask: int = None      # Bit mask:   has_corr=corr_rems_mask&1 ; has_rem=corr_rems_mask&2
    has_check_btn: bool = None      # Store the info about the Ide having its check button visible or not
    has_corr_btn: bool = None       # Store the info about the Ide having its corr button visible or not
    has_reveal_btn: bool = None     # Store the info about the Ide having its reveal button visible or not
    has_counter: bool = None        # Store the info about the Ide having its counter of attempts visible or not
    is_vert: bool = None            # IDEv if true, IDE otherwise.
    max_ide_lines: int = None       # Max number of lines for the ACE editor div
    min_ide_lines: int = None       # Min number of lines for the ACE editor div
    decrease_attempts_on_user_code_failure: str = None    # when errors before entering the actual validation
    deactivate_stdout_for_secrets: bool = None
    show_only_assertion_errors_for_secrets: bool = None
    src_hash: str = None            # Hash code of code+TestToken+tests
    std_key: str = None             # To allow the use of terminal_message during validations
    two_cols: bool = None           # automatically goes int split screen mode if true
    export: bool = None             # Global archive related

    prefill_term: str = None        # Command to insert in the terminal after it's startup.
    stdout_cut_off: int = None      # max number of lines displayed at once in a jQuery terminal
    cut_feedback: bool = None       # shorten stdout/err or not



    def dump_to_js_code(self):
        """
        Convert the current MacroPyConfig object to a valid JSON string representation.

        Properties whose the value is None are skipped!
        """
        # pylint: disable=no-member

        content = ', '.join(
            f'"{k}": { typ }'
            for k,typ in starmap(self._convert, self.__class__.__annotations__.items())
            if typ is not None
        )
        return f"{ '{' }{ content }{ '}' }"



    def _convert(self, prop:str, typ:Type):
        """
        Convert the current python value to the equivalent "code representation" for a JS file.

        @prop:      property name to convert
        @typ:       type (annotation) of the property
        @returns:   Tuple[str, None|Any]

        NOTE: Infinity is not part of JSON specs, so use "Infinity" as string instead, then
              convert back in JS.
        """
        val = getattr(self, prop)

        if   val is None:         out = None if prop!='pypi_white' else "null"
        elif val == inf:          out = '"Infinity"'
        elif prop in IS_LIST:     out = json.dumps(val or [])
        elif typ in CONVERTIBLES: out = json.dumps(val)

        else: raise NotImplementedError(
            f"In {self.__class__.__name__} ({prop=}): conversion for {typ} is not implemented"
        )
        return prop, out



IS_LIST:  Set[str] = [
    f.name for f in fields(MacroPyConfig)
           if f.type is list or getattr(f.type, '_name', None)=='List'
]
""" Properties that should be lists """


CONVERTIBLES: Tuple[Type, ...] = (bool, int, str, float)
""" Basic types that are convertible to JSON """












class PageConfiguration(Dict[EditorName,MacroPyConfig]):
    """
    Augmented dictionary.
    Represent the Configuration of the JS scripts that need to be inserted in each page of the
    documentation, and the logistic to create the corresponding html code.

    Also keeps track of the grouping configuration data for sequential runs of the various
    elements in the page.
    """


    def __init__(self, env):
        super().__init__()
        self.env: PyodideMacrosPlugin = env
        self.needs: Set[DepKind] = set()        # Transformed to frozenset after on_env

        self.group_cnt = -1                     # Incremented first => actually starts at 0, this way
        self.last_group_id: str = None          # Allows to spot some groups misconfigurations
        self.group_idx_dct: Dict[str, int] = {}
        """
        Per page dict of page order values, allowing to know what elements/macros are alternatives
        of each others, and/or in what order everything is supposed to be executed in the page
        (for sequential executions).
        """

        self.group_dct = defaultdict(set)
        """ Secondary dict, to know the number of the elements in one group. """


    def has_need(self, need:DepKind):
        return need in self.needs


    def build_page_script_tag_with_ides_configs_mermaid_and_pool_data(
        self, overlord_classes:List[str]
    ):

        json_ide_configs = '{' + ', '.join(
            f'"{ editor_name }": { ide_conf.dump_to_js_code() }'
            for editor_name, ide_conf in self.items()
        ) + '}'

        if DebugConfig.check_global_json_dump:
            try:
                json.loads(json_ide_configs)
            except json.JSONDecodeError as e:
                raise PmtInternalError(
                    f"Invalid generated json object:\n{json_ide_configs!r}"
                ) from e

        js_data = json_ide_configs
        if self.env.encrypted_js_data:
            js_data = repr(compress_LZW(json_ide_configs, self.env))
            # Dumped needed as string code, so repr needed.

        need_mermaid = self.has_need(DepKind.mermaid)
        script_tag = Html.script(
            dedent(f"""
                CONFIG.needMermaid = { json.dumps(need_mermaid) };
                CONFIG.overlordClasses = { json.dumps(overlord_classes) };
                globalThis.PAGE_IDES_CONFIG = { js_data }
                """),
            type="text/javascript"
        )
        return script_tag


    def get_run_group_data(
        self,
        in_sequential_run: bool,
        has_priority: bool,
        group_id: Optional[str] = None,
    ) -> List[int] :
        """
        Returns the needed "page_order" values:

        - the number of the group for this macro/running element (or skip).
        - the number of the element in the current group (or skip).


        # Rationals

        * Macros are executed strictly in order, in the md content, which allow to assign
          unambiguously a global order fo all the running elements.
        * @group_id (coming from the `RUN_GROUP` argument) allows to tell what elements are
          in the same group, or what elements to "SKIP".
        * Inside a group, the user need a way to pick the element that has priority over
          the others, when nothing has been run in one group yet. This is then "overridden"
          by the users actions (when they are using another element in the group).
        * By default, any new element is alone in its own group.


        # Implementation

        | RUN_GROUP | Returned |
        |-|-|
        | `"SKIP"` | `[-1, -1]` |
        | `None`   | `[n_groups+=1, 1]` if the page is using sequential run, or `[-1,-1]` |
        | `str`    | `[matching_n_groups, n_in_group+=1]` with `n_in_group > 0` |
        | `fr"*?{ str }*?` | `[matching_n_groups, 0]` (with at least one "star") |

        - If group_id is None: increment by one and return [page_order, layer_order].
        - If group_id is not None and is in the dict of page_counts, return
          [stored value, in_group_order+=1].
        - Otherwise, increment by one, store, and return [value,0].
        - If @group_id is a string starting or ending with '*', it will be run in priority
          over the others. This is done by assigning 0 for the layer/"in group" order.
        - "SKIP*" is forbidden and will raise an error.
        """
        if not in_sequential_run:
            return [-1, -1]

        if group_id not in self.group_idx_dct:
            self.last_group_id = group_id
            self.group_cnt += 1
            if group_id is None:
                # None is not stored, so that it always generates a new group with one element
                return [self.group_cnt, 1]

            self.group_idx_dct[group_id] = self.group_cnt

        if group_id != self.last_group_id:
            raise PmtMacrosInvalidArgumentError(
                f"All elements in a group should be defined consecutively: {group_id}. This group "
                f"already exists, but some other groups got registered in between.{ self.env.log() }"
            )

        group = self.group_dct[group_id]
        order = 0 if has_priority else 1 + len(group)
        if order in group:
            # Should only happens if several 0 <=> several stars in the same group, but kept
            # as security check in case of some too much careless implementation changes...
            raise PmtMacrosInvalidArgumentError(
                "Cannot define several elements with priority in the same group.\n"
                f"Invalid group: RUN_GROUP={group_id!r}.{ self.env.log() }"
            )
        group.add(order)

        out = [self.group_idx_dct[group_id], order]
        return out