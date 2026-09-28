# Braid Playground

A Python project for building, drawing, and analysing mathematical braids. Built as a side project by a computer science bachelor's student heading into data science, out of love for math, topology, and beautiful things.

## Goal

An interactive tool where you can:
1. Build a braid from crossings (the "braid word").
2. See it drawn with proper over/under crossings.
3. See its algebra: the word, the permutation, and the Burau matrix.
4. Try presets (plain 3-strand braid, fishtail-style, cancel test).

The visual representation is the most important part.

## Structure

- `braids.py`: all the logic, no plotting. Reusable and testable.
- `braids.ipynb`: the story, chapter by chapter, importing from `braids.py`.
- `tests/`: pytest tests for the logic.
- `README.md`: inspiration, roadmap, what I learned.

Tools: Python, numpy, sympy (symbolic Burau with t), matplotlib (Bezier strands), ipywidgets (buttons and sliders in Jupyter). A web page (Streamlit or JS) is an optional later extra.

## Math to implement

**Braid word.** A braid on n strands is a list of `(i, sign)` pairs, with i from 1 to n-1. `sigma_i` (sign +1): strand at position i crosses over strand at position i+1. `sigma_i^-1` (sign -1): it crosses under.

**Permutation.** Track which strand ends where. Start at `[0..n-1]` and swap positions i-1 and i for every generator.

**Burau representation (unreduced).** Each generator maps to an n x n matrix, the identity except for a 2x2 block at rows and columns i-1, i:
- `sigma_i`: `[[1-t, t], [1, 0]]`
- `sigma_i^-1`: `[[0, 1], [1/t, 1-1/t]]`

A braid's matrix is the product of its generators' matrices, multiplied left to right in word order. Support numeric t and symbolic t (sympy).

**Simplification (later).**
- Cancel `sigma_i sigma_i^-1` and `sigma_i^-1 sigma_i`.
- Far commutativity: `sigma_i sigma_j = sigma_j sigma_i` when |i-j| >= 2.
- Braid relation: `sigma_i sigma_{i+1} sigma_i = sigma_{i+1} sigma_i sigma_{i+1}`.

**Stretch goals.** Braid closure (turn a braid into a knot or link), Alexander polynomial from the Burau matrix, a Garside normal form or another way to test whether two braids are equal.

## Drawing conventions

- Each crossing is one row of fixed height. Strand i sits at x = margin + i * spacing.
- Non-crossing strands are straight vertical lines. Crossing strands use a cubic Bezier from (x_start, y_top) to (x_end, y_bottom) with control points at the row's vertical midpoint.
- For over/under: draw the under-strand first, then the over-strand with a wider background-colored halo stroke beneath it, so the under-strand appears cut.
- One color per strand, tracked by strand id across rows, so the permutation is visible.

A working JavaScript/SVG prototype of this idea exists and can be used as a reference for the crossing logic: track `pos[strand]` per row, and for a crossing at generator i, swap the two strands sitting at positions i-1 and i.

## How I work (please follow this)

1. Claude drafts each chapter or module in full, with explanations in plain language.
2. I go through it chapter by chapter, study it, and rewrite it in my own words and style.
3. The project is finished when I've added everything Claude didn't and made it mine.

So: explain the math, don't just produce code. Add short comments and markdown explanations that teach. Keep code readable over clever. Flag anything I should double check (especially the drawing code, and anything where sign conventions could vary between textbooks).

## Git workflow

- `main` always works.
- One short branch per chapter or feature, e.g. `feature/burau-matrix`, `feature/drawing`, `feature/simplify`.
- Small, clear commits in the imperative mood ("Add permutation tracking").
- Merge into `main` when a feature is done (a pull request is welcome for practice).
- Never commit large output files. Add a proper `.gitignore` (notebook checkpoints, `__pycache__`, etc.).

## Suggested order of work

1. Repo setup, `.gitignore`, `README`, requirements file.
2. `braids.py`: word, permutation, Burau (numeric, then symbolic), with tests.
3. Drawing with matplotlib, including over/under crossings.
4. `ipywidgets` interface: generator buttons, undo, clear, presets, live word, permutation and matrix display.
5. Notebook narrative tying it together.
6. Stretch: simplification, closure, Alexander polynomial.

## Keywords to study

- Prerequisites: group, generators and relations, presentation, symmetric group, homomorphism, matrix representation, Laurent polynomials.
- Topology: homeomorphism, topological invariant, fundamental group, homotopy, configuration space, knot theory.
- Braids: Artin braid group B_n, braid relations, pure braid group, braid closure, Alexander's theorem, Markov's theorem, Garside normal form, word problem.
- Representations: Burau (unreduced and reduced), Alexander polynomial, Jones polynomial, Temperley-Lieb algebra, Lawrence-Krammer representation (faithful; Burau is not faithful for n >= 5).
- Reading: Kassel and Turaev, *Braid Groups*; Colin Adams, *The Knot Book*; Wikipedia pages on the braid group and the Burau representation; SageMath's braid group implementation for comparison.

## Inspiration (for the README)

This project started with an Instagram reel about braids, in which someone commented that there's a linear algebra way to describe them. Other threads that came together:
- The reel itself: a 4-strand braid drawn as colored lines, captioned with The Braid Group. (Add link or creator handle.)
- Discrete Math 2, where I first met groups and permutations. A braid is a permutation with extra information about which strand goes over.
- Homomorphisms, which I mostly skipped on the exam because I ran out of time. This project is my chance to understand them properly.
- A long-standing wish to get into topology.
- Loving math that connects to beauty and to tangible things, like the friendship bracelets and hair braids I made as a kid.

Add a "What I learned" section at the end once the project is done.
