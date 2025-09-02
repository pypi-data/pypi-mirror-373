# How the templates directory works/is used




## At build time

- MkDocs gathers all the files in the tree hierarchy that are either images, css or js files and uses those as base content for the built site directory (keeping the tree structure).
  Note that the templates content from mkdocs-material is gathered first, since PMT is extending material.
- The content of `docs/` is then merged into the destination directory, potentially overriding files that end up at the same final location.
- Html files in the templates directory _may_ be used as jinja templates for this or that, especially `main.html` and `base_pmt.html`, but do not end in the final website (afaik...)


This defines the base content of the root directory of the built site.
<br>Markdown files in the docs are ___then___ rendered to html and added to it at the appropriate locations.




## At runtime/page load time

The big question is: "what script is loaded when?".

All js scripts are systematically present on the server/built site, but their insertion/actual use in one page may depend on how they are registered.
<br>Here is how PMT is loading everything (JS + CSS files in `templates/`): <br><br>



1. CSS files (see `pyodide-css/`) are __always present__ in the Jinja `libs` block (of the `base_pmt.html` file), even if the related elements are not present in the page. This allows:

    - To get consistency on the end users' side, if they start to add their own overloaded rules.
    - These files are inserted before the css files coming from `mkdocs.yml:extra_css`, so that the user _can_ overload the settings coming from the theme.

1. `templates/js-libs` scripts are __always present__ through the `libs` block, meaning, in the `<head>` of the page. Those are scripts that _have_ to be defined before the content of the page is defined.
<br>(Note: this is not entirely true anymore, because most of PMT's scripts are now loaded as modules, but this still applies for some of them (mathjax, config, ...))

1. Some other CDNs and any data related to IDEs config or equivalent are loaded in the `libs` block. See `pyodide_mkdocs_theme/pyodide_macros/html_dependencies/deps.py`:
    * jQuery: always
    * pyodide, ace, jQuery terminal: __only if needed__
    * ...

    ---

1. Extra stylesheets registered by the user in `mkdocs.yml:extra_css/` are loaded at the beginning of the `<body>`. They are __always present__.


1. The html page content is then executed (stuff coming from the original markdown file).


1. `templates/js-per-pages` scripts are run at the end of the page content (added __through mkdocs `on_page_context` event__). They are loaded __only if they are required in the page__.
<br>This reduces the amount of code/data to load, and _also_ allows to not start the pyodide environment when not needed.

    ---

1. JS scripts that are registered into `mkdocs.yml:extra_javascript` are then run. They are __always present__ in ___all___ rendered pages. They are added in the Jinja `scripts` block, meaning they end up at the very end ot the `<body>`.


1. `templates/js-scripts` scripts are finally run. They are __always present__, and added in as a last step of the Jinja `scripts` block.
