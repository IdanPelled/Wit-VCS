import logging
import os
import sys

from add import add
from branch import branch
from checkout import checkout
from commit import commit
from exceptions import MethodNotFoundError
from graph import graph
from init import init
from merge import merge
from status import status
from wit_tools import _search_parent_dir, _set_logger, wit_required


@wit_required
def commands() -> None:
    """Redirects all the commands that require a wit path."""

    wit_path = _search_parent_dir(".wit")
    _set_logger(os.path.join(wit_path, '.wit'))

    if sys.argv[1] == 'add':
        add(sys.argv[2], wit_path)
    elif sys.argv[1] == 'commit':
        print(commit(sys.argv[2], wit_path))
    elif sys.argv[1] == 'status':
        print(status(wit_path))
    elif sys.argv[1] == 'checkout':
        checkout(sys.argv[2], wit_path)
    elif sys.argv[1] == 'graph':
        graph(wit_path)
    elif sys.argv[1] == 'branch':
        branch(sys.argv[2], wit_path)
    elif sys.argv[1] == 'merge':
        merge(sys.argv[2], wit_path)
    else:
        logging.error(MethodNotFoundError(f'unrecognized method: "{sys.argv[1]}".'))


def main() -> None:
    if len(sys.argv) > 1:

        if sys.argv[1] == 'init':
            init()

        else:
            commands()


if __name__ == '__main__':
    main()
