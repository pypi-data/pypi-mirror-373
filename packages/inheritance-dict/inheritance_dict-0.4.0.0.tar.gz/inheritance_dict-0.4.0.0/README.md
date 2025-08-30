# `inheritance_dict`

[![PyPI - Version](https://img.shields.io/pypi/v/inheritance_dict)](https://pypi.org/project/inheritance_dict/)
[![Coverage](https://img.shields.io/coverallsCoverage/github/hapytex/inheritance_dict)](https://coveralls.io/github/hapytex/inheritance_dict)


`inheritance_dict` is a small package where one can map types to values. If one then performs a lookup, it walks down the *Method Resolution Order (MRO)* looking for a match, and thus returns the value associated with the most specific superclass of the type.

## Example

Imagine the following inheritance dictionary:

```
from inheritance_dict import InheritanceDict

example = InheritanceDict({object: 1, int: 2})
```

now we can query it with:

```
example[object]  # 1
example[int]     # 2
example[bool]    # 2
example[float]   # 1
example[str]     # 1
```

It thus for each type tries to find the value that is associated with the most specific key-value pair for that type.

The main application is making mappings between types. For example, in Django the mapping between model fields, and serializer fields, resource fields, etc. is often done through such pattern. We thus aim to encapsulate the logic.

The dictionary can also contain non-type items. For lookups with keys where the key is not a type, it will try to lookup the key, just like it normally does.

The package also provides a `TypeConvertingInheritanceDict` which will, if the key is not found, and the key is not a type itself, try a second time with the type of the object. So if we have:

```
from inheritance_dict import TypeConvertingInheritanceDict

example2 = TypeConvertingInheritanceDict({object: 1, int: 2})
```

we can query with:

```
example2['A']   # 1
example2[0+1j]  # 1
example2[3]     # 2
```
