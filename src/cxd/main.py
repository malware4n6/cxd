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
from pathlib import Path
from colorama import just_fix_windows_console

from cxd import __version__

__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "The Unlicense"

_logger = logging.getLogger(__name__)

from cxd.colored_hex_dump import ColoredHexDump
from cxd.color_range import ColorRange

def import_plugins():
    from cxd.parsers.loader import load_parsers
    return load_parsers()

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
    parser.add_argument("-c", "--colors",
                        help="path to colors ranges. Each line contains 'offset_start,count,color[,comment]'",
                        type=str)
    parser.add_argument("-p", "--parser", help="parser to use. Takes precedence over option colors", type=str)
    parser.add_argument("-po", "--parser-output", help="location to store parser output", type=str)
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
    logformat = "[%(asctime)s] %(levelname)s\t%(name)s\t%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

def read_colors_ranges(colors_file):
    # TODO: improve parsing, maybe using `csv` package
    colors_path = Path(colors_file)
    if not colors_path.exists() or not colors_path.is_file():
        _logger.fatal(f'Colors ranges can not be read from {colors_file}')
        sys.exit(0)
    ret = []
    with colors_path.open('r') as fd:
        for curline in fd.readlines():
            curline = curline.strip()
            if curline:
                _logger.debug(f'{curline=}')
                body = curline.split(',')
                _logger.debug(body)
                start = body[0]
                if '0x' in start:
                    start = int(start, 16)
                else:
                    start = int(start)

                length = body[1]
                if '0x' in length:
                    length = int(length, 16)
                else:
                    length = int(length)

                if len(body) == 2:
                    ret.append(ColorRange(start, length))
                elif len(body) >= 3:
                    color = body[2]
                    if color in ColoredHexDump.ALLOWED_COLORS:
                        ret.append(ColorRange(start, length, color))
                    else:
                        _logger.info(f'Incorrect line due to color: {curline}')
                    # comment field is not considered. if needed, the file
                    # being self-explanatory, one can read it to understand
                    # its own comment
    return ret

def main(args):
    """
    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    ranges = None
    if args.parser:
        parsers = import_plugins()
        _logger.info(f'{parsers=}')
        if args.parser not in parsers.keys():
            _logger.error(f'Parser {args.parser} does not exist. Available: {", ".join(parsers.keys())}')
            return
        _logger.info(f'Parser {args.parser} found')
        parser = parsers[args.parser]
        colors = 'red green yellow blue magenta cyan light_red light_green light_yellow light_blue light_magenta light_cyan'.split()
        colorer = parser['module'].__dict__[parser['name']](str(Path(args.data).absolute()),
                                                            colors)
        if colorer.check():
            ranges = colorer.parse()
            if args.parser_output:
                with open(args.parser_output, 'w') as fd:
                    for r in ranges:
                        fd.write(str(r) + '\n')
        else:
            _logger.error('Parser failed; exiting')
            return
    else:
        if args.colors:
            ranges = read_colors_ranges(args.colors)
        else:
            # these colors are only here to quickly test the colors
            ranges = [ColorRange(0, 4, 'red'),
                    ColorRange(4, 4, 'green'),
                    ColorRange(8, 4, 'blue')]
    just_fix_windows_console()

    # colors can be found here: https://pypi.org/project/termcolor/
    cxd = ColoredHexDump(ranges=ranges, chunk_length=16, address_shift=0, # -0x0100,
                        default_color='white', shadow_color='dark_grey',
                        address_color='cyan', enable_shadow_bytes=True,
                        hide_null_lines=True)
    with open(args.data, 'rb') as fd:
        data = fd.read()
    cxd.print(data)
    # cxd.print_file(args.data)


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
