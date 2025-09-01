class Multiset:
    """A multiset implementation.

    Works fine as an iterable, and `len()` as well as `str`/`repr()` give
    sensible results. The latter is parseable to a copy of the `Multiset`
    — in theory; actually, the class name will be `jpylib.multiset.Multiset`,
    which is most likely not how that as which the Multiset can be recreated.
    """

    def __init__(self, things=()):
        """Initialise a Multiset with, optionally, a bunch of things."""
        self.elems = {}
        for elem in things:
            self.add(elem)

    def add(self, thing):
        """Add a thing to the Multiset."""
        if thing in self.elems:
            self.elems[thing] += 1
        else:
            self.elems[thing] = 1

    def count(self, thing):
        """Get the number of a specific thing in the Multiset."""
        return self.elems.get(thing) or 0

    def set_count(self, thing, count):
        """Set the number of a specific thing in the Multiset."""
        if count == 0:
            del self.elems[thing]
        else:
            self.elems[thing] = count

    def remove(self, thing, completely=False):
        """Remove one of or all of a specific thing from the Multiset."""
        if thing in self.elems:
            self.elems[thing] -= 1
            if self.elems[thing] == 0 or completely:
                del self.elems[thing]

    def items(self):
        """Return all items in the Multiset (generator).

        Also, iteration helper."""
        for thing, count in self.elems.items():
            for _ in range(count):
                yield thing

    def counts(self):
        """Return all items and their counts as (item, count) (generator)."""
        return self.elems.items()        

    def __len__(self):
        """Return the number of items in the Multiset."""
        count = 0
        for value in self.elems.values():
            count += value
        return count

    def __iter__(self):
        """Iterate over the items in the Multiset, for `for t in ...`."""
        return iter(self.items())

    def __str__(self):
        """Return a string representation of the Multiset (parsable)."""
        return (f"{self.__class__.__module__}.{self.__class__.__name__}(("
                + ", ".join(map(repr, self)) +"))")
    
    def __repr__(self):
        """Return a string representation of the Multiset (parsable)."""
        return self.__str__()
