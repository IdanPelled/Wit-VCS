import logging
import os

from wit_tools import _set_logger


def _write_base_files(wit_path):
    """Creates default files."""

    with open(os.path.join(wit_path, 'references.txt'), 'w') as file:
        file.write('HEAD=None\nmaster=None')
    with open(os.path.join(wit_path, 'activated.txt'), 'w') as file:
        file.write('master')


def init() -> None:
    """Initializes the "Wit" program."""

    path = os.path.join(os.getcwd(), '.wit')
    try:
        os.mkdir(path)
        os.mkdir(os.path.join(path, 'images'))
        os.mkdir(os.path.join(path, 'staging_area'))

    except FileExistsError:
        logging.error(FileExistsError('Wit already exists.'))

    except OSError as error:
        logging.error(OSError(f'Can not create folder:\n{error}'))

    else:
        _write_base_files(path)
        _set_logger(os.path.relpath(path, os.getcwd()))
        logging.info('wit was successfully initialized.')
