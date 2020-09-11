from typing import Dict, Tuple

import matplotlib.pyplot as plt

from wit_tools import _get_head, _get_parents

Point = Tuple[float, float]


def _set_config(ax):
    """Sets configurations."""

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.xticks([])
    plt.yticks([])


def _create_circle(ax, index, commit_id):
    """Creates a circle with text."""

    circle = plt.Circle(index, 0.07, color='#28b9c9', clip_on=False)

    if commit_id != 'None':
        plt.text(*index, commit_id[:6], size=8, ha='center', va='center')
    else:
        plt.text(*index, 'Start', size=13, ha='center', va='center')

    ax.add_artist(circle)


def _create_arrow(ax, start: Point, distance: Point):
    """Creates a arrow pointing to the commit's parents."""

    x, y = start
    dx, dy = distance
    ax.arrow(x, y, dx, dy, width=0.01, color='black', clip_on=False, length_includes_head=True)


def _get_arrow_distance(start: Point, end: Point):
    """Returns the delta between to points"""

    start_x, start_y = start
    end_x, end_y = end
    dx, dy = end_x - start_x, end_y - start_y
    return dx, dy + 0.07


def _get_indexes(indexes, current, point: Point, wit_path) -> Dict[str, Point]:
    """Returns a dict of commits and points."""

    parents = [current]
    space = 0.25
    x, y = point
    while 'None' not in indexes:

        if len(parents) == 1:
            indexes.update({parents[0]: (x, y)})
            parents = _get_parents(parents[0], wit_path)
            y -= space

        else:
            indexes.update({parents[0]: (x - space, y)})
            indexes.update({parents[1]: (x + space, y)})

            indexes.update(_get_indexes({}, parents[0], (x - space, y), wit_path).items())
            indexes.update(_get_indexes({}, parents[1], (x + space, y), wit_path).items())

    return indexes


def graph(wit_path):
    """Shows a graph with all of HEAD's parents."""

    head = _get_head(wit_path)
    fig, ax = plt.subplots()
    _set_config(ax)

    x = 0.5
    y = 1

    indexes = _get_indexes({head: (x, y)}, head, (x, y), wit_path)
    for commit_id, point in indexes.items():
        x, y = point

        for parent in _get_parents(commit_id, wit_path):
            end = indexes[parent]
            distance = _get_arrow_distance(point, end)
            _create_arrow(ax, point, distance)

        if commit_id == head:
            plt.text(x, y - 0.035, '(HEAD)', size=8, ha='center', va='center')
        _create_circle(ax, (x, y), commit_id)

    plt.show()
