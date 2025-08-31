"""
Pyodide-MkDocs-Theme is a [MkDocs](https://www.mkdocs.org/) theme for building static websites
that allow to run Python code in browser as:

- code editor snippets (IDEs),
- interactive Python consoles (terminals),
- instant assessments for user-written functions associated with solutions for excercises
  and instructor remarks.

There are many additional features including auto-corrected multiple choice questions (MCQs) and compatibility to use:

- [p5.js animations](https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/p5_processing/how_to/#p5-simple-example),
- dynamic [matplotlib](https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/custom/matplotlib/#exemple-simple) drawings,
- PIL,
- [dynamic mermaid graphs](https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/custom/mermaid/#mermaid-simple-example), and
- mathjax syntax.

## Guarantees

- [x] There are no cookies
- [x] No registration needed
- [x] Created by teachers for teachers and students

## Quickstart

The following commands should install `pyodide_mkdocs_theme`, scaffold a new project and serve a sample website that you can open a browser, usually at `http://127.0.0.1:8000/`.

```console
pip install pyodide_mkdocs_theme
python -m pyodide_mkdocs_theme --new your_project_name
cd your_project_name
pip install -r requirements.txt
mkdocs serve
```

Note: you will need to add `site_url` parameter in `mkdocs.yml`
in order to run `mkdocs build` command.

## Links

- [Online documentation](https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/) (French only)
- [GitLab repository](https://gitlab.com/frederic-zinelli/pyodide-mkdocs-theme)

## Flexibility

Pyodide-MkDocs-Theme is highly configurable on many aspects:

- theme configuration,
- add your own macros to the theme,
- add custom logic here or there,
- and quite a few other options.

![IDE capture example](https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/assets/pyodide-mkdocs-theme-ex.png)

## How it works

The technology enabling this feat is called [Pyodide](https://pyodide.org/en/stable/). It is associated with JavaScript elements such as [jquery.terminal](https://terminal.jcubic.pl/api_reference.php) and [ACE Editor](https://ace.c9.io/).

Pyodide uses WebAssembly to bridge between Python and JavaScript and provide an environment for manipulating the JavaScript DOM with Python, or vice versa for manipulating Python from JavaScript.

Pyodide-MkDocs-Theme is based on a modern [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) theme for MkDocs static site generator.

## Project history

This project is a complete redesign of the prototype [`pyodide-mkdocs`](https://bouillotvincent.gitlab.io/pyodide-mkdocs/) from [Vincent Bouillot](https://gitlab.com/bouillotvincent/).

"""

