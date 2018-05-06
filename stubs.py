import abc as _abc
import operator as _operator
import re as _re


__all__ = [
    'ANY',
    'And',
    'AnyOf',
    'Contains',
    'ContainsRegex',
    'CountOf',
    'EndsWith',
    'Equal',
    'GreaterThan',
    'GreaterThanOrEqual',
    'HasItems',
    'HasSize',
    'InRange',
    'InstanceOf',
    'Is',
    'IsNot',
    'LessThan',
    'LessThanOrEqual',
    'MatchesRegex',
    'NoneOf',
    'Not',
    'NotEqual',
    'Or',
    'PLACEHOLDER',
    'StartsWith',
    'Stub',
    'Xor',
]


def _check_type(arg, expected_type, many=False):
    if many:
        for item in arg:
            _check_type(item, expected_type)
        return

    if not isinstance(arg, expected_type):
        raise TypeError('expected a {} object, got {}'.format(
            expected_type.__name__, type(arg).__qualname__))


class Stub(metaclass=_abc.ABCMeta):
    """Base class for all the stubs."""

    __slots__ = ()

    @_abc.abstractmethod
    def __eq__(self, other):
        """self.__eq__(other)  <==>  self == other"""
        raise NotImplementedError

    def __and__(self, other):
        """self.__and__(other)  <==>  self & other"""
        return And((self, other))

    def __or__(self, other):
        """self.__or__(other)  <==>  self | other"""
        return Or((self, other))

    def __xor__(self, other):
        """self.__xor__(other)  <==>  self ^ other"""
        return Xor((self, other))

    def __invert__(self):
        """self.__invert__()  <==>  ~self"""
        return Not(self)

    def __repr__(self):
        """self.__repr__()  <==>  repr(self)"""
        all_slots = []

        for cls in reversed(self.__class__.__mro__):
            cls_slots = getattr(cls, '__slots__', None)
            if cls_slots:
                all_slots += cls_slots

        args = (repr(getattr(self, name)) for name in all_slots)

        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(args),
        )


# Singletons ##################################################################


class _SingletonMeta(_abc.ABCMeta):

    def __new__(mcls, name, bases, attrs, instantiate=True):
        cls = super().__new__(mcls, name, bases, attrs)
        return cls() if instantiate else cls


class _SingletonStub(Stub, metaclass=_SingletonMeta, instantiate=False):

    __slots__ = ()

    def __repr__(self):
        return self.__class__.__name__


class ANY(_SingletonStub):
    """x == ANY is always True"""

    __slots__ = ()

    def __eq__(self, other):
        return True


class PLACEHOLDER(_SingletonStub):
    """
    x == PLACEHOLDER is always False

    This is meant to be used as a placeholder value to be replaced at a later
    time.
    """

    __slots__ = ()

    def __eq__(self, other):
        return False


# Generics ####################################################################


class _ValuesStub(Stub):

    __slots__ = ('values',)

    def __init__(self, values):
        self.values = tuple(values)


class AnyOf(_ValuesStub):
    """
    x == AnyOf(y)  <==>  x in y

    Examples:

        >>> 'i' == AnyOf(['i', 'j', 'k'])
        True

        >>> 'z' == AnyOf(['i', 'j', 'k'])
        False
    """

    __slots__ = ()

    def __eq__(self, other):
        return other in self.values


class NoneOf(_ValuesStub):
    """x == NoneOf(y)  <==>  x not in y

    Examples:

        >>> 6 == NoneOf([1, 2, 3])
        True

        >>> 2 == NoneOf([1, 2, 3])
        False
    """

    __slots__ = ()

    def __eq__(self, other):
        return other not in self.values


class InstanceOf(Stub):
    """x == InstanceOf(y)  <==>  isinstance(x, y)"""

    __slots__ = ('type',)

    def __init__(self, class_or_tuple):
        if isinstance(class_or_tuple, type):
            _check_type(class_or_tuple, type)
        else:
            class_or_tuple = tuple(class_or_tuple)
            _check_type(class_or_tuple, type, many=True)
        self.type = class_or_tuple

    def __eq__(self, other):
        return isinstance(other, self.type)

    def __repr__(self):
        if isinstance(self.type, type):
            arg = self.type.__qualname__
        else:
            arg = '({})'.format(', '.join(
                cls.__qualname__ for cls in self.type))
        return '{}({})'.format(self.__class__.__name__, arg)


# Operators ###################################################################


class _ValueStub(Stub):

    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


class _OperatorStub(_ValueStub):

    __slots__ = ()

    @property
    @_abc.abstractmethod
    def operator(self):
        raise NotImplementedError

    def __eq__(self, other):
        try:
            return self.operator(other, self.value)
        except TypeError:
            return NotImplemented


class Is(_OperatorStub):
    """x == Is(y)  <==>  x is y"""

    __slots__ = ()

    operator = _operator.is_


class IsNot(_OperatorStub):
    """x == IsNot(y)  <==>  x is not y"""

    __slots__ = ()

    operator = _operator.is_not


class Equal(_OperatorStub):
    """x == Equal(y)  <==>  x == y"""

    __slots__ = ()

    operator = _operator.eq


class NotEqual(_OperatorStub):
    """x == NotEqual(y)  <==>  x != y"""

    __slots__ = ()

    operator = _operator.ne


class LessThan(_OperatorStub):
    """x == LessThan(y)  <==>  x < y"""

    __slots__ = ()

    operator = _operator.lt


class LessThanOrEqual(_OperatorStub):
    """x == LessThanOrEqual(y)  <==>  x <= y"""

    __slots__ = ()

    operator = _operator.le


class GreaterThan(_OperatorStub):
    """x == GreaterThan(y)  <==>  x > y"""

    __slots__ = ()

    operator = _operator.gt


class GreaterThanOrEqual(_OperatorStub):
    """x == GreaterThan(y)  <==>  x >= y"""

    __slots__ = ()

    operator = _operator.ge


class InRange(Stub):
    """x == InRange(y, z)  <==>  y <= x < z"""

    __slots__ = ('start', 'stop')

    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __eq__(self, other):
        try:
            return self.start <= other < self.stop
        except TypeError:
            return NotImplemented


class Contains(_OperatorStub):
    """x == Contains(y)  <==>  y in x"""

    __slots__ = ()

    operator = _operator.contains


# Containers ##################################################################


class HasSize(_ValueStub):
    """x == HasSize(y)  <==>  len(x) == y"""

    __slots__ = ()

    def __eq__(self, other):
        try:
            return len(other) == self.value
        except TypeError:
            return NotImplemented


class CountOf(Stub):
    """
    x == CountOf(y, z)  <==>  operator.countOf(x) == z

    Example:

        >>> 'aaabbc' == CountOf('a', 3)
        True
        >>> 'aaabbc' == CountOf('b', 2)
        True
        >>> 'aaabbc' == CountOf('c', 1)
        True
    """

    __slots__ = ('item', 'count')

    def __init__(self, item, count):
        self.item = item
        self.count = count

    def __eq__(self, other):
        try:
            return _operator.countOf(other, self.item) == self.count
        except TypeError:
            return NotImplemented


class HasItems(Stub):
    """
    x == HasItems({y: z})  <==>  x[y] = z

    This stub may be used to check whether a container contains a certain set
    of items.

    Examples:

        >>> {'a': 1, 'b': 2, 'c': 3} == HasItems(a=1)
        True
        >>> {'a': 1, 'b': 2, 'c': 3} == HasItems(a=5)
        False
        >>> {'a': 1, 'b': 2, 'c': 3} == HasItems(d=4)
        False

    It can be used on any kind of container, not just dicts:

        >>> # This is equivalent to ['a', 'b', 'c'][1] == 'b'
        >>> ['a', 'b', 'c'] == HasItems({1: 'b'})
        True

    Values may be stubs:

        >>> {'a': 10} == HasItems(a=GreaterThan(5))
        True
    """

    __slots__ = ('mapping',)

    def __init__(self, *args, **kwargs):
        self.mapping = dict(*args, **kwargs)

    def __eq__(self, other):
        # Make sure that other is a container type (with hasattr instead of
        # catching TypeError later). This is especially important in case
        # self.mapping is empty.
        if not hasattr(other, '__getitem__'):
            return NotImplemented
        try:
            for key, value in self.mapping.items():
                if other[key] != value:
                    return False
        except (KeyError, IndexError):
            return False
        return True


# Strings #####################################################################


class StartsWith(Stub):
    """x == StartsWith(y)  <==>  x.startswith(y)"""

    __slots__ = ('prefix',)

    def __init__(self, prefix):
        self.prefix = prefix

    def __eq__(self, other):
        if not hasattr(other, 'startswith'):
            return NotImplemented
        try:
            return other.startswith(self.prefix)
        except TypeError:
            return NotImplemented


class EndsWith(Stub):
    """x == EndsWith(y)  <==>  x.endswith(y)"""

    __slots__ = ('suffix',)

    def __init__(self, suffix):
        self.suffix = suffix

    def __eq__(self, other):
        if not hasattr(other, 'endswith'):
            return NotImplemented
        try:
            return other.endswith(self.suffix)
        except TypeError:
            return NotImplemented


class _RegexStub(Stub):

    __slots__ = ('regex',)

    def __init__(self, pattern, flags=0):
        self.regex = _re.compile(pattern, flags)

    def __repr__(self):
        arg = repr(self.regex)
        arg = arg[len('re.compile('):-len(')')]
        return '{}({})'.format(self.__class__.__name__, arg)


class MatchesRegex(_RegexStub):
    """x == MatchesRegex(y)  <==>  re.match(y, x) is not None"""

    __slots__ = ()

    def __eq__(self, other):
        try:
            return self.regex.match(other) is not None
        except TypeError:
            return NotImplemented


class ContainsRegex(_RegexStub):
    """x == ContainsRegex(y)  <==>  re.search(y, x) is not None"""

    __slots__ = ()

    def __eq__(self, other):
        try:
            return self.regex.search(other) is not None
        except TypeError:
            return NotImplemented


# Composition #################################################################


class _UnaryOp(Stub):

    __slots__ = ('condition',)

    def __init__(self, condition):
        _check_type(condition, Stub)
        self.condition = condition


class Not(_UnaryOp):
    """Not(x)  <==>  ~x"""

    __slots__ = ()

    def __eq__(self, other):
        return other != self.condition

    def __invert__(self):
        return self.condition

    def __repr__(self):
        return '~{!r}'.format(self.condition)


class _BinaryOp(Stub):

    __slots__ = ('conditions',)

    def __init__(self, conditions):
        self.conditions = tuple(conditions)
        _check_type(self.conditions, Stub, many=True)


class And(_BinaryOp):
    """And([x, y, ...])  <==>  x & y & ..."""

    __slots__ = ()

    def __eq__(self, other):
        return all(other == cond for cond in self.conditions)

    def __and__(self, other):
        if isinstance(other, And):
            return And(self.conditions + other.conditions)
        else:
            return And(self.conditions + (other,))

    def __repr__(self):
        return '({})'.format(' & '.join(
            repr(cond) for cond in self.conditions))


class Or(_BinaryOp):
    """Or([x, y, ...])  <==>  x | y | ..."""

    __slots__ = ()

    def __eq__(self, other):
        return other in self.conditions

    def __or__(self, other):
        if isinstance(other, Or):
            return Or(self.conditions + other.conditions)
        else:
            return Or(self.conditions + (other,))

    def __repr__(self):
        return '({})'.format(' | '.join(
            repr(cond) for cond in self.conditions))


class Xor(_BinaryOp):
    """Xor([x, y, ...])  <==>  x ^ y ^ ..."""

    __slots__ = ()

    def __eq__(self, other):
        return _operator.countOf(self.conditions, other) == 1

    def __xor__(self, other):
        if isinstance(other, Xor):
            return Xor(self.conditions + other.conditions)
        else:
            return Xor(self.conditions + (other,))

    def __repr__(self):
        return '({})'.format(' ^ '.join(
            repr(cond) for cond in self.conditions))
