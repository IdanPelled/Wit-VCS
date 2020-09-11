import logging
import os
import random
import shutil
import string
from typing import Any, List, Tuple, Union

from exceptions import FileNotSavedError


# credits:
# https://stackoverflow.com/users/717357/yann
# https://stackoverflow.com/questions/9215658/plot-a-circle-with-pyplot

# https://stackoverflow.com/users/3892023/harwee
# https://stackoverflow.com/questions/37427683/python-search-for-a-file-in-current-directory-and-all-its-parents

# https://stackoverflow.com/users/23252/atzz
# https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth


def wit_required(f):
    """Runs the function only if wit was
    initialised in one of the current parent dir.
    """

    def new_function(*args, **kwargs):
        if _search_parent_dir(".wit") is not False:
            f(*args, **kwargs)
        else:
            logging.error(FileNotFoundError('.wit directory was not found. Try "init" function.'))

    return new_function


def filter_list(f):
    """Filters a list and returns as a string."""

    def new_function(*args: Union[List[Tuple[str, bool]], Any], **kwargs: Any):
        try:
            return '\n'.join([file for file, is_saved in
                              {k: v for d in f(*args, **kwargs)
                               for k, v in d.items()}.items() if not is_saved])
        except AttributeError:
            return ''

    return new_function


def _search_parent_dir(file_name):
    """searches for a folder in all current dir's father dirs."""

    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    while current_dir != parent_dir:
        if not os.path.splitdrive(current_dir)[-1]:
            return False
        file_list = os.listdir(current_dir)
        parent_dir = os.path.dirname(current_dir)

        if file_name in file_list:
            return current_dir

        else:
            current_dir = parent_dir
    return False


def _set_logger(path):
    """Sets logging configurations."""

    logging.basicConfig(
        filename=os.path.join(path, 'log.log'),
        filemode='a',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level='INFO'
    )


@filter_list
def _return_as_string(f, *args, **kwargs):
    return f(*args, **kwargs)


def _copy_dir(src, dst):
    """Copies src to dst."""
    if os.path.isdir(src):
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)

            if os.path.isdir(s):
                _copy_dir(s, d)
            else:
                shutil.copy2(s, d)

    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        _delete_file(dst)
        shutil.copy2(src, dst)


def _delete_file(path):
    """Deletes a file."""

    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)


def _delete_dir_content(dir_path):
    """deletes all files in dir."""

    for item in os.listdir(dir_path):
        path = os.path.join(dir_path, item)
        try:
            os.remove(path)

        except PermissionError:
            shutil.rmtree(path)


def _get_staging_area_files(wit_path, plus_root=True):
    """Yields all files from the staging area."""

    for root, _, files in os.walk(os.path.join(wit_path, '.wit', 'staging_area'), topdown=False):
        for name in files:
            if plus_root:
                yield os.path.join(os.path.relpath(root, os.path.join(wit_path, '.wit', 'staging_area')), name)
            else:
                yield name


def _get_untracked_files(wit_path):
    """Returns all untracked file."""

    tracked_files = _get_staging_area_files(wit_path)
    all_files = set(_get_all_files_names(wit_path))
    return all_files.difference(tracked_files)


def _open_file(path):
    """Safely open and returns a file"""

    if 'None.txt' in path:
        return None
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        try:
            with open(path, 'rb') as file:
                return file.read().strip()
        except OSError:
            logging.error(FileNotFoundError(f'Cant open {path}'))


def _compare_file(path1, path2):
    """Compares to files content."""

    try:
        return _open_file(path1) == _open_file(path2)
    except OSError:
        return False


def _get_references_data(wit_path):
    """Returns a dict of all references in references.txt."""

    with open(os.path.join(wit_path, '.wit', 'references.txt'), 'r') as data:
        info = {'None': 'None'}
        info.update({'HEAD': data.readline().split('=')[-1].strip('\n')})
        info.update({'master': data.readline().split('=')[-1].strip('\n')})
        for row in data.readlines():
            name, commit_id = row.split('=')
            info.update({name.strip('\n'): commit_id.strip('\n')})

    return info


def _create_id(length=40):
    """Creates a 40 letter random id."""

    numbers = map(str, range(10))
    letters = string.ascii_lowercase
    options = [*letters[:letters.index('f') + 1], *numbers]

    return ''.join(random.choice(options) for _ in range(length))


def _get_all_files_names(wit_path, dir_name=None, plus_root=True):
    """Returns all file names."""

    if dir_name is None:
        dir_name = wit_path
        directory = os.listdir(dir_name)
        directory.remove('.wit')
    else:
        directory = os.listdir(dir_name)

    for item in directory:
        if os.path.isdir(item):
            for root, _, files in os.walk(os.path.join(dir_name, item), topdown=False):
                for name in files:
                    if plus_root:

                        yield os.path.join(os.path.relpath(root, wit_path), name)
                    else:
                        yield name
        else:
            if plus_root:
                yield os.path.join(os.path.relpath(dir_name, wit_path), item)
            else:
                yield item


def _get_changes_not_staged_for_commit(wit_path):
    """Returns all files that where changed after a commit,
    but were not added to the staging area.
    """

    files = {os.path.relpath(file, wit_path):
             get_full_path(file, '.wit', 'staging_area')
             for file in _get_all_files_names(wit_path)}

    for file in _get_staging_area_files(wit_path):
        if os.path.relpath(file, wit_path) in files:
            yield {os.path.relpath(file, wit_path): _compare_file(file, files[os.path.relpath(file, wit_path)])}


def _get_changes_to_be_committed(wit_path, current_id):
    """Returns all files that where changed after a commit,
    and added to the staging area, but were not committed.
    """

    if current_id != 'None':
        files = {os.path.relpath(file, os.path.join(wit_path, '.wit', 'images', current_id)): file
                 for file in _get_all_files_names(
                 wit_path, dir_name=os.path.join(wit_path, '.wit', 'images', current_id))}

        for file in _get_staging_area_files(wit_path, plus_root=True):
            if os.path.relpath(file, wit_path) in files:
                yield {os.path.basename(file): _compare_file(os.path.join(wit_path, '.wit', 'staging_area', file),
                                                             files[os.path.relpath(file, wit_path)])}
    else:
        yield ''


def _change_references(path, name, val):
    """Yields rows of the new references file."""

    text = _open_file(path)
    for row in text.split('\n'):
        if row.startswith(name + "="):
            row = f'{name}={val}'
        yield row


def _edit_references(wit_path, name, val):
    """Edits references file."""

    path = os.path.join(wit_path, '.wit', 'references.txt')
    text = '\n'.join(list(_change_references(path, name, val)))
    with open(path, 'w') as data:
        data.write(text)


def _edit_activated(wit_path, commit_id):
    """Edits activated file."""

    with open(os.path.join(wit_path, '.wit', 'activated.txt'), 'w') as file:
        if commit_id in list(_get_references_data(wit_path).keys()):
            file.write(commit_id)
        else:
            file.write('None')


def _get_activated(wit_path):
    """Returns activated content."""

    with open(os.path.join(wit_path, '.wit', 'activated.txt'), 'r') as file:
        return file.read().strip('\n')


def _get_head(wit_path):
    """Returns head value, if val is branch,
    returns branch value."""

    head = _get_references_data(wit_path)['HEAD']
    if len(head) == 40:
        return head
    return _get_references_data(wit_path)[head]


def _can_checkout(wit_path) -> bool:
    """Returns True if user can checkout, False otherwise."""

    current_id = _get_head(wit_path)
    changes_to_be_committed = _return_as_string(_get_changes_to_be_committed, wit_path, current_id)
    changes_not_staged_for_commit = _return_as_string(_get_changes_not_staged_for_commit, wit_path)
    if changes_to_be_committed + changes_not_staged_for_commit == '':
        return True
    logging.error(FileNotSavedError('Some files are not saved. Try "status" command to view them.'))
    return False


def _get_parents(commit_id, wit_path):
    """Returns a commit's parents."""

    path = os.path.join(wit_path, '.wit', 'images', os.path.relpath(commit_id, wit_path)) + '.txt'
    if 'None.txt' not in path:
        return _open_file(path).split('parent=')[-1].split('\n')[0].split(', ')
    return ['None']


def _get_all_parents(parent, wit_path, stop_at='None'):
    """Yields all family tree"""

    for _, parents in _get_all_parents_and_sons(parent, wit_path, stop_at):
        yield parents


def _get_all_parents_and_sons(son: str, wit_path: str, stop_at='None'):
    parents = _get_parents(son, wit_path)
    yield son, parents
    while stop_at not in parents and 'None' not in parents:
        if len(parents) > 1:
            for parent in parents:
                yield from _get_all_parents_and_sons(parent, wit_path)
                parents = _get_parents(parent, wit_path)

        else:
            new_parents = _get_parents(parents[0], wit_path)
            yield parents[0], new_parents
            parents = new_parents


def _change_checkout_references(wit_path, commit_id, branch_name=None):
    """Edits references.txt checkout information."""

    # branch checkout
    if branch_name is not None:

        _edit_references(wit_path, 'HEAD', branch_name)
        _edit_activated(wit_path, branch_name)

    # id checkout
    else:
        _edit_references(wit_path, 'HEAD', commit_id)
        _edit_activated(wit_path, commit_id)


def _copy_to_staging_area(wit_path, commit_id):
    """Copies a commit to staging area."""

    images_path = os.path.join(wit_path, '.wit', 'images')
    staging_area_path = os.path.join(wit_path, '.wit', 'staging_area')
    src = os.path.join(images_path, commit_id)
    if 'None' not in src:
        _copy_dir(src.strip(), staging_area_path)


def _get_common_parent(wit_path, head: str, branch: str):
    """Returns a common parent"""

    head_parents = {head}
    branch_parents = {branch}
    all_head_parents = _get_all_parents(head, wit_path)
    all_branch_parents = _get_all_parents(branch, wit_path)

    while not head_parents.intersection(branch_parents):
        if 'None' not in head_parents:
            parents = next(all_head_parents)
            for parent in parents:
                head_parents.add(parent)
        if 'None' not in branch_parents:
            parents = next(all_branch_parents)
            for parent in parents:
                branch_parents.add(parent)

    return list(branch_parents.intersection(head_parents))[0]


def _get_all_saves_names(wit_path):
    """Return all commit names."""
    names = []
    for item in os.listdir(os.path.join(wit_path, '.wit', 'images')):
        path = os.path.join(wit_path, '.wit', 'images', item)
        if os.path.isdir(path):
            names.append(item)
    return names


def is_branch(wit_path, branch):
    """Returns True if "branch" is a branch, False otherwise."""

    branches = _get_references_data(wit_path)
    del branches['HEAD']
    return branch in branches.keys()


def get_full_path(path, *args):
    """Returns a full path."""

    return os.path.join(_search_parent_dir(".wit"), *args, path)


def is_commit_id_valid(commit_id, wit_path):
    """Returns True if commit id is valid."""

    if not is_branch(wit_path, commit_id):
        if commit_id.isalnum() and len(commit_id) == 40:

            if commit_id in _get_all_saves_names(wit_path):
                return True

            else:
                logging.error(f'No commit named {commit_id}.')

        else:
            logging.error('branch or commit does not exist. commit id must be 40 digits long and hexadecimal.')
    else:
        return True
#####