# Import README.rst using cog
# [[[cog
# from cog import out
# out('"""\n{0}\n"""'.format(file('README.rst').read()))
# ]]]
"""
Uniquify - get unique, short and easy-to-read names and paths
=============================================================

Examples
--------

Shorten names/paths by extracting non-common parts:

>>> from uniquify import shortname, shortpath
>>> shortname(['__common_part___abc___common_part__',
...            '__common_part___xbc___common_part__',
...            '__common_part___xyz___common_part__'])
['abc', 'xbc', 'xyz']
>>> shortpath(['some/long/path/___/alpha/___/___/',
...            'some/long/path/___/beta/___/___/',
...            'some/long/path/___/gamma/___/___/'])
['alpha', 'beta', 'gamma']


Convert common parts into skip marks:

>>> from uniquify import skipcommonname, skipcommonpath
>>> skipcommonname(['ab__common_part___c',
...                 'ij__common_part___k',
...                 'xy__common_part___z'])
['ab...c', 'ij...k', 'xy...z']
>>> skipcommonpath(['alpha/common/path/beta',
...                 'epsilon/common/path/delta',
...                 'phi/common/path/psi'])
['alpha/.../beta', 'epsilon/.../delta', 'phi/.../psi']


Install
-------

Install it from pypi_

::

  pip install uniquify
  # easy_install uniquify

.. _pypi: http://pypi.python.org/pypi/uniquify/

"""
# [[[end]]]

__author__ = "Takafumi Arakaki"
__version__ = '0.0.1'
__license__ = "MIT License"
__all__ = ["shortname", "shortpath", "shortpath", "shortname"]


import os
import functools


def _pass_empty_list(func):
    @functools.wraps(func)
    def new_func(lst, *args, **kwds):
        if not lst:
            return []
        return func(lst, *args, **kwds)
    return new_func


@_pass_empty_list
def shortname(names, sep=None, skip='...', utype='tail', minlen=1):
    """
    Get unique short names from a list of strings

    >>> shortname(['_____abc___def',
    ...            '_____xyz___uvw'])
    ['f', 'w']
    >>> shortname(['_____abc___def',
    ...            '_____xyz___uvw'], utype='head')
    ['a', 'x']
    >>> shortname(['_____abc___def',
    ...            '_____xyz___def',
    ...            '_____xyz___uvw'])
    ['c...def', 'z...def', 'z...uvw']
    >>> shortname(['_____abc___def',
    ...            '_____xyz___def',
    ...            '_____x'])
    ['abc___def', 'xyz___def', 'x']
    >>> shortname(['_____abc___def',
    ...            '_____xyz___def',
    ...            '_____xy'], minlen=2)
    ['abc___def', 'xyz___def', 'xy']
    >>> shortname(['_____abc___def',
    ...            '_____xyz___def',
    ...            '_____x'], minlen=2)
    ['...abc___def', '...xyz___def', '...x']

    """
    names = list(names)
    if utype not in ['tail', 'head']:
        raise ValueError("'{0}' is not a recognized ``utype``".format(utype))
    if not isinstance(sep, (tuple, list)):
        sep = (sep,)

    sl = SeqList.skipcommon(names, sep, skip).filled(None)
    if utype == 'tail':
        sl.reverseseq()

    numnames = len(set(names))
    i0set = False
    for i in range(sl.maxseqlen()):
        if not i0set and not sl.col(i).homo():
            i0 = i
            i0set = True
        if i0set:
            subsl = sl.subseqlist(i0, i + 1)
            if utype == 'tail':
                subsl.reverseseq()
            subnames = subsl.joinseqs_skipping_nones()
            if (len(set(subnames)) == numnames and
                min(map(len, subnames)) >= minlen):
                return subnames
    if utype == 'tail':
        sl.reverseseq()
    return sl.joinseqs_skipping_nones()


@_pass_empty_list
def shortpath(names, skip='...', utype='tail', minlen=1):
    """
    Get unique short paths from a list of strings

    >>> shortpath(['some/long/path/ABC/middle/part/DEF',
    ...            'some/long/path/XYZ/middle/part/UVW'])
    ['DEF', 'UVW']
    >>> shortpath(['some/long/path/ABC/middle/part/DEF',
    ...            'some/long/path/XYZ/middle/part/DEF',
    ...            'some/long/path/XYZ/middle/part/UVW'])
    ['ABC/.../DEF', 'XYZ/.../DEF', 'XYZ/.../UVW']

    """
    return shortname(names, os.path.sep, skip, utype, minlen)


@_pass_empty_list
def skipcommonname(names, sep=None, skip='...'):
    """
    Generate unique names from a list of strings

    >>> skipcommonname(['aa', 'ab'], skip='')
    ['a', 'b']
    >>> skipcommonname(['aac', 'abc'], skip='')
    ['a', 'b']
    >>> skipcommonname(['aac', 'abc'])
    ['aac', 'abc']
    >>> skipcommonname(['aaxxxxc', 'abxxxxb', 'abxxxxc'])
    ['aa...c', 'ab...b', 'ab...c']
    >>> skipcommonname(['aa|c|c|de', 'ab|c|c|dd', 'ab|c|c|de'], sep='|')
    ['aa|...|de', 'ab|...|dd', 'ab|...|de']
    >>> skipcommonname(['aa|c|de', 'ab|c|dd', 'ab|c|de'], sep='|')
    ['aa|c|de', 'ab|c|dd', 'ab|c|de']
    >>> skipcommonname(['aa|c|d_e',
    ...                 'ab|c|d_d',
    ...                 'ab|c|d_e'],
    ...                sep=('|', '_'), skip='*')
    ['aa|*|*_e', 'ab|*|*_d', 'ab|*|*_e']

    """
    names = list(names)
    if not isinstance(sep, (tuple, list)):
        sep = (sep,)
    return SeqList.skipcommon(names, sep, skip).joinseqs()


def _split_names(names, sep):
    """
    Split strings in ``names`` and returns ``(names, sep)`` pair

    >>> _split_names(['abc'], None)
    ([['a', 'b', 'c']], '')
    >>> _split_names(['a/b/c'], '/')
    ([['a', 'b', 'c']], '/')

    """
    if sep is None:
        return ([list(n) for n in names], '')
    else:
        return ([n.split(sep) for n in names], sep)


@_pass_empty_list
def skipcommonpath(paths, skip='...'):
    """
    Generate unique names from a list of file paths

    >>> skipcommonpath(['a/a', 'a/b'], skip='*')
    ['*/a', '*/b']
    >>> skipcommonpath(['a/a/c', 'a/b/c'], skip='*')
    ['*/a/*', '*/b/*']
    >>> skipcommonpath(['a/ac', 'a/bc'], skip='*')
    ['*/ac', '*/bc']

    """
    return skipcommonname(paths, os.path.sep, skip)


def _skip_common_parts_in_lol(lol, chunks, sep, skip):
    return list(_skip_common_parts(n, chunks, sep, skip) for n in lol)


def _skip_common_parts(name, chunks, sep, skip):
    """
    Convert common parts in ``name`` to ``skip``

    Skipping is avoided if it makes name longer.

    >>> chunks = ([(0, 5), (5, 10), (10, 15)], [True, False, True])
    >>> _skip_common_parts(list('aaaaa*****ccccc'), chunks, '', '...')
    'aaaaa...ccccc'
    >>> chunks = ([(0, 1), (1, 2), (2, 3)], [True, False, True])
    >>> _skip_common_parts(['a', '*', 'c'], chunks, '/', '...')
    'a/*/c'
    >>> _skip_common_parts(['aaaaa', '*****', 'ccccc'], chunks, '/', '...')
    'aaaaa/.../ccccc'
    >>> _skip_common_parts(['aaaaa', '*****'], chunks, '/', '...')
    'aaaaa/...'

    """
    return sep.join(_skip_common_parts_as_list(name, chunks, len(sep), skip))


def _every_other(iterative, sep, head=False, tail=False):
    """
    Put ``sep`` into every other element in ``iterative``

    >>> list(_every_other([1, 2, 3], 0))
    [1, 0, 2, 0, 3]
    >>> list(_every_other([1, 2, 3], 0, head=True, tail=True))
    [0, 1, 0, 2, 0, 3, 0]

    """
    iterative = iter(iterative)
    if head:
        yield sep
    yield iterative.next()
    for elem in iterative:
        yield sep
        yield elem
    if tail:
        yield sep


def _skip_common_parts_as_list(name, chunks, sepwidth, skip):
    skipwidth = len(skip)
    newname = []
    for ((start, stop), diff) in zip(*chunks):
        subname = name[start:stop]
        subwidth = sum(map(len, subname)) + sepwidth * (stop - start)
        if diff or subwidth < skipwidth:
            newname.extend(subname)
        else:
            newname.append(skip)
    return newname


def _get_chunks(lol):
    """
    Returns common and different "chunks" of the list in the list (``lol``)

    Data structure of chunks
    ------------------------

    chunks : (ranges, diffs)
        Common and different chunks

        ranges : [(start, stop)]
            A list of ranges (start-stop pairs)

            start : int
                The first index of the range

            stop : int
                The last + 1 index of the range

        diffs : [bool]
            True if the corresponding element in ``ranges`` is
            different, otherwise False.

    Examples
    --------

    >>> _get_chunks([[1, 2, 3],
    ...              [1, 2, 2]])
    ([(0, 2), (2, 3)], [False, True])
    >>> _get_chunks([[1, 2, 1, 2, 3, 3, 1, 2],
    ...              [1, 2, 1, 2, 4, 4, 1, 2]])
    ([(0, 4), (4, 6), (6, 8)], [False, True, False])

    """
    ranges = []
    diffs = []
    rawdiffs = _diff_list(lol)
    start = 0
    d1 = rawdiffs[0]
    for (i, (d0, d1)) in enumerate(zip(rawdiffs[:-1], rawdiffs[1:])):
        if d0 != d1:
            ranges.append((start, i + 1))
            diffs.append(d0)
            start = i + 1
    ranges.append((start, len(rawdiffs)))
    diffs.append(d1)
    return (ranges, diffs)


def _diff_list(lol):
    """
    Find the different part in `lol` (list of list)

    >>> _diff_list([[1, 2, 3],
    ...             [1, 2, 2]])
    [False, False, True]
    >>> _diff_list([[1, 2, 3],
    ...             [1, 2, 2],
    ...             [1, 1, 2]])
    [False, True, True]
    >>> _diff_list([[1, 2, 3],
    ...             [1, 2]])
    [False, False, True]
    >>> _diff_list([[1, 2, 3]])
    [False, False, False]
    >>> _diff_list([])
    []

    """
    if len(lol) == 0:
        return []
    elif len(lol) == 1:
        return [False] * len(lol[0])

    ls0 = lol[0]
    ls0len = len(ls0)
    maxlen = max(len(ls) for ls in lol)
    indices = range(maxlen)
    diff = [False] * maxlen
    for ls in lol[1:]:
        for i in indices:
            if ls0len <= i or len(ls) <= i or ls0[i] != ls[i]:
                diff[i] = True
    return diff


class SeqList(object):
    r"""
    List of sequence to hold data to be uniquified

    Here, a "sequence" typically means a list of string.
    (However, it can be a list of any comparable elements.)

    List of sequence, its indices and columns::

        Definition
                        columns
                 /-------------------\
                   j=0  j=1  j=2
        Seq. i=0:   a0   a1   a2   ...   \
        Seq. i=1:   b0   b1   b2   ...   | List
        Seq. i=2:   c0   c1   c2   ...   |  of
           ...                           | Sequence
        Seq. i=N:   z0   z1   z2   ...   /
                    |    |
                    |    `- 1-st column
                    `- 0-th column

    """

    def __init__(self, los):
        """Create SeqList from a list of sequence `los`"""
        self._los = los

    def __unicode__(self):
        return u"{0}({1})".format(self.__class__.__name__, self._los)

    def __repr__(self):
        return u"{0}({1!r})".format(self.__class__.__name__, self._los)

    def __len__(self):
        return len(self._los)

    def __iter__(self):
        return iter(self._los)

    @classmethod
    def skipcommon(cls, names, seplist, skip):
        if seplist:
            (lol, sep) = _split_names(names, seplist[0])
            chunks = _get_chunks(lol)
            newlol = [_skip_common_parts_as_list(n, chunks, len(sep), skip)
                      for n in lol]
            if sep:
                newlol = [list(_every_other(l, sep)) for l in newlol]
            newsl = cls(newlol)
            fullsl = cls.makeempty(len(newsl))
            for i in range(newsl.maxseqlen()):
                subnames = newsl.col(i)
                if subnames.homo() and subnames.nonnull() in (sep, skip):
                    subnews = [[n] for n in subnames]
                else:
                    subnews = cls.skipcommon(subnames, seplist[1:], skip)
                fullsl.extendseq(subnews, subnames.indices)
            return fullsl
        else:
            return cls([[n] for n in names])

    def col(self, i):
        """
        Get `i`-th column as a view

        >>> sl = SeqList([[0, 1, 2], [3, 4]])
        >>> list(sl.col(0))
        [0, 3]
        >>> list(sl.col(2))
        [2]
        >>> sl.col(2).indices
        [0]

        """
        return ColView(self._los, i)

    def extendseq(self, los, indices):
        """
        Extend sequences by adding each sequence in the list `los`

        >>> sl = SeqList([[0], [3]])
        >>> sl.extendseq([[1], [4]], [0, 1])
        >>> sl
        SeqList([[0, 1], [3, 4]])
        >>> sl.extendseq([[2, 2]], [0])
        >>> sl
        SeqList([[0, 1, 2, 2], [3, 4]])

        """
        for (s, i) in zip(los, indices):
            self._los[i].extend(s)

    @classmethod
    def makeempty(cls, numseq):
        return cls([[] for _dummy in range(numseq)])

    def subseqlist(self, start, stop):
        """
        Get list of subsequences

        >>> sl = SeqList([[0, 1, 2], [3, 4, 5]])
        >>> sl.subseqlist(1, 3)
        SeqList([[1, 2], [4, 5]])

        """
        return self.__class__([s[start:stop] for s in self._los])

    def reverseseq(self):
        """
        Reverse all sequences

        >>> sl = SeqList([[0, 1, 2], [3, 4, 5]])
        >>> sl.reverseseq()
        >>> sl
        SeqList([[2, 1, 0], [5, 4, 3]])

        """
        self._los = [list(reversed(s)) for s in self._los]

    def filled(self, fill):
        """
        Return a new SeqList instance whose sequences have same length

        >>> SeqList([[0, 1, 2], [3, 4]]).filled(None)
        SeqList([[0, 1, 2], [3, 4, None]])

        """
        seqlen = self.maxseqlen()
        return self.__class__(
            [s + [fill] * (seqlen - len(s)) for s in self._los])

    def maxseqlen(self):
        return max(map(len, self._los))

    def joinseqs(self):
        return map(''.join, self._los)

    def joinseqs_skipping_nones(self, none=None):
        """
        Return a new SeqList instance whose sequences have same length

        >>> SeqList([['a', None, 'b', None, None, 'c'],
        ...          [None, 'x', 'y', None, 'z', None]]
        ...         ).joinseqs_skipping_nones()
        ['abc', 'xyz']

        """
        return [''.join(x for x in l if x is not none) for l in self._los]


class ColView(object):

    def __init__(self, los, i):
        self._los = los
        self._i = i
        self.indices = [j for (j, seq) in enumerate(los) if i < len(seq)]

    def __iter__(self):
        return (self._los[j][self._i] for j in self.indices)

    def __getitem__(self, j):
        return self._los[j][self._i]

    def homo(self):
        """
        Return true if this column is homogeneous (all elements are the same)
        """
        return len(set(self)) == 1

    def nonnull(self, k=0):
        """
        Return a non-null value in this column
        """
        return self._los[self.indices[k]][self._i]


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Uniquify CLI')
    parser.add_argument(
        'file', nargs='?', default='-',
        help='file to read. "-" means stdin. (default: %(default)s)')
    parser.add_argument(
        '-m', '--method', default='skipcommonpath',
        choices=['shortpath', 'shortname', 'skipcommonname', 'skipcommonpath'],
        help='function to call (default: %(default)s)')
    parser.add_argument('-s', '--sep')
    parser.add_argument('-u', '--utype')
    parser.add_argument('-l', '--minlen', type=int)
    args = parser.parse_args()

    kwds = dict((k, getattr(args, k)) for k in ['sep', 'utype', 'minlen']
                if getattr(args, k))

    if args.file == '-':
        import sys
        infile = sys.stdin
    else:
        infile = file(args.file)
    lines = map(str.strip, infile.readlines())

    print '\n'.join(globals()[args.method](lines, **kwds))


if __name__ == '__main__':
    main()
