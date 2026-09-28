"""
braids.py: the logic behind Braids on Geek.

No plotting lives here, only math. That keeps it easy to test and to reuse
from the notebook, the drawing code, and (later) a web page.

The big picture
---------------
A braid on n strands is n strings hanging from a top bar to a bottom bar,
crossing over and under each other on the way down. We describe a braid by
listing its crossings from top to bottom. That list is the *braid word*.

Every crossing is one of the *generators* of the braid group B_n:

    sigma_i       the strand at position i crosses OVER  the strand at position i+1
    sigma_i^-1    the strand at position i crosses UNDER the strand at position i+1

Positions are counted 1..n from left to right, so i runs from 1 to n-1.
"Generators" means every braid can be built out of these, the same way every
integer can be built by adding and subtracting 1s.

In code, one generator is a pair (i, sign) with sign = +1 or -1, and a braid
word is a list of such pairs:

    [(1, +1), (2, -1)]    means    sigma_1 sigma_2^-1

From a word we compute two things:

1. The permutation: which strand ends up where at the bottom.
   This forgets over/under, so it only remembers part of the braid.
2. The Burau matrix: an n x n matrix whose entries are polynomials in a
   variable t. It remembers over/under, and it respects composition:
   gluing two braids together corresponds to multiplying their matrices.
   A map that turns "gluing" into "multiplying" like this is a
   *homomorphism* (here, from the braid group B_n to invertible matrices).
"""

import numpy as np
import sympy as sp

# The symbol used for symbolic Burau matrices.
t = sp.symbols("t")

# A few braids to play with. Each preset is (number of strands, word).
PRESETS = {
    # The everyday 3-strand hair braid: left strand over the middle, then
    # right strand over the middle, repeated. Crossing "right over middle"
    # means the strand at position 3 goes over the one at position 2, which
    # in our convention is sigma_2^-1 (position 2 goes UNDER position 3).
    "plain 3-strand braid": (3, [(1, +1), (2, -1)] * 3),
    # A crossing followed by its undo. The braid is "nothing" (the identity),
    # so its permutation is the identity and its Burau matrix is I.
    "cancel test": (3, [(1, +1), (1, -1)]),
    # Both sides of the braid relation. They look different but are the same
    # braid, so they must give the same permutation and the same matrix.
    "braid relation, left side": (3, [(1, +1), (2, +1), (1, +1)]),
    "braid relation, right side": (3, [(2, +1), (1, +1), (2, +1)]),
    # TODO: fishtail-style braid (needs a decision on how to model it).
}


# ---------------------------------------------------------------------------
# Braid words
# ---------------------------------------------------------------------------

def validate_word(word, n):
    """Raise ValueError if `word` is not a valid braid word on n strands."""
    if n < 1:
        raise ValueError(f"a braid needs at least 1 strand, got n={n}")
    for index, (i, sign) in enumerate(word):
        if not 1 <= i <= n - 1:
            raise ValueError(
                f"crossing #{index} is sigma_{i}, but on {n} strands "
                f"i must be between 1 and {n - 1}"
            )
        if sign not in (+1, -1):
            raise ValueError(f"crossing #{index} has sign {sign}, expected +1 or -1")


_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def word_to_string(word):
    """Pretty-print a braid word, e.g. [(1, 1), (2, -1)] -> 'σ₁ σ₂⁻¹'."""
    if not word:
        return "e"  # the empty word is the identity braid, usually written e
    parts = []
    for i, sign in word:
        part = "σ" + str(i).translate(_SUBSCRIPTS)
        if sign == -1:
            part += "⁻¹"
        parts.append(part)
    return " ".join(parts)


def inverse_word(word):
    """
    The inverse braid: undo the crossings in reverse order.

    Same idea as taking off socks and shoes: (ab)^-1 = b^-1 a^-1.
    Gluing a braid to its inverse gives the identity braid.
    """
    return [(i, -sign) for i, sign in reversed(word)]


# ---------------------------------------------------------------------------
# Permutation
# ---------------------------------------------------------------------------

def permutation(word, n):
    """
    Follow the strands down the braid and report where each one ends up.

    Strands are labelled 0..n-1 by their starting position at the top.
    `perm[p]` is the label of the strand sitting at position p at the bottom.

    A crossing sigma_i swaps whatever is at positions i and i+1 (list indices
    i-1 and i). Over or under doesn't matter here, which is why the
    permutation alone can't tell sigma_i and sigma_i^-1 apart.
    """
    validate_word(word, n)
    perm = list(range(n))
    for i, _sign in word:
        perm[i - 1], perm[i] = perm[i], perm[i - 1]
    return perm


# ---------------------------------------------------------------------------
# Burau representation (unreduced)
# ---------------------------------------------------------------------------
#
# Each generator becomes an n x n matrix: the identity, except for a 2x2
# block at rows and columns i-1, i (0-based):
#
#     sigma_i     ->  [[1-t,  t   ],        sigma_i^-1  ->  [[0,    1      ],
#                      [1,    0   ]]                         [1/t,  1 - 1/t]]
#
# You can check by hand that these two blocks multiply to the identity,
# so the matrix of sigma_i^-1 really is the inverse of the matrix of sigma_i.
#
# DOUBLE CHECK: textbooks disagree on conventions here. Some use the
# transpose of these blocks, some swap t and 1/t, and some multiply the word
# right to left. Every convention gives a valid representation, but the
# matrices differ, so compare conventions before comparing numbers with a
# book, Wikipedia, or SageMath.


def _block(sign, t_value):
    """The 2x2 block for sigma_i (sign +1) or sigma_i^-1 (sign -1)."""
    if sign == +1:
        return [[1 - t_value, t_value],
                [1,           0]]
    return [[0,           1],
            [1 / t_value, 1 - 1 / t_value]]


def _is_symbolic(t_value):
    return isinstance(t_value, sp.Basic)


def burau_generator(i, sign, n, t_value=t):
    """
    The Burau matrix of one generator.

    Returns a sympy Matrix if t_value is symbolic (the default), otherwise
    a numpy array of numbers.
    """
    validate_word([(i, sign)], n)
    block = _block(sign, t_value)
    if _is_symbolic(t_value):
        matrix = sp.eye(n)
        matrix[i - 1:i + 1, i - 1:i + 1] = sp.Matrix(block)
    else:
        # result_type lets t be an int, a float, or even a complex number
        matrix = np.eye(n, dtype=np.result_type(t_value, float))
        matrix[i - 1:i + 1, i - 1:i + 1] = block
    return matrix


def burau_matrix(word, n, t_value=t):
    """
    The Burau matrix of a whole braid word on n strands.

    Multiplies the generator matrices left to right in word order, so the
    first crossing (at the top) is the leftmost factor.

    With the default t_value (the sympy symbol t) you get exact polynomial
    entries. Pass a number, e.g. t_value=0.5, for a numpy array instead.

    Two useful sanity checks you'll find in the tests:
    - t = 1 turns every block into [[0, 1], [1, 0]], a plain swap, so the
      Burau matrix becomes the permutation matrix of the braid. Burau is
      a "t-deformation" of the permutation.
    - Every row sums to 1, for every t. (Check the blocks: 1-t + t = 1,
      and 1/t + 1 - 1/t = 1.) So the vector (1, 1, ..., 1) is never changed
      by a Burau matrix.
    """
    validate_word(word, n)
    if _is_symbolic(t_value):
        result = sp.eye(n)
        for i, sign in word:
            result = result * burau_generator(i, sign, n, t_value)
        # expand + simplify so equal braids print equal-looking matrices
        return sp.simplify(result)
    result = np.eye(n, dtype=np.result_type(t_value, float))
    for i, sign in word:
        result = result @ burau_generator(i, sign, n, t_value)
    return result


def permutation_matrix(perm):
    """
    The 0/1 matrix P with P[perm[p], p] = 1.

    It's what burau_matrix gives at t = 1, which ties the two views of a
    braid together.
    """
    n = len(perm)
    matrix = np.zeros((n, n))
    for position, strand in enumerate(perm):
        matrix[strand, position] = 1
    return matrix
