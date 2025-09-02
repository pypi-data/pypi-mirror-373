"""
p5.js wrapper for Pyodide-MkDocs-Theme, by Frédéric Zinelli.

Basic use:

1. Import p5 as a namespace (no wildcard imports!):
2. Define the setup and draw callbacks, using calls to the original p6 JS functions,
   using`p5.functionName()` syntax.
3. Call `p5.run(setup, draw, preload, target="div_id")` at the end of the code (`preload`
   is optional / `target` is also optional and defaults to the current PMT option value
   for `args.figure.div_id`).

NOTE:
    * Use the `{{ figure() }}` macro to create the target elements in the page.
    * Use `{{ figure(..., p5_buttons="left") }}` (or "right") to also insert start and stop
    buttons, controlling the sketch event loop.
    * Any number of animation can be built in the page, through any number of IDEs, terminals,
    or py_btns as long as each of them targets a different DOM element.



Example:

```python
import p5

def setup():
    p5.createCanvas(200,200)
    p5.background(0)

def draw():
    p5.circle(p5.mouseX, p5.mouseY, 50)

p5.run(setup, draw)                     # Targets "figure1"
p5.run(setup, draw, target='figure2')   # Second figure with the same behavior
```


Help about p5 use:
    - https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/p5_processing/
    - https://p5js.org/reference/


Sources:
    - https://p5js.org/
    - https://github.com/processing/p5.js/wiki/Global-and-instance-mode
    - https://forge.apps.education.fr/basthon/basthon-kernel/-/tree/master/packages/kernel-python3/src/modules/p5/p5?ref_type=heads
      (p5 adaptation for Basthon, by Romain Casati)
"""

# pylint: disable=E0401, C0103, C0116, C0321, C0415, W0105, W0613, W0621





from typing import Iterable, Union, Any, Callable, Dict


def __define():

    import js                                   # type: ignore
    from pyodide.ffi import to_js               # type: ignore
    from pyodide.ffi.wrappers import (          # type: ignore
        add_event_listener,
        remove_event_listener,
    )

    from functools import wraps


    JS_P5 = js.p5
    GLOB_SKETCH = None
    """
    Current sketch to handle. Automatically sent back when accessing js.p5 attributes.
    Use js.p5 (global mode) if sketch is None.
    """


    DEFAULT_ID: str = js.config().argsFigureDivId

    HANDLERS_TRACKER: Dict[str,'Sketch'] = {}       # type: ignore



    # ENTRY POINT from PMT runtime:
    def run(
        setup:Callable,
        draw:Callable=None,
        preload:Callable=None,
        *,
        target:str=None,
        stop_others:bool=True,
        **routines
    ) -> None :
        """
        Starts a p5 animation with the given callbacks and target element in the DOM.

        Note: THIS P5 PACKAGE IS NOT RELATED IN ANY WAY TO THE P5 PACKAGE AVAILABLE ON PyPI.
              If you need documentation about how to use the present package, seek for:

              - The related documentation on PMT:
                    https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/p5_processing/

              - The documentation of the original javascript version of p5:
                    https://p5js.org/reference/


        ## Example:

        ```python
        import p5

        def setup():
            p5.createCanvas(200,200)
            p5.background(0)

        def draw():
            p5.circle(p5.mouseX, p5.mouseY, 50)

        p5.run(setup, draw)                     # Targets "figure1"
        p5.run(setup, draw, target='figure2')   # Second figure with the same behavior
        ```

        Note that the `target` argument is a keyword only argument.



        ## Stopping (or not) existing animations:

        By default, `p5.run` will stop all running animations in the page when creating a new one.
        If several animations need to be running at the same time, the `stop_others`
        keyword argument can be passed with its value set to `False` :

        ```python
        p5.run(..., stop_others=False)
        ```
        WARNING: Beware of global shared states, when several animations are running concurrently!


        ## Other events:

        Other routines can also be used, passing them as additional keyword arguments:

        ```python
        import p5

        def setup():
            p5.createCanvas(200,200)
            p5.background(50)

        def mouseDragged(e):      # NOTE: the argument is not optional, in PMT context.
            terminal_message(0, e.x, e.y)

        p5.run(setup, mouseDragged=mouseDragged, target='figure2')
        ```

        ---

        Help about p5 use:
            - https://p5js.org/reference/
            - https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/p5_processing/
        """
        routines.update({'setup':setup, 'draw':draw, 'preload':preload})
        Sketch().run(target, stop_others=stop_others, **routines)




    class Sketch:
        """
        Parent class that can be used to build children classes that will provide complete
        encapsulation of the animations.
        Use it to build complex animations while avoiding any global shared state.

        See the documentation to know how to use it:

        https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/p5_processing/p5_sketch/
        """

        target: str
        """ Html id of the figure/div where to draw the animation. """

        p5: Any  # JsProxy; PUBLIC/clearer alias for sketch!

        __sketch:     Any = None # JsProxy
        __p5instance: Any = None # JsProxy
        __routines: Dict[ str, Callable[[],None] ]
        """ All p5 functions/events that will need to be bound to the sketch object. """

        __proxies: list
        __buttons: dict # {name: (button_elt, python_cbk)}


        __consumed = False
        """
        Class level flag: if true on instance level, consider the instance as improper to
        use for anim.run(...) call.
        """

        #------------------------------------------------------------


        def run(self, target:str=None, stop_others=True, **_):
            """
            Starts a p5 animation, taking the @target id.
            If @stop_others is True, all existing animations will be stopped before creating this one.
            """
            if self.__consumed:
                raise ValueError(
                    f"The current instance is already in use ({self.target}). Create another one."
                )

            self.__consumed = True
            self.target     = target or DEFAULT_ID

            self.__proxies  = []
            self.__buttons  = {}
            self.__routines = {
                method._p5_hook: method         # pylint: disable=W0212
                    for method in map(lambda name: getattr(self, name), dir(self.__class__))
                    if callable(method) and hasattr(method, '_p5_hook')
            }
            self.__routines.update(_) # Arguments (given last) override the methods, if mixed.

            # By default, do not allow several animations to run at once (avoids troubles because
            # of the shared GLOB_SKETCH object, if the code has not been written using the class):
            if stop_others:
                old_animations: Iterable[Sketch] = HANDLERS_TRACKER.values()
                for old_anim in old_animations:
                    if old_anim.p5.isLooping():
                        old_anim.p5.noLoop()

            # Destroy the current animation's target if it already exists:
            if target in HANDLERS_TRACKER:
                anim: Sketch = HANDLERS_TRACKER.pop(target)
                anim.remove()
                # Popping allows for more flexibility, in case of troubles or when developing
                # (if one`remove()` triggers an error here, it won't occur on the next run).

            HANDLERS_TRACKER[self.target] = self
            self.__p5instance = js.p5.new(
                self.__to_proxy(self.__call__),     # Already contextualized!
                self.target,
            )


        def __log(self, *a,**kw):
            """ Debugging logger, if needed """
            js.console.log(self.target, *a, str(kw))
            # print(*a, **kw)


        def __call__(self, js_sketch):

            # Make sure the div is emptied (needed in case a default message is in the
            # {{ figure() }} macros):
            js.document.getElementById(self.target).replaceChildren()

            # self.__log('Calling P5Handler')
            self.p5 = self.__sketch = js_sketch

            self.__handle_buttons(True)
            for prop, py_cbk in self.__routines.items():
                self.__build_proxy_cbk_with_global_sketch_rotation(
                    js_sketch, prop, py_cbk or (lambda *_a,**_kw: None)
                )
            # self.__log("Done with P5Handler call")



        def __build_proxy_cbk_with_global_sketch_rotation(self, js_sketch, prop, py_cbk):
            """
            Create and register a JsProxy function, based on the user defined python function,
            wrapped in another function that will ensure the nonlocal SKETCH object is updated
            before the user function is called so that the animation/drawing is always done in
            the right DOM element.
            """
            # self.__log(f'{prop}: creating proxy and binding sketch')

            @wraps(py_cbk)
            def py_wrapper(*a, **kw):
                nonlocal GLOB_SKETCH
                GLOB_SKETCH = js_sketch
                return py_cbk(*a, **kw)

            # Create and store the JsProxy (setup, draw, ...) then affect it to the sketch object
            proxy = self.__to_proxy(py_wrapper)
            setattr(js_sketch, prop, proxy)
                # See: https://github.com/processing/p5.js/wiki/Global-and-instance-mode
                # Note: JS method binding isn't needed here because of the wrapper function:
                # all method calls are going through the module p5.__getattr__ and then are
                # redirected to the js_sketch instance.


        def __to_proxy(self, cbk):
            """
            Create a JsProxy for the given callback and store its reference for later destruction.
            """
            proxy = to_js(cbk)
            self.__proxies.append(proxy)
            return proxy



        def start(self, _event):
            """ Basthon legacy """
            self.__sketch.loop()

        def stop(self,  _event):
            """ Basthon legacy """
            self.__sketch.noLoop()

        def step(self,  _event):
            self.__sketch.noLoop()
            self.__sketch.redraw()



        def __handle_buttons(self, add:bool):
            """
            Add or remove the event listeners for the start and stop buttons (if needed).

            WARNING:
                Removal of event listeners is done an a different method call, meaning the JsProxy
                sent back by `js.document.getElementById` will _NOT_ return the same instance as
                the first time. And because listeners identification is always done using (at some
                point) the id of the JS object, the proxy _HAS_ to be stored with the callback so
                that the listener removal can properly happen.
            """
            if add:
                for prop in ('start','stop', 'step'):

                    btn_id = f'{ prop }-btn-{ self.target }'
                    elt    = js.document.getElementById(btn_id)
                    if not elt: continue

                    cbk = getattr(self, prop)
                    # NOTE: NOT proxying a JsProxy, but a python function.

                    self.__buttons[prop] = (elt, cbk)
                    add_event_listener(elt, 'click', cbk)
            else:
                for elt,cbk in self.__buttons.values():
                    remove_event_listener(elt, 'click', cbk)
                self.__buttons.clear()


        def remove(self):
            """
            Destroy all proxies + unbind the js objects.
            """
            nonlocal GLOB_SKETCH

            # self.__log('Remove buttons listeners')
            self.__handle_buttons(False)

            # self.__log('Stop drawing + cleanup p5 instance & DOM')
            # Protect against a possible failure on the previous run, implying missing objects:
            if self.__sketch:     self.__sketch.noLoop()
            if self.__p5instance: self.__p5instance.remove()

            # self.__log('Destroy all JsProxies')
            for proxy in self.__proxies:
                proxy.destroy()
            self.__proxies.clear()
            self.__routines.clear()

            # self.__log('Remove JsProxies references')
            self.__p5instance = self.p5 = self.__sketch = GLOB_SKETCH = None





    def __getattr__(prop):
        """
        Enforce p5 contracts within PMT, and handle redirections of p5 functions or constants
        at call time.
        """
        if prop=='__all__':
            raise ImportError(
                "Wildcard imports of p5 is forbidden within Pyodide-MkDocs-Theme context.\n"
                "Import the module as a namespace instead:\n    import p5\n    p5.createCanvas()"
            )
        try:
            return getattr(GLOB_SKETCH or JS_P5, prop)
        except:
            raise AttributeError(f"p5.{ prop } is not defined") from None


    return run, __getattr__, Sketch





run, __getattr__, Sketch = __define()


def __dir__():
    return ['run', 'Sketch', 'hook']


def hook(name_or_method:Union[str,Callable]):
    """
    Decorator to mark an instance method as being a p5 function that should normally
    be passed to the `p5.run(...)` function. With this decorator, the class will find
    and register the functions for p6 on its own.
    The method name should match the name of the p5.js original function, otherwise,
    a string can be passed to the decorator as argument, with the desired camelCase
    function name.
    """
    def relay(method):
        method._p5_hook = name          # pylint: disable=W0212
        return method

    if callable(name_or_method):
        name = name_or_method.__name__
        return relay(name_or_method)
    else:
        name = name_or_method
        return relay
