"""

"""

import logging
import string

from termcolor import colored

__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "The Unlicense"

_logger = logging.getLogger(__name__)

class ColorRange():
    def __init__(self, start, length, color = None) -> None:
        self.start = start
        self.length = length
        self.color = color
        self.end = start + length

class ColoredHexDump():
    def __init__(self, ranges=None, chunk_length: int=32, replace_not_printable='.', column_separator='\t', address_shift:int=0) -> None:
        self.color_ranges = [] if ranges is None else ranges
        self.chunk_length = chunk_length
        self.replace_not_printable = replace_not_printable
        self.column_separator = column_separator
        self.address_shift = address_shift
        self.printable = string.ascii_letters + string.digits + string.punctuation + ' '
        self.default_color = 'white'
        self.light_color = 'dark_grey'
        self.address_color = 'light_blue'

    def __get_color_for_offset(self, offset:int, x):
        # x is a byte
        # TODO improve search
        # currently the last
        ret = None

        # no break as the **last** range is chosen
        # in case of an offset belongs to multiple ranges
        for r in self.color_ranges:
            if r.start <= offset and offset <= r.end:
                ret = r.color

        # if belongs to a range -> provided color is chosen first
        # if not in a range:
            # if x == 0x00 -> light_color
            # else -> default_color
        if ret is None:
            if x == 0: # consider a list?
                ret = self.light_color
            else:
                ret = self.default_color
        return ret

    def print(self, data: bytes):

        for data_offset_i in range(0, len(data), self.chunk_length):
            chunk = data[data_offset_i:data_offset_i + self.chunk_length]
            addr = self.address_shift + data_offset_i

            print(colored(f'{addr:08x}', self.address_color), end='')
            
            print(self.column_separator, end='')

            ascii_content = ''
            raw_ascii_content = ''
            # Iterate over each byte value in the chunk
            for i, c in enumerate(chunk):
                color = self.__get_color_for_offset(data_offset_i + i, c)
                print(colored(f'{c:02X}', color), end='')
                print(' ', end='')
                if chr(c) in self.printable:
                    # ascii_content += chr(c)
                    raw_ascii_content += chr(c)
                    ascii_content += colored(f'{chr(c)}', color)
                else:
                    raw_ascii_content += self.replace_not_printable
                    ascii_content += self.replace_not_printable

            # handle last line
            if len(raw_ascii_content) != self.chunk_length:
                print(3*(self.chunk_length - len(raw_ascii_content))*' ', end='')
            print(self.column_separator, end='')
            print(ascii_content, end='')
            # for e in ascii_content:
            #    print(e, end='')
            print()

