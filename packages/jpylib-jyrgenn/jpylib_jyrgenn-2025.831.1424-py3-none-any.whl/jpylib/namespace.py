#!/usr/bin/env python3

class Namespace:
    """Simple name space class as a key-value store.

    Values can be assigned and read directly (`ns.key = value`) or using the
    `set()`/`get()` methods or the `ns[key]` indexing. An `update()` method
    (as with a dictionary) has the options to skip keys beginning with an
    underscore, or raise a `KeyError` if a key is not previously known.
    Actually most things work as with a dict -- `iter(ns)`, `len(ns)` etc.

    """

    def __init__(self, **kwargs):
        """Initialize a Namespace object from the `kwargs` mapping."""
        self.__dict__.update(kwargs)

    def update(self, new_values, skip_underscore=False, reject_unknown=False):
        """Update the object with a dictionary of new key/value pairs.

        If `reject_unknown` is true, it is an error if the argument dictionary
        contains keys that are not in the object's key set.

        If `skip_underscore` is true, keys that start with an underscore (`_`)
        are not considered for update.

        """
        for key, value in new_values.items():
            if key.startswith("_") and skip_underscore:
                continue
            if reject_unknown and key not in self.__dict__:
                raise KeyError("unknown key in {}: {}".format(
                    self.__class__.__name__, key))
            self.__dict__[key] = value

    def __setitem__(self, key, value):
        """Set an item's value in the namespace."""
        self.__dict__[key] = value

    def set(self, key, value):
        """Set a value for `key`."""
        self.__dict__[key] = value

    def __getitem__(self, key):
        """Get an item from the namespace."""
        return self.__dict__[key]

    def get(self, key, default=None):
        """Get the value for `key`; return `default` if `key` is not present."""
        return self.__dict__.get(key, default)

    def __delitem__(self, key):
        """Delete an item from the namespace; implements `del key`."""
        del self.__dict__[key]

    def __iter__(self):
        """Return an iterator over the keys of the namespace."""
        return iter(self.__dict__)

    def __contains__(self, key):
        """Return true iff the key is in the namespace."""
        return key in self.__dict__

    def __len__(self):
        """Return the number of keys in the namespace."""
        return len(self.__dict__)        

    def __str__(self):
        """Return a string repr in the form of '<class>(key1=value1, ...)'."""
        return self.__class__.__name__ + "(" + ", ".join(
            ["{}={}".format(k, repr(v)) for k, v in self.__dict__.items()]) \
            + ")"

    def __repr__(self):
        return self.__str__()
