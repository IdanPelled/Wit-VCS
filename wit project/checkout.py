import logging
import os

from wit_tools import (_can_checkout, _change_checkout_references, _copy_dir, _copy_to_staging_area,
                       _delete_dir_content, _get_references_data, is_branch, is_commit_id_valid)


def _restore_files(wit_path, commit_id, branch_name=None):
    """Restores all files."""

    staging_area_path = os.path.join(wit_path, '.wit', 'staging_area')

    _copy_dir(staging_area_path, wit_path)
    _change_checkout_references(wit_path, commit_id, branch_name)
    logging.info(f'"{_get_references_data(wit_path)["HEAD"]}" was successfully checked-out.')


def checkout(commit_id: str, wit_path: str) -> None:
    """Restores a save by replacing the original file."""

    if is_commit_id_valid(commit_id, wit_path):
        if _can_checkout(wit_path):
            staging_area_path = os.path.join(wit_path, '.wit', 'staging_area')
            _delete_dir_content(staging_area_path)

            if is_branch(wit_path, commit_id):
                branch_id = _get_references_data(wit_path)[commit_id]
                _copy_to_staging_area(wit_path, branch_id)
                _restore_files(wit_path, branch_id, branch_name=commit_id)

            else:
                _restore_files(wit_path, commit_id)
                _copy_to_staging_area(wit_path, commit_id)
