Uniquify - get unique, short and easy-to-read names and paths
=============================================================

Examples
--------

Shorten names/paths by extracting non-common parts:

>>> from uniquify import shortname, shortpath
>>> shortname(['__common_part___abc___common_part__',
...            '__common_part___ijk___common_part__',
...            '__common_part___xyz___common_part__'])
['abc', 'ijk', 'xyz']
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
