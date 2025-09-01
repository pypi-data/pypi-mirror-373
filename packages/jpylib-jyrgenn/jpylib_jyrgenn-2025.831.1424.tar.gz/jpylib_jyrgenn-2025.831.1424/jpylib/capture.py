#!python3

"""This module implements three context managers. `outputCaptured()`
captures output to stdout and stderr from the code run in the
context; in addition, `outputAndExitCaptured()` also captures a
`sys.exit()` call from the code run in the context and the status
value passed to `sys.exit()`.

The latter will fail if the code run in the context catches
`_SysExitException`, which can be the case if the code catches all
of class `BaseException`.

Finally, `inputFrom()` is a context manager to temporarily redirect
`sys.stdin` to an open file.

The meat of the first part is from Rob Kennedy on stackoverflow:
[https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python](https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python)
"""

import sys
from io import StringIO
from contextlib import contextmanager

@contextmanager
def outputCaptured():
    """Context manager to capture output to stdout and stderr.

    This works by temporarily replacing `sys.stdout` and `sys.stderr` with
    `StringIO` ports; these are both returned, so the output of the code
    run on the context can be retrieved from them:

        with outputCaptured() as (out, err):
            <code with output captured>
        theOutput = out.getvalue()        # stdout output as string
        theErrout = err.getvalue()        # stderr outout as string
    """
    saved_out = sys.stdout
    saved_err = sys.stderr
    try:
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout = saved_out
        sys.stderr = saved_err


@contextmanager
def inputFrom(input):
    """Context manager to redirect stdin from an open file.

    This works by temporarily replacing `sys.stdin` with an open file.
    Typical code would look like this:

        with open(inputFile) as input:
            with inputFrom(input):
                ...                       # code with input as sys.stdin
    """
    saved_stdin = sys.stdin
    try:
        sys.stdin = input
        
        yield
    finally:
        sys.stdin = saved_stdin


# From here, it's my own, built on the above. I feel pretty smug not only
# capturing the sys.exit(), but also the exit status value at the first
# attempt. ¡yay Python!

class _SysExitException(Exception):
    """Exception to be used by the fake `sys.exit()` function."""
    
    def __init__(self, status):
        """Keep the status value for later perusal."""
        self.status = status

        
class _ExitStatus():
    """Bog standard namespace. We use the `value` field.

    To keep the exit status, we need to return something from the context
    manager where we can store the exit status later, and this is it.
    """
    value = None


def _fake_sysexit(status=0):
    """Replacement for `sys.exit()` in `OutputAndExitCaptured` context manager.

    It throws the control flow out of code's context by raising an
    exception. (This will of course fail if the code run in the context
    captures all exceptions; let's just say it shouldn't.) The exit
    status value is passed to the context manager as the exception
    parameter.

    """
    raise _SysExitException(status)


@contextmanager
def outputAndExitCaptured():
    """Context manager to capture output to stdout/stderr and exit status.

    Like with `outputCaptured()`, stdout and stderr are captured in the
    returned `StringIO` objects. In addition, the exit status in case of a
    `sys.exit()` is captured in the `value` property of the returned
    status object:

        with outputAndExitCaptured() as (out, err, status):
            <code with output and exit status captured>
        theOutput = out.getvalue()    # stdout output as string
        theErrout = err.getvalue()    # stderr outout as string
        theStatus = status.value      # sys.exit() argument (or 0 or None)

    The status value is `None` if the code run in the context hasn't
    called `sys.exit()`.

    """
    saved_out = sys.stdout
    saved_err = sys.stderr
    saved_sysexit = sys.exit
    exit_status = _ExitStatus()
    
    try:
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        sys.exit = _fake_sysexit
        
        yield sys.stdout, sys.stderr, exit_status
    except _SysExitException as syse:
        exit_status.value = syse.status
    finally:
        sys.stdout = saved_out
        sys.stderr = saved_err
        sys.exit = saved_sysexit


# EOF
