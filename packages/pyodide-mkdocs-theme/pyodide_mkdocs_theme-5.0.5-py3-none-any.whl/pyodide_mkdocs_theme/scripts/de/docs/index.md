
_Current version : {{ config.plugins.pyodide_macros.version }}_

<br>

---

<div style="display:flex;gap:2em;align-items:top">
<svg viewBox="0 0 512 512"
    height="24px" width="24px" version="1.1" xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" fill="gray">
    <g>
        <path class="st0" d="M329.368,237.908l42.55-39.905c25.237-23.661,39.56-56.701,39.56-91.292V49.156 c0.009-13.514-5.538-25.918-14.402-34.754C388.24,5.529,375.828-0.009,362.314,0H149.677c-13.514-0.009-25.918,5.529-34.754,14.401 c-8.872,8.837-14.41,21.24-14.402,34.754v57.554c0,34.591,14.315,67.632,39.552,91.292l42.55,39.888 c2.352,2.205,3.678,5.272,3.678,8.493v19.234c0,3.221-1.326,6.279-3.67,8.475l-42.558,39.905 c-25.237,23.653-39.552,56.702-39.552,91.292v57.554c-0.009,13.514,5.529,25.918,14.402,34.755 c8.836,8.871,21.24,14.409,34.754,14.401h212.636c13.514,0.008,25.926-5.53,34.763-14.401c8.863-8.838,14.41-21.241,14.402-34.755 v-57.554c0-34.59-14.324-67.64-39.56-91.292l-42.55-39.896c-2.344-2.205-3.678-5.263-3.678-8.484v-19.234 C325.69,243.162,327.025,240.095,329.368,237.908z M373.942,462.844c-0.009,3.273-1.266,6.055-3.403,8.218 c-2.162,2.135-4.952,3.402-8.226,3.41H149.677c-3.273-0.009-6.055-1.275-8.225-3.41c-2.128-2.163-3.394-4.945-3.402-8.218v-57.554 c0-24.212,10.026-47.356,27.691-63.91l42.55-39.906c9.914-9.285,15.538-22.274,15.538-35.857v-19.234 c0-13.592-5.624-26.58-15.547-35.866l-42.541-39.896c-17.666-16.555-27.691-39.69-27.691-63.91V49.156 c0.008-3.273,1.274-6.055,3.402-8.226c2.17-2.127,4.952-3.394,8.225-3.402h212.636c3.273,0.009,6.064,1.275,8.226,3.402 c2.136,2.171,3.394,4.952,3.403,8.226v57.554c0,24.22-10.026,47.355-27.683,63.91l-42.55,39.896 c-9.922,9.286-15.547,22.274-15.547,35.866v19.234c0,13.583,5.625,26.572,15.547,35.874l42.55,39.88 c17.658,16.563,27.683,39.707,27.683,63.918V462.844z"></path>
        <path class="st0" d="M256,248.674c10.017,0,18.131-8.122,18.131-18.139c3.032-12.051,9.397-23.161,18.578-31.757l42.542-39.888 c13.592-12.739,21.602-30.448,22.446-48.984H154.302c0.844,18.536,8.854,36.245,22.438,48.984l42.541,39.888 c9.19,8.596,15.547,19.706,18.579,31.757C237.861,240.552,245.983,248.674,256,248.674z"></path>
        <path class="st0" d="M256,267.796c-10.017,0-18.139,8.122-18.139,18.139c0,10.009,8.122,18.131,18.139,18.131 c10.017,0,18.131-8.122,18.131-18.131C274.131,275.918,266.017,267.796,256,267.796z"></path>
        <path class="st0" d="M256,332.137c-10.017,0-18.139,8.122-18.139,18.14c0,10.009,8.122,18.131,18.139,18.131 c10.017,0,18.131-8.122,18.131-18.131C274.131,340.259,266.017,332.137,256,332.137z"></path>
        <path class="st0" d="M239.876,389.742l-66.538,66.538h165.315l-66.537-66.538C263.21,380.845,248.782,380.845,239.876,389.742z"></path>
    </g>
</svg> <div class='gray'>As long as this animated hourglass is present in the top banner, some elements of the page are inactive:<br>the Pyodide environment is starting up.</div>
</div>

---


## Preview `IDE`

A full installation gives the following result result by adding this command in a markdown file:

```markdown
{% raw %}{{ IDE('exo') }}{% endraw %}
```

<br>

{{ IDE('exo') }}



## Preview `section`


```markdown
{% raw %}{{ section('exo', 'secrets') }}{% endraw %}
```

<br>

{{ section('exo', 'secrets') }}


## Preview `terminal`


```markdown
{% raw %}{{ terminal(FILL="3+9") }}{% endraw %}
```

<br>

{{ terminal(FILL="3+9") }}



## Preview `multi_qcm`

??? help "Macro call, in the markdown file"

    ```markdown
    {% raw %}
    
    {{ multi_qcm(
        [
        """
        The following code was entered:
        ```python title=''
        n = 8
        while n > 1:
            n = n//2
        ```
    
        What is the value of `n` after the code is executed?
        """,
            [
                "0",
                "1",
                "2",
                "4",
            ],
            [2]
        ],
        [
            "Which machine will execute a JavaScript program included in an HTML page?",
            [
                "The user's machine where the web browser is running.",
                "The user's machine or the server, whichever is more available.",
                "The user's machine or the server, depending on the confidentiality of the data handled.",
                "The web server where the HTML page is stored."
            ],
            [1],
        ],
        [
            """
            Tick all the correct answers:
            ```python title=''
            furniture = ['table', 'chest of drawers', 'wardrobe', 'cupboard', 'sideboard']
            ```
            """,
            [
                "`#!py furniture[1]` is `#!py table`",
                "`#!py furniture[1]` is `#!py chest of drawers`",
                "`#!py furniture[4]` is `#!py sideboard`",
                "`#!py furniture[5]` is `#!py sideboard`",
            ],
            [2, 3],
            {'multi':True}
        ],
        multi = False,
        qcm_title = "A multiple-choice quiz with automatic shuffling of the questions (button at the bottom to restart)",
        DEBUG = False,
        shuffle = True,
        description = "_(An additional description can be added at the beginning of the admonition...)_\n{style=\"color:orange\"}"
    ) }}
    
    {% endraw %}
    ```

<br>


{{ multi_qcm(
    [
    """
    The following code was entered:
    ```python title=''
    n = 8
    while n > 1:
        n = n//2
    ```

    What is the value of `n` after the code is executed?
    """,
        [
            "0",
            "1",
            "2",
            "4",
        ],
        [2]
    ],
    [
        "Which machine will execute a JavaScript program included in an HTML page?",
        [
            "The user's machine where the web browser is running.",
            "The user's machine or the server, whichever is more available.",
            "The user's machine or the server, depending on the confidentiality of the data handled.",
            "The web server where the HTML page is stored."
        ],
        [1],
    ],
    [
        """
        Tick all the correct answers:
        ```python title=''
        furniture = ['table', 'chest of drawers', 'wardrobe', 'cupboard', 'sideboard']
        ```
        """,
        [
            "`#!py furniture[1]` is `#!py table`",
            "`#!py furniture[1]` is `#!py chest of drawers`",
            "`#!py furniture[4]` is `#!py sideboard`",
            "`#!py furniture[5]` is `#!py sideboard`",
        ],
        [2, 3],
        {'multi':True}
    ],
    multi = False,
    qcm_title = "A multiple-choice quiz with automatic shuffling of the questions (button at the bottom to restart)",
    DEBUG = False,
    shuffle = True,
    description = "_(An additional description can be added at the beginning of the admonition...)_\n{style=\"color:orange\"}"
) }}

