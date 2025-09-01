#!/usr/bin/env python3

from jpylib import is_trace, trace

trace_len = 31                            # max. width of obj. trace
trace_ellipsis = "[…]"


def crop(s):
    l = len(s)
    if l <= trace_len:
        return s
    return s[:trace_len - len(trace_ellipsis)] + trace_ellipsis


def tracefn(func):
    """Decorator: trace function's calls if alert level is `L_TRACE` or higher.
    """
    def wrapper(*args, **kwargs):
        if is_trace():
            s = "call {}({}".format(func.__name__,
                                    ', '.join(map(crop, map(repr, args))))
            if kwargs:
                for k, v in kwargs.items():
                    s += ", {}={}".format(k, crop(repr(v)))
            trace(s + ")")
        return func(*args, **kwargs)
    return wrapper

