#!/usr/bin/env python3

"""The jpylib library contains a number of modules to provide the functionality
I like to have at hand when I write Python programs. """

import os
import pwd
import sys

from .options import pgetopts
from .alerts import L_ERROR, L_NOTICE, L_INFO, L_DEBUG, L_TRACE, \
    alert_config, alert_level, alert_level_name, \
    alert_level_up, alert_level_zero, is_notice, is_info, is_debug, is_trace, \
    debug_vars, fatal, err, notice, info, debug, trace, \
    tracef, debugf, infof, noticef, errorf, fatalf, temporary_alert_level
from .fntrace import tracefn
from .stringreader import StringReader
from .kvs import parse_kvs
from .namespace import Namespace
from .config import Config
from .secrets import putsecret, getsecret, getsecret_main, putsecret_main, \
     FileModeError
from .sighandler import sanesighandler, exit_on_error
from .terminal import ttyi, ttyo, ptty
from .capture import outputCaptured, outputAndExitCaptured, inputFrom
from .process import backquote, system
from .assorted import boolish, flatten, is_sequence, identity
from .numeric import maybe_int, is_int, maybe_num, is_num, \
     avg_midrange, remove_outliers
from .iohelper import all_input_lines, read_items, read_mapping
from .time import isotime, isotime_ms, iso_time, iso_time_ms, iso_time_us
from .table import format_table
from .singleton import Singleton
from .multiset import Multiset

version = "2025.831.1424"
"""The version of the `jpylib` package."""

program = os.path.basename(sys.argv[0])
"""The name of the current program without its directory path."""

real_home = pwd.getpwuid(os.getuid()).pw_dir
"""The home directory of the current user as defined for its user id."""

home = os.environ.get("HOME") or real_home
"""The home directory of the current user as defined in the environment or for
its user id.
"""


__all__ = sorted("""pgetopts L_ERROR L_NOTICE L_INFO L_DEBUG L_TRACE
  alert_config alert_level alert_level_name
  alert_level_up alert_level_zero is_notice is_info is_debug is_trace
  debug_vars fatal err notice info debug trace
  tracef debugf infof noticef errorf fatalf temporary_alert_level
  tracefn StringReader parse_kvs Namespace Config putsecret getsecret
  getsecret_main putsecret_main FileModeError sanesighandler ttyi ttyo
  ptty outputCaptured outputAndExitCaptured inputFrom backquote boolish
  flatten is_sequence identity maybe_int is_int maybe_num is_num
  avg_midrange remove_outliers all_input_lines read_items isotime
  isotime_ms iso_time iso_time_ms iso_time_us format_table Singleton
  Multiset version program real_home home""".split())
