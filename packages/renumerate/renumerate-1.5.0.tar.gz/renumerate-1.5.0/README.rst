renumerate
==========

Reverse enumerate.

Overview
========

**renumerate(sequence, start=len(sequence)-1, end=0):**

| Return an enumerate_ object.
| *sequence* must be an object that has a __reversed__() method or supports the
  sequence protocol (the __len__() method and the __getitem__() method with
  integer arguments starting at 0).
| The __next__() method of the iterator returned by renumerate() returns a tuple
  containing a count (from *start* which defaults to len(*sequence*) - 1 or ends at
  *end* which defaults to 0 - but not both) and the values obtained from reverse
  iterating over *sequence*.

`PyPI record`_.

`Documentation`_.

Usage
-----

.. code:: python

  >>> from renumerate import renumerate
  >>> seasons = ['Spring', 'Summer', 'Fall', 'Winter']
  >>> list(renumerate(seasons))
  [(3, 'Winter'), (2, 'Fall'), (1, 'Summer'), (0, 'Spring')]
  >>> list(renumerate(seasons, start=4))
  [(4, 'Winter'), (3, 'Fall'), (2, 'Summer'), (1, 'Spring')]
  >>> list(renumerate(seasons, end=2))
  [(5, 'Winter'), (4, 'Fall'), (3, 'Summer'), (2, 'Spring')]

Equivalent to:

.. code:: python

  def renumerate(sequence, start=None, end=None):
      if start is not None and end is not None:
          raise TypeError("renumerate() only accepts start argument or end argument"
                          " - not both.")
      if start is None: start = len(sequence) - 1
      if end   is None: end   = 0
      n = start + end
      for elem in reversed(sequence):
          yield n, elem
          n -= 1

Installation
============

Prerequisites:

+ Python 3.10 or higher

  * https://www.python.org/

+ pip and setuptools

  * https://pypi.org/project/pip/
  * https://pypi.org/project/setuptools/

To install run:

  .. parsed-literal::

    python -m pip install --upgrade |package|

Development
===========

Prerequisites:

+ Development is strictly based on *tox*. To install it run::

    python -m pip install --upgrade tox

Visit `Development page`_.

Installation from sources:

clone the sources:

  .. parsed-literal::

    git clone |respository| |package|

and run:

  .. parsed-literal::

    python -m pip install ./|package|

or on development mode:

  .. parsed-literal::

    python -m pip install --editable ./|package|

License
=======

  | |copyright|
  | Licensed under the zlib/libpng License
  | https://opensource.org/license/zlib
  | Please refer to the accompanying LICENSE file.

Authors
=======

* Adam Karpierz <adam@karpierz.net>

.. |package| replace:: renumerate
.. |package_bold| replace:: **renumerate**
.. |copyright| replace:: Copyright (c) 2016-2025 Adam Karpierz
.. |respository| replace:: https://github.com/karpierz/renumerate.git
.. _Development page: https://github.com/karpierz/renumerate
.. _PyPI record: https://pypi.org/project/renumerate/
.. _Documentation: https://renumerate.readthedocs.io/
.. _enumerate: https://docs.python.org/library/functions.html#enumerate
