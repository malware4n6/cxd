import json
import logging
from pathlib import Path

_logger = logging.getLogger(__name__)

class Configuration():
    @staticmethod
    def generate(config_path) -> None:
        new_config = Path(config_path)
        default_config = {
            'chunk_length': 16,
            'replace_not_printable': '.',
            'column_separator': '\t',
            'address_shift': 0,
            'default_color': 'white',
            'shadow_color': 'dark_grey',
            'address_color': 'cyan',
            'title_color': 'dark_grey',
            'enable_shadow_bytes': True,
            'hide_null_lines': True,
            'stop_at_first_color_found': True,
            'show_columns_name_at_start': True,
            'show_columns_name_at_end': True
        }

        with new_config.open('w') as fd:
            json.dump(default_config, fd)
        _logger.info(f'Generated configuration here: {new_config.absolute()}')

    @staticmethod
    def parse(config_path):
        ret = {}
        config = Path(config_path)
        try:
            with config.open('r') as fd:
                ret = json.load(fd)
        except Exception as exc:
            _logger.error(f'An error occured while reading the configuration: {exc}. Default configuration will be used.')
        _logger.debug(f'Configuration: {ret}')
        return ret
