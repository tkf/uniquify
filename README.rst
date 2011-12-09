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
