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


from collections import defaultdict
import ast
import re
import sys
from pathlib import Path
from typing import Callable, List, Tuple

sys.setrecursionlimit(10000)



P5_NAMES = set('''
BASELINE                 BEVEL                    BOTTOM                   CENTER
CHAR                     CHORD                    ESCAPE                   FLAT
FLOAT                    LEFT                     MITER                    NORMAL
REPEAT                   RIGHT                    ROUND                    TOP
WORD
ADD                      ALT                      ARROW                    AUDIO
AUTO                     AXES                     BACKSPACE                BEZIER
BLEND                    BLUR                     BOLD                     BOLDITALIC
BURN                     CLAMP                    CLOSE                    CONTAIN
CONTROL                  CORNER                   CORNERS                  COVER
CROSS                    CURVE                    DARKEST                  DEGREES
DEG_TO_RAD               DELETE                   DIFFERENCE               DILATE
DODGE                    DOWN_ARROW               ENTER                    ERODE
EXCLUSION                FALLBACK                 FILL                     GRAY
GRID                     HALF_FLOAT               HALF_PI                  HAND
HARD_LIGHT               HSB                      HSL                      IMAGE
IMMEDIATE                INVERT                   ITALIC                   LABEL
LANDSCAPE                LEFT_ARROW               LIGHTEST                 LINEAR
LINES                    LINE_LOOP                LINE_STRIP               MIRROR
MOVE                     MULTIPLY                 NEAREST                  OPAQUE
OPEN                     OPTION                   OVERLAY                  P2D
PI                       PIE                      POINTS                   PORTRAIT
POSTERIZE                PROJECT                  QUADRATIC                QUADS
QUAD_STRIP               QUARTER_PI               RADIANS                  RADIUS
RAD_TO_DEG               REMOVE                   REPLACE                  RETURN
RGB                      RGBA                     RIGHT_ARROW              SCREEN
SHIFT                    SMOOTH                   SOFT_LIGHT               SQUARE
STROKE                   SUBTRACT                 TAB                      TAU
TESS                     TEXT                     TEXTURE                  THRESHOLD
TRIANGLES                TRIANGLE_FAN             TRIANGLE_STRIP           TWO_PI
UNSIGNED_BYTE            UNSIGNED_INT             UP_ARROW                 VERSION
VIDEO                    WAIT                     WEBGL                    WEBGL2
accelerationX            accelerationY            accelerationZ            alpha
ambientLight             ambientMaterial          angleMode                append
applyMatrix              arc                      arrayCopy                as_object_map
background               baseColorShader          baseMaterialShader       baseNormalShader
baseStrokeShader         beginClip                beginContour             beginGeometry
beginShape               bezier                   bezierDetail             bezierPoint
bezierTangent            bezierVertex             blend                    blendMode
blue                     box                      brightness               buildGeometry
byte                     callRegisteredHooksFor   camera                   canvas
char                     clearDepth               clearStorage             clip
colorMode                cone                     constrain                createA
createAudio              createButton             createCamera             createCanvas
createCapture            createCheckbox           createColorPicker        createDiv
createElement            createFileInput          createFilterShader       createFramebuffer
createGraphics           createImage              createImg                createInput
createModel              createNumberDict         createP                  createRadio
createSelect             createShader             createSlider             createSpan
createStringDict         createVector             createVideo              createWriter
cursor                   curve                    curveDetail              curvePoint
curveTangent             curveTightness           curveVertex              cylinder
day                      debugMode                deltaTime                describeElement
deviceOrientation        directionalLight         displayDensity           displayHeight
displayWidth             downloadFile             drawingContext
ellipse                  ellipseMode              ellipsoid                emissiveMaterial
encodeAndDownloadGif     endClip                  endContour               endGeometry
endShape                 erase                    exitPointerLock          focused
fract                    frameCount               frameRate                freeGeometry
frustum                  fullscreen               getFilterGraphicsLayer   getFrameRate
getItem                  getTargetFrameRate       getURL                   getURLParams
getURLPath               green                    gridOutput               hasOwnProperty
height                   hour                     httpDo                   httpGet
httpPost                 hue                      image                    imageLight
imageMode                isKeyPressed             isLooping                isPrototypeOf
js_id                    keyCode                  keyIsDown                keyIsPressed
lerp                     lerpColor                lightFalloff             lightness
lights                   line                     linePerspective          loadBytes
loadFont                 loadImage                loadJSON                 loadModel
loadPixels               loadShader               loadStrings              loadTable
loadXML                  mag                      matchAll                 metalness
millis                   minute                   mouseButton              mouseIsPressed
mouseX                   mouseY                   movedX                   movedY
nf                       nfc                      nfp                      nfs
noCanvas                 noCursor                 noDebugMode              noErase
noFill                   noLights                 noLoop                   noSmooth
noStroke                 noTint                   noise                    noiseDetail
noiseSeed                norm                     normal                   normalMaterial
object_entries           object_keys              object_values            orbitControl
ortho                    pAccelerationX           pAccelerationY           pAccelerationZ
pRotateDirectionX        pRotateDirectionY        pRotateDirectionZ        pRotationX
pRotationY               pRotationZ               paletteLerp              panorama
perspective              pixelDensity             pixels                   plane
pmouseX                  pmouseY                  point                    pointLight
popMatrix                popStyle                 propertyIsEnumerable
push                     pushMatrix               pushStyle                pwinMouseX
pwinMouseY               quad                     quadraticVertex          randomGaussian
randomSeed               rectMode                 red                      redraw
registerMethod           registerPreloadMethod    registerPromisePreload   removeElements
removeItem               requestPointerLock       resetMatrix              resetShader
resizeCanvas             rotate                   rotateX                  rotateY
rotateZ                  rotationX                rotationY                rotationZ
saturation               save                     saveCanvas               saveFrames
saveGif                  saveJSON                 saveJSONArray            saveJSONObject
saveStrings              saveTable                scale                    second
selectAll                setAttributes            setCamera                setFrameRate
setMoveThreshold         setShakeThreshold        shader                   shearX
shearY                   shininess                smooth                   sort
specularColor            specularMaterial         sphere                   splitTokens
spotLight                sq                       square                   storeItem
stroke                   strokeCap                strokeJoin               strokeWeight
subset                   textAlign                textAscent               textDescent
textFont                 textLeading              textOutput               textSize
textStyle                textWidth                textWrap                 texture
textureMode              textureWrap              tint                     toLocaleString
toString                 to_py                    torus                    touchend
touches                  touchstart               triangle                 trim
turnAxis                 typeof                   unchar                   unregisterMethod
updatePixels             valueOf                  vertex                   webglVersion

acos                     asin                     atan                     atan2
boolean                  ceil                     circle                   clear
color                    concat                   copy
cos                      degrees                  describe                 dist
exp                      fill                     floor                    get
key                      log                      loop
model                    month                    pop
radians                  random                   rect
remove                   select
shorten                  shuffle
sin                      sqrt                     tan                      text
translate                run                      stop                     start
'''.split())




DUNNO_WHAT_TO_DO = {
    'print', 'filter', 'set', 'map', 'abs',
}


def to_terminal_message(node:ast.Name, line:str):

    j1, j2 = node.col_offset, node.end_col_offset
    j_open = line.find('(', j2)
    if j_open < 0:
        print(f"Couldn't find the opening parentheses after `print` call at line { node.lineno }")
        return 'print'

    repl = f"{ line[:j1] }terminal_message(None, { line[j_open+1:] }"
    return repl


def to_p5_name_default(node: ast.Name, line:str, updated:str=None):
    if updated is None:
        updated = f"p5.{ node.id }"
    j1,j2 = node.col_offset, node.end_col_offset
    repl  = f"{ line[:j1] }{ updated }{ line[j2:] }"
    return repl


def fixed_updater(updated:str):
    return lambda node, line: to_p5_name_default(node, line, updated)



CALL_CONVERSIONS = {
    'stop':  fixed_updater('p5.noLoop'),
    'start': fixed_updater('p5.loop'),
    'print': to_terminal_message,
}







def update_basthon_p5_code(file:str, target:str, tail:str=None):
    """
    Convert automatically, with feedback, a python file written for a p5 animation on Basthon,
    to the equivalent code for PMT.
    """

    py_file = Path(file)
    if not py_file.is_file() or py_file.suffix != '.py':
        raise FileNotFoundError(f"{py_file} should be a python file.")

    source_code = py_file.read_text(encoding='utf-8')


    # Determine the output file name:
    i_end = None
    tail  = tail or '_pmt'
    if re.fullmatch(r'-\d+', tail):
        tail, i_end = '', int(tail)

    out_name = f'{ py_file.stem[:i_end] }{ tail }.py'
    out_file = py_file.with_name(out_name)

    print('Convert:', py_file, 'to', out_name)


    # First pass to update each p5 name to p5.name:
    p5_code, tree = update_code_with_nodes(source_code, find_p5_names, name_transform)


    # Second pass to update the `run` calls:
    run_call   = find_runs_signature_call(tree, target)
    out_code,_ = update_code_with_nodes(p5_code, find_p5_run_calls, run_transformer(run_call))
    out_code   = out_code.replace('from p5 import *', "import p5")


    # Show useful info to the user:
    P5Visitor().visit(ast.parse(out_code))
    P5Visitor.show_messages(run_call)


    # Dump the fixed file, in the same folder:
    out_file.write_text(out_code, encoding='utf-8')






def find_p5_names(node:ast.AST) -> bool :
    return (
        isinstance(node, ast.Name)
        and node.id not in DUNNO_WHAT_TO_DO
        and node.id in P5_NAMES
    )

def name_transform(node:ast.Name, lines:List[str]) -> None :
    i = node.lineno-1
    line = lines[i]
    repl = CALL_CONVERSIONS.get(node.id, to_p5_name_default)(node, line)
    lines[i] = repl






def find_p5_run_calls(node:ast.AST) -> bool :
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == 'run'
    )

def run_transformer(runner:str):

    def run_transform(node:ast.Call, lines:List[str]) -> None :
        i1, i2 = node.lineno-1,   node.end_lineno-1
        j1, j2 = node.col_offset, node.end_col_offset

        start, end = lines[i1][:j1], lines[i2][j2:]
        fresh      = f"{ start }{ runner }{ end }"
        lines[i1]  = fresh
        lines[i1+1:i2+1] = ('',) * (i2-i1)      # Avoids O(N) deletion...

    return run_transform





NodePredicate = Callable[[ast.AST], bool]
LinesMutation = Callable[[ast.AST, List[str]], None]


def update_code_with_nodes(
    code:      str,
    predicate: NodePredicate,
    transform: LinesMutation,
) -> Tuple[str, ast.Module] :
    """
    Transform the given code string, searching for the location to update through the use of
    the python ast tree (note: working on strings because the work with ast only would remove
    the comments... x/ ), and performing the given transformation in the code.
    All modifications are performed from last to first node, so that the locations stay exact
    all along the way.
    """
    lines = code.splitlines(keepends=1)
    tree  = ast.parse(code)
    nodes = [ node for node in ast.walk(tree) if predicate(node) ]
    sort_last_to_first(nodes)

    print(f'{ len(nodes) } { transform.__name__ }')

    for node in nodes:
        transform(node, lines)

    return ''.join(lines), tree





def sort_last_to_first(lst:List[ast.AST]) -> ast.AST :
    """
    Sort in place, in reversed order of the node location in the code.
    """
    lst.sort(key=lambda node: (node.lineno, node.col_offset), reverse=True)






def find_runs_signature_call(tree:ast.Module, target:str) -> ast.Call :
    """
    Explore the ast tree to find what should be the `p5.run(...)` call to use, depending
    on the functions defined in the module (seeking for setup draw and preload), and the
    given target id (for PMT figure).
    """
    specials = ('setup', 'draw', 'preload')

    used = sorted({
        node.name for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef) and node.name in specials
    }, key=specials.index)

    if target:
        used.append(f"{target=!r}")

    return f"p5.run({ ', '.join(used) })"







class P5Visitor(ast.NodeVisitor):
    """
    Explore the given ast tree to show information to the user about what should be looked after.
    """

    WARN: List[ast.Name] = []
    RUNS: List[ast.Call] = []

    def visit_Name(self, node: ast.Name):
        if node.id in DUNNO_WHAT_TO_DO:
            self.WARN.append(node)

    def visit_Call(self, node: ast.Call):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'run':
            self.RUNS.append(node)


    @classmethod
    def show_messages(cls, runner):
        cls._show_message(
            cls.WARN, lambda node: node.id,
            "Locations of names that were not updated. You should check if they need `p5.funcName`"
        )
        cls._show_message(
            cls.RUNS, lambda node: node.func.attr,
            "Locations where calls to `run(...)` have been updated: you should check that they are "
            f"correct.\nThe code used is:\n    { runner }"
        )

    @classmethod
    def _show_message(cls, lst:List[ast.AST], getter:Callable, header:str):
        if not lst: return

        dct = defaultdict(list)
        for node in lst:
            dct[getter(node)].append(node.lineno)

        msg = ''.join(
            f"\n\n    * `{ name }` used at lines:\n        { ', '.join(map(str,sorted(lst))) }"
            for name,lst in sorted(dct.items())
        )
        print(f"\n-------------------------\n{ header }{ msg }\n\n")






if __name__=="__main__":
    pass
    # update_basthon_p5_code('ast-P5/alien.py', 'figure1')
