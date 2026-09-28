"""
Tests for drawing.py.

We can't easily test that a picture "looks right", so we test the layout
logic underneath it, plus a smoke test that drawing doesn't crash.
"""

import matplotlib

matplotlib.use("Agg")  # draw off-screen, no window needed

import pytest

from braids import PRESETS, permutation
from drawing import bezier_points, braid_layout, draw_braid


def test_layout_has_one_row_per_crossing():
    assert len(braid_layout([(1, 1), (2, -1), (1, 1)], 3)) == 3


def test_positive_crossing_left_strand_goes_over():
    (row,) = braid_layout([(1, 1)], 2)
    assert row == [(0, 0, 1, "over"), (1, 1, 0, "under")]


def test_negative_crossing_right_strand_goes_over():
    (row,) = braid_layout([(1, -1)], 2)
    assert row == [(0, 0, 1, "under"), (1, 1, 0, "over")]


def test_other_strands_go_straight():
    (row,) = braid_layout([(2, 1)], 4)
    assert row[0] == (0, 0, 0, "straight")
    assert row[3] == (3, 3, 3, "straight")


def test_every_row_has_exactly_one_over_and_one_under():
    for row in braid_layout([(1, 1), (3, -1), (2, 1), (1, -1)], 4):
        roles = sorted(role for *_, role in row)
        assert roles == ["over", "straight", "straight", "under"]


@pytest.mark.parametrize("name", list(PRESETS))
def test_layout_ends_match_the_permutation(name):
    # Following the strands through the drawing must give the same answer
    # as braids.permutation.
    n, word = PRESETS[name]
    last_row = braid_layout(word, n)[-1]
    ends = [None] * n
    for strand, _start, end, _role in last_row:
        ends[end] = strand
    assert ends == permutation(word, n)


def test_bezier_starts_and_ends_at_the_right_points():
    xs, ys = bezier_points(0, 0, 1, 2)
    assert (xs[0], ys[0]) == (0, 0)
    assert (xs[-1], ys[-1]) == (1, 2)


@pytest.mark.parametrize("word, n", [([], 3), ([(1, 1), (2, -1)], 3), ([(1, 1)], 2)])
def test_draw_braid_runs(word, n):
    ax = draw_braid(word, n)
    assert ax is not None
