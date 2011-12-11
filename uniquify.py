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
__version__ = '0.0.1.dev0'
__license__ = "MIT License"


import os
import itertools


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

    lol = _lol_fill(_skipcommon_lol(names, sep, skip), None)
    if utype == 'tail':
        lol = _reversed_rows(lol)

    numnames = len(set(names))
    i0set = False
    for i in range(len(lol[0])):
        if not i0set and len(set(l[i] for l in lol)) > 1:
            i0 = i
            i0set = True
        if i0set:
            sublol = [l[i0:i + 1] for l in lol]
            if utype == 'tail':
                sublol = _reversed_rows(sublol)
            subnames = [''.join(x for x in l if x is not None) for l in sublol]
            if (len(set(subnames)) == numnames and
                min(map(len, subnames)) >= minlen):
                return subnames


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
    return map(''.join, _skipcommon_lol(names, sep, skip))


def _skipcommon_lol(names, seplist, skip):
    if seplist:
        (lol, sep) = _split_names(names, seplist[0])
        chunks = _get_chunks(lol)
        newlol = [_skip_common_parts_as_list(n, chunks, len(sep), skip)
                  for n in lol]
        if sep:
            newlol = [list(_every_other(l, sep)) for l in newlol]
        fulllol = [[] for _dummy in range(len(newlol))]
        for i in itertools.count():
            (subnames, j2k) = _lol_col(newlol, i)
            if not subnames:
                break
            if subnames[0] in (sep, skip):
                subnews = [[n] for n in subnames]
            else:
                subnews = _skipcommon_lol(subnames, seplist[1:], skip)
            for (j, subfull) in enumerate(fulllol):
                if j in j2k:
                    subfull.extend(subnews[j2k[j]])
        return fulllol
    else:
        return [[n] for n in names]


def _reversed_rows(lol):
    return [list(reversed(l)) for l in lol]


def _lol_fill(lol, fill):
    """
    Fill each row of ``lol`` with ``fill`` making them same length

    >>> _lol_fill([[0, 1], [2, 3], [4, 5]], None)
    [[0, 1], [2, 3], [4, 5]]
    >>> _lol_fill([[0, 1], [2], [4, 5]], None)
    [[0, 1], [2, None], [4, 5]]

    """
    lenrow = max(map(len, lol))
    indicies = range(lenrow)
    return [[l[i] if i < len(l) else fill for i in indicies] for l in lol]


def _lol_col(lol, i):
    """
    Get ``i``-th column of list of list ``lol`` as (possibly shorter) list

    >>> (col, j2k) = _lol_col([[0, 1], [2, 3], [4, 5]], 0)
    >>> col
    [0, 2, 4]
    >>> (col, j2k) = _lol_col([[0, 1], [2], [4, 5]], 1)
    >>> col
    [1, 5]
    >>> col[j2k[0]]
    1
    >>> col[j2k[2]]
    5

    """
    col = []
    j2k = {}
    k = 0
    for (j, lst) in enumerate(lol):
        if i < len(lst):
            col.append(lst[i])
            j2k[j] = k
            k += 1
    return (col, j2k)


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

    """
    if  len(lol) < 2:
        raise ValueError('Need at least 2 list. {0} given'.format(len(lol)))

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
