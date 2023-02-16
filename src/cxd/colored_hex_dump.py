"""

"""

import logging
import string
from pathlib import Path
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
                default_color:str='white', shadow_color:str='dark_grey', address_color:str='cyan', title_color:str='dark_grey',
                enable_shadow_bytes=True,
                hide_null_lines=True, stop_at_first_color_found=True,
                memorize_last_color_range=True,
                show_columns_name_at_start=True,
                show_columns_name_at_end=True) -> None:
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
        self.title_color = title_color
        assert self.title_color in ColoredHexDump.ALLOWED_COLORS
        # bytes with these values will be colored with self.shadow_color
        self.shadow_bytes = (0x0, )
        self.enable_shadow_bytes = enable_shadow_bytes
        # if hide_null_lines is set and 
        self.hide_null_lines = hide_null_lines
        # if multiple ranges contain an offset, the user decides whether
        # the first or the last must be selected
        self.stop_at_first_color_found = stop_at_first_color_found
        # if ranges are ordered, do not lose time to search across all the ranges
        # and start only from the last range
        # this may be a problem if the user modify self.color_ranges (i.e out of bound index)
        self.memorize_last_color_range = memorize_last_color_range
        self.start_color_ranges = 0
        self.show_columns_name_at_start = show_columns_name_at_start
        self.show_columns_name_at_end = show_columns_name_at_end

    def __get_color_for_offset(self, offset:int, x,
                                            stop_at_first_color_found):
        # x is not a byte because of the use of `enumerate`
        ret = None

        for range_index, color_range in enumerate(self.color_ranges[self.start_color_ranges:],
                                                start=self.start_color_ranges):
            if color_range.start <= offset and offset <= color_range.end:
                ret = color_range.color
                if self.memorize_last_color_range:
                    self.start_color_ranges = range_index
                if stop_at_first_color_found:
                    break

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
            color = self.__get_color_for_offset(chunk_offset + i, c,
                                                self.stop_at_first_color_found)
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
