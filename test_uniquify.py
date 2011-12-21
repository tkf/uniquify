import uniquify
from nose.tools import eq_


class CheckData(object):

    def check(self, *args):
        raise NotImplementedError

    def test(self):
        for row in self.data:
            yield (self.check,) + tuple(row)


def rak(result, *args, **kwds):
    return (result, args, kwds)


class TestShortName(CheckData):

    data = [
        rak([], []),
        rak(['f', 'w'],
            ['_____abc___def',
             '_____xyz___uvw']),
        rak(['a', 'x'],
            ['_____abc___def',
             '_____xyz___uvw'],
            utype='head'),
        rak(['c...def', 'z...def', 'z...uvw'],
            ['_____abc___def',
             '_____xyz___def',
             '_____xyz___uvw']),
        rak(['abc___def', 'xyz___def', 'xy'],
            ['_____abc___def',
             '_____xyz___def',
             '_____xy'],
             minlen=2),
        rak(['...abc___def', '...xyz___def', '...x'],
            ['_____abc___def',
             '_____xyz___def',
             '_____x'], minlen=2),
        ]

    def check(self, result, args, kwds):
        eq_(result, uniquify.shortname(*args, **kwds))


class TestShortPath(CheckData):

    data = [
        rak([], []),
        rak(['DEF', 'UVW'],
            ['some/long/path/ABC/middle/part/DEF',
             'some/long/path/XYZ/middle/part/UVW']),
        rak(['ABC/.../DEF', 'XYZ/.../DEF', 'XYZ/.../UVW'],
            ['some/long/path/ABC/middle/part/DEF',
             'some/long/path/XYZ/middle/part/DEF',
             'some/long/path/XYZ/middle/part/UVW']),
        ]

    def check(self, result, args, kwds):
        eq_(result, uniquify.shortpath(*args, **kwds))


class TestSkipCommonName(CheckData):

    data = [
        rak([], []),
        rak(['a', 'b'],
            ['aa', 'ab'], skip=''),
        rak(['a', 'b'],
            ['aac', 'abc'], skip=''),
        rak(['aac', 'abc'],
            ['aac', 'abc']),
        rak(['aa...c', 'ab...b', 'ab...c'],
            ['aaxxxxc', 'abxxxxb', 'abxxxxc']),
        rak(['aa|...|de', 'ab|...|dd', 'ab|...|de'],
            ['aa|c|c|de', 'ab|c|c|dd', 'ab|c|c|de'], sep='|'),
        rak(['aa|c|de', 'ab|c|dd', 'ab|c|de'],
            ['aa|c|de', 'ab|c|dd', 'ab|c|de'],
            sep='|'),
        rak(['aa|*|*_e', 'ab|*|*_d', 'ab|*|*_e'],
            ['aa|c|d_e', 'ab|c|d_d', 'ab|c|d_e'],
            sep=('|', '_'), skip='*'),
        ]

    def check(self, result, args, kwds):
        eq_(result, uniquify.skipcommonname(*args, **kwds))


class TestSkipCommonPath(CheckData):

    data = [
        rak([], []),
        rak(['*/a', '*/b'],
            ['a/a', 'a/b'], skip='*'),
        rak(['*/a/*', '*/b/*'],
            ['a/a/c', 'a/b/c'], skip='*'),
        rak(['*/ac', '*/bc'],
            ['a/ac', 'a/bc'], skip='*'),
        ]

    def check(self, result, args, kwds):
        eq_(result, uniquify.skipcommonpath(*args, **kwds))
