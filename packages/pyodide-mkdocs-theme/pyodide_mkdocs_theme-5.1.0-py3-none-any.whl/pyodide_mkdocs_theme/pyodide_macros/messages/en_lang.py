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


from .classes import (
    Tr,
    TestsToken,
    Msg,
    MsgPlural,
    Tip,
)
from .fr_lang import Lang


class LangEn(Lang):

    # LANG_TOKEN
    # Editors:
    tests:      Tr = TestsToken("\n# Tests\n")  ###
    """
    Separator placed between the user code and public tests.

    * Line breaks at the beginning or end indicate the number of empty lines before or after the text itself.
    * The separator itself must start with `#` and have at least 6 characters (excluding spaces).
    """###
    comments:   Tr = Tip(16, "(De-)Activate the code after the line <code>{tests}</code> "
                             "(case insensitive)", "Ctrl+I")    ###
    """
    Tooltip for the button to enable or disable public tests.
    The string used must contain {tests} because the content of TestsToken.msg will be inserted there.
    """###
    split_screen: Tr = Tip(23, 'Enter or exit the "split screen" mode<br>(<kbd>Alt+:</kbd> '
                               '/ <kbd>Ctrl</kbd> to reverse the columns)')    ###
    """
    Tooltip for the button to enter or exit the split screen mode.
    """###
    split_mode_placeholder: Tr = Msg("Editor in the other column")   ###
    """
    Message shown instead of the IDE that is currently in "split screen" mode.
    """###
    full_screen: Tr = Tip(10, 'Enter or exit the "full screen" mode', 'Esc')    ###
    """
    Tooltip for the button to enter or exit the full screen mode.
    """###


    # Terminals
    feedback:      Tr = Tip(19, "Truncate or not the feedback in the terminals (standard output "
                                "& stacktrace / run the code again to apply)")    ###
    """
    Tooltip for the button controlling the "feedback level" displayed in the terminal.
    """###
    wrap_term:     Tr = Tip(18, "If enabled, text copied from the terminal is joined into a single "
                                "line before being copied to the clipboard")    ###
    """
    Tooltip for the button indicating whether the text copied from the terminal is joined before being copied or not.
    """###


    # Runtime feedback
    run_script:    Tr = Msg("Script started...", format='info')    ###
    """
    Message announcing the start of executions (pyodide).
    """###
    install_start: Tr = Msg("Installing Python packages. This may take some time...", format='info')    ###
    """
    Message displayed in the terminal before loading micropip, in order to install missing packages.
    """###
    install_done:  Tr = Msg("Installations completed!", format='info')    ###
    """
    Message displayed when micropip package installations are finished.
    """###
    refresh:       Tr = Msg("A newer version of the code exists.\nPlease copy any of your changes "
                            "then reset the IDE.", format='warning')    ###
    """
    Message displayed in the terminal when the code in the user's localStorage is older than the
    last pipeline date.
    """###

    validation:    Tr = Msg("Validation - ", format='info')    ###
    """
    Name starting the lines of the feedback in the terminal, for the validation steps
    """###
    editor_code:   Tr = Msg("Editor", format='info')    ###
    """
    Name associated to the content of the editor
    """###
    public_tests:  Tr = Msg("Public tests", format='info')    ###
    """
    Name given to the original public tests (step 2 during validations)
    """###
    secret_tests:  Tr = Msg("Secret tests", format='info')    ###
    """
    Name given to the secret tests (step 3 during validations)
    """###
    success_msg:   Tr = Msg("OK", format='success')    ###
    """
    Message when one step of the tests is successful.
    """###
    success_msg_no_tests: Tr = Msg("Ended without error.", format='info')    ###
    """
    Message displayed when the executions completed and there are no validation button and 'tests' section."
    """###
    unforgettable: Tr = Msg("Don't forget to validate the code!", format='warning')    ###
    """
    Message displayed at the end of the public tests if no errors were encountered and secret tests exist.
    """###


    # Terminals: validation success/failure messages
    success_head:  Tr = Msg("Bravo !", format='success')    ###
    """
    Header of the success message (bold, italic, green)
    """###
    success_head_extra: Tr = Msg("You have passed all the tests!")    ###
    """
    End of the message indicating a success.
    """###
    success_tail:  Tr = Msg("Don't forget to read")    ###
    """
    End of the success message.
    """###
    fail_head:     Tr = Msg("Oops!", format='warning')    ###
    """
    Header of the failure message (bold, italic, orange)
    """###
    reveal_corr:   Tr = Msg("the solution")    ###
    """
    Chunk of sentence indicating a solution code exists.
    """###
    reveal_join:   Tr = Msg("and")    ###
    """
    Coordinating conjunction joining `reveal_corr` and `reveal_rem` when correction and
    comments are present.
    """###
    reveal_rem:    Tr = Msg("comments")    ###
    """
    Chunk of sentence indicating the existence of remarks.
    """###
    fail_tail:     Tr = MsgPlural("is now available", "are now available") ###
    """
    End of the message indicating a failure.
    """###


    # Corr  rems admonition:
    title_corr:    Tr = Msg('Solution')    ###
    """
    Used to build the title of the admonition holding solution and/or comments, below IDEs.
    """###
    title_rem:     Tr = Msg('Comments')   ###
    """
    Used to build the title of the admonition holding solution and/or comments, below IDEs.
    """###
    corr:          Tr = Msg('🐍 Suggested solution')    ###
    """
    Title of the code block containing the solution for an IDE, in the "solution & comments"
    admonition.
    """###
    rem:           Tr = Msg('Comments')    ###
    """
    Title (&lt;h3&gt; equivalent) announcing the comments, in the "solution & comments" admonition.
    """###


    # Buttons, IDEs buttons & counter:
    py_btn:        Tr = Tip(8,  "Run the code")    ###
    """
    Tooltip for a standalone button that allows running python code.
    """###
    play:          Tr = Tip(9,  "Run the code", "Ctrl+S")    ###
    """
    Tooltip for the button to run public tests.
    """###
    check:         Tr = Tip(9,  "Validate<br><kbd>Ctrl</kbd>+<kbd>Enter</kbd><br>(Right click for historic)")    ###
    """
    Tooltip for the button to run validation tests.
    """###
    download:      Tr = Tip(0,  "Download")    ###
    """
    Tooltip for the button to download the content of a code editor.
    """###
    upload:        Tr = Tip(0,  "Upload")    ###
    """
    Tooltip for the button to replace the content of a code editor with the content of a local file.
    """###
    restart:       Tr = Tip(6,  "Reset the editor")    ###
    """
    Tooltip for the button resetting the content of a code editor.
    """###
    restart_confirm: Tr = Tip(0, "WARNING: resetting the editor, you will lose previous codes, validation status and histories.")    ###
    """
    Confirmation question before resetting an IDE.
    """###
    save:          Tr = Tip(7,  "Save in the browser")    ###
    """
    Tooltip for the button to save the content of a code editor to the browser's localStorage.
    """###
    zip:           Tr = Tip(0, "Archive all codes")    ###
    """
    Tooltip for the button archiving the content of all editors in a zip file.
    """###
    corr_btn:      Tr = Tip(9,  "Test the solution (serve)")    ###
    """
    Tooltip for the button to test the solution code (`corr` section / only during mkdocs serve).
    """###
    show:          Tr = Tip(10, "Show corr & REMs")    ###
    """
    Tooltip for the button to reveal the solution and the comments (only during mkdocs serve).
    """###
    attempts_left: Tr = Msg("Attempts left")    ###
    """
    Texte indicating the number of remaining validation attempts.
    """###


    # Testing
    tests_done:    Tr = Msg("Tests done.", 'info')    ###
    """
    Message displayed in the terminal after finishing the tests of all IDEs.
    """###
    test_ides:     Tr = Tip(8, "Run all tests...")    ###
    """
    Tooltip related to the IDEs testing page.
    """###
    test_stop:     Tr = Tip(6, "Stop all tests")    ###
    """
    Tooltip related to the IDEs testing page.
    """###
    test_1_ide:     Tr = Tip(7, "Run this test")    ###
    """
    Tooltip related to the IDEs testing page.
    """###
    load_ide:      Tr = Tip(8, "Setup the IDE with this.")    ###
    """
    Tooltip related to the IDEs testing page.
    """###


    # QCMS
    qcm_title:     Tr = MsgPlural("Question")    ###
    """
    Default title used for admonitions containing the MCQs (when no argument is provided with the
    `multi_qcm` macro call).
    """###
    qcm_mask_tip:  Tr = Tip(13, "Answers will stay hidden...")    ###
    """
    Tooltip displayed on hover over the mask, for MCQs whose answers are not revealed.
    """###
    qcm_check_tip: Tr = Tip(8,  "Check answers")    ###
    """
    Tooltip for the button to validate MCQ answers.
    """###
    qcm_redo_tip:  Tr = Tip(8,  "Restart")    ###
    """
    Tooltip for the button to restart the MCQ.
    """###


    # Others
    tip_trash: Tr = Tip(15, "Remove the saved codes for {site_name} from the browser") ###
    """
    Tooltip for the button to delete the data stored in the browser's localStorage
    (the trash can at the top next to the search bar).
    The actual site name (`site_name` in `mkdocs.yml`) is automatically inserted into the
    sentence with "{site_name}".
    """###

    figure_admo_title: Tr = Msg("Your figure") ###
    """
    Title given to admonitions containing "figures" (see about drawings made with `matplotlib`
    and the `figure(...)` macro).
    """###
    figure_text:       Tr = Msg("Your figure will appear here") ###
    """
    Text placeholder for a `figure` (see about drawings made with `matplotlib` and the
    `figure(...)` macro).
    """###
    p5_start:          Tr = Tip(0, "Start the animation") ###
    """
    Tooltip for the button to start the p5 animation event loop.
    """###
    p5_stop:           Tr = Tip(0, "Stop the animation") ###
    """
    Tooltip for the button to stop the p5 animation event loop.
    """###
    p5_step:           Tr = Tip(0, "One step forward") ###
    """
    Tooltip for the button to make one step in a p5 animation.
    """###

    picker_failure:    Tr = Msg(
            "Please, click somewhere on the page in between keyboard shortcuts or use a "
            "button to be able to upload a file."
        ) ###
    """
    Message displayed in the browser when the user tries to run code using `pyodide_uploader_async`
    multiple times using keyboard shortcuts, without other interaction with the page in between
    attempts: this is not allowed by browsers.

    Note: browsers that do not support `HTMLInputElement.showPicker` will not display this message.
    """###

    zip_ask_for_names: Tr = Msg("Please enter your name (no empty string):") ###
    """
    Message shown to the user when they want to create a zip archive with the contents of all
    the IDEs in the page, if the site author required something to identify the students.
    """###


    # LANG_TOKEN
    #-------------------------------------------------------------------------
