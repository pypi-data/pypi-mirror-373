
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
        "comments":   Tip(19, "(De-)Aktiviert den Code nach der Zeile <code>{tests}</code> "
                             "(Groß-/Kleinschreibung wird nicht beachtet)", "Ctrl+I"),
        "split_screen": Tip(10, 'Ein- oder Ausstieg aus dem "Split-Screen"-Modus<br>(<kbd>Alt+:</kbd> ; '
                               '<kbd>Ctrl</kbd>, um die Spalten zu vertauschen)'),
        "split_mode_placeholder": Msg("Editor in die andere Spalte"),
        "full_screen": Tip(10, 'Ein- oder Ausstieg aus dem "Vollbildmodus"', "Esc"),


    # Terminals
        "feedback":      Tip(19, "Kürzen/nicht kürzen der Rückmeldungen im Terminal (Standardausgabe & Stacktrace"
                                "/ Starte das Programm erneut zum Anwenden)"),
        "wrap_term":     Tip(17, "Wenn aktiviert, wird der aus dem Terminal kopierte Text in eine Zeile umgewandelt, "
                                "bevor er in die Zwischenablage kopiert wird."),


    # Runtime feedback
        "run_script":    Msg("Programm gestartet...", format='info'),
        "install_start": Msg("Installation von Python-Paketen. Dies kann eine Weile dauern...", format='info'),
        "install_done":  Msg("Installationen abgeschlossen!", format='info'),
        "refresh":       Msg("Eine neuere Version des Codes ist verfügbar.\nBitte kopieren Sie Ihre "
                            "eventuellen Änderungen und setzen Sie die IDE zurück.", format='warning'),


        "validation":    Msg("Validierung - ", format='info'),
        "editor_code":   Msg("Editor", format='info'),
        "public_tests":  Msg("Öffentliche tests", format='info'),
        "secret_tests":  Msg("Geheime tests", format='info'),
        "success_msg":   Msg("OK", format='success'),
        "success_msg_no_tests": Msg("Ohne Fehler beendet.", format='info'),
        "unforgettable": Msg("Vergiss nicht, den Code zu validieren!", format='warning'),


    # Terminals: validation success/failure messages
        "success_head":  Msg("Gut gemacht!", format='success'),
        "success_head_extra":  Msg("Du hast alle Tests bestanden!"),
        "success_tail":  Msg("Vergiss nicht das folgende zu lesen:"),
        "fail_head":     Msg("Schade!", format='warning'),
        "reveal_corr":   Msg("die lösung"),
        "reveal_join":   Msg("und"),
        "reveal_rem":    Msg("die kommentare"),
        "fail_tail":     MsgPlural("ist jetzt verfügbar", "sind jetzt verfügbar"),


    # Corr  rems admonition:
        "title_corr":    Msg('Lösung'),
        "title_rem":     Msg('Bemerkungen'),
        "corr":          Msg('🐍 Lösungsvorschlag'),
        "rem":           Msg('Bemerkungen'),


    # Buttons, IDEs buttons & counter:
        "py_btn":        Tip(9, "Code ausführen"),
        "play":          Tip(9,  "Code ausführen", "Ctrl+S"),
        "check":         Tip(9,  "Überprüfen<br><kbd>Ctrl</kbd>+<kbd>Enter</kbd><br>(Rechtsklick für Verlauf)"),
        "download":      Tip(0,  "Herunterladen"),
        "upload":        Tip(0,  "Hochladen"),
        "restart":       Tip(0,  "Editor zurücksetzen"),
        "restart_confirm": Tip(0, "ACHTUNG: Durch das Zurücksetzen des Editors gehen alle bisherigen Codes, Validierungsstatus und Verlauf verloren."),
        "save":          Tip(9,  "Im Webbrowser speichern"),
        "zip":           Tip(0, "Alle Codes archivieren"),
        "corr_btn":      Tip(10, "Lösung überprüfen (serve)"),
        "show":          Tip(12, "Lösung und Bemerkungen anzeigen"),
        "attempts_left": Msg("Verbleibende Versuche"),


    # Testing
        "tests_done":    Msg("Tests durchgeführt.", 'info'),
        "test_ides":     Tip(8, "Run all tests..."),
        "test_stop":     Tip(6, "Stoppen aller Tests"),
        "test_1_ide":     Tip(7, "Run this test"),
        "load_ide":      Tip(8, "Setup the IDE with this."),


    # QCMS
        "qcm_title":     MsgPlural("Frage"),
        "qcm_mask_tip":  Tip(11, "Die Antworten bleiben versteckt..."),
        "qcm_check_tip": Tip(11, "Antworten überprüfen"),
        "qcm_redo_tip":  Tip(11, "Neu anfangen"),


    # Others
        "tip_trash": Tip(15, "Lösche die gespeicherten Codes im Webbrowser für {site_name}"),

        "figure_admo_title": Msg("Deine Abbildung"),
        "figure_text": Msg("Deine Abbildung wird hier erscheinen"),
        "p5_start":          Tip(0, "Animation starten"),
        "p5_stop":           Tip(0, "Animation stoppen"),
        "p5_step":           Tip(0, "Vorrücken eines Bildes in der Animation"),

        "picker_failure": Msg(
        "Bitte klicke irgendwo auf der Seite zwischen der Verwendung von Tastenkombinationen oder "
        "klicke auf eine Schaltfläche, um eine Datei hochzuladen."
    ),

        "zip_ask_for_names": Msg("Bitte geben Sie Ihren Namen ein (kein leerer String) :")
    })
