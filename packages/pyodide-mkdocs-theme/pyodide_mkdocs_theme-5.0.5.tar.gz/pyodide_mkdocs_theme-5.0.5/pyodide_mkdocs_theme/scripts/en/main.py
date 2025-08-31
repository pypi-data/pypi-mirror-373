
from pyodide_mkdocs_theme.pyodide_macros import (
    PyodideMacrosPlugin,
    Msg, MsgPlural, TestsToken, Tip,
)


def define_env(env:PyodideMacrosPlugin):
    """ The customization has to be done at macro definition time.
        You could paste the code inside this function into your own main.py (or the
        equivalent package if you use a package instead of a single file). If you don't
        use personal macros so far, copy the full code into a `main.py` file at the root
        of your project (note: NOT in the docs_dir!).

        NOTE: you can also completely remove this file if you don't want to use personal
              macros or customize the messages in the built documentation.

        * Change whatever string you want.
        * Remove the entries you don't want to modify
        * Do not change the keyboard shortcuts for the Tip objects: the values are for
          informational purpose only.
        * See the documentation for more details about which string is used for what
          purpose, and any constraints on the arguments:
          https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/custom/messages/#messages-details

        ---

        The signatures for the various objects defined below are the following:

        ```python
        Msg(msg:str)

        MsgPlural(msg:str, plural:str="")

        Tip(width_in_em:int, msg:str, kbd:str=None)

        TestsToken(token_str:str)
        ```
    """

    env.lang.overload({

    # Editors:
        "tests":      TestsToken("\n# Tests\n"),
        "comments":   Tip(16, "(De-)Activate the code after the line <code>{tests}</code> "
                             "(case insensitive)", "Ctrl+I"),
        "split_screen": Tip(23, 'Enter or exit the "split screen" mode<br>(<kbd>Alt+:</kbd> '
                               '/ <kbd>Ctrl</kbd> to reverse the columns)'),
        "split_mode_placeholder": Msg("Editor in the other column"),
        "full_screen": Tip(10, 'Enter or exit the "full screen" mode', 'Esc'),


    # Terminals
        "feedback":      Tip(19, "Truncate or not the feedback in the terminals (standard output "
                                "& stacktrace / run the code again to apply)"),
        "wrap_term":     Tip(18, "If enabled, text copied from the terminal is joined into a single "
                                "line before being copied to the clipboard"),


    # Runtime feedback
        "run_script":    Msg("Script started...", format='info'),
        "install_start": Msg("Installing Python packages. This may take some time...", format='info'),
        "install_done":  Msg("Installations completed!", format='info'),
        "refresh":       Msg("A newer version of the code exists.\nPlease copy any of your changes "
                            "then reset the IDE.", format='warning'),

        "validation":    Msg("Validation - ", format='info'),
        "editor_code":   Msg("Editor", format='info'),
        "public_tests":  Msg("Public tests", format='info'),
        "secret_tests":  Msg("Secret tests", format='info'),
        "success_msg":   Msg("OK", format='success'),
        "success_msg_no_tests": Msg("Ended without error.", format='info'),
        "unforgettable": Msg("Don't forget to validate the code!", format='warning'),


    # Terminals: validation success/failure messages
        "success_head":  Msg("Bravo !", format='success'),
        "success_head_extra": Msg("You have passed all the tests!"),
        "success_tail":  Msg("Don't forget to read"),
        "fail_head":     Msg("Oops!", format='warning'),
        "reveal_corr":   Msg("the solution"),
        "reveal_join":   Msg("and"),
        "reveal_rem":    Msg("comments"),
        "fail_tail":     MsgPlural("is now available", "are now available"),


    # Corr  rems admonition:
        "title_corr":    Msg('Solution'),
        "title_rem":     Msg('Comments'),
        "corr":          Msg('🐍 Suggested solution'),
        "rem":           Msg('Comments'),


    # Buttons, IDEs buttons & counter:
        "py_btn":        Tip(8,  "Run the code"),
        "play":          Tip(9,  "Run the code", "Ctrl+S"),
        "check":         Tip(9,  "Validate<br><kbd>Ctrl</kbd>+<kbd>Enter</kbd><br>(Right click for historic)"),
        "download":      Tip(0,  "Download"),
        "upload":        Tip(0,  "Upload"),
        "restart":       Tip(6,  "Reset the editor"),
        "restart_confirm": Tip(0, "WARNING: resetting the editor, you will lose previous codes, validation status and histories."),
        "save":          Tip(7,  "Save in the browser"),
        "zip":           Tip(0, "Archive all codes"),
        "corr_btn":      Tip(9,  "Test the solution (serve)"),
        "show":          Tip(10, "Show corr & REMs"),
        "attempts_left": Msg("Attempts left"),


    # Testing
        "tests_done":    Msg("Tests done.", 'info'),
        "test_ides":     Tip(8, "Run all tests..."),
        "test_stop":     Tip(6, "Stop all tests"),
        "test_1_ide":     Tip(7, "Run this test"),
        "load_ide":      Tip(8, "Setup the IDE with this."),


    # QCMS
        "qcm_title":     MsgPlural("Question"),
        "qcm_mask_tip":  Tip(13, "Answers will stay hidden..."),
        "qcm_check_tip": Tip(8,  "Check answers"),
        "qcm_redo_tip":  Tip(8,  "Restart"),


    # Others
        "tip_trash": Tip(15, "Remove the saved codes for {site_name} from the browser"),

        "figure_admo_title": Msg("Your figure"),
        "figure_text":       Msg("Your figure will appear here"),
        "p5_start":          Tip(0, "Start the animation"),
        "p5_stop":           Tip(0, "Stop the animation"),
        "p5_step":           Tip(0, "One step forward"),

        "picker_failure":    Msg(
            "Please, click somewhere on the page in between keyboard shortcuts or use a "
            "button to be able to upload a file."
        ),

        "zip_ask_for_names": Msg("Please enter your name (no empty string):")
    })
