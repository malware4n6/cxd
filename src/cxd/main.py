"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = cxd.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys
from colorama import just_fix_windows_console

from cxd import __version__

__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "The Unlicense"

_logger = logging.getLogger(__name__)

from cxd.colored_hex_dump import ColoredHexDump, ColorRange

def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Colored Hex Dump")
    parser.add_argument("--version", action="version", version="cxd {ver}".format(ver=__version__))
    parser.add_argument("-d", "--data", help="path to some data", type=str)
    parser.add_argument("-r", "--ranges", help="path to ranges. Each line contains 'offset_start,count'", type=str)
    parser.add_argument("-v", "--verbose", dest="loglevel", help="set loglevel to INFO",
                        action="store_const", const=logging.INFO)
    parser.add_argument("-vv", "--very-verbose", dest="loglevel", help="set loglevel to DEBUG",
                        action="store_const", const=logging.DEBUG)
    return parser.parse_args(args)

def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """
    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    just_fix_windows_console()
    _logger.debug("Starting display...")
    ranges = [ColorRange(0, 10, 'red'),
                ColorRange(10, 10, 'green'),
                ColorRange(20, 10, 'blue')]
    # colors can be found here: https://pypi.org/project/termcolor/
    cxd = ColoredHexDump(ranges, chunk_length=16)
    with open(args.data, 'rb') as fd:
        data = fd.read()
    cxd.print(data)
    _logger.info("Ending display...")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m cxd.skeleton 42
    #
    run()
