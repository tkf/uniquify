# Import README.rst using cog
# [[[cog
# from cog import out
# out('"""\n{0}"""'.format(file('README.rst').read()))
# ]]]
"""
Uniquify - get unique, short and easy-to-read names and paths
=============================================================


Shorten names/paths by extracting non-common parts:

>>> from uniquify import shortname, shortpath
>>> shortname(['__common_part___abc___common_part__',
...            '__common_part___ijk___common_part__',
...            '__common_part___xyz___common_part__'])
['abc', 'ijk', 'xyz']
>>> shortpath(['some/long/path/___/abc/___/___/',
...            'some/long/path/___/ijk/___/___/',
...            'some/long/path/___/xyz/___/___/'])
['abc', 'ijk', 'xyz']


Convert common parts into skip marks:

>>> from uniquify import skipcommonname, skipcommonpath
>>> skipcommonname(['ab__common_part___c',
...                 'ij__common_part___k',
...                 'xy__common_part___z'])
['ab...c', 'ij...k', 'xy...z']
>>> skipcommonpath(['ab/common/path/c',
...                 'ij/common/path/k',
...                 'xy/common/path/z'])
['ab/.../c', 'ij/.../k', 'xy/.../z']
"""
# [[[end]]]

__author__ = "Takafumi Arakaki"
__version__ = '0.0.0'
__license__ = "MIT License"


import os


def shortname(names, utype='tail', sep=None, skip='...'):
    """
    Get unique short names from a list of strings

    >>> shortname(['_____abc___def',
    ...            '_____xyz___uvw'])
    ['def', 'uvw']
    >>> shortname(['_____abc___def',
    ...            '_____xyz___uvw'], utype='head')
    ['abc', 'xyz']
    >>> shortname(['_____abc___def',
    ...            '_____xyz___def',
    ...            '_____xyz___uvw'])
    ['abc...def', 'xyz...def', 'xyz...uvw']

    """
    if utype not in ['tail', 'head']:
        raise ValueError("'{0}' is not a recognized ``utype``".format(utype))
    numnames = len(set(names))
    (lol, sep) = _split_names(names, sep)
    chunks = _get_chunks(lol)

    if utype == 'tail':
        chunks = _reverse_chunks(chunks)

    i0set = False
    for (i, ((_dummy, _dummy), diff)) in enumerate(zip(*chunks)):
        if diff:
            if not i0set:
                i0 = i
                i0set = True
            subchunks = (chunks[0][i0:i + 1], chunks[1][i0:i + 1])
            if utype == 'tail':
                subchunks = _reverse_chunks(subchunks)
            newnames = _skip_common_parts_in_lol(lol, subchunks, sep, skip)
            if len(set(newnames)) == numnames:
                return newnames


def shortpath(names, utype='tail', skip='...'):
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
    return shortname(names, utype, os.path.sep, skip)


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

    """
    (lol, sep) = _split_names(names, sep)
    chunks = _get_chunks(lol)
    return _skip_common_parts_in_lol(lol, chunks, sep, skip)


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

    """
    skipwidth = len(skip)
    newname = []
    for ((start, stop), diff) in zip(*chunks):
        subname = sep.join(name[start:stop])
        if diff or len(subname) < skipwidth:
            newname.append(subname)
        else:
            newname.append(skip)
    return sep.join(newname)


def _reverse_chunks(chunks):
    return (chunks[0][::-1], chunks[1][::-1])


def _get_chunks(lol):
    """
    Returns common and different "chunks" of the list in the list (``lol``)


    chunks : (ranges, diffs)
        Common and different chunks

        ranges : [(start, stop)] --- list of start-stop pairs
            Definition of the ranges

            start : int
                The first index of the range

            stop : int
                The last + 1 index of the range

        diffs : [bool] --- list of bools
            True if the corresponding element in ``ranges`` is
            different, otherwise False.

    Examples:

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
