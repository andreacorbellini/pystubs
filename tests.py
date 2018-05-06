import doctest
import re
import unittest

import stubs


def iter_public_names():
    return (name for name in dir(stubs) if not name.startswith('_'))


def iter_public_objects():
    return (getattr(stubs, name) for name in iter_public_names())


def iter_stubs():
    for obj in iter_public_objects():
        if isinstance(obj, stubs.Stub):
            yield obj
        if isinstance(obj, type) and issubclass(obj, stubs.Stub):
            yield obj


def iter_stub_types():
    for stub in iter_stubs():
        if not isinstance(stub, type):
            stub = type(stub)
        yield stub


class TestModule(unittest.TestCase):

    def test_all(self):
        actual = sorted(stubs.__all__)
        expected = sorted(iter_public_names())
        self.assertEqual(actual, expected)

    def test_slots(self):
        for stub in iter_stub_types():
            for cls in stub.__mro__:
                if cls is not object:
                    self.assertIn(
                        '__slots__', cls.__dict__,
                        '{} has no __slots__'.format(cls.__qualname__))

    def test_docstrings(self):
        for cls in iter_stub_types():
            self.assertTrue(
                cls.__doc__,
                '{} has no docstring'.format(cls.__qualname__))

    def test_doctests(self):
        doctest.testmod(stubs)


class StubsTestCase(unittest.TestCase):

    def assertEqual(self, first, second, msg=None):
        # Test both first==second and second==first. This is needed to make
        # sure that NotImplemented fallbacks work as expected in all situations
        super().assertEqual(first, second, msg)
        super().assertEqual(second, first, msg)

    def assertNotEqual(self, first, second, msg=None):
        super().assertNotEqual(first, second, msg)
        super().assertNotEqual(second, first, msg)


class TestSingletons(StubsTestCase):

    def test_any(self):
        self.assertEqual(repr(stubs.ANY), 'ANY')
        self.assertEqual(0, stubs.ANY)
        self.assertEqual(1j, stubs.ANY)
        self.assertEqual('abc', stubs.ANY)
        self.assertEqual([1, 2, 3], stubs.ANY)

    def test_placeholder(self):
        self.assertEqual(repr(stubs.PLACEHOLDER), 'PLACEHOLDER')
        self.assertNotEqual(0, stubs.PLACEHOLDER)
        self.assertNotEqual(1j, stubs.PLACEHOLDER)
        self.assertNotEqual('abc', stubs.PLACEHOLDER)
        self.assertNotEqual([1, 2, 3], stubs.PLACEHOLDER)


class TestGenerics(StubsTestCase):

    def test_any_of(self):
        self.assertRaises(TypeError, stubs.AnyOf)
        self.assertEqual(repr(stubs.AnyOf('abc')), "AnyOf(('a', 'b', 'c'))")
        self.assertNotEqual('b', stubs.AnyOf(''))
        self.assertEqual('b', stubs.AnyOf('abc'))
        self.assertNotEqual('d', stubs.AnyOf('abc'))

    def test_none_of(self):
        self.assertRaises(TypeError, stubs.NoneOf)
        self.assertEqual(repr(stubs.NoneOf('abc')), "NoneOf(('a', 'b', 'c'))")
        self.assertEqual('b', stubs.NoneOf(''))
        self.assertNotEqual('b', stubs.NoneOf('abc'))
        self.assertEqual('d', stubs.NoneOf('abc'))

    def test_instance_of(self):
        self.assertRaises(TypeError, stubs.InstanceOf)
        self.assertRaises(TypeError, stubs.InstanceOf, 1)
        self.assertEqual(repr(stubs.InstanceOf(str)), 'InstanceOf(str)')
        self.assertEqual('abc', stubs.InstanceOf(str))
        self.assertNotEqual(1, stubs.InstanceOf(str))


class TestOperators(StubsTestCase):

    def test_is(self):
        x = ['a', 'b', 'c']
        y = x[:]
        self.assertRaises(TypeError, stubs.Is)
        self.assertEqual(repr(stubs.Is(1)), 'Is(1)')
        self.assertEqual(x, stubs.Is(x))
        self.assertNotEqual(y, stubs.Is(x))

    def test_is_not(self):
        x = ['a', 'b', 'c']
        y = x[:]
        self.assertRaises(TypeError, stubs.IsNot)
        self.assertEqual(repr(stubs.IsNot(1)), 'IsNot(1)')
        self.assertNotEqual(x, stubs.IsNot(x))
        self.assertEqual(y, stubs.IsNot(x))

    def test_equal(self):
        self.assertRaises(TypeError, stubs.Equal)
        self.assertEqual(repr(stubs.Equal(1)), 'Equal(1)')
        self.assertEqual('abc', stubs.Equal('abc'))
        self.assertNotEqual('abc', stubs.Equal('def'))

    def test_not_equal(self):
        self.assertRaises(TypeError, stubs.NotEqual)
        self.assertEqual(repr(stubs.NotEqual(1)), 'NotEqual(1)')
        self.assertEqual('abc', stubs.NotEqual('def'))
        self.assertNotEqual('abc', stubs.NotEqual('abc'))

    def test_less_than(self):
        self.assertRaises(TypeError, stubs.LessThan)
        self.assertEqual(repr(stubs.LessThan(1)), 'LessThan(1)')
        self.assertNotEqual(1j, stubs.LessThan(2j))
        self.assertEqual(0, stubs.LessThan(1))
        self.assertEqual(0.0, stubs.LessThan(1))
        self.assertNotEqual(1, stubs.LessThan(1))
        self.assertNotEqual(1.0, stubs.LessThan(1))
        self.assertNotEqual(2, stubs.LessThan(1))
        self.assertNotEqual(2.0, stubs.LessThan(1))

    def test_less_than_or_equal(self):
        self.assertRaises(TypeError, stubs.LessThanOrEqual)
        self.assertEqual(repr(stubs.LessThanOrEqual(1)), 'LessThanOrEqual(1)')
        self.assertNotEqual(1j, stubs.LessThanOrEqual(2j))
        self.assertEqual(0, stubs.LessThanOrEqual(1))
        self.assertEqual(0.0, stubs.LessThanOrEqual(1))
        self.assertEqual(1, stubs.LessThanOrEqual(1))
        self.assertEqual(1.0, stubs.LessThanOrEqual(1))
        self.assertNotEqual(2, stubs.LessThanOrEqual(1))
        self.assertNotEqual(2.0, stubs.LessThanOrEqual(1))

    def test_more_than(self):
        self.assertRaises(TypeError, stubs.GreaterThan)
        self.assertEqual(repr(stubs.GreaterThan(1)), 'GreaterThan(1)')
        self.assertNotEqual(1j, stubs.GreaterThan(2j))
        self.assertNotEqual(0, stubs.GreaterThan(1))
        self.assertNotEqual(0.0, stubs.GreaterThan(1))
        self.assertNotEqual(1, stubs.GreaterThan(1))
        self.assertNotEqual(1.0, stubs.GreaterThan(1))
        self.assertEqual(2, stubs.GreaterThan(1))
        self.assertEqual(2.0, stubs.GreaterThan(1))

    def test_more_than_or_equal(self):
        self.assertRaises(TypeError, stubs.GreaterThanOrEqual)
        self.assertEqual(
            repr(stubs.GreaterThanOrEqual(1)), 'GreaterThanOrEqual(1)')
        self.assertNotEqual(1j, stubs.GreaterThanOrEqual(2j))
        self.assertNotEqual(0, stubs.GreaterThanOrEqual(1))
        self.assertNotEqual(0.0, stubs.GreaterThanOrEqual(1))
        self.assertEqual(1, stubs.GreaterThanOrEqual(1))
        self.assertEqual(1.0, stubs.GreaterThanOrEqual(1))
        self.assertEqual(2, stubs.GreaterThanOrEqual(1))
        self.assertEqual(2.0, stubs.GreaterThanOrEqual(1))

    def test_in_range(self):
        self.assertRaises(TypeError, stubs.InRange)
        self.assertRaises(TypeError, stubs.InRange, 1)
        self.assertEqual(repr(stubs.InRange(1, 2)), 'InRange(1, 2)')
        self.assertNotEqual(1j, stubs.InRange(5, 10))
        self.assertNotEqual(0, stubs.InRange(5, 10))
        self.assertNotEqual(0.0, stubs.InRange(5, 10))
        self.assertEqual(5, stubs.InRange(5, 10))
        self.assertEqual(5.0, stubs.InRange(5, 10))
        self.assertEqual(7, stubs.InRange(5, 10))
        self.assertEqual(7.0, stubs.InRange(5, 10))
        self.assertNotEqual(10, stubs.InRange(5, 10))
        self.assertNotEqual(10.0, stubs.InRange(5, 10))

    def test_contains(self):
        self.assertRaises(TypeError, stubs.Contains)
        self.assertEqual(repr(stubs.Contains(1)), 'Contains(1)')
        self.assertEqual('abc', stubs.Contains('a'))
        self.assertNotEqual('abc', stubs.Contains('d'))


class TestContainers(StubsTestCase):

    def test_has_size(self):
        self.assertRaises(TypeError, stubs.HasSize)
        self.assertEqual(repr(stubs.HasSize(1)), 'HasSize(1)')
        self.assertNotEqual(5, stubs.HasSize(5))
        self.assertEqual([], stubs.HasSize(0))
        self.assertEqual([1], stubs.HasSize(1))
        self.assertEqual('abc', stubs.HasSize(3))
        self.assertNotEqual([1], stubs.HasSize(5))

    def test_count_of(self):
        self.assertRaises(TypeError, stubs.CountOf)
        self.assertRaises(TypeError, stubs.CountOf, 'a')
        self.assertEqual(repr(stubs.CountOf(1, 2)), 'CountOf(1, 2)')
        self.assertNotEqual(5, stubs.CountOf('a', 5))
        self.assertEqual([], stubs.CountOf(1, 0))
        self.assertEqual([1], stubs.CountOf(1, 1))
        self.assertEqual('aabbcc', stubs.CountOf('a', 2))
        self.assertNotEqual([1], stubs.CountOf(2, 1))

    def test_has_items(self):
        self.assertEqual(repr(stubs.HasItems(a=1)), "HasItems({'a': 1})")
        self.assertNotEqual(5, stubs.HasItems(a=5))
        self.assertNotEqual([], stubs.HasItems({0: 1}))
        self.assertEqual([1], stubs.HasItems({0: 1}))
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, stubs.HasItems(a=1))
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, stubs.HasItems(a=1, b=2))
        self.assertNotEqual({'a': 1, 'b': 2, 'c': 3}, stubs.HasItems(a=2))
        self.assertNotEqual({'a': 1, 'b': 2, 'c': 3}, stubs.HasItems(a=2, b=2))
        self.assertNotEqual({'a': 1, 'b': 2, 'c': 3}, stubs.HasItems(a=1, d=4))


class BaseStringTestCase:

    def test_startswith(self):
        abc = self.convert('abc')
        a = self.convert('a')
        c = self.convert('c')
        self.assertRaises(TypeError, stubs.StartsWith)
        self.assertEqual(
            repr(stubs.StartsWith(abc)), 'StartsWith({!r})'.format(abc))
        self.assertNotEqual(1, stubs.StartsWith(a))
        self.assertNotEqual('x', stubs.StartsWith(b'x'))
        self.assertNotEqual(b'x', stubs.StartsWith('x'))
        self.assertEqual(abc, stubs.StartsWith(a))
        self.assertNotEqual(abc, stubs.StartsWith(c))

    def test_endswith(self):
        abc = self.convert('abc')
        a = self.convert('a')
        c = self.convert('c')
        self.assertRaises(TypeError, stubs.EndsWith)
        self.assertEqual(
            repr(stubs.EndsWith(abc)), 'EndsWith({!r})'.format(abc))
        self.assertNotEqual(1, stubs.EndsWith(a))
        self.assertNotEqual('x', stubs.EndsWith(b'x'))
        self.assertNotEqual(b'x', stubs.EndsWith('x'))
        self.assertEqual(abc, stubs.EndsWith(c))
        self.assertNotEqual(abc, stubs.EndsWith(a))

    def test_matches_regex(self):
        abc = self.convert('abc')

        self.assertRaises(TypeError, stubs.MatchesRegex)
        self.assertRaises(
            ValueError, stubs.MatchesRegex, re.compile(abc), re.I)

        self.assertEqual(
            repr(stubs.MatchesRegex(abc)),
            'MatchesRegex({!r})'.format(abc))
        self.assertEqual(
            repr(stubs.MatchesRegex(abc, re.I)),
            'MatchesRegex({!r}, re.IGNORECASE)'.format(abc))

        self.assertNotEqual(1, stubs.MatchesRegex('a'))
        self.assertEqual(abc, stubs.MatchesRegex(self.convert('a')))
        self.assertEqual(abc, stubs.MatchesRegex(self.convert('^.{2}c$')))
        self.assertNotEqual(abc, stubs.MatchesRegex(self.convert('A')))
        self.assertEqual(abc, stubs.MatchesRegex(self.convert('A'), re.I))
        self.assertNotEqual(
            abc, stubs.MatchesRegex(re.compile(self.convert('A'))))
        self.assertEqual(
            abc, stubs.MatchesRegex(re.compile(self.convert('A'), re.I)))

    def test_contains_regex(self):
        abc = self.convert('abc')

        self.assertRaises(TypeError, stubs.ContainsRegex)
        self.assertRaises(
            ValueError, stubs.ContainsRegex, re.compile(abc), re.I)

        self.assertEqual(
            repr(stubs.ContainsRegex(abc)),
            'ContainsRegex({!r})'.format(abc))
        self.assertEqual(
            repr(stubs.ContainsRegex(abc, re.I)),
            'ContainsRegex({!r}, re.IGNORECASE)'.format(abc))

        self.assertNotEqual(1, stubs.ContainsRegex('a'))
        self.assertEqual(abc, stubs.ContainsRegex(self.convert('b')))
        self.assertNotEqual(abc, stubs.ContainsRegex(self.convert('B')))
        self.assertEqual(abc, stubs.ContainsRegex(self.convert('B'), re.I))
        self.assertNotEqual(
            abc, stubs.ContainsRegex(re.compile(self.convert('B'))))
        self.assertEqual(
            abc, stubs.ContainsRegex(re.compile(self.convert('B'), re.I)))


class TestStrings(BaseStringTestCase, StubsTestCase):

    convert = str


class TestBytes(BaseStringTestCase, StubsTestCase):

    def convert(self, s):
        return s.encode('utf-8')


class TestComposition(StubsTestCase):

    def test_not(self):
        s = ~stubs.LessThan(5)
        self.assertIsInstance(s, stubs.Not)

        self.assertRaises(TypeError, stubs.Not)
        self.assertRaises(TypeError, stubs.Not, 1)
        self.assertEqual(repr(s), '~LessThan(5)')

        self.assertEqual('x', s)
        self.assertEqual(10, s)
        self.assertNotEqual(1, s)

    def test_and(self):
        s = stubs.HasSize(2) & stubs.Contains('a') & stubs.Contains('b')
        self.assertIsInstance(s, stubs.And)

        self.assertRaises(TypeError, stubs.And)
        self.assertRaises(TypeError, stubs.And, [1])
        self.assertEqual(
            repr(s), "(HasSize(2) & Contains('a') & Contains('b'))")

        self.assertEqual('ab', s)
        self.assertEqual('ba', s)
        self.assertNotEqual('abc', s)

    def test_or(self):
        s = stubs.LessThan(1) | stubs.GreaterThan(2) | stubs.HasSize(2)
        self.assertIsInstance(s, stubs.Or)

        self.assertRaises(TypeError, stubs.Or)
        self.assertRaises(TypeError, stubs.Or, [1])
        self.assertEqual(
            repr(s), '(LessThan(1) | GreaterThan(2) | HasSize(2))')

        self.assertEqual(0, s)
        self.assertNotEqual(1, s)
        self.assertNotEqual(1.5, s)
        self.assertNotEqual(2, s)
        self.assertEqual(3, s)
        self.assertEqual('ab', s)
        self.assertNotEqual('abc', s)

    def test_xor(self):
        s = stubs.Equal('x') ^ stubs.Contains('a') ^ stubs.Contains('b')
        self.assertIsInstance(s, stubs.Xor)

        self.assertRaises(TypeError, stubs.Or)
        self.assertRaises(TypeError, stubs.Or, [1])
        self.assertEqual(
            repr(s), "(Equal('x') ^ Contains('a') ^ Contains('b'))")

        self.assertEqual('x', s)
        self.assertEqual('xa', s)
        self.assertEqual('xb', s)
        self.assertNotEqual('ab', s)
        self.assertNotEqual('xx', s)


if __name__ == '__main__':
    unittest.main()
