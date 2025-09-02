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

import os
import sys
from pathlib import Path
from argparse import ArgumentParser
from contextlib import redirect_stdout


from .__version__ import __version__
from .basthon_p5_to_pmt import update_basthon_p5_code


PMT_SCRIPTS = 'scripts'

MIMES = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types"
LANGS = ('de', 'en', 'fr')




parser = ArgumentParser(
    'pyodide_mkdocs_theme',
    description = "Scripts for pyodide-mkdocs-theme",
    epilog = "Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli. "
             "This program comes with ABSOLUTELY NO WARRANTY."
)
parser.add_argument(
    '-v', '--version', action='version', version=f'pyodide-mkdocs-theme {__version__}'
)
parser.add_argument(
    '-n', '--new', default="",
    help='Starts a new PMT project, creating a directory with the given name in the current '
         'folder, then adds some basic contents to the directory (docs and examples, mkdocs.yml, '
         'requirements.txt, main.py, pyodide_plot.py). '
         'Works with the --lang argument.'
)
parser.add_argument(
    '-m', '--mime', action='store_true',
    help='Open a page in the browser, to the MDN documentation about MIME types (useful '
         'when using pyodide_downloader).'
)
parser.add_argument(
    '--lang', action='extend', nargs='*', choices=LANGS, default=[],
    help=f'Optional. Choices: { ", ".join(LANGS) }. '
         'Print the base python code to customize some messages. '
         'Can also be used with other arguments to get the information in languages other '
         'than "fr", when relevant.'
)
parser.add_argument(    # Effect strictly equivalent to --lang, but present for semantic
    '-M', '--macros', action='store_true',
    help='Print the content a `main.py` file usable to create custom macros for the '
         'documentation. The file also contains the code used to modify PMT messages. '
         'You can remove it if you don\'t need it.'
         'Works with the --lang argument (defaults to english if the language is not available).'
)
parser.add_argument(
    '-P', '--plot', action='store_true',
    help='Print the content of the PyodidePlot declaration file, helping to run it locally.'
)
parser.add_argument(
    '-p', '--py', action='store_true',
    help='Print an example of python file, for {{IDE(...)}} or {{terminal(...)}} macros. '
         'Works with the --lang argument (defaults to english if the language is not available).'
)
parser.add_argument(
    '-t', '--toolbox', action='store_true',
    help='Print the content of the python file defining the coding tools to help running the '
         'python files of the documentation locally.'
)
parser.add_argument(
    '-y', '--yml', action='store_true',
    help='Print a base configuration for the mkdocs.yml file. '
         'Works with the --lang argument.'
)
parser.add_argument(
    '-F', '--file', default="",
    help='When used in combination with one of --lang, --py or --yml, the information will '
         'be written into the given file instead of the stdout (any existing content will '
         'be overwritten / use an absolute path or a path relative to the cwd).'
)
parser.add_argument(
    '-C', '--copy', action='store_true',
    help='Acts like --file, but using the original name of the file.'
)


parser.add_argument(
    '-B', '--basthonP5', action='extend', nargs='*', type=str, default=[],
    help='Converts the given python file(s), written for a p5 animation in Basthon, to the '
         'equivalent p5 code for PMT. The html id of the target container (for PMT) can be '
         'given through the --id argument. Use also the --tail argument, to adapt the names '
         'of the files after conversion.'
)
parser.add_argument(
    '-i', '--id', default='figure1', type=str,
    help='Html id of the figure receiving a p5 animation, when converting a Basthon python file '
         'to that equivalent PMT file. To use with the --basthonP5 argument.'
)
parser.add_argument(
    '--tail', default='_pmt',
    help='Define what to add of remove to the original filenames when converting p5 Basthon codes '
    'to PMT codes. By default, "exo.py" will become "exo_pmt.py". The tail part can be modified '
    'through this argument. If a negative integer is given, it will be the number of characters '
    'removed from the original name: `--tail -4` would convert "exo1_src.py" to "exo1.py".'
)







def main():
    # pylint: disable=multiple-statements


    def get_filepath_in_lang(pathname:str=None):
        """
        Build the path to a given file, with automatic fallback to the models directory if it
        doesn't exist in the desired lang directory.
        """
        if not pathname:
            return lang_path

        file = build_path_to_file(lang_path, pathname) or build_path_to_file(models_path, pathname)

        if file is None:
            raise FileNotFoundError(
                f'No script source for { pathname }. Please contact the author and raise an issue'
                ' on https://gitlab.com/frederic-zinelli/pyodide-mkdocs-theme/-/issues'
            )
        return file


    def build_path_to_file(src_dir:Path, pathname:str):
        path = src_dir
        for segment in pathname.split('/'):
            path /= segment
        out = path if path.is_file() else None
        return out


    def copy_folder_content(src_dir:Path, project:Path, skip_if_exist=False):
        for src in src_dir.rglob('*.*'):
            target = project / src.relative_to(src_dir)
            if skip_if_exist and target.exists():
                continue
            content = src.read_bytes()
            target.parent.mkdir(exist_ok=1, parents=1)
            target.touch(exist_ok=1)
            target.write_bytes(content)


    def initiate_project(args):
        """
        Create the initial stub for a new PMT based documentation project, merging the content
        of the desired lang directory, with the files extra files present in the models directory
        """
        project = Path(args.new)
        project.mkdir(parents=True)     # raise if already exists

        lang_directory = get_filepath_in_lang()

        copy_folder_content(lang_directory, project)
        copy_folder_content(models_path,    project, skip_if_exist=True)





    def handle_one_file(args, prop:str):

        src_file = arg_to_targets[prop]
        if args.file or args.copy:
            handle_one_file_writing_to_disk(args, src_file)
        else:
            display_file(src_file)


    def handle_one_file_writing_to_disk(args, filename):
        target_name = args.file or Path(filename).name      # Ensure only a filename

        path = Path(target_name)
        with open(path, 'w', encoding='utf-8') as f, redirect_stdout(f):
            display_file(filename)


    def display_file(filename:str):
        """ Display the base code for GUI messages customizations """

        src = get_filepath_in_lang(filename)
        txt = src.read_text(encoding='utf-8')
        print(txt)


    #------------------------------------------------------------------------




    if len(sys.argv) < 2:
        sys.argv.append('-h')

    args = parser.parse_args()

    if not args.lang:
        args.lang.append('fr')

    # print(args)
    # return


    lang_folder     = args.lang[0]
    pmt_scripts_dir = Path(__file__).parent / PMT_SCRIPTS
    lang_path       = pmt_scripts_dir / lang_folder
    models_path     = pmt_scripts_dir / 'models'
    did_some        = False
    raise_toolbox   = False

    arg_to_targets = {
        'macros':   'main.py',
        'plot':     'pyodide_plot.py',
        'py':       'docs/exo.py',
        'toolbox':  'toolbox.py',
        'yml':      'mkdocs.yml',
        'lang':     'main.py' ,
    }

    if args.basthonP5:
        for p5_file in args.basthonP5:
            update_basthon_p5_code(p5_file, args.id, args.tail)
        return


    if args.mime:
        # Do not update did_some here (not related to --lang)
        import webbrowser
        webbrowser.open(MIMES, new=2)


    if args.new:
        did_some = True
        initiate_project(args)


    props = ['macros','plot','py','toolbox','yml']
    for prop in props:
        if getattr(args, prop):
            did_some = True
            handle_one_file(args, prop)

            if prop=='toolbox':
                cwd = os.getcwd()
                if cwd not in sys.path:
                    raise_toolbox = True


    if not did_some and args.lang:
        did_some = True
        handle_one_file(args, 'lang')


    if raise_toolbox:
        raise SystemError(
            f"WARNING: your CWD ({ cwd !r}) is not present in `sys.path`: If you cannot import the "
            "`toolbox` module from other files, you'll need to add the CWD to your PYTHONPATH. "
            "\n(note: adding it to sys.path will also work, but for the current session only)"
        )

    if not did_some and not args.mime:
        raise ValueError(f"Invalid call:\n{args!r}")




if __name__ == '__main__':
    main()
