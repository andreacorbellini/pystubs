# PyStubs: dummy values for equality testing

This tiny Python module provides various types that can be used to check
for conditions using equality (`==`) testing. For example, to test whether
a number is less than 5:

```python
>>> from stubs import *
>>> 2 == LessThan(5)
True
```

Which is completely equivalent to:

```
>>> 2 < 5
True
```

This approach comes in handy when comparing nested containers, such as
JSON objects returned by an API:

```python
>>> expected_order = {
...     'id': MatchesRegex('[0-9a-z]{10}'),
...     'quantity': GreaterThan(10),
...     'shippingAddress': Contains('Dublin'),
...     'deliveryDate': ANY,
...     'amount': InRange(200, 500),
...     'items': Contains('apples') &
...              Contains('bananas') &
...              ~Contains('pears'),
... }

>>> expected_order == {
...     'id': 'cxw23fac3n',
...     'quantity': 26,
...     'shippingAddress': '18 Some Street, Dublin, London',
...     'deliveryDate': 'tomorrow',
...     'amount': 300,
...     'items': [
...         'apples',
...         'avocados',
...         'bananas',
...     ],
... }
True

>>> expected_order == {
...     'id': 'XXX',
...     'quantity': 3,
...     'shippingAddress': '18 Some Other Street, New York City, USA',
...     'deliveryDate': 'yesterday',
...     'amount': 600,
...     'items': [
...         'apples',
...         'pears',
...     ],
... }
False
```

This approach can be very useful in unit testing, to make tests cases
shorter and easier to understand.


# Installation

PyStubs has no external dependencies. To install it:

```shell
$ pip install pystubs
```


## List of stubs

**Generics:**

| Stub                      | Usage                         | Equivalent to                 | Notes                                                             |
|---------------------------|-------------------------------|-------------------------------|-------------------------------------------------------------------|
| **ANY**                   | `x == ANY`                    | `True`                        |                                                                   |
| **PLACEHOLDER**           | `x == PLACEHOLDER`            | `False`                       | Meant to be used as a placeholder to be replaced at a later time  |
| **AnyOf**                 | `x == AnyOf([...])`           | `x in [...]`                  |                                                                   |
| **NoneOf**                | `x == NoneOf([...])`          | `x not in [...]`              |                                                                   |

**Equality:**

| Stub                      | Usage                         | Equivalent to                 | Notes                                                             |
|---------------------------|-------------------------------|-------------------------------|-------------------------------------------------------------------|
| **Equal**                 | `x == Equal(y)`               | `x == y`                      | Useful when combined with other stubs                             |
| **NotEqual**              | `x == NotEqual(y)`            | `x != y`                      |                                                                   |

**Order:**

| Stub                      | Usage                         | Equivalent to                 | Notes                                                             |
|---------------------------|-------------------------------|-------------------------------|-------------------------------------------------------------------|
| **LessThan**              | `x == LessThan(y)`            | `x < y`                       |                                                                   |
| **LessThanOrEqual**       | `x == LessThanOrEqual(y)`     | `x <= y`                      |                                                                   |
| **GreaterThan**           | `x == GreaterThan(y)`         | `x > y`                       |                                                                   |
| **GreaterThanOrEqual**    | `x == GreaterThanOrEqual(y)`  | `x >= y`                      |                                                                   |
| **InRange**               | `x == InRange(a, b)`          | `a <= x < b`                  |                                                                   |

**Containers:**

| Stub                      | Usage                         | Equivalent to                 | Notes                                                             |
|---------------------------|-------------------------------|-------------------------------|-------------------------------------------------------------------|
| **Contains**              | `x == Contains(y)`            | `y in x`                      |                                                                   |
| **HasSize**               | `x == HasSize(y)`             | `len(x) == y`                 |                                                                   |
| **CountOf**               | `x == CountOf(y, c)`          | `x.count(y) == c`             | Works on any iterable, even those that don't support `count()`    |
| **HasItems**              | `x == HasItems({key: value})` | `x[key] = value`              |                                                                   |

**Strings:**

These works on both `str` and `bytes` objects.

| Stub                      | Usage                         | Equivalent to                 | Notes                                                             |
|---------------------------|-------------------------------|-------------------------------|-------------------------------------------------------------------|
| **StartsWith**            | `x == StartsWith(y)`          | `x.startswith(y)`             |                                                                   |
| **EndsWith**              | `x == EndsWith(y)`            | `x.endswith(y)`               |                                                                   |
| **MatchesRegex**          | `x == MatchesRegex(p)`        | `re.match(p, x) is not None`  |                                                                   |
| **ContainsRegex**         | `x == ContainsRegex(p)`       | `re.search(p, x) is not None` |                                                                   |

**Type and identity testing:**

| Stub                      | Usage                         | Equivalent to                 | Notes                                                             |
|---------------------------|-------------------------------|-------------------------------|-------------------------------------------------------------------|
| **Is**                    | `x == Is(y)`                  | `x is y`                      |                                                                   |
| **IsNot**                 | `x == IsNot(y)`               | `x is not y`                  |                                                                   |
| **InstanceOf**            | `x == InstanceOf(type)`       | `isinstance(x, type)`         |                                                                   |


## Combining stubs

Stubs can be combined with the `|` (or), `&` (and), `^` (exclusive or) and
`~` (not) operators. For example, the following stub expression:

```python
>>> 'apple' == HasSize(5) & Contains('a')
True
```

is equivalent to the expression:

```python
>>> len('apple') == 5 and 'a' in 'apple'
True
```


## License

PyStubs is placed in the public domain. Feel free to do whatever you want with
it and/or it's source code!
