"""
Tests for braids.py.

Most of these don't check specific numbers. They check *properties* that the
math guarantees, e.g. "a braid glued to its inverse gives the identity".
If a property test fails, something in the logic is wrong, whatever the
convention.
"""

import numpy as np
import pytest
import sympy as sp

from braids import (
    PRESETS,
    burau_generator,
    burau_matrix,
    inverse_word,
    permutation,
    permutation_matrix,
    t,
    validate_word,
    word_to_string,
)


def symbolic_equal(a, b):
    """True if two sympy matrices are equal as rational functions of t."""
    return sp.simplify(a - b) == sp.zeros(*a.shape)


# --- braid words -----------------------------------------------------------

def test_word_to_string():
    assert word_to_string([(1, 1), (2, -1)]) == "σ₁ σ₂⁻¹"
    assert word_to_string([]) == "e"


def test_inverse_word_reverses_and_flips():
    assert inverse_word([(1, 1), (2, -1)]) == [(2, 1), (1, -1)]


@pytest.mark.parametrize("word, n", [
    ([(0, 1)], 3),    # i too small
    ([(3, 1)], 3),    # i too big: on 3 strands only sigma_1, sigma_2 exist
    ([(1, 2)], 3),    # sign must be +1 or -1
])
def test_invalid_words_are_rejected(word, n):
    with pytest.raises(ValueError):
        validate_word(word, n)


# --- permutation -----------------------------------------------------------

def test_empty_word_is_identity_permutation():
    assert permutation([], 4) == [0, 1, 2, 3]


def test_single_crossing_swaps_neighbours():
    assert permutation([(1, 1)], 3) == [1, 0, 2]
    assert permutation([(2, 1)], 3) == [0, 2, 1]


def test_permutation_ignores_over_under():
    assert permutation([(1, 1), (2, -1)], 3) == permutation([(1, -1), (2, 1)], 3)


def test_hair_braid_returns_after_six_crossings():
    # (sigma_1 sigma_2^-1)^3: every strand has visited every position once
    # and is back where it started.
    n, word = PRESETS["plain 3-strand braid"]
    assert permutation(word, n) == [0, 1, 2]


# --- Burau: single generators ------------------------------------------------

@pytest.mark.parametrize("i", [1, 2, 3])
def test_generator_times_inverse_is_identity(i):
    n = 4
    product = burau_generator(i, +1, n) * burau_generator(i, -1, n)
    assert symbolic_equal(product, sp.eye(n))


def test_numeric_and_symbolic_agree():
    word = [(1, 1), (2, -1), (1, 1)]
    symbolic = burau_matrix(word, 3)
    numeric = burau_matrix(word, 3, t_value=0.7)
    assert np.allclose(np.array(symbolic.subs(t, 0.7), dtype=float), numeric)


# --- Burau: the braid group relations ---------------------------------------
# These are the rules that define the braid group. If the matrices didn't
# satisfy them, Burau wouldn't be a representation of the braid group at all.

def test_braid_relation():
    # sigma_1 sigma_2 sigma_1 = sigma_2 sigma_1 sigma_2
    _, left = PRESETS["braid relation, left side"]
    _, right = PRESETS["braid relation, right side"]
    assert symbolic_equal(burau_matrix(left, 3), burau_matrix(right, 3))


def test_far_commutativity():
    # sigma_1 sigma_3 = sigma_3 sigma_1: crossings far apart don't interact
    assert symbolic_equal(
        burau_matrix([(1, 1), (3, 1)], 4),
        burau_matrix([(3, 1), (1, 1)], 4),
    )


def test_cancel_preset_is_identity():
    n, word = PRESETS["cancel test"]
    assert symbolic_equal(burau_matrix(word, n), sp.eye(n))


# --- Burau: homomorphism and sanity checks -----------------------------------

def test_homomorphism_gluing_is_multiplying():
    # Gluing braid w1 on top of w2 is just concatenating the words.
    # The matrix of the glued braid must be the product of the matrices.
    w1 = [(1, 1), (2, -1)]
    w2 = [(2, 1), (1, 1), (1, -1), (2, 1)]
    assert symbolic_equal(
        burau_matrix(w1 + w2, 3),
        burau_matrix(w1, 3) * burau_matrix(w2, 3),
    )


def test_inverse_braid_gives_inverse_matrix():
    word = [(1, 1), (2, -1), (3, 1), (2, 1)]
    product = burau_matrix(word, 4) * burau_matrix(inverse_word(word), 4)
    assert symbolic_equal(product, sp.eye(4))


def test_t_equals_one_gives_permutation_matrix():
    word = [(1, 1), (2, 1), (3, -1), (1, -1)]
    n = 4
    assert np.allclose(
        burau_matrix(word, n, t_value=1),
        permutation_matrix(permutation(word, n)),
    )


def test_rows_sum_to_one():
    word = [(1, 1), (2, -1), (1, 1), (3, 1)]
    matrix = burau_matrix(word, 4)
    for row in range(4):
        assert sp.simplify(sum(matrix.row(row)) - 1) == 0


def test_sigma_and_its_inverse_differ():
    # Unlike the permutation, Burau CAN tell over from under.
    assert not symbolic_equal(burau_matrix([(1, 1)], 2), burau_matrix([(1, -1)], 2))
