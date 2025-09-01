"""Assorted smallish functions for the jpylib lbrary."""

import collections

# Yes, this is a bit silly. But hey...
means_true = \
  set("yes y sure ja j jou si on oui t true  aye 1 affirmative".split())
"""Words, letters, and a number meaning "true/yes" (for `boolish()`).
"""
means_false = \
  set("no n  nope nein nee   off non f false nay 0 negative".split())
"""Words, letters, and a number meaning "false/no" (for `boolish()`).
"""

def boolish(value, default=None):
    """Return a truth value for `value`.

    This works if `value` is something that matches a string in `means_true`
    or `means_false`. If that isn't the case, fall back to default (if not
    `None`) or raise a `ValueError` exception. This can be used for parsing
    config files (that aren't Python) or interactive answers or the like.

    """

    val = str(value).strip().lower()
    if val in means_true:
        return True
    if val in means_false:
        return False
    if default is None:
        raise ValueError(f"'{value}' cannot be understood as false or true")
    else:
        return default


def flatten(seq):
    """Flatten a nested sequence into a flat one with the same leaf elements.

    Return a flat generator object containing just the elements. If the
    argument is a string or not a sequence, the generator object will
    contain just the argument.

    """
    if not isinstance(seq, str) and isinstance(seq, collections.abc.Iterable):
        for elem in seq:
            yield from flatten(elem)
    else:
        yield seq


def is_sequence(arg):
    """Return True iff the argument is a sequence other than string."""
    if isinstance(arg, (str, collections.UserString)):
        return False
    return isinstance(arg, collections.abc.Sequence)


def identity(arg):
    """Return `arg`."""
    return arg
