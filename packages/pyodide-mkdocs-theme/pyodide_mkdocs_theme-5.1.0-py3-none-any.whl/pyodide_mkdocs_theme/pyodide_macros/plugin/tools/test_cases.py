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
# pylint: disable=multiple-statements, no-member



from typing import ClassVar, Dict, List, Literal, Optional, Tuple, Union
from dataclasses import dataclass, field, fields

from ...exceptions import PmtMacrosInvalidArgumentError
from ...messages.fr_lang import Lang





@dataclass
class Case:
    """
    Represent a test case for an IDE TEST argument (or profile).

    By default, the corr section is run against the tests and secrets sections.
    """

    KEEP_FALSY_EXPORTS: ClassVar[Tuple[str]] = (
        'reveal_corr_rems', 'set_max_and_hide', 'no_clear', 'delta_attempts',
    )
    """
    Specific values that should always be transferred to JS, even when falsy.
    """

    DESC_SKIPPED: ClassVar[Tuple[str]] = (
        'subcases', 'skip', 'title', 'std_capture_regex', 'not_std_capture_regex',
    )
    """
    Not shown in the automatic descriptions.
    """


    SHORTEN: ClassVar[Dict[str,str]] = {
        'decrease_attempts_on_user_code_failure': 'decrease_condition',
        'deactivate_stdout_for_secrets':          'secrets_std_out',
        'show_only_assertion_errors_for_secrets': 'secrets_only_assert',
    }
    """
    Automatic descriptions formatting.
    """


    # Globals for string definitions (public interface)
    DEFAULT: ClassVar['Case'] = None     # Defined after class declaration
    SKIP:    ClassVar['Case'] = None     # Defined after class declaration
    HUMAN:   ClassVar['Case'] = None     # Defined after class declaration
    FAIL:    ClassVar['Case'] = None     # Defined after class declaration
    NO_CLEAR:ClassVar['Case'] = None     # Defined after class declaration
    CODE:    ClassVar['Case'] = None     # Defined after class declaration
    CORR:    ClassVar['Case'] = None     # Defined after class declaration


    # Private interface
    REVEAL_SUCCESS:             ClassVar['Case'] = None
    REVEAL_FAIL:                ClassVar['Case'] = None
    ERROR_IN_POST_REVEAL:       ClassVar['Case'] = None
    ERROR_NO_REVEAL:            ClassVar['Case'] = None
    SUCCESS_AFTER_REVEAL:       ClassVar['Case'] = None
    DELAYED_NO_REVEAL:          ClassVar['Case'] = None
    SUCCESS_NOTHING_TO_REVEAL:  ClassVar['Case'] = None


    #--------------------------------------------------------------------------


    human: Optional[bool] = None
    """
    If True, this IDE is not tested by default, but it can be selected with the human button (to
    use for tests that require human actions, like up-/downloads).
    """

    skip: Optional[bool] = None
    """
    Don't test this IDE
    """

    fail: Optional[bool] = None
    """
    This IDE has to raise something during the test
    """

    code: Optional[bool] = None
    """
    Run the `code` section instead of the `corr` one.
    """

    no_clear: Optional[bool] = None
    """
    Don't clear the scope before doing this test (NOTE: this would become useless if the tests
    were not run in order).
    """

    term_cmd: Optional[str] = None
    """
    One command to execute through the terminal. If given, corr/code sections to test are ignored.
    """

    description: Optional[str] = None
    """
    Quick description of the test (optional).
    """



    #-------------------------------------------------------------------------
    # Private interface:

    all_in_std: Optional[List[str]] = None
    """
    If given, automatically build a regex with all the element for `std_capture_regex`.

    !!! warn ""
        * This will apply on content already formatted by jQuery.terminal output, so terminal
        colors may mess up the patterns.
        * The order of the string to match matters: all string have to be matched in order.
    """

    none_in_std: Optional[List[str]] = None
    """
    If given, automatically build a regex with all the element for `not_std_capture_regex`.

    !!! warn ""
        * This will apply on content already formatted by jQuery.terminal output, so terminal
        colors may mess up the patterns.
        * The order of the string to match DOES NOT matter: they can be given in any order.
    """

    in_error_msg: Optional[str] = None
    """
    String that should be found in the error message (test failed if no error message).
    """

    not_in_error_msg: Optional[str] = None
    """
    String that should NOT be found in the error message (success if no error message).
    """




    auto_run: Optional[bool] = None
    """
    Allow to test AUTO_RUN arguments.

    If True, will run the code using this.runner, or runnerTerm if a term_cmd is defined.
    """

    clear_libs: List[str] = field(default_factory=list)
    """
    List of names of libs to remove before a test. This will automatically remove the zip files
    in the WASM file system, and remove the entry from `sys.modules` so that the python_lib can
    be loaded and trigger the import message again in the terminal.
    """

    deactivate_stdout_for_secrets:          Optional[bool] = None
    """ Override the current value for the source page, if given. """

    decrease_attempts_on_user_code_failure: Optional[str]  = None
    """ Override the current value for the source page, if given. """

    run_play: Optional[bool] = None
    """
    Runs the public tests only. Here, it's still possible to run either the code or the
    corr section, along with the tests section.
    """

    run_corr: Optional[bool] = None
    """
    Runs the ValidationCorr
    """

    set_max_and_hide: Optional[int] = None
    """
    Allow to change the number of attempts left before the test, and reset the state of any
    previously revealed stuff. Use 1000 to get infinite number of attempts.
    """

    show_only_assertion_errors_for_secrets: Optional[bool] = None
    """ Override the current value for the source page, if given. """





    assertions: Optional[str] = None
    """
    Space separated strings of boolsy `IdeRunner` properties to check at the end of the test.

    * Prefix with '!' to check for falsy values.
    * Identifiers can be in camelCase or snake_case, so any JS property can be tested.
    * If a property returns undefined, the test will be considered failed.

    Available properties (non exhaustive):

    - `attemptsLeft`
    - `autoLogAssert`
    - `autoRun`
    - `corrContent`
    - `corrRemsMask`
    - `cutFeedback`
    - `deactivateStdoutForSecrets`
    - `decreaseAttemptsOnUserCodeFailure`
    - `envContent`
    - `envTermContent`
    - `excluded`
    - `excludedKws`
    - `excludedMethods`
    - `export`
    - `hasCheckBtn`
    - `hasCorrBtn`
    - `hasCounter`
    - `hasRevealBtn`
    - `hasTerminal`
    - `hasTerminal`
    - `hasTerminal`
    - `isIde`
    - `isIde`
    - `isInSequentialRun`
    - `isInSplit`
    - `isPyBtn`
    - `isPyBtn`
    - `isRunner`
    - `isStarredGroup`
    - `isTerminal`
    - `isTerminal`
    - `isTerminal`
    - `isVert`
    - `maxIdeLines`
    - `minIdeLines`
    - `orderInGroup`
    - `postContent`
    - `postTermContent`
    - `prefillTerm`
    - `profile`
    - `publicTests`
    - `pyName`
    - `pypiWhite`
    - `pythonLibs`
    - `recLimit`
    - `revealCorrRems`
    - `runGroup`
    - `secretTests`
    - `seqRun`
    - `showOnlyAssertionErrorsForSecrets`
    - `splitScreenActivated`
    - `srcHash`
    - `stdKey`
    - `stdoutCutOff`
    - `twoCols`
    - `userContent`
    - `whiteList`
    """
    # GENERATED doc
    # ^^^^^^^^^

    delta_attempts: Optional[Literal[0,-1]] = None
    """
    `#!py 0` or `#!py -1`, if used: expected variation of number of attempts at the end or the test.
    """



    subcases: List['Case'] = field(default_factory=list)
    """
    List of Case objects, defining a group of tests.

    ```python
    Case(description="nom du groupe de tests", subcases=[
        Case(title='cas 2', ...),
        Case(title='cas 1', ...),
        ...
    ])
    ```
    """

    title: Optional[str] = None
    """
    String prepended to the automatic description when no description value given
    """


    #---------------------------------------------------------------------

    std_capture_regex: Optional[str] = None
    """ INTERNAL ONLY: DON'T USE THAT AS ARGUMENT """
    not_std_capture_regex: Optional[str] = None
    """ INTERNAL ONLY: DON'T USE THAT AS ARGUMENT """

    def __post_init__(self):
        if self.std_capture_regex or self.not_std_capture_regex:
            raise PmtMacrosInvalidArgumentError(
                "std_capture_regex and not_std_capture_regex properties are internals only "
                "=> don't use them as arguments, use all_in_std or none_in_std instead."
            )

        if self.subcases:
            self.subcases = [*map(self.auto_convert_str_to_case, self.subcases)]


    def times(self, n:int, with_:Dict[Union[int,Tuple[int]],'Case']=None):
        """
        Creates `n` subcases for the current Case object. This is useful for tests involving
        `py_libs.auto_N(...)` and `py_libs.do_it(...)`.

        If the `with_` dict is given, the subcases at the indices given as keys (either int
        or tuple of ints) will be replaced with the `Case` corresponding value.
        """
        if self.subcases:
            raise PmtMacrosInvalidArgumentError(
                "Cannot use `Case.times(n)` method if the instance already has a `subcases` array."
            )
        self.subcases = [ Case(description=f"Run {i+1}") for i in range(n) ]
        if with_:
            for ns,case in with_.items():
                if isinstance(ns,int):
                    ns = (ns,)
                for n in ns:
                    self.subcases[n-1] = case
        return self


    def with_(self, **kwargs):
        """
        Build a new Case instance based on the current one, updating all the properties with the
        one of the kwargs.
        """
        kw = {**self._to_dict(), **kwargs}
        if self.description is not None and kwargs and 'description' not in kwargs:
            kw['description'] += ' | '+', '.join( self.format_item(k,v) for k,v in kwargs.items() )
        return Case(**kw)



    @classmethod
    def auto_convert_str_to_case(cls, case: Union[str,'Case']) -> 'Case':
        """
        Convert a string to the related Case instance, or just return the instance.
        """
        if isinstance(case, Case):
            return case
        if not isinstance(case, str):
            raise PmtMacrosInvalidArgumentError(
                f"TEST argument should be a string or a Case instance, but was: {case!r}"
            )
        out = cls.DEFAULT if not case else getattr(cls, case.upper())
        return out.with_()      # Always return a copy!



    @classmethod
    def format_item(cls, k, v):
        """
        Used to make some automatic descriptions shorter...
        """
        return f"{ cls.SHORTEN.get(k,k) }={ repr(v) }"



    def _to_dict(self):
        """
        Convert to a dict, without the properties whose the value is None.
        """
        return { f.name: v for f in fields(self)
                           if (v:=getattr(self, f.name)) is not None
               }


    def as_dict(self, merge_with:dict=None):
        """
        Convert recursively to a dict, removing falsy values.
        """
        is_not_top_level = merge_with is not None

        dct = self._to_dict()
        if merge_with:
            dct = {**merge_with, **dct}
            for p in ('subcases', 'std_capture_regex', 'not_std_capture_regex'):
                dct.pop(p, None)

        if dct.get('all_in_std'):
            dct['std_capture_regex'] = r'.*?'.join(dct['all_in_std'])
        if dct.get('none_in_std'):
            dct['not_std_capture_regex'] = r'|'.join(dct['none_in_std'])


        # Filter falsy values AFTER merging (or lose overrides...):
        dct = {k:v for k,v in dct.items()
                    if v or v is not None and k in self.KEEP_FALSY_EXPORTS
        }

        if self.subcases:
            dct['subcases'] = [ case.as_dict(merge_with=dct) for case in self.subcases ]

        if self.description is None:
            dct['description'] = ', '.join(
                self.format_item(k,v)
                    for k,v in dct.items()
                    if k not in self.DESC_SKIPPED           # Don't show irrelevant info
                        and (k!='code' or is_not_top_level) # Useless at top level: already known
                        and k!='description'                # Don't reuse upper level description
            )
            if self.title:
                dct['description'] = f"{ self.title }: { dct['description'] }"

        return dct







Case.SKIP     = Case(skip=True)
Case.FAIL     = Case(fail=True)
Case.CODE     = Case(code=True)
Case.CORR     = Case()                  # Default case before PMT 5.0
Case.HUMAN    = Case(human=True)
Case.NO_CLEAR = Case(no_clear=True)

Case.DEFAULT = Case(no_clear=False, description="", subcases=[
    Case(description="corr vs `tests`+`secrets` (succès)"),
    Case(description="code vs validation (échec)", code=True, fail=True),
    # Case(description="`code` vs `tests` (échec)", code=True, fail=True, run_play=True),
])



LANG = Lang.get_langs_dct()['fr']

Case.REVEAL_SUCCESS = Case(
    description = "Success reveal with: bravo, passé tous les tests, pensez à lire",
    no_clear = True,
    fail = False,
    run_play = False,
    delta_attempts = 0,
    assertions = "corrRemsMask hasCheckBtn reveal_corr_rems",
    all_in_std = [LANG.success_head.msg, LANG.success_head_extra.msg, LANG.success_tail.msg],
    none_in_std = [LANG.fail_head.msg],
)

Case.REVEAL_FAIL = Case(
    description = "Fail reveal with: Dommage! and none of the success messages",
    fail = True,
    no_clear = True,
    run_play = False,
    delta_attempts = -1,
    assertions = "corrRemsMask hasCheckBtn reveal_corr_rems",
    none_in_std = [LANG.success_head.msg, LANG.success_head_extra.msg, LANG.success_tail.msg],
    all_in_std = [LANG.fail_head.msg],
)

Case.ERROR_IN_POST_REVEAL = Case(
    description = "Assertion in post is a success",
    fail = True,
    no_clear = True,
    run_play = False,
    delta_attempts = 0,
    assertions = "corrRemsMask hasCheckBtn reveal_corr_rems",
    none_in_std = [],
    all_in_std = [
        LANG.success_head.msg, LANG.success_head_extra.msg,
        LANG.success_tail.msg,
        'Error:'
    ],
)

Case.ERROR_NO_REVEAL = Case(
    description = "Error without revelation",
    fail = True,
    no_clear = True,
    run_play = False,
    delta_attempts = -1,
    assertions = "corrRemsMask hasCheckBtn !reveal_corr_rems",
    all_in_std = ['Error:'],
    none_in_std = [ LANG.fail_head.msg,
                    LANG.success_head.msg, LANG.success_head_extra.msg, LANG.success_tail.msg],
)

Case.SUCCESS_AFTER_REVEAL = Case(
    description = "SUCCESS_AFTER_REVEAL",
    no_clear = True,
    fail = False,
    run_play = False,
    delta_attempts = 0,
    assertions = "hasCheckBtn !reveal_corr_rems",
    none_in_std = [LANG.success_head.msg, LANG.success_head_extra.msg, LANG.fail_head.msg, LANG.success_tail.msg],
)

Case.SUCCESS_NOTHING_TO_REVEAL = Case.SUCCESS_AFTER_REVEAL.with_(
    none_in_std = [LANG.fail_head.msg, LANG.success_tail.msg],
    all_in_std  = [LANG.success_head.msg, LANG.success_head_extra.msg],
)

Case.DELAYED_NO_REVEAL = Case(
    description = "DELAYED_NO_REVEAL",
    no_clear = False,
    fail = False,
    run_play = False,
    delta_attempts = -1,
    assertions = "hasCheckBtn !reveal_corr_rems",
    none_in_std = [LANG.success_head.msg, LANG.success_head_extra.msg, LANG.fail_head.msg, LANG.success_tail.msg],
)
