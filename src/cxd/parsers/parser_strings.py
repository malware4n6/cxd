import argparse
import logging
import sys
from pathlib import Path
import subprocess

from platform import system as psystem
from cxd.color_range import ColorRange

_logger = logging.getLogger(__name__)

__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "The Unlicense"


class StringsColorer():
    """quick win: run 
    - `strings -n 4 -td` and get the output (offset, len(detected_string), color, detected_string as comment)
    - `strings -el  -n 4 -td` and get the output (offset, 2*len(detected_string), color, detected_string as comment)
    2 * len(detected_string) because `strings`' output is ASCII-encoded and I don't want to write a precise
    all-possible-strings-formats-and-encodings detection tool.
    """
    def __init__(self, path, colors) -> None:
        self.colors = colors
        self.colors_ranges = None
        # if self.colors_ranges is None, then the parser did not do its job yet.
        # this value is used to be sure the file is parsed only once.
        # the method .parse() is responsible for the creation of a list.
        # if .parse() is called multiple times, only the first call will parse the file,
        # and the already-generated list will be returned.
        self.path = path
        self.pe = None
        self.__check = None
        self.__color_index = 0
    
    def check(self):
        if self.__check is None:
            if psystem() != 'Linux':
                _logger.error('Parser "strings" only works on Linux systems')
                self.__check = False    
            else:
                self.__check = True
        return self.__check

    def parse(self):
        if self.colors_ranges is None:
            self.colors_ranges = []
            out = subprocess.check_output(['strings', '-n', '4', '-td', str(Path(self.path))])
            if out:
                lines = out.decode().split('\n')
                for curline in lines:
                    curline = curline.strip()
                    arr = curline.split(' ', maxsplit=1)
                    if len(arr) > 1:
                        offset = int(arr[0])
                        detected_string = arr[1].strip()
                        nb_spaces_at_start = len(arr[1]) - len(arr[1].lstrip()) 
                        self.colors_ranges.append(ColorRange(offset + nb_spaces_at_start, len(detected_string),
                                                            self.colors[self.__color_index], detected_string))
                        self.__color_index = (self.__color_index+1) % len(self.colors)

            out = subprocess.check_output(['strings', '-el', '-n', '4', '-td', str(Path(self.path))])
            if out:
                lines = out.decode().split('\n')
                for curline in lines:
                    curline = curline.strip()
                    arr = curline.split(' ', maxsplit=1)
                    if len(arr) > 1:
                        offset = int(arr[0])
                        detected_string = arr[1].strip()
                        nb_spaces_at_start = len(arr[1]) - len(arr[1].lstrip()) 
                        self.colors_ranges.append(ColorRange(offset + nb_spaces_at_start, 2*len(detected_string),
                                                            self.colors[self.__color_index], detected_string))
                        self.__color_index = (self.__color_index+1) % len(self.colors)

        return self.colors_ranges

def parse_args(args):
    parser = argparse.ArgumentParser(description="Strings parser")
    parser.add_argument("-i", "--input", help="path to some file", type=str)
    parser.add_argument("-o", "--output", help="path to output file (colors ranges). Each line contains 'offset_start,count,color'", type=str)
    parser.add_argument("-v", "--verbose", dest="loglevel", help="set loglevel to INFO",
                        action="store_const", const=logging.INFO)
    parser.add_argument("-vv", "--very-verbose", dest="loglevel", help="set loglevel to DEBUG",
                        action="store_const", const=logging.DEBUG)
    return parser.parse_args(args)

def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s\t%(name)s\t%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    colors = 'red green yellow blue magenta cyan light_red light_green light_yellow light_blue light_magenta light_cyan'.split()
    strings_colorer = StringsColorer(args.input, colors)
    if strings_colorer.check():
        colors = strings_colorer.parse()
        with open(args.output, 'w') as fd:
            for c in colors:
                fd.write(str(c) + '\n')

def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
