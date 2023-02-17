from importlib import import_module
import logging
from pathlib import Path

_logger = logging.getLogger(__name__)

def load_parsers():
    _logger.debug('load_parsers' + __file__)

    parsers = {}
    for g in Path(__file__).parent.glob('parser_*.py'):
        _logger.info(f'{g}')
        format_ = g.stem[7:]
        name = f'{format_.title()}Colorer'
        _logger.info(f'Found {g} => {name}')
        parsers[format_] = {'name': name,
                        'module': import_module(f'cxd.parsers.parser_{format_}')}
    return parsers