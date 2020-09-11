import logging
import os

from wit_tools import _copy_dir


def add(path: str, wit_path: str) -> None:
    """Adds a file or directory to staging_area."""

    if os.path.exists(path):
        dst = os.path.join(wit_path, '.wit', 'staging_area', os.path.relpath(path, wit_path))
        try:
            _copy_dir(path, dst)

        except OSError as error:
            logging.error(f'could not add "{path}": {error}.')

        else:
            logging.info(f'"{os.path.basename(path)}" was successfully added to staging area.')
    else:
        logging.error(f'path dose not exists "{path}".')
