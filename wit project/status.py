from wit_tools import (_get_changes_not_staged_for_commit, _get_changes_to_be_committed,
                       _get_head, _get_references_data, _get_untracked_files, _return_as_string)


def _get_full_id(current_id, head_name):
    """Returns commit id plus branch name if exists."""

    if current_id != head_name:
        return f'\n\ncommit id:\n{head_name} ({current_id})\n\n'
    return f'\n\ncommit id:\n{current_id}\n\n'


def status(wit_path: str) -> str:
    """Prints a status report."""

    current_id = _get_head(wit_path)
    head_name = _get_references_data(wit_path)['HEAD']
    untracked_files = '\n'.join(_get_untracked_files(wit_path))
    changes_to_be_committed = _return_as_string(_get_changes_to_be_committed, wit_path, current_id)
    changes_not_staged_for_commit = _return_as_string(_get_changes_not_staged_for_commit, wit_path)

    return(
        '\nstatus report:\n'
        + '-' * 14

        + _get_full_id(current_id, head_name)

        + 'Changes to be committed:\n'
        + f'{changes_to_be_committed}\n\n'

        + 'Changes not staged for commit:\n'
        + f'{changes_not_staged_for_commit}\n\n'

        + 'Untracked files:\n'
        + f'{untracked_files}\n\n'
    )
