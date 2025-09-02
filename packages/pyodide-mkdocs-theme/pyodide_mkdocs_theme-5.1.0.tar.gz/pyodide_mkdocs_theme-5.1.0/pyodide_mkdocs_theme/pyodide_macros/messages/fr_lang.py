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
    LangBase,
    Tr,
    TestsToken,
    Msg,
    MsgPlural,
    Tip,
)


class Lang(LangBase):

    # LANG_TOKEN
    # Editors:
    tests:      Tr = TestsToken("\n# Tests\n")  ###
    """
    Séparateur placé entre le code utilisateur et les tests publics.

    * Les sauts de lignes situés au début ou à la fin indiquent le nombre de lignes vides avant
    ou après le texte lui-même.
    * Le séparateur lui-même doit commencer par `#` et avoir au moins 6 caractères (hors espaces).
    """###
    comments:   Tr = Tip(17, "(Dés-)Active le code après la ligne <code>{tests}</code> "
                             "(insensible à la casse)", "Ctrl+I")    ###
    """
    Info-bulle pour le bouton permettant d'activer ou désactiver les tests publics.
    La chaîne utilisée doit contenir `{tests}` car le contenu de TestsToken.msg y sera inséré.
    """###
    split_screen: Tr = Tip(23, 'Entrer ou sortir du mode "deux colonnes"<br>(<kbd>Alt+:</kbd> '
                               '; <kbd>Ctrl</kbd> pour inverser les colonnes)')    ###
    """
    Info-bulle pour le bouton permettant d'activer ou désactiver le mode deux colonnes.
    """###
    split_mode_placeholder: Tr = Msg("Éditeur dans l'autre colonne")   ###
    """
    Message affiché à la place de l'IDE placé en mode deux colonnes, à sa position
    d'origine dans la page.
    """###
    full_screen: Tr = Tip(10, 'Entrer ou sortir du mode "plein écran"', "Esc")    ###
    """
    Info-bulle pour le bouton permettant d'activer ou désactiver le mode plein écran.
    """###


    # Terminals
    feedback:      Tr = Tip(19, "Tronquer ou non le feedback dans les terminaux (sortie standard"
                                " & stacktrace / relancer le code pour appliquer)")    ###
    """
    Info-bulle du bouton contrôlant le "niveau de feedback" affiché dans le terminal
    """###
    wrap_term:     Tr = Tip(19, "Si activé, le texte copié dans le terminal est joint sur une "
                                "seule ligne avant d'être copié dans le presse-papier")    ###
    """
    Info-bulle du bouton indiquant si le texte copié depuis le terminal est join anat d'être copié ou non.
    """###


    # Runtime feedback
    run_script:    Tr = Msg("Script lancé...", format='info')    ###
    """
    Message annonçant le début des exécutions (pyodide).
    """###
    install_start: Tr = Msg("Installation de paquets python. Ceci peut prendre un certain temps...", format='info')    ###
    """
    Message affiché dans la console avant le chargement de micropip, en vue d'installer des modules manquants.
    """###
    install_done:  Tr = Msg("Installations terminées !", format='info')    ###
    """
    Message affiché lorsque les installation de paquets par micropip sont finies.
    """###
    refresh:       Tr = Msg("Une version plus récente du code existe.\nVeuillez copier vos "
                            "éventuelles modifications puis réinitialiser l'IDE.", format='warning')    ###
    """
    Message affiché dans le terminal lorsque le code contenu dans le localStorage de l'utilisateur
    est plus vieux que celui du dernier pipeline.
    """###


    validation:    Tr = Msg("Validation - ", format='info')    ###
    """
    Nom donné en début de ligne de feedback les étapes passées avec succès lors des validations.
    """###
    editor_code:   Tr = Msg("Éditeur", format='info')    ###
    """
    Nom désignant le contenu de l'éditeur.
    """###
    public_tests:  Tr = Msg("Tests publics", format='info')    ###
    """
    Nom donné aux tests publics originaux, exécuté en étape 2 des validations.
    """###
    secret_tests:  Tr = Msg("Tests secrets", format='info')    ###
    """
    Nom donné aux tests exécutés à la dernière étape des validations.
    """###
    success_msg:   Tr = Msg("OK", format='success')    ###
    """
    Message annonçant qu'une étape des tests est validée.
    """###
    success_msg_no_tests: Tr = Msg("Terminé sans erreur.", format='info')    ###
    """
    Message annonçant la fin des exécutions, lorsqu'il n'y a ni bouton de validation, ni section `tests`.
    """###
    unforgettable: Tr = Msg("N'oubliez pas de faire une validation !", format='warning')    ###
    """
    Message affiché à la fin des tests publics, si aucune erreur n'a été rencontrée et qu'une validation est disponible.
    """###


    # Terminals: validation success/failure messages
    success_head:  Tr = Msg("Bravo !", format='success')    ###
    """
    Entête du message de succès (gras, italique, en vert)
    """###
    success_head_extra:  Tr = Msg("Vous avez réussi tous les tests !")    ###
    """
    Fin du message annonçant un succès.
    """###
    success_tail:  Tr = Msg("Pensez à lire")    ###
    """
    Fin du message de succès.
    """###
    fail_head:     Tr = Msg("Dommage !", format='warning')    ###
    """
    Entête du message d'échec (gras, italique, en orange)
    """###
    reveal_corr:   Tr = Msg("le corrigé")    ###
    """
    Bout de phrase annonçant l'existence d'une correction.
    """###
    reveal_join:   Tr = Msg("et")    ###
    """
    Conjonction de coordination joignant `reveal_corr` et `reveal_rem`, quand correction et
    remarques sont présentes.
    """###
    reveal_rem:    Tr = Msg("les commentaires")    ###
    """
    Bout de phrase annonçant l'existence de remarques.
    """###
    fail_tail:     Tr = MsgPlural("est maintenant disponible", "sont maintenant disponibles") ###
    """
    Fin du message annonçant un échec.
    """###


    # Corr / rems admonition:
    title_corr:    Tr = Msg('Solution')    ###
    """
    Utilisé pour construire le titre de l'admonition contenant la correction et/ou les remarques,
    sous les IDEs.
    """###
    title_rem:     Tr = Msg('Remarques')   ###
    """
    Utilisé pour construire le titre de l'admonition contenant la correction et/ou les remarques,
    sous les IDEs.
    """###
    corr:          Tr = Msg('🐍 Proposition de correction')    ###
    """
    Titre du bloc de code contenant la correction d'un IDE, dans l'admonition "correction &
    remarques".
    """###
    rem:           Tr = Msg('Remarques')    ###
    """
    Titre (équivalent &lt;h3&gt;) annonçant le début des remarques, dans l'admonition "correction &
    remarques"
    """###


    # Buttons, IDEs buttons & counter:
    py_btn:        Tr = Tip(9, "Exécuter le code")    ###
    """
    Info-bulle d'un bouton isolé, permettant de lancer un code python.
    """###
    play:          Tr = Tip(9, "Exécuter le code", "Ctrl+S")    ###
    """
    Info-bulle du bouton pour lancer les tests publics.
    """###
    check:         Tr = Tip(9, "Valider<br><kbd>Ctrl</kbd>+<kbd>Enter</kbd><br>(Clic droit pour l'historique)")    ###
    """
    Info-bulle du bouton pour lancer les validations.
    """###
    download:      Tr = Tip(0, "Télécharger")    ###
    """
    Info-bulle du bouton pour télécharger le contenu d'un éditeur.
    """###
    upload:        Tr = Tip(0, "Téléverser")    ###
    """
    Info-bulle du bouton pour remplacer le contenu d'un éditeur avec un fichier stocké en local.
    """###
    restart:       Tr = Tip(0, "Réinitialiser l'éditeur")    ###
    """
    Info-bulle du bouton réinitialisant le contenu d'un éditeur.
    """###
    restart_confirm: Tr = Tip(0, "ATTENTION: réinitialiser l'éditeur fera perdre les anciens codes, status de validation et historiques.")    ###
    """
    Demande de confirmation à l'utilisateur avec de faire un restart de l'IDE.
    """###
    save:          Tr = Tip(0, "Sauvegarder dans le navigateur")    ###
    """
    Info-bulle du bouton pour enregistrer le contenu d'un éditeur dans le localStorage du
    navigateur.
    """###
    zip:           Tr = Tip(14, "Archiver les codes des IDEs exportables de la page")    ###
    """
    Info-bulle du bouton permettant de télécharger un zip avec tous les contenus des éditeurs.
    """###
    corr_btn:      Tr = Tip(0, "Tester la correction (serve)")    ###
    """
    Info-bulle du bouton pour tester le code de la correction (uniquement durant `mkdocs serve`).
    """###
    show:          Tr = Tip(0, "Afficher corr & REMs")    ###
    """
    Info-bulle du bouton pour révéler les solutions & REMs (uniquement durant `mkdocs serve`).
    """###
    attempts_left: Tr = Msg("Évaluations restantes")    ###
    """
    Texte annonçant le nombres d'essais de validation restant.
    """###


    # Testing
    tests_done:    Tr = Msg("Tests terminés", 'info')    ###
    """
    Message apparaissant à la fin des tests de tous les IDEs, dans le terminal
    """###
    test_ides:     Tr = Tip(7, "Lance tous les tests...")    ###
    """
    Info-bulle de la page de test des IDEs.
    """###
    test_stop:     Tr = Tip(6, "Arrête les tests")    ###
    """
    Info-bulle de la page de test des IDEs.
    """###
    test_1_ide:    Tr = Tip(7, "Lance ce test")    ###
    """
    Info-bulle de la page de test des IDEs.
    """###
    load_ide:      Tr = Tip(10, "Configure l'IDE avec ces données")    ###
    """
    Info-bulle de la page de test des IDEs.
    """###



    # QCMS
    qcm_title:     Tr = MsgPlural("Question")    ###
    """
    Titre utilisé par défaut pour les admonitions contenant les qcms (si pas d'argument renseigné
    dans l'appel de la macro `multi_qcm`).
    """###
    qcm_mask_tip:  Tr = Tip(11, "Les réponses resteront cachées...")    ###
    """
    Info-bulle affichée au survol du masque, pour les qcms dont les réponses ne sont pas révélées.
    """###
    qcm_check_tip: Tr = Tip(11, "Vérifier les réponses")    ###
    """
    Info-bulle du bouton de validation des réponses des qcms.
    """###
    qcm_redo_tip:  Tr = Tip(9,  "Recommencer")    ###
    """
    Info-bulle du bouton de réinitialisation des qcms.
    """###


    # Others
    tip_trash: Tr = Tip(15, "Supprimer du navigateur les codes enregistrés pour {site_name}") ###
    """
    Info-bulle du bouton de pour supprimer les données stockées dans le navigateur
    (la poubelle en haut à côté de la barre de recherche).
    Le nom du site (`site_name` dans `mkdocs.yml`) est automatiquement intégré dans la phrase
    avec "{site_name}".
    """###


    figure_admo_title: Tr = Msg("Votre figure") ###
    """
    Titre donné aux admonitions contenant des "figures" (voir à propos des dessins faits avec
    `matplotlib` et la macro `figure(...)`).
    """###
    figure_text:       Tr = Msg("Votre tracé sera ici") ###
    """
    Texte affiché avent qu'une `figure` ne soit dessinée (voir à propos des dessins faits avec
    `matplotlib` et la macro `figure(...)`).
    """###
    p5_start:          Tr = Tip(0, "Démarre l'animation") ###
    """
    Info-bulle du bouton pour démarrer la boucle d'évènement des animations p5.
    """###
    p5_stop:           Tr = Tip(0, "Arrête l'animation") ###
    """
    Info-bulle du bouton pour stopper la boucle d'évènement des animations p5.
    """###
    p5_step:           Tr = Tip(0, "Avance d'une image") ###
    """
    Info-bulle du bouton pour stopper la boucle d'évènement des animations p5.
    """###


    picker_failure: Tr = Msg(
            "Veuillez cliquer sur la page entre deux utilisations des raccourcis clavier ou "
            "utiliser un bouton, afin de pouvoir téléverser un fichier."
        ) ###
    """
    Message s'affichant dans le navigateur quand l'utilisateur essaie de lancer plusieurs fois un
    code utilisant `pyodide_uploader_async` via un raccourci clavier sans autre interaction avec la
    page entre les deux : ceci n'est pas autorisé par les navigateurs.

    Nota: les utilisateur de navigateurs non compatibles avec `HTMLInputElement.showPicker` n'auront
    jamais cette information.
    """###

    zip_ask_for_names: Tr = Msg("Veuillez préciser votre/vos noms (chaîne vide interdite) :") ###
    """
    Message affiché dans la fenêtre avant la création d'une archive zip des contenues des IDEs
    exportables, si l'auteur requière l'ajout du nom du ou des utilisateurs.
    """###


    # LANG_TOKEN
    #-------------------------------------------------------------------------
