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

from typing import Tuple
from mkdocs.config import config_options as C



from ....parsing import items_comma_joiner
from ....tools_and_constants import (
    KEYWORDS_SEPARATOR,
    HtmlClass,
    IdeConstants,
    IdeMode,
    MacroShowConfig,
    P5BtnLocation,
    NamedTestCase,
)
from .._string_tools_and_constants import InclusionProfile
from ..config_option_src import ConfigOptionIdeLink, ConfigOptionSrc
from ..sub_config_src import SubConfigSrc
from ..macro_config_src import MacroConfigSrc, MultiQcmConfigSrc

from .docs_dirs_config import (
    to_page,
    DOCS_CONFIG,
    DOCS_FIGURES,
    DOCS_IDE_DETAILS,
    DOCS_PY_BTNS,
    DOCS_RUN_MACRO,
    DOCS_QCMS,
    DOCS_RESUME,
    DOCS_TERMINALS,
)




OP,CLO = '{{', '}}'

ACTIVATE_COMPOSITION_INFOS = False


# Composition information deactivated!!
PMT_5_COMPOSING = ACTIVATE_COMPOSITION_INFOS * """
            À partir de PMT 5.0^+^, il est possible de renseigner plusieurs noms de fichiers,
            avec des instructions de [combinaisons des différentes sections ou fichiers de
            remarques](--composite-py)."""



PY_GLOBAL = SubConfigSrc.with_default_docs(
    to_page(DOCS_IDE_DETAILS) / '#IDE-{name}'
)(
    '', elements=(

    ConfigOptionIdeLink(
        'py_name',
        # str, default="",          # Replace the line below for older version
        Tuple[str], conf_type=C.ListOfItems(C.Type(str), default=['']), is_varargs=True,
        inclusion_profile = InclusionProfile.all_but_yaml_stuff,
        index=0,
        fake_name="py_name", fake_type='str', fake_default='',
        yaml_desc = """
            Relative path (no extension) toward the `{exo}.py` file for an IDE, terminal, ...
        """,
        docs = """
            Chemin relatif (sans l'extension du fichier) vers le fichier `{exo}.py` et les
            éventuels autres fichiers annexes, sur lesquels baser l'IDE.
        """ + PMT_5_COMPOSING,
        extra_docs = """
            Chemin relatif au dossier contenant le ficher markdown {{ orange('source') }}
            permettant d'accéder au fichier python {{ annexe('principal') }} pour l'IDE.

            * Si l'argument n'est pas renseigné ou est une chaîne vide, l'IDE sera créé vide
            (ex : [bac à sable](--bac_a_sable/)).
            * Le chemin ne donne que le préfixe commun des fichiers {{annexes()}} pour cet IDE,
            et il faut donc {{red("omettre l'extension")}} : si le fichier {{annexe("principal")}}
            est `.../exercice.py`, l'argument `py_name` doit être  `".../exercice"`.
            * Une {{red('erreur')}} est levée si un chemin est donné mais qu'aucun fichier python
            ne peut être trouvé pour les différentes [organisations de fichiers
            supportées](--ide-files-organization).
        """,
    ),
    ConfigOptionIdeLink(
        'ID', int, is_optional=True,
        inclusion_profile=InclusionProfile.all_but_yaml_stuff,
        fake_type = "None|int",
        yaml_desc = "Disambiguate different macro calls using the same underlying files.",
        docs = """
            À utiliser pour différencier deux IDEs utilisant les mêmes fichiers
            [{{annexes()}}](--ide-files), afin de différencier leurs sauvegardes
            (nota: $ID \\ge 0$).
        """,
        extra_docs = """
            Pour pouvoir sauvegarder, télécharger et téléverser des codes dans ou depuis les IDEs,
            l'`id` html de chaque IDE doit être unique. Or, ceux-ci sont construits à partir de la
            localisation du fichier python principal sur le disque.

            Le thème vérifie notamment l'unicité des `id` générés pour l'intégralité du site et
            lève une erreur si le même fichier python (argument `py_name`) est utilisé plusieurs
            fois dans différents IDEs.

            L'argument `ID` de la macro `IDE` permet donc de différencier deux IDEs utilisant le
            même fichier python, afin de garantir l'unicité des ids html.

            Exemple :

            ```
            Fichier 1: docs/index.md
                {% raw %} {{ IDE('exemples/ex1', ID=1)}} {% endraw %}

            Fichier 2: docs/aide.md
                {% raw %} {{ IDE('exemples/ex1', ID=2)}} {% endraw %}
            ```

            !!! note "Argument `ID` pour les autres macros"

                Cet argument existe également pour les autres macros impliquant des fichiers python
                et peut parfois être nécessaire lorsqu'on utilise les macros `terminal`, `py_btn`, ...
        """,
    ),
    ConfigOptionIdeLink(
        'SANS', str, default="",
        yaml_desc="""
            Used to forbid the use of builtins, attribute accesses, packages or keywords in the
            python code (space or comma separated identifiers).
        """,
        docs=f"""
            Pour interdire des fonctions builtins, des modules, des accès d'attributs ou
            de méthodes, ou des mots clefs : chaîne de noms séparés par des virgules, des
            points-virgules et/ou espaces.

            Les mots clefs sont à renseigner en dernier, après le séparateur `{ KEYWORDS_SEPARATOR }`.
        """,
        extra_docs = """
            Voici le détail des syntaxes et contraintes sur l'utilisation de l'argument `SANS` :

            * Les identifiants utilisés dans l'argument `SANS` peuvent êtres séparés par des
            espaces, des virgules ou des points-virgules.
            * Les fonctions builtins et les modules sont simplement renseignés en donnant leur
            identifiant (pour les modules, renseigner le nom du "top niveau": `matplotlib`, et
            non `matplotlib.pyplot`).
            * Les restrictions d'accès à des attributs ou des méthodes sont l'identifiant de
            l'attribut ou la méthode, préfixé avec un point.
            * Les mots clefs et opérateurs doivent être renseignés en dernier, après avoir ajouté
            le séparateur `"{{AST()}}"` : `SANS="... AST: mot_clefs + ** // ..."`.

                | Syntaxe  {{width(10)}} | Ce qui est interdit |
                |-|-|
                | `identifiant` | [Interdit la fonction builtin](--restrictions-functions)
            correspondant, ou si aucune fonction n'est trouvée, [interdit le module/package](--restrictions-packages)
            correspondant.{{pmt_note("Les imports sont couverts quelle que soit la méthode utilisée :
            `import`{.pmt_note}, `from`{.pmt_note}, aliasing, ...")}} |
                | `.attribut`<br>`.method` | [Interdit les accès d'attributs](--restrictions-methods)
            correspondant à ce nom lève une erreur s'ils sont trouvés dans le code. |
                | `keyword` ou `operator` | [Interdit des opérateurs et des mots clefs](--restrictions-keywords)
            ou assimilés.{{pmt_note("Ceux-ci sont différenciés des identifiants de fonctions ou des
            modules en les renseignant après le séparateur `{{ AST() }}`{.pmt_note}.")}} |

            Exemple d'utilisation :

            ```
            {% raw %}{{ IDE('exo', SANS="sorted, max ; .find .index AST: for") }}{% endraw %}
            ```

            Cet appel de macro interdit :

            - Les fonctions `sorted` et `max`.
            - Les appels de méthodes `.find` et `.index`.
            - Tous types de boucles `for` (boucles normales et comprehensions).

            {{pmt_note("Des informations plus détaillées sur les interdictions et notamment sur les
            restrictions de mots-clefs et opérateurs sont disponibles dans la [page détaillant les
            exécutions](--restrictions).")}}

            <br>

            ??? tip "Sections/code appliquant les différents types de restrictions"

                {{ md_include("docs_tools/inclusions/restrictions_where.md") }}

                Cela signifie que l'on ne peut normalement pas utiliser les éléments interdits dans
                les tests `secrets` pour vérifier les réponses de l'utilisateur (il existe en fait
                un moyen... Voir la section des utilisations avancées).

            {{ kws_exclusions() }}


            ??? warning "But recherché avec les restrictions"

                {{ md_include("docs_tools/inclusions/restrictions_goals.md") }}


            ??? warning "Efficacité des interdictions"

                {{ md_include("docs_tools/inclusions/restrictions_efficiency.md") }}
        """,
    ),
    ConfigOptionIdeLink(
        'WHITE', str, default="",
        yaml_desc="""
            Names of packages to import automatically in the global scope (to avoid troubles with
            forbidden modules).
        """,
        docs="""
            {{ orange('**_L\\'argument `WHITE`{.orange} est normalement obsolète_**') }}.

            (_\"White list\"_) Ensemble de noms de modules/packages à pré-importer avant que les
            interdictions ne soient mises en place (voir argument `SANS`.

        """,
        extra_docs="""
            ??? help "_Cet argument est normalement {{ orange('**obsolète**') }}._"

                Permet de déclarer un ensemble de modules/packages à préimporter avant que les
                restrictions d'imports ne soient mises en place.

                La syntaxe est la même que celle de l'argument [`SANS`](--IDE-SANS): des identifiants
                séparés par des espaces, des virgules ou des points-virgules.

                Exemple: `{% raw %}{{ IDE(..., SANS="sys", WHITE="math") }}{% endraw %}`

                !!! tip "Le problème que `WHITE` essaie de résoudre..."

                    Certains modules de "bas niveau" sont utilisés pour importer d'autres modules,
                    même dans des cas inattendus (ex: `math` qui importe `sys`). Si le module sys
                    est interdit (_ce qui est une très mauvaise idée !_), il peut devenir
                    nécessaire de préimporter d'autres modules que l'utilisateur pourrait avoir
                    besoin d'utiliser dans son code.

                    Voir la page concernant les [restrictions](--restrictions) pour plus de détails.

                !!! warning "`WHITE` n'a pas pour but de remplacer du code python !"

                    Cet argument est un ersatz d'une version antérieure du thème.

                    Il a été conservé dans l'éventualité où un rédacteur se retrouverait tout de
                    même confronté à un problème d'import interdit pour de mauvaises raisons, mais
                    des changements intervenus plus tard dans le développement ont normalement
                    rendu cet argument obsolète : réaliser les préimports depuis la section `env`
                    devrait suffire à éviter ce type de problèmes.


                !!! warning "Efficacité des interdictions"

                    {{ md_include("docs_tools/inclusions/restrictions_efficiency.md") }}
    """,
    ),
    ConfigOptionIdeLink(
        'REC_LIMIT', int, default=-1,
        yaml_desc = f"""
            Limit the recursion depth (do not use values below { IdeConstants.min_recursion_limit }).
        """,
        docs = f"""
            Pour imposer une profondeur de récursion maximale.

            Nota: ne jamais descendre en-dessous de { IdeConstants.min_recursion_limit }. La valeur
            par défaut, `#!py -1`, signifie que l'argument n'est pas utilisé.
        """,
        extra_docs = f"""
            Si cet argument est utilisé avec une valeur positive, la profondeur de récursion sera
            limitée et une erreur sera levée si elle est atteinte durant les exécutions.

            ??? tip "Limitations, particularités, conseils pour cet argument..."

                * Ne pas oublier que ce réglage affecte la stack, qui est globale. Ce qui veut
                dire que le premier appel de fonction de l'utilisateur n'est __pas__ à une
                profondeur 0 ou 1.

                * Pour cette raison, une erreur est levée par la macro si une valeur inférieure
                à { IdeConstants.min_recursion_limit } est utilisée pour `REC_LIMIT`, car
                l'environnement lui-même ne pourrait pas faire tourner le code de l'utilisateur
                et les tests.

                * Côté utilisateur, la fonction `sys.setrecursionlimit` est désactivée lorsque
                cette fonctionnalité est utilisée.

                    - Le procédé utilisé est le même que pour les restrictions de code.
                    - Ce réglage affecte donc également les différents types de tests et le
                      terminal de l'IDE.

                * Ne surtout pas activer cette fonctionnalité si vous utilisez des structures de
                  données récursives, avec des implantations pour `__str__` ou `__repr__` :
                  l'utilisateur se retrouverait probablement avec un crash dû à la restriction à
                  des moments inopportuns :

                    - Sur un `print` (même si la sortie standard n'est pas affichée !)
                    - Lors de la construction d'un message d'erreur affichant une structure de
                      données.
        """,
        # yaml_desc="Limite de la profondeur de récursion (ne pas descendre en-dessous de "
        # +f"{ IdeConstants.min_recursion_limit }).",
    ),
    ConfigOptionIdeLink(
        'SHOW', str,
        conf_type = C.Choice(
            tuple(MacroShowConfig.gen_values(keep=True)),       # with "python"
            default = MacroShowConfig.none,
        ),
        line_feed_link = False,
        yaml_desc="Display macro related infos in the terminal.",
        docs=f"""
            Affiche des données sur l'appel de macro dans la console durant `mkdocs serve` :
            {'{{'} ul_li([
                "`#!py '{ MacroShowConfig.none }'`: Ne fait rien (défaut).",
                "`#!py '{ MacroShowConfig.args }'`: Affiche tous les arguments de l'appel de macro.",
                "`#!py '{ MacroShowConfig.python }'`: Affiche les contenus des sections python, telles que vues par PMT.",
                "`#!py '{ MacroShowConfig.contents }'`: Affiche les contenus des sections python et les REMs, telles que vues par PMT.",
                "`#!py '{ MacroShowConfig.all }'`: Combine `#!py 'args'` et `#!py 'content'`.",
            ]) {'}}'}
        """,
        extra_docs="""
            Lorsque les codes pythons sont affichés (avec `#!pt "python"` ou `#!pt "all"`), les
            sections sont affichées en utilisant des séparateurs supplémentaires, qui permettent
            de comprendre comment le thème a interprété les différentes sections. Les sections
            sont alors affichées comme suit :

            ```python
            #############################
            # --- PYODIDE:{section} --- #
            ...
            ```

            Cela peut permettre d'identifier des fautes de frappes dans le code qui font que l'on
            ne cerne pas forcément au premier abord pourquoi le code de l'IDE ne se comporte pas
            du tout de manière attendue.
        """
    ),
    ConfigOptionIdeLink(
        'RUN_GROUP', str, is_optional=True,
        line_feed_link = False,
        yaml_desc = """
            Allow to identify elements that are grouped together (for sequential executions),
            or that should be SKIPped.
        """,
        docs = """
            Permet d'indiquer les éléments faisant partie d'un même groupe vis-à-vis de la logique
            d'exécution séquentielle, ou "[exécutions liées](--redactors/sequential_runs/)"
            (typiquement, des contenus en "tabs": `=== "..."`).
            {{ul_li([
                "`#!py None` (défaut) : nouvel élément individuel.",
                "`#!py 'SKIP'` : cet élément ne sera jamais exécuté automatiquement.",
                "`#!py str` : un identifiant sous forme de chaîne de caractère, permettant
                d'identifier des éléments groupés dans la page en cours, dont un seul pourra
                être exécuté automatiquement.",
            ], trailing_new_line=True)}}
            Par défaut, lorsque des groupes sont utilisés, c'est le premier élément
            qui est prioritaire. Il est possible de définir un autre élément comme prioritaire
            en ajoutant une étoile au début ou à la fin de la chaîne : `#!py "group*"`.

            {{orange('_ATTENTION_')}} : les [exécutions liées](--sequential-run-activate)
            doivent être activées pour que cet argument ait un effet visible.
            """,
    ),
    ConfigOptionIdeLink(
        'AUTO_RUN', bool, default=False,
        yaml_desc = "Run the python code on page load or not.",
        docs = "Lance automatiquement le code après avoir affiché la page.",
    ),
    ConfigOptionIdeLink(
        'MERMAID', bool, default=False,
        yaml_desc="Mark a page as containing dynamic Mermaid graphs built during executions.",
        docs="""
            Signale qu'un rendu de graphe mermaid sera attendu à un moment ou un autre des
            exécutions.
            {{pmt_note("L'extension markdown `pymdownx.superfences`{.pmt_note} doit être configurée
            pour accepter les blocs de code `mermaid`{.pmt_note}.<br>Voir la configuration par défaut du fichier
            `mkdocs.yml`{.pmt_note}, par exemple via les scripts du thème avec
            `python -m pyodide_mkdocs_theme --yml`{.pmt_note}.") }}
        """,
        extra_docs = """
            Le rôle de cet argument est un peu particulier : son but est de signaler au thème
            que cette page devra intégrer la logistique javascript et pyodide pour construire
            dynamiquement des graphes `mermaid` dans la page.

            Ce "signalement" est en fait global à la page entière de la documentation, et il
            n'est donc pas nécessaire de l'utiliser pour chaque IDE d'une page : {{green("__une
            seule fois par page est suffisant__")}}.

            Voir la page dédiée à [l'utilisation dynamique de `mermaid`](--custom/mermaid/) dans
            pyodide pour plus d'informations.
        """,
    ),
))







MOST_LIKELY_USELESS_ID = {'docs': f"""
    À utiliser pour différencier deux appels de macros différents, dans le cas où vous tomberiez
    sur une collision d'id{ ''' (peut arriver à partir de PMT 5.0^+^, lorsque la macro utilise des
    [combinaisons de fichiers](--composite-py))''' * ACTIVATE_COMPOSITION_INFOS }.
"""}

MEANINGLESS_ARGS_FOR_PY_BTNS_USER_DOCS = ('SANS','WHITE','REC_LIMIT')


def _py_globals_copy_gen(skip_from_macros_docs=(), **replacements:ConfigOptionIdeLink):
    return (
        arg.copy_with(
            inclusion_profile = (
                InclusionProfile.config
                    if name in skip_from_macros_docs else
                arg.inclusion_profile
            ),
            **replacements.get(name, {})
        )
        for name,arg in PY_GLOBAL.subs_dct.items()
    )







#----------------------------------------------------------------------------------------





BS_MACRO = '" + back_slash() + "'
"""
Necessary to bypass jinja deprecation warning when using backslashes where it doesn't like it...
(...the pretty well named... XD )
"""



IDE = MacroConfigSrc(
    'IDE',
    force_kwargs_index = 1,
    docs = "Valeurs par défaut pour les arguments des macros `IDE` et `IDEv`.",
    yaml_desc = "Default values for arguments used in the `IDE` and `IDEv` macros.",
    docs_page_url = to_page(DOCS_IDE_DETAILS),
    elements = (

    *_py_globals_copy_gen(
        AUTO_RUN = {
            'docs': PY_GLOBAL.AUTO_RUN.docs.rstrip(' \n\t.')+" (lance uniquement les tests publics)."
        }
    ),
    ConfigOptionIdeLink(
        'MAX', int, default=5,
        fake_type = "int|'+'",
        yaml_desc = "Maximum number of attempts before revealing correction and remarks.",
        docs="""
            Nombre maximal d'essais de validation avant de rendre la correction et/ou les
            remarques disponibles.
        """,
        extra_docs="""
            * En l'absence de correction et de fichiers de remarques, le compteur d'essais
            sera automatiquement passé à $\\infty/\\infty$.
            * Il est possible d'imposer un nombre d'essais infini en passant `#!py 1000` ou
            `#!py "+"` en argument.
            <br>Ceci impliquerait que la seule façon pour l'utilisateur de voir la solution
            et/ou les remarques serait de passer tous les tests avec succès.


            ??? danger "Erreur levée pour les contenus `corr/REM` avec des compteurs d'essais
            à l'$\\infty$"

                Par défaut, le thème considère que du contenu `corr` ou des remarques (visibles
                ou non) qui seraient "cachés" par un compteur d'essais réglé à l'$\\infty$ est
                une situation non désirée. Une erreur est donc levée durant le build si la
                situation est rencontrée.

                Si c'est effectivement le but recherché, il faut alors modifier l'option {{
                config_link("ides.forbid_corr_and_REMs_with_infinite_attempts") }} du plugin,
                soit via le fichier `mkdocs.yml`,  soit via la configuration des métadonnées
                ([fichiers `{{meta()}}` ou entêtes de pages](--custom/metadata/)) :

                ```yaml
                plugins:
                    pyodide_macros:
                        ides:
                            forbid_corr_and_REMs_with_infinite_attempts: false  # (défaut : true)
                ```
            """
    ),
    ConfigOptionIdeLink(
        'LOGS', bool, default=True,
        yaml_desc = """
            Build or not missing assertion messages for failed assertions in the secret tests
        """,
        docs="""
            {{ red('Durant des tests de validation') }}, si `LOGS` est `True`, le code complet
            d'une assertion est utilisé comme message d'erreur, quand l'assertion a été écrite
            sans message.
        """,
        extra_docs="""
            Lors d'une assertion échouée durant une validation, si le code de l'assertion n'a
            aucun message d'erreur, le thème peut en construire un automatiquement. Selon le
            type d'exercices que vous rédigez, ou si l'exercice provient d'un ancien site
            utilisant [pyodide-mkdocs][pyodide-mkdocs]{: target=_blank } vous pourriez
            souhaiter que les messages d'erreur automatiques soient construits ou non,
            pour ces assertions sans messages.

            <br>

            !!! warning "Migration depuis `pyodide-mkdocs` : ___BREAKING CHANGE___"

                ---8<--- "docs_tools/inclusions/IDE_assertions_feedback.md"

                {{ orange("_Notez que ce changement de comportement par rapport à `pyodide-mkdocs`{
                .orange } concerne aussi les tests publics._") }}
        """,
    ),
    ConfigOptionIdeLink(
        'MODE', str, is_optional=True,
        conf_type = C.Choice(IdeMode.VALUES),
        fake_type = 'None|str',
        line_feed_link = False,
        yaml_desc = f"""
            Change the execution  mode of an IDE (`{IdeMode.no_reveal!r}`, `{IdeMode.no_valid!r}`,
            by default: `null`).
        """,
        docs = f"""
            Change le mode d'exécution des codes python. Les modes disponibles sont :
            { OP } ul_li([
                "`#!py None` : exécutions normales.",
                "`#!py {IdeMode.delayed_reveal!r}` : pour des IDEs n'ayant pas de tests (pas de
                section `tests` ni `secrets`) mais dont on ne veut pas que la solution s'affiche
                dès la première exécution (typiquement, des exercices turtle ou p5). Chaque
                validation fait décroître le nombre d'essais et les solutions et remarques, si
                elles existent, sont révélées une fois tous les essais consommés (une erreur est
                levée durant le build, si l'IDE  a des sections `tests` ou `secrets`, ou s'il a
                un nombre d'essais infini).",
                "`#!py {IdeMode.no_reveal!r}` : exécutions normales, mais les solutions et
                remarques, si elles existent, ne sont jamais révélées, même en cas de succès.
                Le compteur d'essais est ${ BS_MACRO }infty$.",
                "`#!py {IdeMode.no_valid!r}` : quels que soient les fichiers/sections
                disponibles, le bouton et les raccourcis de validations sont inactifs.
                Le compteur d'essais est absent.",
                "`#!py {IdeMode.revealed!r}` : les solutions et remarques, si elles existent,
                sont révélées dès le chargement de la page.
                Le compteur d'essais est absent.",
            ]) { CLO }
        """,
        extra_docs="""
            Une erreur est levée si une valeur est passée en argument alors qu'elle ne correspond
            à aucun `MODE` existant.

            !!! danger "L'utilisation de l'argument `MODE`supprime les routines de validation
            des données des IDEs"

                Si les profiles sont utilisés, toutes les vérifications faites habituellement par
                le thème lorsqu'il construit l'IDE sont supprimées.

                Ceci concerne notamment les vérifications liées aux options suivantes du plugin :

                * {{ config_link('ides.forbid_corr_and_REMs_with_infinite_attempts', 1) }}
                * {{ config_link('ides.forbid_hidden_corr_and_REMs_without_secrets', 1) }}
                * {{ config_link('ides.forbid_secrets_without_corr_or_REMs', 1) }}
        """
    ),
    ConfigOptionIdeLink(
        'MIN_SIZE', int, default=3,
        yaml_desc = "Minimum number of lines of an editor.",
        docs = "Nombre de lignes minimal de l'éditeur.",
        extra_docs="""
            Permet de définir le nombre maximal de lignes de la fenêtre de l'éditeur : si le code
            comporte plus de lignes, des glissières apparaîtront.
        """,
    ),
    ConfigOptionIdeLink(
        'MAX_SIZE', int, default=30,
        yaml_desc = "Maximum number of lines of an editor.",
        docs = "Impose la hauteur maximale possible pour un éditeur, en nombres de lignes.",
        extra_docs = "Permet de définir le nombre minimal de lignes de la fenêtre de l'éditeur.",
    ),
    ConfigOptionIdeLink(
        'TERM_H', int, default=10,
        yaml_desc="Initial number of lines of a terminal (approximative).",
        docs = "Nombre de lignes initiales utilisées pour la hauteur du terminal (_très_ approximatif).",
        extra_docs="""
            Remarques :

            * Le réglage n'est pas très précis et peut devenir erroné selon les règles CSS surchargées
              par vos soins.
            * Cet argument est ignoré pour les macros `IDEv`.
        """,
    ),
    ConfigOptionIdeLink(
        'TEST', str,
        conf_type = C.Choice(NamedTestCase.VALUES, default=NamedTestCase.none),
        line_feed_link = False,
        yaml_desc = """
            Configuration to use when testing this IDE (more options through macro call arguments)
        """,
        docs = """
            Définit la façon dont l'IDE doit être géré lors des tests dans [la page générée
            automatiquement pour tester tous les IDEs de la documentation](--redactors/IDE-tests-page/).
            {{ ul_li([
                "Depuis un fichier de configuration, un fichier" + meta() + " ou l'entête d'une page
                markdown, les valeurs utilisables sont : " + joined_enum_options(NamedTestCase()) + ".",
                "Depuis un appel de macro: les mêmes, ou bien utiliser un object `Case` (défini dans
                l'environnement) pour plus de possibilités."
            ])}}
        """,
        extra_docs="""
            Voir la page dédiée pour plus d'information sur les [tests automatiques des IDEs de la
            documentation](--redactors/IDE-tests-page/).
        """,
    ),
    ConfigOptionIdeLink(
        'TWO_COLS', bool, default=False,
        yaml_desc="Automatically goes in split screen mode if `true`.",
        docs = """
            Si `True`, cet IDE passe automatiquement en mode "deux colonnes" au chargement de la page.
        """,
        extra_docs="""
            Comme tous les autres arguments de macros, il peut être défini au niveau des `meta`
            (fichiers, entêtes, mkdocs.yml).
            <br>À noter que si plusieurs IDEs ont ce réglage à True dans la même page, il n'y
            a aucune garantie sur celui qui sera effectivement en mode "deux colonnes" après
            chargement de la page.
        """
    ),
    ConfigOptionIdeLink(
        'STD_KEY', str, default="",
        yaml_desc="""
            Key to pass as first argument of the `terminal_message` python function (in pyodide),
            to allow to print messages directly in the terminal of an IDE, when the stdout is
            deactivated.
        """,
        docs = """
            Clef à passer en argument de [`terminal_message`](--IDEs-terminal_message) pour
            autoriser son utilisation lorsque la sortie standard est désactivée pendant les
            tests.
        """,
        extra_docs='--8<-- "docs_tools/inclusions/IDE_STD_KEY_validation.md"',
    ),
    ConfigOptionIdeLink(
        'EXPORT', bool, default=False,
        yaml_desc="""
            Add the content of this editor to the zip archive, when extracting all the codes
            of the IDEs in the page.
        """,
        docs = """
            Défini si le contenu de l'éditeur de cet IDE doit être ajouté à l'archive zip
            récupérant les codes de tous les IDEs de la page.
        """,
        extra_docs="""
            Les IDEs marqués avec `#!py EXPORT=True` se voient ajouté un bouton {{btn('zip',
            in_tag='span')}} permettant de télécharger une archive `.zip` avec les contenus
            de tous les éditeurs marqués dans la page en cours.

            Le but de cette fonctionnalité est multiple :

            * Permettre aux utilisateurs de télécharger en une fois tous les contenus des
            éditeurs (marqués) de la page, pour garder une trace de leurs codes.
            * Générer en un clic une archive que l'enseignant peut ensuite récupérer (voir
            plus bas pour ce qui concerne les noms de fichiers donnés aux archives)
            * Il est en fait possible de charger dans la page du site le contenu d'un fichier
            zip en faisant un glissé-déposé de l'archive sur le bouton de création du fichier
            zip de l'un des IDEs marqués de la page. Cela permet de tester rapidement les
            codes d'un élève ou groupe d'élèves. Cette fonctionnalité n'est pas décrite dans
            la documentation des utilisateurs.

            ___Gestion des noms de fichiers des archives zip :___

            * Par défaut, le nom de l'archive zip est créé à partir de l'adresse de la page sur
              le site construit (en excluant la racine du site).
            * Il est possible à l'auteur d'ajouter un préfixe de son choix aux noms des archives,
              en renseignant l'option {{config_link('ides.export_zip_prefix')}}, dans les métadonnées
              de la page.
            * Si l'enseignant envisage de récupérer les archives zip des élèves, il est également
            possible de forcer les utilisateurs à renseigner leur nom au moment de créer l'archive
            zip (ou tout autre chose pouvant servir d'identifiant). Pour cela configurer dans les
            métadonnées l'option {{config_link('ides.export_zip_with_names', val="true")}}.

            Le nom complet des archives est généré selon le modèle suivant, selon les éléments
            activés via les options de configuration : `PREFIX-NAMES-DEFAULT`.
        """,
    ),
))










TERMINAL = MacroConfigSrc.with_default_docs(
    to_page(DOCS_TERMINALS) / '#signature'
)(
    'terminal',
    force_kwargs_index = 1,
    docs = "Valeurs par défaut pour les arguments de la macro `terminal`.",
    yaml_desc = "Default values for arguments used in the `terminal` macro.",
    elements=(

    *_py_globals_copy_gen(
        ID = MOST_LIKELY_USELESS_ID,
        py_name = {'docs': """
            Crée un terminal isolé utilisant le fichier python correspondant (sections
            autorisées: `env`, `env_term`, `post_term`, `post` et `ignore`).
        """ + PMT_5_COMPOSING},
    ),
    ConfigOptionIdeLink(
        'TERM_H', int, default=10,
        docs = "Nombre de lignes initiales utilisées pour la hauteur du terminal (approximatif).",
        yaml_desc="Initial number of lines of a terminal (approximative).",
    ),
    ConfigOptionSrc(
        'FILL', str, default='',
        docs = """
            Commande à afficher dans le terminal lors de sa création.

            {{ red('Uniquement pour les terminaux isolés.') }}
        """,
        yaml_desc="Command used to prefill the terminal (isolated terminals only).",
        # yaml_desc="Commande pour préremplir le terminal (terminaux isolés uniquement).",
    ),
))










PY_BTN = MacroConfigSrc.with_default_docs(
    to_page(DOCS_PY_BTNS) / '#signature'
)(
    'py_btn',
    force_kwargs_index = 1,
    docs = "Valeurs par défaut pour les arguments de la macro `py_btn`.",
    yaml_desc = "Default values for arguments used in the `py_btn` macro.",
    elements=(

    *_py_globals_copy_gen(
        skip_from_macros_docs = MEANINGLESS_ARGS_FOR_PY_BTNS_USER_DOCS,
        ID      = MOST_LIKELY_USELESS_ID,
        py_name = {'docs': """
            Crée un bouton isolé utilisant le fichier python correspondant
            (sections `env` et `ignore` uniquement).
        """ + PMT_5_COMPOSING}
    ),
    ConfigOptionSrc(
        'ICON', str, default="",
        docs = """
            Par défaut, le bouton \"play\" des tests publics des IDE est utilisé.

            Peut également être une icône `mkdocs-material`, une adresse vers une image (lien ou
            fichier), ou du code html.<br>
            Si un fichier est utilisé, l'adresse doit être relative au `docs_dir` du site construit.
        """,
        yaml_desc="Image of the button (by default: `play`  / file path / :icon-material: / url).",
        # yaml_desc="Image pour le bouton (`play` par défaut / fichier / :icon-material: / lien).",
    ),
    ConfigOptionSrc(
        'HEIGHT', int, is_optional=True, fake_type="None|int",
        docs = "Hauteur par défaut du bouton.",
        yaml_desc="Default height for the button",
    ),
    ConfigOptionSrc(
        'WIDTH', int, is_optional=True, fake_type="None|int",
        docs = "Largeur par défaut du bouton.",
        yaml_desc="Default width for the button",
    ),
    ConfigOptionSrc(
        'SIZE', int, is_optional=True, fake_type="None|int",
        docs = "Si définie, utilisée pour la largeur __et__ la hauteur du bouton.",
        yaml_desc="If given, define the height and the width for the button",
    ),
    ConfigOptionSrc(
        'TIP', str, lang_default_access='py_btn.msg',
        docs = "Message à utiliser pour l'info-bulle.",
        yaml_desc="Tooltip message",
    ),
    ConfigOptionSrc(
        'TIP_SHIFT', int, default=50,
        docs = """
            Décalage horizontal de l'info-bulle par rapport au bouton, en `%` (c'est le
            décalage vers la gauche de l'info-bulle par rapport au point d'ancrage de
            la flèche au-dessus de celle-ci. `50%` correspond à un centrage).
        """,
        yaml_desc="Horizontal leftward shifting of the tooltip (%)",
        # yaml_desc="Décalage horizontal de l'info-bulle vers la gauche (%)",
    ),
    ConfigOptionSrc(
        'TIP_WIDTH', float, default=0.0,
        docs = "Largeur de l'info-bulle, en `em` (`#!py 0` correspond à une largeur automatique).",
        yaml_desc="Tooltip width (in em units. Use `0` for automatic width)",
    ),
    ConfigOptionSrc(
        'WRAPPER', str, default='div',
        docs = "Type de balise dans laquelle mettre le bouton.",
        yaml_desc = "Tag type the button will be inserted into",
    ),
))











AUTO_RUN = MacroConfigSrc.with_default_docs(
    to_page(DOCS_RUN_MACRO) / '#signature'
)(
    'run',
    force_kwargs_index = 1,
    docs      = "Valeurs par défaut pour les arguments de la macro `run`.",
    yaml_desc = "Default values for arguments used in the `run` macro.",
    elements  = tuple(_py_globals_copy_gen(
        skip_from_macros_docs = MEANINGLESS_ARGS_FOR_PY_BTNS_USER_DOCS,
        ID       = MOST_LIKELY_USELESS_ID,
        AUTO_RUN = {'default': True},
        py_name  = {'docs': """
            Chemin relatif vers le fichier python (sans extension) à exécuter au chargement de
            la page (sections `env` et `ignore` uniquement).
        """ + PMT_5_COMPOSING},
    ),
))








SECTION = MacroConfigSrc.with_default_docs(
    to_page(DOCS_RESUME) / '#section'
)(
    'section',
    docs = "Valeurs par défaut pour les arguments de la macro `section`.",
    yaml_desc = "Default values for arguments used in the `section` macro.",
    inclusion_profile = InclusionProfile.all_but_yaml_stuff,
    elements = (

    # Required on the python side, but should never be given through "meta", so it has to be
    # non blocking on the config side:
    ConfigOptionSrc(
        "py_name", str, index=0, default="",
        inclusion_profile = InclusionProfile.all_but_yaml_stuff,
        docs="""
            [Fichier python {{ annexe() }}](--ide-files).""" + ACTIVATE_COMPOSITION_INFOS * """
            {{pmt_note("Cette macro _{{orange('ne fonctionne pas')}}_ pour combiner des sections de
            différents fichiers (voir [combinaisons de fichiers à partir de PMT 5^+^](--composite-py))")}}
        """,
        extra_docs = """
            Chemin relatif au dossier contenant le ficher markdown {{ orange('source') }},
            permettant d'accéder au fichier python {{ annexe('principal') }} pour l'IDE.

            * Si l'argument n'est pas renseigné ou est une chaîne vide, l'IDE sera créé vide
            (ex : [bac à sable](--bac_a_sable/)).
            * Le chemin ne donne que le préfixe commun des fichiers {{annexes()}} pour cet IDE,
            et il faut donc {{red("omettre l'extension")}} : si le fichier {{annexe("principal")}}
            est `.../exercice.py`, l'argument `py_name` doit être  `".../exercice"`.
            * Une {{red('erreur')}} est levée si un chemin est donné mais qu'aucun fichier python
            ne peut être trouvé pour les différentes [organisations de fichiers
            supportées](--ide-files-organization).

            NOTE: cette macro ne marche pas avec des contenus python composés de plusieurs fichiers
            différents. Utiliser la macro `composed_section` à la place.
        """,
        yaml_desc = """
            Relative path (no extension) toward the `{exo}.py` file for an IDE, terminal, ...
        """,
    ),
    ConfigOptionSrc(
        'section', str, index=1, is_optional=True,
        docs = "Nom de la section à extraire.",
        yaml_desc="Name of the section to extract.",
    ),
))







# Excluded from all documentations, but kept around...
COMPOSED_PY = MacroConfigSrc.with_default_docs(
    to_page(DOCS_RESUME) / '#composed_py'
)(
    'composed_py',
    docs = "Valeurs par défaut pour les arguments de la macro `composed_py`.",
    yaml_desc = "Default values for arguments used in the `composed_py` macro.",
    force_kwargs_index = 1,
    elements = (

    # Required on the python side, but should never be given through "meta", so it has to be
    # non blocking on the config side:
    ConfigOptionSrc(
        'py_name', Tuple[str], conf_type=C.ListOfItems(C.Type(str), default=['']),
        index=0, is_varargs=True,
        fake_name="py_name", fake_type='str', fake_default='',
        inclusion_profile = InclusionProfile.all_but_yaml_stuff,
        docs="""
            Ensemble des noms des [fichiers python {{ annexe() }}](--ide-files)""" + ACTIVATE_COMPOSITION_INFOS * """, avec les
            [instructions de combinaison nécessaires](--composite-py).
        """,
        yaml_desc = """
            Relative paths (no extension) toward the `{exo}.py` files, with combination
            instructions.
        """,
    ),
    ConfigOptionSrc(
        'sections', str, default='',
        docs = """
            <br>Noms de sections à afficher, séparés par des espaces, virgules et/ou points virgule.
            Par défaut, toutes les sections avec du contenu sont affichées (python et REMs).
        """,
        yaml_desc="List of section names from the composed python code to display.",
    ),
    ConfigOptionSrc(
        'with_headers', bool, default=True,
        docs = """
            Si `#!py False`, les entêtes `# --- PYODIDE:{section} --- #` ne sont pas incorporées au
            contenu.
            {{pmt_note("Dans ce cas, le contenu final affiché peut ne pas être un code python/PMT
            syntaxiquement valide.", lf_location=0)}}
        """,
        yaml_desc="Specify if the `# --- PYODIDE:{section} --- #` headers are added to the content or not.",
    ),
    ConfigOptionSrc(
        'auto_title', bool, default=False,
        docs = """
            Si vrai, le nom du fichier python est utilisé comme titre pour le bloc de code.

            Sans effet si `title` est donné.
        """,
        yaml_desc="If true, use the python filename as title for the code block.",
    ),
    ConfigOptionSrc(
        'name_only', bool, default=True,
        docs = """
            Si vrai, Seul le nom du fichier est utilisé pour construire automatiquement le titre
            du bloc de code. Si faux, le chemin relatif, tel que passé en argument avec `py_name`,
            est utilisé (en y ajoutant l'extension `.py`).

            Sans effet si `title` est donné.
        """,
        yaml_desc="Use the name only or the full relative path argument for the automatic title.",
    ),
    ConfigOptionSrc(
        'title', str, default='',
        docs = "Titre à utiliser pour décrire le bloc de code.",
        yaml_desc = "Title to use for the code block.",
    ),
))








PY = MacroConfigSrc.with_default_docs(
    to_page(DOCS_RESUME) / '#py'
)(
    'py',
    docs = "Valeurs par défaut pour les arguments de la macro `py`.",
    yaml_desc = "Default values for arguments used in the `py` macro.",
    elements = (

    # Required on the python side, but should never be given through "meta", so it has to be
    # non blocking on the config side:
    ConfigOptionSrc(
        'py_name', str, is_optional=True, index=0,
        fake_default = "",
        docs = "Chemin relatif vers le fichier source à utiliser (sans l'extension).",
        yaml_desc="Relative path to the python file to use (without extension).",
    ),
    ConfigOptionSrc(
        'auto_title', bool, default=False,
        docs = """
            Si vrai, le nom du fichier python est utilisé comme titre pour le bloc de code.

            Sans effet si `title` est donné.
        """,
        yaml_desc="If true, use the python filename as title for the code block.",
    ),
    ConfigOptionSrc(
        'name_only', bool, default=True,
        docs = """
            Si vrai, Seul le nom du fichier est utilisé pour construire automatiquement le titre
            du bloc de code. Si faux, le chemin relatif, tel que passé en argument avec `py_name`,
            est utilisé (en y ajoutant l'extension `.py`).

            Sans effet si `title` est donné.
        """,
        yaml_desc="Use the name only or the full relative path argument for the automatic title.",
    ),
    ConfigOptionSrc(
        'title', str, default='',
        docs = "Titre à utiliser pour décrire le bloc de code.",
        yaml_desc = "Title to use for the code block.",
    ),
))








MULTI_QCM = MultiQcmConfigSrc.with_default_docs(
    to_page(DOCS_QCMS) / '#arguments'
)(
    'multi_qcm',
    docs = "Valeurs par défaut pour les arguments de la macro `multi_qcm`.",
    yaml_desc = "Default values for arguments used in the `multi_qcm` macro.",
    elements = (

    # Required on the python side, but should never be given through "meta": must not be blocking:
    ConfigOptionSrc(
        'questions',
        list, index=0, is_varargs=True,
        inclusion_profile = InclusionProfile.not_in(
            InclusionProfile.config,
            InclusionProfile.yaml_schema,
            InclusionProfile.yaml_docs_tree,
        ),
        fake_type="str", fake_default="",
        yaml_desc = """
            From PMT 2.4.0, relative path to a `.json` file containing the informations for the MCQ.
        """,
        docs = """
            À partir de la version 2.4.0, devrait être un unique chemin relatif vers un
            [fichier `json`](--qcms-json) contenant les données pour les différentes
            questions, et potentiellement les valeurs pour tous les autres arguments de
            la macro.
        """,
        extra_docs = """
            Suite à la version `2.4.0` du thème, cet argument devrait être une unique chaîne de
            caractères indiquant le chemin relatif vers un [fichier `json`](--qcms-json) contenant
            les données pour les différentes questions, et potentiellement les valeurs pour tous
            les autres arguments de la macro.
            <br>Ce fichier peut être facilement créé grâce à [l'outil de création de fichier
            `json` pour les qcms](--qcm-builder), disponible dans la documentation du thème.

            {{ pmt_note("Si la déclaration est écrite à la main, chaque argument individuel est
            alors une [liste décrivant une question avec ses choix et réponses](--qcm_question).
            Cette méthode est cependant vivement déconseillée car elle présente de nombreux
            pièges lors de la rédaction de l'appel de macro.") }}
        """,
    ),
    ConfigOptionSrc(
        'description', str, default='',
        docs = """
            Texte d'introduction (markdown) d'un QCM, ajouté au début de l'admonition, avant
            la première question. Cet argument est optionnel.
        """,
        yaml_desc="Introduction text at the beginning of the quiz admonition.",
        # yaml_desc="Texte d'introduction au début de l'admonition du QCM.",
    ),
    ConfigOptionSrc(
        'hide', bool, default=False,
        docs = """
            Si `#!py True`, un masque apparaît au-dessus des boutons pour signaler à l'utilisateur
            que les réponses resteront cachées après validation.
        """,
        yaml_desc = """
            Indicates whether correct/incorrect answers are visible or not after validation.
        """,
        # yaml_desc="Indique si les réponses correctes/incorrects sont visibles à la correction.",
    ),
    ConfigOptionSrc(
        'multi', bool, default=False,
        docs = """
            Réglage pour toutes les questions du qcm ayant une seule bonne réponse, indiquant si
            elles doivent être considérées comme étant à choix simple ou multiples.
        """,
        yaml_desc="Disambiguate MCQ and SCQ if not automatically decidable.",
        # yaml_desc="Permet de clarifier entre QCM et QCU quand ambiguë.",
    ),
    ConfigOptionSrc(
        'shuffle', bool, default=False,
        docs = "Mélange les questions et leurs choix ou pas, à chaque fois que le qcm est joué.",
        yaml_desc="Shuffle questions and their items or not.",
    ),
    ConfigOptionSrc(
        'shuffle_questions', bool, default=False,
        docs = "Mélange les questions uniquement, à chaque fois que le qcm est joué.",
        yaml_desc="Shuffling or not, questions only.",
    ),
    ConfigOptionSrc(
        'shuffle_items', bool, default=False,
        docs="Mélange seulement les items de chaque question, à chaque fois que le qcm est joué.",
        yaml_desc="Shuffling the items of each question or not.",
    ),
    ConfigOptionSrc(
        'admo_kind', str, conf_type=C.Choice(('!!!', '???', '???+', None), default="!!!"),
        yaml_desc="Type of the admonition wrapping the whole MCQ (`!!!`, ...).",
        docs = """
            Type d'admonition dans laquelle les questions seront rassemblées :{{ul_li([
                "`#!py '!!!'` : classique,",
                "`#!py '???'` : dépliable,",
                "`#!py '???+'` : repliable,",
                "`None` : pas d'admonition autour du qcm."
            ])}}
        """,
        extra_docs="""
            `None` permet d'ajouter du contenu markdown autour du qcm de manière plus fine, si besoin.
            {{ pmt_note("À noter que l'admonition restera visible dans le markdown généré par la macro :
            elle sera supprimée dans la couche JS, au moment de l'affichage de la page html") }}.
        """,
    ),
    ConfigOptionSrc(
        'admo_class', str, default="tip",
        yaml_desc="Html class(es) for the admonition wrapping the whole MCQ (default: `tip`).",
        docs = """
            Pour changer la classe d'admonition. Il est également possible d'ajouter d'autres
            classes si besoin, en les séparant par des espaces (exemple : `#!py 'tip inline end
            my-class'`).
        """,
    ),
    ConfigOptionSrc(
        'qcm_title', str, lang_default_access="qcm_title.msg",
        docs = "Pour changer le titre de l'admonition.",
        yaml_desc="Override the default title of the MCQ admonition.",
    ),
    ConfigOptionSrc(
        'tag_list_of_qs', str, conf_type=C.Choice(('ul', 'ol')), is_optional=True,
        docs = """
            {{ ul_li([
                '`#!py None` : automatique (défaut).',
                '`#!py "ol"` : questions numérotées.',
                '`#!py "ul"` : questions avec puces.',
            ]) }}
        """,
        extra_docs="""
            Définit le type de liste html utilisée pour construire les questions.
            <br>Si la valeur est `None`, '`#!py "ol"` est utilisé, sauf s'il n'y a qu'une seule
            question pour le qcm, où c'est alors `#!py "ul"` qui est utilisé.
        """,
        yaml_desc="Enforce the list tag used to build the questions in a MCQ.",
    ),
    ConfigOptionSrc(
        'DEBUG', bool, default=False,
        docs = "Si `True`, affiche dans la console le code markdown généré pour ce qcm.",
        yaml_desc="""
            If `True`, the generated markdown of the MCQ will be printed to the console
            during mkdocs build.
        """,
    ),
    ConfigOptionSrc(
        'SHOW', str, conf_type=C.Choice(MacroShowConfig.VALUES, default=MacroShowConfig.none),
        docs="""
            Affiche des données sur l'appel de macro dans le terminal, durant le `mkdocs serve` :
            {{ul_li([
                "`#!py ''`: Ne fait rien (défaut).",
                "`#!py 'args'`: Affiche tous les arguments de l'appel de macro.",
            ])}}
        """,
        yaml_desc="Display macro related infos in the terminal.",
    ),
))









FIGURE = MacroConfigSrc.with_default_docs(
    to_page(DOCS_FIGURES) / '#signature'
)(
    'figure',
    docs = "Valeurs par défaut pour les arguments de la macro `figure`.",
    yaml_desc = "Default values for arguments used in the `figure` macro.",
    elements = (

    # Required on the python side, but should never be given through "meta": must not be blocking:
    ConfigOptionSrc(
        'div_id', str, default="figure1", index=0,
        docs = """
            Id html de la div qui accueillera la figure ou l'élément inséré dynamiquement.
            <br>À modifier s'il y a plusieurs figures insérées dans la même page.
        """,
        yaml_desc="""
            Html id of the `div` tag that will hold the dynamically generated figure
            (default: `\"figure1\"`).
        """,
    ),
    ConfigOptionSrc(
        'div_class', str, default="",
        docs = f"""
            Classe html à ajouter à la div qui accueillera la figure.<br>La classe
            `{ HtmlClass.py_mk_figure }` est systématiquement présente : il possible de
            surcharger les règles css de cette classe pour obtenir l'affichage voulu.
        """,
        yaml_desc="Html class to add to the `div` tag that will hold dynamically generated figures.",
        # yaml_desc="Classe html à donner à la div qui accueillera la figure.",
    ),
    ConfigOptionSrc(
        'inner_text', str, lang_default_access="figure_text.msg",
        docs = "Texte qui sera affiché avant qu'une figure ne soit tracée.",
        yaml_desc="Text used as placeholder before any figure is inserted.",
    ),
    ConfigOptionSrc(
        'admo_kind', str, default="!!!",
        docs = """
            Type d'admonition dans laquelle la figure sera affichée (`'???'` et `'???+'`
            sont également utilisables).
            <br>Si `admo_kind` est `''`, la `<div>` sera ajoutée sans admonition, et les
            arguments suivants seront alors ignorés.
        """,
        yaml_desc="Type of the admonition wrapping the generated figure (`!!!`, ...).",
        # yaml_desc="Type d'admonition pour la figure (`!!!`, ...).",
    ),
    ConfigOptionSrc(
        'admo_class', str, default="tip",
        docs = """
            Pour changer la classe d'admonition. Il est également possible d'ajouter d'autres
            classes si besoin, en les séparant par des espaces (exemple : `#!py 'tip inline end
            my-class'`).
        """,
        yaml_desc = """
            Html class(es) of the admonition wrapping the generated figure (default: `tip`).
        """,
        # yaml_desc="Classe(s) utilisée(s) pour l'admonition de la figure (défaut: `tip`)."
    ),
    ConfigOptionSrc(
        'admo_title', str, lang_default_access="figure_admo_title.msg",
        docs = "Pour changer le titre de l'admonition.",
        yaml_desc="Admonition title.",
    ),
    ConfigOptionSrc(
        'p5_buttons', str, conf_type=C.Choice(P5BtnLocation.VALUES), is_optional=True,
        docs = f"""
            Si défini, ajoute les boutons start/step/stop pour gérer les animations construites avec
            [p5](--p5_processing/how_to/).

            Les boutons sont ajoutés sur le côté indiqué du canevas, les valeurs possibles étant
            { items_comma_joiner(['`#!py "'+loc+'"`' for loc in P5BtnLocation.VALUES]) }.
        """,
        yaml_desc="""
            Add start, step and stop buttons for p5 animations, on the given side of the canvas.
        """,
    ),
    ConfigOptionSrc(
        'SHOW', str, conf_type=C.Choice(MacroShowConfig.VALUES, default=MacroShowConfig.none),
        docs="""
            Affiche des données sur l'appel de macro dans le terminal, durant le `mkdocs serve` :
            {{ul_li([
                "`#!py ''`: Ne fait rien (défaut).",
                "`#!py 'args'`: Affiche tous les arguments de l'appel de macro.",
            ])}}
        """,
        yaml_desc="Display macro related infos in the terminal.",
    ),
))






ARGS_MACRO_CONFIG = SubConfigSrc(
    'args',
    docs_page_url = to_page(DOCS_CONFIG) / '#{py_macros_path}',
    extra_docs = """
        Réglages des arguments par défaut accessibles pour les différentes macros du thème.
        Explications détaillées dans la page [Aide rédacteurs/Résumé](--redactors/resume/).
    """,
    yaml_desc = """
        Configurations of default values for arguments used in `PyodideMacrosPlugin` macros.
    """,
    # yaml_desc = "Configurations des arguments par défaut pour les différentes macros du thème.",
     elements = (
        IDE,
        TERMINAL,
        PY_BTN,
        AUTO_RUN,
        SECTION,
        COMPOSED_PY,
        PY,
        MULTI_QCM,
        FIGURE,
     )
)
