import argparse
import logging
import sys
from itertools import pairwise
from pathlib import Path
import pefile

from cxd.colored_hex_dump import ColorRange

__author__ = "malware4n6"
__copyright__ = "malware4n6"
__license__ = "The Unlicense"

_logger = logging.getLogger(__name__)

class PeColorer():
    def __init__(self, path, colors) -> None:
        self.colors = colors
        self.colors_ranges = None
        self.path = path
        self.pe = None
        self.__check = None
        self.__file_length = 0
        self.__color_index = 0
    
    def check(self):
        if self.__check is None:
            try:
                self.pe = pefile.PE(self.path)
                self.__file_length = Path(self.path).stat().st_size
                self.__check = True
                _logger.info(f'Can read {self.path}')
            except:
                self.pe = None
                self.__check = False
                _logger.error(f'Can read {self.path}')
        return self.__check

    def parse(self):
        if self.colors_ranges is None:
            self.colors_ranges = []
            self.pe.parse_data_directories( directories=[ 
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DEBUG'],
                # pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_BASERELOC'], # Do not parse relocations
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT'] ] )
            # for section in self.pe.sections:
                # print(section.Name, hex(section.VirtualAddress), hex(section.Misc_VirtualSize), section.SizeOfRawData )
                # print(section.Name, hex(section.VirtualAddress), hex(section.Misc_VirtualSize), section.SizeOfRawData )
            pe_file_dict_data = self.pe.dump_dict()
            # consider a PE as a list of offsets for the moment
            # sure: that's not the best idea, as some bytes that should not be colored will get colored - for nothing.
            # some keys may also not exist - or not be in the correct order
            # the following try...except should also be better handled
            file_offsets = []
            # DOS_HEADER
            for k in ('e_magic', 'e_cblp', 'e_cp', 'e_crlc', 'e_cparhdr', 'e_minalloc', 'e_maxalloc', 'e_ss', 'e_sp', 'e_csum',
                    'e_ip', 'e_cs', 'e_lfarlc', 'e_ovno', 'e_res', 'e_oemid', 'e_oeminfo', 'e_res2', 'e_lfanew'):
                file_offsets.append(pe_file_dict_data['DOS_HEADER'][k]['FileOffset'])
            # NT_HEADERS
            file_offsets.append(pe_file_dict_data['NT_HEADERS']['Signature']['FileOffset'])
            # FILE_HEADER
            for k in ('Machine', 'NumberOfSections', 'TimeDateStamp', 'PointerToSymbolTable', 'NumberOfSymbols', 'SizeOfOptionalHeader', 'Characteristics'):
                file_offsets.append(pe_file_dict_data['FILE_HEADER'][k]['FileOffset'])

            # OPTIONAL_HEADER
            for k in ('Magic', 'MajorLinkerVersion', 'MinorLinkerVersion', 'SizeOfCode', 'SizeOfInitializedData', 'SizeOfUninitializedData', 'AddressOfEntryPoint', 'BaseOfCode', 'ImageBase', 'SectionAlignment', 'FileAlignment', 'MajorOperatingSystemVersion', 'MinorOperatingSystemVersion', 'MajorImageVersion', 'MinorImageVersion', 'MajorSubsystemVersion', 'MinorSubsystemVersion', 'Reserved1', 'SizeOfImage', 'SizeOfHeaders', 'CheckSum', 'Subsystem', 'DllCharacteristics', 'SizeOfStackReserve', 'SizeOfStackCommit', 'SizeOfHeapReserve', 'SizeOfHeapCommit', 'LoaderFlags', 'NumberOfRvaAndSizes'):
                file_offsets.append(pe_file_dict_data['OPTIONAL_HEADER'][k]['FileOffset'])

            # consider the offsets read until there
            for pair in pairwise(file_offsets):
                self.colors_ranges.append(ColorRange(pair[0], pair[1] - pair[0], self.colors[self.__color_index]))
                self.__color_index = (self.__color_index+1) % len(self.colors)
            # add the imports
            _logger.debug(f'## imports')
            if self.pe.__dict__.get('DIRECTORY_ENTRY_IMPORT'):
                for import_entry in self.pe.DIRECTORY_ENTRY_IMPORT:
                    # _logger.debug(f'{import_entry.dll=}')
                    for imp in import_entry.imports:
                        # _logger.debug(f'\t-{imp.name=}')
                        if imp.name and imp.name_offset:
                            self.colors_ranges.append(ColorRange(imp.name_offset, len(imp.name), self.colors[self.__color_index]))
                            self.__color_index = (self.__color_index+1) % len(self.colors)
                        else:
                            _logger.error(f'\t-{imp.name=} not handled')
            # add the exports
            _logger.debug(f'## exports')
            if self.pe.__dict__.get('DIRECTORY_ENTRY_EXPORT'):
                for exp in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
                    _logger.debug(f'{exp.name=}')
                    self.colors_ranges.append(ColorRange(exp.name_offset, len(exp.name), self.colors[self.__color_index]))
                    self.__color_index = (self.__color_index+1) % len(self.colors)
                    if exp.forwarder_offset:
                        self.colors_ranges.append(ColorRange(exp.forwarder_offset, len(exp.forwarder), self.colors[self.__color_index]))
                        self.__color_index = (self.__color_index+1) % len(self.colors)
        return self.colors_ranges

def parse_args(args):
    parser = argparse.ArgumentParser(description="PE parser")
    parser.add_argument("-i", "--input", help="path to some PE", type=str)
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
    pe_colorer = PeColorer(args.input, colors)
    if pe_colorer.check():
        colors = pe_colorer.parse()
        with open(args.output, 'w') as fd:
            for c in colors:
                fd.write(str(c) + '\n')

def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
