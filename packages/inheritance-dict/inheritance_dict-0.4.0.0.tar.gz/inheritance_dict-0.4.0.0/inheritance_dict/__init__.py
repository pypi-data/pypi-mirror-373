"""
The module defines an InheritanceDict, which is a dictionary, but for lookups where the key is a
type, it will walk over the Method Resolution Order (MRO) looking for a value.
"""

from collections.abc import Iterable


__all__ = ["InheritanceDict", "TypeConvertingInheritanceDict"]

MISSING = object()


class InheritanceDict(dict):
    """
    A dictionary that for type lookups, will walk over the Method Resolution Order (MRO) of that
    type, to find the value for the most specific superclass (including the class itself) of that
    type.
    """

    def _get_keys(self, key) -> Iterable[object]:
        """
        Yield lookup candidate keys.

        If `key` is a type, yields the classes in its method-resolution order (key.__mro__) in
        order; otherwise yields the key itself. Used to produce the sequence of keys to try for
        dictionary lookups that support type-based inheritance resolution.
        """
        if isinstance(key, type):
            return key.__mro__
        return (key,)

    def __getitem__(self, key):
        """
        Return the value for `key`, using type inheritance when appropriate.

        If `key` is a type, this performs lookups in the key's MRO (key.__mro__) in order and
        returns the first mapped value found. If `key` is not a type, it performs a direct lookup
        using `key`. Raises KeyError if no matching mapping exists.
        """
        for item in self._get_keys(key):
            result = super().get(item, MISSING)
            if result is not MISSING:
                return result
        raise KeyError(key)

    def get(self, key, default=None):
        """
        Return the value mapped to `key` or `default` if no mapping exists.

        If `key` is a type, the lookup walks the type's MRO (including the type itself) and returns
        the first matching value; for non-type keys a direct lookup is attempted. If no candidate
        is found, `default` is returned.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default=None):
        """
        Return the value for `key` if present; otherwise insert `default` for `key` and return it.

        This method uses the same lookup semantics as __getitem__: if `key` is a type, the mapping
        is searched along the key's MRO and the first matching value is returned. If no mapping is
        found, `default` is stored under the exact `key` provided (no MRO walking when writing)
        and `default` is returned.

        Parameters:
            key: The lookup key (may be a type; type keys are resolved via MRO on read).
            default: Value to insert and return if no existing mapping is found.

        Returns:
            The existing mapped value (found via lookup) or `default` after insertion.
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def __repr__(self):
        """
        Return a canonical string representation of the mapping.

        The format is "<ClassName>(<dict-repr>)", where <ClassName> is the runtime class
        name (e.g., "InheritanceDict" or a subclass) and <dict-repr> is the underlying
        dictionary's repr() value.

        Returns:
            str: The formatted representation.
        """
        return f"{type(self).__name__}({super().__repr__()})"


class TypeConvertingInheritanceDict(InheritanceDict):
    """
    A variant of InheritanceDict that, on a missing direct lookup for non-type keys,
    retries the lookup using the key's type and resolves via that type's MRO.
    """

    def _get_keys(self, key):
        """
        Yield candidate lookup keys for a given key, extending the base behavior by including the
        key's type MRO for non-type keys.

        For non-type keys, yields the candidates produced by the superclass
        (_e.g., the key itself_), followed by the method resolution order (MRO) of type(key).
        For keys that are types, yields only the superclass candidates (typically the type's MRO).

        Parameters:
            key: The lookup key. If `key` is not a `type`, this generator will include the MRO of
            `type(key)` after the superclass candidates.

        Yields:
            Candidate keys (types or other keys) in the order they should be tried for lookup.
        """
        yield from super()._get_keys(key)
        if not isinstance(key, type):
            yield from type(key).__mro__
