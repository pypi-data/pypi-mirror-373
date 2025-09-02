# Case-insensitive string set

A Python package providing a `set` class for case-insensitive strings.

Useful for doing things like `foo in bar` where `bar` is a set of strings and you want the check to be case-insensitive,
but also preserve the original casing of the strings in the set when iterating over it.

## Examples

```doctest
>>> c = CaseInsensitiveStringSet()
>>> c.add("a")
>>> 'a' in c
True
>>> 'A' in c
True
>>> 'b' in c
False
>>> list(c)
['a']
>>> c.add("A")
>>> list(c)
['a']
```
