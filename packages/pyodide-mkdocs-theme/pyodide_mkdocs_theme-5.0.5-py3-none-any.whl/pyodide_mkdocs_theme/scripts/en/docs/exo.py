# --- PYODIDE:ignore --- #
"""
The `ignore` sections are... ignored. You can use them to leave
comments in your files or to archive Python code that won't be used
for the built website.
---------------------------------------------------------------------------

The `env` section (below) is run before the user's code.
Its content is not visible to the user, but everything defined here
is available in the environment afterward.
If the code in the ENV section raises an error, nothing else will be run.
"""
# --- PYODIDE:env --- #

class Stack:
    """ (Interface to be described in the statement) """
    def __init__(self): self.__stk=[]
    def push(self, v): self.__stk.append(v)
    def pop(self): return self.__stk.pop()
    def is_empty(self): return not self.__stk



# --- PYODIDE:ignore --- #
"""
The `code` section is the initial state of the code provided to the user
in the editor, excluding public tests (see `tests` section).
"""
# --- PYODIDE:code --- #

def is_even(n):
    ...



# --- PYODIDE:ignore --- #
"""
The `corr` section contains the code that will be displayed in the solution,
under the IDE.
"""
# --- PYODIDE:corr --- #

def is_even(n):
    return not n%2



# --- PYODIDE:ignore --- #
"""
The `tests` section contains the public tests that will be displayed under
the user's code in the editor.
"""
# --- PYODIDE:tests --- #

assert is_even(3) is False
assert is_even(24) is True



# --- PYODIDE:ignore --- #
"""
The `secrets` section contains validation tests. These tests are not visible
to the user.

WARNING:
    It is crucial to use messages in validation test assertions, otherwise,
    the user cannot debug their code as `print` is disabled during these
    tests! (unless... => See configuration options)
    It's up to you to decide the level of information you want to provide
    in the message.

Additionally, it is recommended to use a function to avoid having test
variables leaking in the global scope.
"""
# --- PYODIDE:secrets --- #

def tests():
    for n in range(100):
        val = is_even(n)
        exp = n%2 == 0

        msg = f"is_even({n})"                           # Minimum required
        msg = f"is_even({n}): returned {val}"           # Recommended
        msg = f"is_even({n}): {val} should be {exp}"    # Full details

        assert val == exp, msg

tests()         # Don't forget to call the test function...! x)
del tests       # If you don't want to leave traces...


# --- PYODIDE:post --- #
# The post section contains "cleanup" code, to be systematically applied
# after the code and tests have been run.
# This content is executed even if an error was raised earlier, EXCEPT if
# the error originates from the ENV section.
