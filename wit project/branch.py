import logging
import os

from wit_tools import _get_head


def _add_branch(wit_path, name, head):
    """Adds a branch to references.txt."""

    with open(os.path.join(wit_path, '.wit', 'references.txt'), 'a') as data:
        data.write(''.join(f'\n{name}={head}'))


def branch(name, wit_path):
    """Creates a new branch."""

    if name != 'None':

        if len(name) < 30:
            head = _get_head(wit_path)
            _add_branch(wit_path, name, head)
        else:
            logging.error(f'branch name is too long "{name}" (max 30 digits).')
    else:
        logging.error(f'branch name is not valid {name}.')

