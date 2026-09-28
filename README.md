# Braids on Geek

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dora-mitic/Braids-on-Geek/blob/main/braids.ipynb)

A playground for building, drawing, and analysing mathematical braids in Python.

You build a braid one crossing at a time and see it drawn with proper over/under crossings. Alongside the drawing you see its algebra: the braid word, the permutation of the strands, and the Burau matrix.

> *Draft README. Rewrite it in your own words as the project grows.*

## Inspiration

This project started with an Instagram reel: a 4-strand braid drawn as colored lines, captioned *The Braid Group*. Someone in the comments mentioned that there's a linear algebra way to describe braids, and I wanted to understand what that meant.

<!-- TODO: add the reel link or creator handle -->

Other threads that came together:

- **Discrete Math 2**, where I first met groups and permutations. A braid turns out to be a permutation with extra information about which strand goes over.
- **Homomorphisms**, which I mostly skipped on the exam because I ran out of time. This project is my chance to understand them properly. (The Burau representation *is* a homomorphism, from the braid group to a group of matrices.)
- A long-standing wish to get into **topology**.
- Loving math that connects to beauty and to tangible things, like the friendship bracelets and hair braids I made as a kid.

## What's in here

| File | What it does |
| --- | --- |
| `braids.py` | All the logic: braid words, permutations, Burau matrices. No plotting. |
| `drawing.py` | Draws braids with matplotlib, with over/under crossings. |
| `braids.ipynb` | The story, chapter by chapter, using `braids.py`. |
| `tests/` | pytest tests for the logic. |
| `LITERATURE.md` | Lecture notes, videos, and articles I learned from. |

## Getting started

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python -m ipykernel install --user --name braids-on-geek --display-name "Python (Braids on Geek)"
```

The last line registers the project's Python with Jupyter, so the notebook uses the environment where numpy and sympy are installed. You only need it once.

Then, whenever you want to play:

```bash
.venv\Scripts\jupyter-lab     # Windows
# .venv/bin/jupyter-lab       # macOS / Linux
```

and open `braids.ipynb`.

Run the tests with:

```bash
.venv\Scripts\python -m pytest
```

## Roadmap

- [x] Repo setup
- [x] Braid words, permutations, and the Burau matrix (numeric and symbolic), with tests
- [x] Drawing braids with matplotlib, including over/under crossings
- [ ] Interactive interface with ipywidgets: generator buttons, undo, clear, presets
- [ ] Notebook that tells the story
- [ ] Stretch: simplifying words, braid closure, Alexander polynomial

## What I learned

*To be written once the project is done.*
