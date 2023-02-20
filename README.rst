.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/cxd.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/cxd
    .. image:: https://readthedocs.org/projects/cxd/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://cxd.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/cxd/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/cxd
    .. image:: https://img.shields.io/pypi/v/cxd.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/cxd/
    .. image:: https://pepy.tech/badge/cxd/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/cxd


.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

===
cxd
===

    Colored heX Dump

Setup
=====


..  code-block:: sh

    python3 -m venv venv
    . venv/bin/activate
    # putup cxd
    cd cxd
    pip install -e .
    # for offline locations
    # pip wheel . --wheel-dir /path


Usage
=====

0. Optional. Define a coloration scheme (read src/cxd/sample_colors_ranges.txt if you need an example)

Columns are under the format "start,length[,color]":

   * start and length must be decimal or hexadecimal integers
   * if provided, color must be in "black red green yellow blue magenta cyan white light_grey dark_grey light_red light_green light_yellow light_blue light_magenta light_cyan".
   These colors are defined here: https://pypi.org/project/termcolor/

1. Use ``cxd``:

..  code-block:: sh

    cxd -d path/to/binary/file -c src/cxd/sample_colors_ranges.txt


Or if you want to integrate ``cxd`` in your Python code:

..  code-block:: python

    from colorama import just_fix_windows_console
    from cxd.colored_hex_dump import ColoredHexDump, ColorRange
    import string

    # for Windows
    just_fix_windows_console()
    
    # define your colors ranges
    ranges = [ColorRange(0, 4, 'red'), ColorRange(4, 4, 'green'), ColorRange(8, 4, 'blue')]
    cxd = ColoredHexDump(ranges=ranges, chunk_length=16)
    cxd.print(string.printable.encode())

See the function `ColoredHexDump.__init__` in `src/cxd/colored_hex_dump` to see all options.

Parsers
=======

For the moment, only one *real* parser exists, and it uses the excellent project https://github.com/erocarrera/pefile

..  code-block:: sh

    pip install cxd[parsers]

Available parsers: pe, strings

If you want to add your own parser `foo`, create a script called `parser_foo.py` in src/cxd/parsers.
Inside, create a class `FooColorer`, with the methods `__init__`, `check` and `parse`, as already done in parser_pe.py and parser_strings.py.

If you need to add some dependencies, add them in the file `setup.cfg`, in the section `[options.extras_require]`, in the `parsers` list.


Test
====

..  code-block:: sh

    pip install cxd[testing]
    pytest


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
