import os


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
    return list(_skip_common_parts(n, chunks, sep, skip) for n in lol)


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
