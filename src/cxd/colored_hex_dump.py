"""

"""

import logging
import string
from pathlib import Path
from intervaltree import IntervalTree
from termcolor import colored

__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "The Unlicense"

_logger = logging.getLogger(__name__)


class ColoredHexDump():
    # colors can be found here: https://pypi.org/project/termcolor/
    ALLOWED_COLORS = 'black red green yellow blue magenta cyan white light_grey dark_grey light_red light_green light_yellow light_blue light_magenta light_cyan'.split()

    def __init__(self, ranges=None, chunk_length: int=16, replace_not_printable:str='.', column_separator:str='\t', address_shift:int=0,
                default_color:str='white', shadow_color:str='dark_grey', address_color:str='cyan', title_color:str='dark_grey',
                enable_shadow_bytes=True, hide_null_lines=True, stop_at_first_color_found=True,
                show_columns_name_at_start=True, show_columns_name_at_end=True) -> None:
        self.color_ranges = [] if ranges is None else ranges
        self.color_tree = IntervalTree()
        for cr in self.color_ranges:
            self.color_tree[cr.start:cr.end+1] = cr
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
        self.title_color = title_color
        assert self.title_color in ColoredHexDump.ALLOWED_COLORS
        # bytes with these values will be colored with self.shadow_color
        self.shadow_bytes = (0x0, )
        self.enable_shadow_bytes = enable_shadow_bytes
        # if hide_null_lines is set we replace the line by "ADDR *" 
        self.hide_null_lines = hide_null_lines
        self.__content_to_hide = bytes(chunk_length)
        self.__hide_mode = False
        # if multiple ranges contain an offset, the user decides whether
        # the first or the last must be selected
        self.stop_at_first_color_found = stop_at_first_color_found
        self.show_columns_name_at_start = show_columns_name_at_start
        self.show_columns_name_at_end = show_columns_name_at_end

    def __get_color_for_offset(self, offset:int, x):
        # x is not a byte because of the use of `enumerate`
        ret = None

        intervals = sorted(self.color_tree[offset])
        if intervals:
            if self.stop_at_first_color_found:
                ret = intervals[0].data.color
            else:
                ret = intervals[-1].data.color

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

    def __print_snip(self, addr: int):
        print(colored(f'{addr:08x}', self.address_color), end='')
        print(self.column_separator, end='')
        print('*')

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

    def __print_columns_names(self):
        print(colored(f'  Offset', self.title_color), end='')
        print(self.column_separator, end='')
        for i in range(self.chunk_length):
            print(colored(f'{i:02X}', self.title_color), end='')
            print(' ', end='')
        print(self.column_separator)

    def print(self, data: bytes):
        if self.show_columns_name_at_start:
            self.__print_columns_names()
        for chunk_offset in range(0, len(data), self.chunk_length):
            chunk = data[chunk_offset:chunk_offset + self.chunk_length]
            addr = self.address_shift + chunk_offset
            # print(len(data), chunk_offset, ((len(data) - chunk_offset)//self.chunk_length))
            if self.hide_null_lines and chunk_offset != 0 and ((len(data) - chunk_offset)//self.chunk_length) not in (0, 1):
                # check only if option is enabled and it's not the first or last line of the dump
                if chunk == self.__content_to_hide:
                    if not self.__hide_mode:
                        self.__hide_mode = True
                        self.__print_snip(addr)
                else:
                    self.__hide_mode = False
                    self.__print_chunk(addr, chunk, chunk_offset)
            else:
                self.__print_chunk(addr, chunk, chunk_offset)
        if self.show_columns_name_at_end:
            self.__print_columns_names()

    def print_file(self, filepath: str):
        path = Path(filepath)
        if not path.exists() or not path.is_file():
            _logger.error(f'Check {filepath} is a file')
            return
        
        with path.open('rb') as fd:
            offset = 0
            if self.show_columns_name_at_start:
                self.__print_columns_names()
            while True:
                chunks = fd.read(4096) # self.chunk_length)
                if not chunks:
                    break
                for chunk_offset in range(0, len(chunks), self.chunk_length):
                    chunk = chunks[chunk_offset:chunk_offset + self.chunk_length]
                    addr = self.address_shift + offset + chunk_offset

                    self.__print_chunk(addr, chunk, offset + chunk_offset)
                offset += len(chunks)

                # addr = self.address_shift + offset
                # self.__print_chunk(addr, chunk, offset)
                # offset += len(chunk)
            if self.show_columns_name_at_end:
                self.__print_columns_names()
