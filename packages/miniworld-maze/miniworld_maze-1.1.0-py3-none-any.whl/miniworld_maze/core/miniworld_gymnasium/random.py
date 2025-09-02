"""Random number generation utilities for MiniWorld environments."""

from gymnasium.utils import seeding


class RandGen:
    """
    Thread-safe random value generator for environment simulation.

    Provides consistent random number generation across different runs
    when seeded properly, which is essential for reproducible experiments.
    """

    def __init__(self, seed=None):
        """Initialize random generator with optional seed."""
        self.np_random, _ = seeding.np_random(seed)

    def random_int(self, low, high):
        """
        Generate random integer in the range [low, high).

        Args:
            low: Lower bound (inclusive)
            high: Upper bound (exclusive)

        Returns:
            Random integer in specified range
        """
        return self.np_random.integers(low, high)

    def random_float(self, low, high, shape=None):
        """
        Generate random float(s) in the range [low, high).

        Args:
            low: Lower bound (inclusive)
            high: Upper bound (exclusive)
            shape: Optional shape for array output

        Returns:
            Random float or array of floats in specified range
        """
        return self.np_random.uniform(low, high, size=shape)

    def random_bool(self):
        """
        Generate random boolean value with 50/50 probability.

        Returns:
            Random boolean (True or False)
        """

        return self.np_random.integers(0, 2) == 0

    def choice(self, iterable, probs=None):
        """
        Pick a random element in a list
        """

        lst = list(iterable)
        idx = self.np_random.choice(len(lst), p=probs)
        return lst[idx]

    def random_color(self):
        """
        Pick a random color name
        """

        from .entities.base_entity import COLOR_NAMES

        return self.choice(COLOR_NAMES)

    def subset(self, iterable, num_elems):
        """
        Sample a random subset of distinct elements of a list
        """

        lst = list(iterable)
        assert num_elems <= len(lst)

        out = []

        while len(out) < num_elems:
            elem = self.choice(lst)
            lst.remove(elem)
            out.append(elem)

        return out

    # Backward compatibility aliases
    def int(self, low, high):
        """Legacy alias for random_int (deprecated: shadows built-in)"""
        return self.random_int(low, high)

    def float(self, low, high, shape=None):
        """Legacy alias for random_float (deprecated: shadows built-in)"""
        return self.random_float(low, high, shape)

    def bool(self):
        """Legacy alias for random_bool (deprecated: shadows built-in)"""
        return self.random_bool()

    def color(self):
        """Legacy alias for random_color (deprecated: not descriptive)"""
        return self.random_color()
