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
        rak(['...'], ['one']),
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
        rak(['...'], ['one']),
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
        rak(['...'], ['one']),
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
        rak(['*/b/z', '*/c/d/z'],
            ['a/b/z', 'a/c/d/z'],
            sep='/', skip='*'),
        ]

    def check(self, result, args, kwds):
        eq_(result, uniquify.skipcommonname(*args, **kwds))


class TestSkipCommonPath(CheckData):

    data = [
        rak([], []),
        rak(['...'], ['one']),
        rak(['*/a', '*/b'],
            ['a/a', 'a/b'], skip='*'),
        rak(['*/a/*', '*/b/*'],
            ['a/a/c', 'a/b/c'], skip='*'),
        rak(['*/ac', '*/bc'],
            ['a/ac', 'a/bc'], skip='*'),
        ]

    def check(self, result, args, kwds):
        eq_(result, uniquify.skipcommonpath(*args, **kwds))


class TestSeqListSkipCommon(CheckData):

    skipmarker = "@@@@@"
    data = [
        ([['a', 'b', 'c'], ['x', 'y', 'z']], ('|', )),
        ([['a', skipmarker, 'b', 'c'],
          ['x', skipmarker, 'y', 'z']], ('|', )),
        ([['a', [skipmarker, 'b'], 'c'],
          ['x', [skipmarker, 'y'], 'z']], ('|', '-')),
        ]
    # note that skipmarker must be at exactly the same place for each
    # list in the namesources

    def check(self, namesources, seplist, skip="..."):
        names = [makename(ns, seplist) for ns in namesources]
        desired = [makename(ns, seplist) for ns in
                   deeplyreplaced(namesources, self.skipmarker, skip)]
        sl = uniquify.SeqList.skipcommon(names, seplist, skip)
        eq_(desired, sl.joinseqs())


def makename(namesource, seplist):
    """
    Make a list of string joined using `sep`-s in `seplist`

    >>> makename(['a', 'b', 'c'], ('.',))
    'a.b.c'
    >>> makename([['a', 'b'], ['c'], ['d']], ('.', '-'))
    'a-b.c.d'

    """
    if seplist:
        remseps = seplist[1:]
        return seplist[0].join(makename(sub, remseps) for sub in namesource)
    else:
        return namesource


def deeplyreplaced(lst, old, new):
    """
    Replace element `old` in (possibility nested) list

    >>> deeplyreplaced([[1, [1, 1, [0, 1], 1]], [1, 1]], 0, 'REPLACED')
    [[1, [1, 1, ['REPLACED', 1], 1]], [1, 1]]

    """
    newlst = []
    for elem in lst:
        if isinstance(elem, list):
            elem = deeplyreplaced(elem, old, new)
        elif elem == old:
            elem = new
        newlst.append(elem)
    return newlst


class TestColViewHomo(CheckData):

    data = [
        (True,  [[0, 1], [0, 2], [0, 2]], 0),
        (False, [[0, 1], [0, 2], [0, 2]], 1),
        (False, [[0, 1], [0, 2], [0, 2]], 2),
        (False, [[0, 1], [0, 2], [0, 2]], 0, []),
        (True,  [[0, 1], [0, 2], [0, 2]], 1, range(1, 3)),
        ]

    def check(self, result, los, i, indices=None):
        col = uniquify.ColView(los, i)
        if indices is not None:
            col.indices = indices
        eq_(result, col.homo())
