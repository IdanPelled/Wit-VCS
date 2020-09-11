import logging
import os
from time import gmtime, strftime

from wit_tools import _copy_dir, _create_id, _edit_references, _get_activated, _get_head, _get_references_data


def _create_commit_data_file(commit_path, parents, message):
    """Creates a data file."""

    with open((commit_path + '.' + 'txt'), 'w') as metadata:
        metadata.write(f"parent={parents}\n"
                       + f"date={strftime('%c %z', gmtime())}\n"
                       + f"message={message}\n")


def _update_commit_references(wit_path, commit_id):
    """Updates commit references."""

    active_branch_name = _get_activated(wit_path)
    active_branch_id = _get_references_data(wit_path)[active_branch_name]
    head_val = _get_references_data(wit_path)['HEAD']
    if (head_val == active_branch_id) or (_get_head(wit_path) == active_branch_id):
        _edit_references(wit_path, active_branch_name, commit_id)
        _edit_references(wit_path, 'HEAD', active_branch_name)
    else:
        _edit_references(wit_path, 'HEAD', commit_id)


def commit(message: str, wit_path: str, second_parent=None) -> str:
    """Creates save of all wanted files."""

    if len(message) < 100:
        commit_id = _create_id()
        commit_path = os.path.join(wit_path, '.wit', 'images', commit_id)
        _copy_dir(
            src=os.path.join(wit_path, '.wit', 'staging_area'),
            dst=os.path.join(wit_path, '.wit', 'images', commit_path),
        )
        parents = _get_head(wit_path)
        if second_parent is not None:
            parents = f'{parents}, {second_parent}'

        _create_commit_data_file(commit_path, parents, message)
        _update_commit_references(wit_path, commit_id)
        logging.info('your project was successfully saved.')
        return commit_id
    else:
        logging.error('Message is too long (max 50 letters).')
