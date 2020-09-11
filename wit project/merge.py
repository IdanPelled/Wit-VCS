import logging
import os

from checkout import checkout
from commit import commit
from wit_tools import (_can_checkout, _copy_to_staging_area, _delete_dir_content, _get_all_parents,
                       _get_common_parent, _get_head, _get_references_data, is_branch)


def _move_files(wit_path, common_parent, branch):
    """Copies all files from the common dir and up."""

    staging_area_path = os.path.join(wit_path, '.wit', 'staging_area')
    images_path = os.path.join(wit_path, '.wit', 'images')
    common_parent_path = os.path.join(images_path, os.path.relpath(common_parent, wit_path))
    _delete_dir_content(staging_area_path)

    branch_parent = list(_get_all_parents(branch, wit_path, common_parent)) + [[branch]]
    head_parent = list(_get_all_parents(_get_head(wit_path), wit_path, common_parent)) + [[_get_head(wit_path)]]
    _copy_to_staging_area(wit_path, common_parent_path)

    for parents in branch_parent:
        for parent in parents:
            _copy_to_staging_area(wit_path, os.path.join(images_path, parent))

    for parents in head_parent:
        for parent in parents:
            _copy_to_staging_area(wit_path, os.path.join(images_path, parent))


def merge(branch: str, wit_path: str):
    """Merges two commits in to a new commit."""

    if _can_checkout:
        if is_branch(wit_path, branch):
            branch_on_head = _get_references_data(wit_path)["HEAD"]
            branch_id = _get_references_data(wit_path)[branch]
            if _get_head(wit_path) == branch_on_head:
                commit_id = commit(f'A merge between "{branch_on_head}" and "{branch}"', wit_path, branch_id)

            else:
                common_parent = _get_common_parent(wit_path, _get_head(wit_path), branch_id)
                _move_files(wit_path, common_parent, branch_id)
                commit_id = commit(f'A merge between "{branch_on_head}" and "{branch}"', wit_path, branch_id)
                checkout(branch_on_head, wit_path)

            logging.info(f'"{branch}" was successfully merged with {branch_on_head}.')
            print(commit_id)

        else:
            logging.error(f'"{branch}" is not a branch, try "branch" function to create a new branch.')
