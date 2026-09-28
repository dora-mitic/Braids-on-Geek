"""
drawing.py: pictures of braids with matplotlib.

The math lives in braids.py. This file only turns a braid word into a picture.

How a braid is drawn
--------------------
- The braid is drawn from top to bottom, one crossing per row.
- Positions 0..n-1 are fixed x coordinates. Strands move between them.
- In a row with crossing sigma_i, the strands at positions i-1 and i (0-based)
  swap places along smooth S-shaped curves. Every other strand goes straight
  down.
- Over/under trick: draw the under-strand first. Then draw a thick stroke in
  the background color along the over-strand (the "halo"), and the over-strand
  itself on top of that. The halo erases a little gap in the under-strand, so
  it looks like it passes behind.
- Every strand keeps its own color from top to bottom, so you can see the
  permutation just by following the colors.
"""

import matplotlib.pyplot as plt
import numpy as np

from braids import validate_word, word_to_string

# One color per strand. Chosen to be easy to tell apart; strands beyond the
# end of the list reuse colors from the start.
STRAND_COLORS = [
    "#e6194b",  # red
    "#3cb4ff",  # blue
    "#f5b400",  # yellow
    "#2aa876",  # green
    "#9b5de5",  # purple
    "#ff7f0e",  # orange
    "#f15bb5",  # pink
    "#00bbbb",  # teal
]


# ---------------------------------------------------------------------------
# Layout: which strand goes where in each row (pure logic, no matplotlib)
# ---------------------------------------------------------------------------

def braid_layout(word, n):
    """
    Work out every strand's movement, row by row.

    Returns a list with one entry per row. Each row is a list of
    (strand, start_position, end_position, role) tuples, where role is
    "straight", "over" or "under".

    This is the same bookkeeping as braids.permutation, but it remembers
    every step instead of only the end result. We keep `at_position`, where
    at_position[p] is the strand currently at position p, and swap two
    entries at every crossing.
    """
    validate_word(word, n)
    at_position = list(range(n))
    rows = []
    for i, sign in word:
        left, right = i - 1, i  # the two positions that cross (0-based)
        # sigma_i (sign +1): the strand coming from the LEFT goes over.
        # sigma_i^-1 (sign -1): the strand coming from the RIGHT goes over.
        left_role, right_role = ("over", "under") if sign == +1 else ("under", "over")
        row = []
        for p, strand in enumerate(at_position):
            if p == left:
                row.append((strand, left, right, left_role))
            elif p == right:
                row.append((strand, right, left, right_role))
            else:
                row.append((strand, p, p, "straight"))
        rows.append(row)
        at_position[left], at_position[right] = at_position[right], at_position[left]
    return rows


# ---------------------------------------------------------------------------
# Curves
# ---------------------------------------------------------------------------

def bezier_points(x_start, y_start, x_end, y_end, samples=50):
    """
    Points along a cubic Bezier curve from (x_start, y_start) to (x_end, y_end).

    A cubic Bezier curve has four control points P0, P1, P2, P3 and is
        B(s) = (1-s)^3 P0 + 3(1-s)^2 s P1 + 3(1-s) s^2 P2 + s^3 P3,  s in [0, 1].
    It starts at P0 heading towards P1, and ends at P3 arriving from P2.

    We put P1 straight below the start and P2 straight above the end, both at
    the row's vertical middle. So the strand leaves and arrives going straight
    down, which makes it join smoothly with the rows above and below.
    """
    y_mid = (y_start + y_end) / 2
    p0 = np.array([x_start, y_start])
    p1 = np.array([x_start, y_mid])
    p2 = np.array([x_end, y_mid])
    p3 = np.array([x_end, y_end])
    s = np.linspace(0, 1, samples)[:, None]  # column, so it broadcasts with the points
    curve = (1 - s) ** 3 * p0 + 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s ** 2 * p2 + s ** 3 * p3
    return curve[:, 0], curve[:, 1]


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def draw_braid(
    word,
    n,
    ax=None,
    spacing=1.0,
    row_height=1.0,
    linewidth=5,
    halo_width=6,
    background="white",
    colors=None,
    title=True,
):
    """
    Draw a braid word on n strands. Returns the matplotlib Axes.

    spacing:     horizontal distance between neighbouring positions
    row_height:  vertical size of one crossing
    halo_width:  how much wider the background stroke under the over-strand
                 is. Larger means a bigger gap in the under-strand.
    """
    colors = colors or STRAND_COLORS
    rows = braid_layout(word, n)
    if not rows:
        # the empty braid: draw one row of straight strands so there's something to see
        rows = [[(p, p, p, "straight") for p in range(n)]]

    if ax is None:
        fig, ax = plt.subplots(figsize=(0.8 + 0.7 * n * spacing, 0.6 + 0.7 * len(rows) * row_height))
        fig.patch.set_facecolor(background)
    ax.set_facecolor(background)

    def x_of(position):
        return position * spacing

    def color_of(strand):
        return colors[strand % len(colors)]

    # "butt" caps end each line exactly at its endpoint, so a halo never pokes
    # into the row above or below.
    line = dict(linewidth=linewidth, solid_capstyle="butt")

    for row_index, row in enumerate(rows):
        y_top = row_index * row_height
        y_bottom = y_top + row_height

        # Order matters: straight strands and the under-strand first,
        # then the halo, then the over-strand on top.
        drawing_order = {"straight": 0, "under": 1, "over": 2}
        for strand, start, end, role in sorted(row, key=lambda r: drawing_order[r[3]]):
            if role == "straight":
                ax.plot([x_of(start), x_of(end)], [y_top, y_bottom], color=color_of(strand), **line)
                continue
            xs, ys = bezier_points(x_of(start), y_top, x_of(end), y_bottom)
            if role == "over":
                ax.plot(xs, ys, color=background, linewidth=linewidth + halo_width,
                        solid_capstyle="butt")
            ax.plot(xs, ys, color=color_of(strand), **line)

    # Small dots mark where the strands are attached at the top and bottom.
    bottom = len(rows) * row_height
    for p in range(n):
        ax.plot(x_of(p), 0, "o", color="#444444", markersize=4, zorder=5)
        ax.plot(x_of(p), bottom, "o", color="#444444", markersize=4, zorder=5)

    ax.set_xlim(-0.5 * spacing, x_of(n - 1) + 0.5 * spacing)
    ax.set_ylim(bottom + 0.3 * row_height, -0.3 * row_height)  # flipped: y grows downwards
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(word_to_string(word))
    return ax
