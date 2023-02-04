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
        # -1 because (start + length) define the first next excluded byte
        self.end = start + length - 1

class ColoredHexDump():
    # colors can be found here: https://pypi.org/project/termcolor/
    ALLOWED_COLORS = 'black red green yellow blue magenta cyan white light_grey dark_grey light_red light_green light_yellow light_blue light_magenta light_cyan'.split()

    def __init__(self, ranges=None, chunk_length: int=32, replace_not_printable:str='.', column_separator:str='\t', address_shift:int=0,
                default_color:str='white', shadow_color:str='dark_grey', address_color:str='cyan', enable_shadow_bytes=True) -> None:
        self.color_ranges = [] if ranges is None else ranges
        self.chunk_length = chunk_length
        assert self.chunk_length > 0
        self.replace_not_printable = replace_not_printable
        assert len(self.replace_not_printable) == 1
        self.column_separator = column_separator
        self.address_shift = address_shift
        self.printable = string.ascii_letters + string.digits + string.punctuation + ' '
        self.default_color = default_color
        assert self.default_color in ColoredHexDump.ALLOWED_COLORS
        self.shadow_color = shadow_color
        assert self.shadow_color in ColoredHexDump.ALLOWED_COLORS
        self.address_color = address_color
        assert self.address_color in ColoredHexDump.ALLOWED_COLORS
        # bytes with these values will be colored with self.shadow_color
        self.shadow_bytes = (0x0, )
        self.enable_shadow_bytes = enable_shadow_bytes

    def __get_color_for_offset(self, offset:int, x):
        # x is not a byte because of the use of `enumerate`
        # TODO improve search
        # currently the **last** color found among self.color_ranges is applied
        ret = None

        # no break as the **last** range is chosen
        # in case of an offset belongs to multiple ranges
        for r in self.color_ranges:
            if r.start <= offset and offset <= r.end:
                ret = r.color

        # if belongs to a range -> provided color is chosen first
        # if not in a range:
            # if x == 0x00 -> shadow_color
            # else -> default_color
        if ret is None:
            if x in self.shadow_bytes and self.enable_shadow_bytes:
                ret = self.shadow_color
            else:
                ret = self.default_color
        _logger.debug(f'Color for {offset=}: {ret}')
        return ret

    def __print_chunk(self, addr: int, chunk: bytes, chunk_offset: int):
        # addr is the address displayed in the first column of the output
        # self.address_shift is not added in the function
        # chunk_offset is the offset of the chunk in a larger binary object

        # print address column and separator
        print(colored(f'{addr:08x}', self.address_color), end='')
        print(self.column_separator, end='')

        # generate ascii content
        # hex chars are print directly
        ascii_content = ''
        raw_ascii_content = ''
        # iterate over each byte value in the chunk
        for i, c in enumerate(chunk):
            color = self.__get_color_for_offset(chunk_offset + i, c)
            print(colored(f'{c:02X}', color), end='')
            print(' ', end='')
            if chr(c) in self.printable:
                raw_ascii_content += chr(c)
                ascii_content += colored(f'{chr(c)}', color)
            else:
                raw_ascii_content += self.replace_not_printable
                ascii_content += colored(f'{self.replace_not_printable}', color)

        # handle the last line so that the columns are OK
        if len(raw_ascii_content) != self.chunk_length:
            print(3*(self.chunk_length - len(raw_ascii_content))*' ', end='')
        print(self.column_separator, end='')
        print(ascii_content, end='')
        # end of the line!
        print()

    def print(self, data: bytes):
        for chunk_offset in range(0, len(data), self.chunk_length):
            chunk = data[chunk_offset:chunk_offset + self.chunk_length]
            addr = self.address_shift + chunk_offset
            self.__print_chunk(addr, chunk, chunk_offset)
