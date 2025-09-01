import fcntl
import struct
import termios

from .alerts import debug

# Here used to be terminal_size(). In between I have learned of
# os.get_terminal_size(), which has the exact same call signature.

ttyo_file = None
ttyi_file = None

def ttyo(close=False):
    """Return an open output file handle to the process's controlling terminal.

    If `close` is true, close that file handle.
    """
    global ttyo_file
    if close:
        if ttyo_file:
            ttyo_file.close()
            ttyo_file = None
        return
    if not ttyo_file:
        ttyo_file = open("/dev/tty", "w")
    return ttyo_file

def ttyi(close=False):
    """Return an open input file handle to the process's controlling terminal.

    If `close` is true, close that file handle.
    """
    global ttyi_file
    if close:
        if ttyi_file:
            ttyi_file.close()
            ttyi_file = None
        return
    if not ttyi_file:
        ttyi_file = open("/dev/tty")
    return ttyi_file

def ptty(*args, **kwargs):
    """Print something to the process's controlling terminal.

    `args` and `kwargs` are passed to `print()`.
    """
    print(*args, file=ttyo(), **kwargs)

# EOF
