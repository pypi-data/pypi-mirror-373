
import collections


def avg_midrange(values):
    """Return the arithmetic mean of the highest and lowest value of `values`

    (an iterable of numbers).
    """
    vmin = min(values)
    vmax = max(values)
    return (vmin + vmax) / 2


def remove_outliers(values):
    """Return a copy of the `values` with the highest and lowest value removed.

    If there is more than one highest or lowest value, only one of them is
    removed.

    """
    vmax = None
    vmin = None
    for value in values:
        if vmin is None or value < vmin:
            vmin = value
        if vmax is None or value > vmax:
            vmax = value
    new_values = values.copy()
    if new_values:
        new_values.remove(vmin)
    if new_values:
        new_values.remove(vmax)
    return new_values


def maybe_int(arg):
    """Return the corresponding int if `arg` represents one, or `None`.

    `arg` could be a string or a number."""
    try:
        return int(arg)
    except:
        return None


def maybe_num(arg):
    """Return the corresponding int or float if `arg` represents one, or `None`.
    """
    the_int = maybe_int(arg)
    if the_int is None:
        try:
            return float(arg)
        except:
            return None
    return the_int


def is_int(arg):
    """Return `True` if `arg` represents an `int`, or `False`.
    
    `arg` may be not an int (maybe e.g. a string), but if it
    can be read as an int, it represents an int.

    """
    return maybe_int(arg) is not None


def is_num(arg):
    """Return `True` if `arg` represents a number, or False.
    
    `arg` may be not numeric (maybe e.g. a string), but if it
    can be read as a number, it represents a number.

    """
    return maybe_num(arg) is not None


