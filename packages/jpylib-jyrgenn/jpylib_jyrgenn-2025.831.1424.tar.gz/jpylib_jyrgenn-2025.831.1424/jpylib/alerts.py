"""Print alerts and other messages depending on a level of verbosity.

This module works on the idea of a numeric *alert level*, which determines the
amount of output generated. On each alert level, the associated messages are
printed, as well as those of the lower levels.

For each alert level, there are one or more functions to print messages at
that level. The functions with a name ending with `f` take a format string
and positional arguments to format a message; most of the others take any
number of arguments, which will be stringified and concatenated to print
the message.

`L_ERROR`: alert level 0. On this level, only error messages are
printed, including fatal error messages. In the default configuration,
these messages are tagged with the program name and `Error:`. Functions
printing at that level: `err()`, `error()` (an alias for `err`), `errf()`,
`errorf()` (an alias for `errf`), `fatal()`, `fatalf()`.

`L_NOTICE`: alert level 1. It includes `L_ERROR`. Error messages and
messages of some importance are printed. Functions printing at that level:
`notice()`, `noticef()`.

`L_INFO`: alert level 2. It includes `L_NOTICE` and `L_ERROR`. In addition
to those of the lower levels, informational messages of possible interest
are printed, e.g. something indicating a program's progress through its
operation. Functions printing at that level: `info()`, `infof()`.

`L_DEBUG`: alert level 3. It includes `L_INFO`, `L_NOTICE` and `L_ERROR`.
In addition to those of the lower levels, messages intended to help
debugging the program are printed. In the default configuration,
these messages are tagged with `DBG`. Functions printing at that level:
`dbg()`, `debug()` (an alias for `dbg`), `debugf()`, `debug_vars()`.

`L_TRACE`: alert level 4. It includes `L_DEBUG`, `L_INFO`, `L_NOTICE` and
`L_ERROR`. In addition to those of the lower levels, high-volume trace
messages may be printed. In the default configuration, these messages are
tagged with `TRC`. Functions printing at that level: `trace()`, `tracef()`.

Some aspects of the module can be customised using a configuration that looks
like this:

    Config(
        # decoration to print before a message, per level
        decoration=[""{cfg.program}: Error:", None, None, "DBG", TRC"]

        # program name to use in a message
        program=os.path.basename(sys.argv[0]),

        # syslog facility; if set, syslog will be used
        syslog_facility=None,

        # syslog priority, per level
        syslog_prio = [
            syslog.LOG_ERR,
            syslog.LOG_NOTICE,
            syslog.LOG_INFO,
            syslog.LOG_DEBUG,
            None,                   # don't let this go to syslog
        ],

        # status: syslog has been opened
        syslog_opened=False,

        # fd to print message to, per level
        fd=[2, 2, 2, 2, 2],

        # current alert level
        level=L_NOTICE,

        # maximum alert level
        max_level=4,

        # print timestamps with messages
        timestamps=False,

        # had any errors yet?
        had_errors=False,
    )


"""

import os
import sys
import syslog
import inspect
from contextlib import contextmanager

import jpylib as y
from .config import Config

# properties of the alert levels; the decoration will be formatted with the
# locals() values
alert_levels = (
    # level name, message decoration, fd (will look up later to make output
    # capturing work)
    ("L_ERROR", "{cfg.program}: Error:",   2),
    ("L_NOTICE", None,                     2),
    ("L_INFO",   None,                     2),
    ("L_DEBUG",  "DBG",                    2),
    ("L_TRACE",  "TRC",                    2),
)
for i, props in enumerate(alert_levels):
    name, *_ = props
    locals()[name] = i

# the module configuration; will be initialised in alert_init()
cfg = None

def alert_config(*, decoration=None, fd=None, level=None, program=None,
                 syslog_facility=None, syslog_prio=None, reset_defaults=None,
                 timestamps=None, fatal_label="(fatal)"):
    """Customise the alerts configuration with the given values.

    If `reset_defaults` is true, reset everything to the specified or
    default values.
    """
    global cfg
    if not any(locals().values()) or reset_defaults:
        cfg = Config(
            # decoration to print before a message, per level
            decoration=[level[1] for level in alert_levels],
            
            # program name to use in a message
            program=os.path.basename(sys.argv[0]),
            
            # syslog facility; if set, syslog will be used
            syslog_facility=None,

            # syslog priority, per level
            syslog_prio = [
                syslog.LOG_ERR,
                syslog.LOG_NOTICE,
                syslog.LOG_INFO,
                syslog.LOG_DEBUG,
                None,                   # don't let this go to syslog
            ],
            
            # status: syslog has been opened
            syslog_opened=False,
            
            # fd to print message to, per level
            fd=[level[2] for level in alert_levels],

            # current alert level
            level=L_NOTICE,
            
            # maximum alert level
            max_level=len(alert_levels)-1,

            # print timestamps with messages
            timestamps=False,

            # print "Fatal" label for fatal errors
            fatal_label=fatal_label,

            # had any errors yet?
            had_errors=False,
        )
    del reset_defaults
    for var, value in locals().items():
        if value is not None:
            cfg.set(var, value)
    if cfg.timestamps is True:
        cfg.timestamps = y.isotime

def alert_init(**kwargs):
    """Initialise the module to default or given values."""
    alert_config(reset_defaults=True, **kwargs)

alert_init()


def alert_redirect(level, file):
    """Redirect printing of alerts from `level` to `file` (a file handle)."""
    cfg.fd[level] = file


def alert_level(level=None):
    """Get and/or set the verbosity level for the alert functions.
    """
    if level is not None:
        if type(level) is str:
            level = globals()[level]
        cfg.level = max(0, min(level, cfg.max_level))
    return cfg.level

def alcf():
    """Return the alerts configuration (used for testing)."""
    return cfg

def alert_level_name(level=None):
    """Return the name of the specified (or current) level number."""
    if level is None:
        level = cfg.level
    return alert_levels[level][0]


def alert_level_up():
    """Increase the alert level by one.

    This is intended to be used as the callback function for the type of a
    `pgetopts` option to increase the verbosity. Returns the new level.

    """
    if cfg.level < cfg.max_level:
        cfg.level += 1
    return cfg.level


def alert_level_zero():
    """Set the alert level to zero (errors only).

    This is intended to be used as the callback function for the type of a
    `pgetopts` option to set the verbosity to zero. Returns the new level.

    """
    cfg.level = 0
    return cfg.level


def is_notice():
    """Return `True` iff the alert level is at least at `L_NOTICE`."""
    return cfg.level >= L_NOTICE

def is_info():
    """Return `True` iff the alert level is at least at `L_INFO`."""
    return cfg.level >= L_INFO

def is_debug():
    """Return `True` iff the alert level is at least at `L_DEBUG`."""
    return cfg.level >= L_DEBUG

def is_trace():
    """Return `True` iff the alert level is at least at `L_TRACE`."""
    return cfg.level >= L_TRACE


@contextmanager
def temporary_alert_level(level):
    """Context manager to temporarily raise the alert level."""
    savedLevel = alert_level()
    alert_level(level)
    try:
        yield
    finally:
        alert_level(savedLevel)


def alert_if_level(level, *msgs):
    """Print a message if `level` is <= the cfg.level.

    If a decoration exists in `cfg.decoration[]` for that level, is it prepended
    to the message. By default, all levels print to stderr; this can be changed
    in `cfg.fd[]` by level.

    If one of the elements in `msgs` is a callable, it will be called withaout
    arguments to get the value of the element. This way, compute-intensive task
    can be delayed to the alerting moment, meaning they don't need to be done if
    not called for.

    This function provides the meat of the module's functionality for the
    convenience functions `debug()`, `info()`, etc. It is not intended to be
    called directly by the user.

    """
    # return fast if not needed
    if level > cfg.level:
        return

    # make all msgs elements strings, calling those that are callable
    msgs = list(msgs)                   # is a tuple before
    for i, elem in enumerate(msgs):
        if callable(elem):
            msgs[i] = elem()
        else:
            msgs[i] = str(elem)
    if cfg.decoration[level]:
        msgs = [cfg.decoration[level].format(**globals()), *msgs]
    if cfg.timestamps:
        msgs.insert(0, cfg.timestamps())

    channel = cfg.fd[level]
    channel = { 1: sys.stdout, 2: sys.stderr }.get(channel) or channel

    msgtext = " ".join(msgs).rstrip()
    print(msgtext, file=channel, flush=True)

    if cfg.syslog_facility and cfg.syslog_prio[level]:
        if not cfg.syslog_opened:
            syslog.openlog(logoption=syslog.LOG_PID,
                           facility=cfg.syslog_facility)
            cfg.syslog_opened = True
        level = max(0, min(cfg.max_level, level))
        message = " ".join(map(str, msgs))
        syslog.syslog(cfg.syslog_prio[level], message)


def debug_vars(*vars):
    """Print debug output for the named variables if alert level >= `L_DEBUG`.

    The arguments are the variable names (strings). Each variable will be
    printed as a debug message with its name and value on a separate line.
    """
    if cfg.level >= L_DEBUG:
        context = inspect.currentframe().f_back.f_locals
        for var in vars:
            debug("VAR {}: {}".format(var, repr(context[var])))


def err(*msgs):
    """Print `L_ERROR` level output."""
    cfg.had_errors = True
    alert_if_level(L_ERROR, *msgs)
error = err                             # alias

def errf(template, *args):
    """Print `L_ERROR` level output as a formatted string.

    `template` is the format template, `args` are its arguments.
    """
    err(template.format(*args))
errorf = errf

def fatal(*msgs, exit_status=1):
    """Print `L_ERROR` level output and end the program with `exit_status`."""
    if cfg.fatal_label:
        alert_if_level(L_ERROR, cfg.fatal_label, *msgs)
    else:
        alert_if_level(L_ERROR, *msgs)
    sys.exit(exit_status)

def fatalf(template, *args, exit_status=1):
    """Print `L_ERROR` level output and end the program with `exit_status`.

    `template` is the format template, `args` are its arguments.
    """
    fatal(template.format(*args), exit_status=exit_status)

def notice(*msgs):
    """Print `L_NOTICE` level output."""
    alert_if_level(L_NOTICE, *msgs)

def noticef(template, *args):
    """Print `L_NOTICE` level output as a formatted string.

    `template` is the format template, `args` are its arguments.
    """
    if is_notice():
        alert_if_level(L_NOTICE, template.format(*args))

def info(*msgs):
    """Print `L_INFO` level output."""
    alert_if_level(L_INFO, *msgs)

def infof(template, *args):
    """Print `L_INFO` level output as a formatted string.

    `template` is the format template, `args` are its arguments.
    """
    if is_info():
        info(template.format(*args))

def debug(*msgs):
    """Print `L_DEBUG` level output."""
    alert_if_level(L_DEBUG, *msgs)
dbg = debug                             # alias

def debugf(template, *args):
    """Print `L_DEBUG` level output as a formatted string.

    `template` is the format template, `args` are its arguments.
    """
    if is_debug():
        debug(template.format(*args))

def trace(*msgs):
    """Print `L_TRACE` level output."""
    alert_if_level(L_TRACE, *msgs)

def tracef(template, *args):
    """Print `L_TRACE` level output as a formatted string.

    `template` is the format template, `args` are its arguments.
    """
    if is_trace():
        trace(template.format(*args))

# EOF
