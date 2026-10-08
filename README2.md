# Lab: Recursion Trees and the Master Theorem

<img src=img/meme.jpg width=400px />

When you look at a recursive function, you see a few lines of code.
What the computer actually does is build a *tree* of function calls,
and the shape and size of that tree determines how long the function
takes to run.

This lab teaches three things:

1. **A decorator is just a function that takes a function and returns
   a function.**  You already pass functions as arguments to other
   functions (e.g. the `key=` argument to `sort`).  A decorator is
   the same idea with a small piece of syntactic sugar on top.

2. **graphviz outputs an intermediate language, not a picture.**
   Compilers output assembly which an assembler turns into a binary.
   graphviz outputs the *DOT language* which the `dot` program turns
   into a PNG.  Separating "describe the picture" from "render the
   picture" is a recurring pattern in software.

3. **The master theorem is a shortcut for a picture you can draw.**
   When a recurrence has the form $T(n) = a T(n/b) + f(n)$, the
   master theorem tells you the runtime without drawing anything.
   The theorem is easier to remember once you understand the picture
   it summarizes.

## Part 0: Setup

Fork this repo and clone your fork on the lambda server.
The instructions below ask you to directly edit the README of your
fork.

Install the python dependencies:
```
$ pip3 install -r requirements.txt
```

> **NOTE:**
> The `graphviz` python package is a thin wrapper around the `dot`
> program, which is preinstalled on the lambda server.
> If you are working on your own computer, you will need to install
> `dot` yourself.  See <https://graphviz.org/download/>.

Verify that the provided files are correct by running the doctests:
```
$ python3 -m doctest recurrences.py
```

You should see no output if all the tests pass.

## Part 1: Decorators are just functions

In python, functions are *first-class objects*.
That means you can store them in variables, pass them to other
functions, and return them from other functions.
You have already seen this in earlier labs:
```
>>> xs = ['hello', 'hi', 'howdy']
>>> xs.sort(key=len)
```
The `key=len` argument passes the function `len` as a value to `sort`.

A **decorator** is a function whose input is a function and whose
output is a function.  Here is the simplest decorator I can think of:
```python
def twice(f):
    def g(*args, **kwargs):
        return f(f(*args, **kwargs))
    return g
```

To see what it does, apply it to a function by hand:
```
>>> def inc(x):
...     return x + 1
>>> inc2 = twice(inc)
>>> inc2(0)
2
>>> inc2(10)
12
```

Now observe that the following code does exactly the same thing:
```python
@twice
def inc(x):
    return x + 1
```

The `@twice` line is *syntactic sugar*.
The python interpreter takes the function object defined on the
following lines, passes it to `twice`, and rebinds the name `inc` to
the result.  In other words,
```
@twice
def inc(x): ...
```
is *exactly* the same as
```
def inc(x): ...
inc = twice(inc)
```

### The `trace` decorator

The file `trace.py` defines a decorator `trace` with the signature
```python
trace(f, outputfile=None, highlight_duplicates=False)
```
It returns a wrapper function that:

1. behaves *identically* to `f` (same inputs, same output, same
   exceptions), and
2. as a side effect, writes a DOT description of the call tree of
   `f` to `outputfile`, and renders it to a PNG.

We will use this decorator on every function in this lab.

> **NOTE:**
> You do not need to read or understand the body of `trace.py`.
> (That is a topic for a later lab on metaprogramming.)
> For now, treat it as a black box that takes a function and returns
> a "traced" version of the function.

Before we trust the decorator, we should **prove by example** that
it does not change the behavior of the function it wraps.
The first thing every good scientist does with a new instrument is
verify that it does not perturb what it is measuring.

Add the following to a file `test_trace.py`:
```python
import recurrences
from trace import trace

def test_trace_does_not_change_behavior():
    for f, args in [
        (recurrences.bsearch, ([1, 2, 3, 4, 5], 3)),
        (recurrences.merge_sort, ([3, 1, 2],)),
        (recurrences.fib, (10,)),
        (recurrences.hanoi, (3,)),
    ]:
        assert trace(f, 'img/tmp.png')(*args) == f(*args)
```

Run the tests:
```
$ python3 -m pytest
```

> **HINT:**
> `trace` writes a file every time it is called, which is slow and
> will spam your `img/` folder.  Once you trust the decorator, you
> can delete this test file, or pass `outputfile=None` to disable
> rendering.

Now that we have proved the decorator is transparent, we can use the
`@trace` syntax anywhere we want to trace a function:
```python
from recurrences import fib
from trace import trace

@trace
def traced_fib(n):
    return fib(n)

if __name__ == '__main__':
    traced_fib(5)
```

You should see a file `img/traced_fib.png` appear.

> **NOTE:**
> When we say graphviz "outputs an intermediate language," we mean
> this literally.  Look at `img/traced_fib.dot` (which `trace` also
> writes) — it is a *text* description of the tree.  The `dot`
> program reads that text and renders the PNG.  This is exactly like
> how `gcc -S` outputs assembly and `as` turns it into an object
> file.

### Viewing the PNGs on the lambda server

You cannot view images in a terminal.
The simplest way to view them on the lambda server is to commit and
push to github, and reference them from this README:
```html
<img src=img/traced_fib.png width=400px>
```

Try it now: copy the HTML line above into your README, commit and
push, and refresh this page on github.
You should see your tree.

> **NOTE:**
> This is exactly the workflow from lab-timeit2, where you viewed
> the `first_example.png` plot the same way.

## Part 2: Trees for algorithms you know

You have already seen several recursive algorithms this semester.
For each function below, generate the recursion tree, sketch it by
hand, and fill in the table.

The functions live in `recurrences.py`.
To trace one and render its tree, use a script like:
```python
from recurrences import bsearch
from trace import trace

traced = trace(bsearch, 'img/bsearch.png')
traced(list(range(64)), 17)
```

You will need to choose a value of $n$ that is small enough for the
tree to be legible but large enough to show the shape.
For balanced-split algorithms like merge sort, $n=8$ works well;
for exponential algorithms you may need to go as small as $n=4$.

> **WARNING:**
> The `@trace` decorator builds a python object for every call,
> and the recursion tree of `fib(30)` has about a million nodes.
> Start with tiny inputs.

Fill in the following table:

| function | tree shape | depth | # recursive calls | recurrence T(n) | predicted runtime |
| --- | --- | --- | --- | --- | --- |
| `bsearch` | | | | | |
| `merge_sort` | | | | | |
| `quick_sort` | | | | | |
| `quick_select` | | | | | |
| `sequential_search_rec` | | | | | |

For the "tree shape" column, use one of:
*path* (each call has one child),
*balanced binary* (each call has two children and halves the input),
*uneven binary* (each call has two children but the halves are
unequal),
*subtractive* (each call has children but the input size decreases by
a constant rather than a factor),
or *other*.

> **HINT:**
> The "# recursive calls" column is what we really care about.
> The runtime of a recursive function is (approximately) the number
> of calls times the work done inside each call.  Since we are not
> measuring wall-clock time in this lab, "number of calls" is our
> proxy for "runtime."

## Part 3: New functions

Now do the same thing for the following functions, which you have
not seen before:

| function | tree shape | depth | # recursive calls | recurrence T(n) | predicted runtime |
| --- | --- | --- | --- | --- | --- |
| `power(x, n)` | | | | | |
| `fib(n)` | | | | | |
| `hanoi(n, a, b, c)` | | | | | |
| `binom(n, k)` | | | | | |
| `grid_paths(m, n)` | | | | | |
| `edit_distance(a, b)` | | | | | |
| `subsets(xs, i)` | | | | | |
| `foo(xs, i)` | | | | | |

`foo` is the function from class:
```python
def foo(xs, i):
    if i >= len(xs):
        return 1
    return xs[i] + foo(xs, i + 1) + foo(xs, i + 3)
```
(In class it was written with slicing; here it is rewritten with an
index so that `@trace` can record the arguments.)

> **NOTE:**
> The tree shapes here are more varied than in Part 2.
> Some are paths, some are balanced, some are uneven, and some grow
> so fast that you will barely be able to see the leaves.
> That variation is the whole point.

## Part 4: Does the master theorem apply?

Now we are ready to bring in the master theorem.

> **The Master Theorem.**
> Suppose $T(n)$ satisfies the recurrence
> $$T(n) = a \, T(n/b) + f(n)$$
> where $a \ge 1$, $b > 1$, and $f$ is asymptotically positive.
> Let $c = \log_b a$.  Then:
>
> 1. If $f(n) = O(n^{c - \epsilon})$ for some $\epsilon > 0$,
>    then $T(n) = \Theta(n^c)$.
> 2. If $f(n) = \Theta(n^c)$,
>    then $T(n) = \Theta(n^c \log n)$.
> 3. If $f(n) = \Omega(n^{c + \epsilon})$ for some $\epsilon > 0$,
>    and if $a f(n/b) \le k f(n)$ for some $k < 1$ (the
>    *regularity condition*), then $T(n) = \Theta(f(n))$.

The master theorem only applies to recurrences of the *specific form*
$T(n) = a T(n/b) + f(n)$.
Many of the functions in this lab do **not** have this form.
Your job is to figure out which ones do, and for those, which case
applies.

For each function from Parts 2 and 3, fill in the following table.
If the recurrence does not have the form required by the master
theorem, leave the $a$, $b$, $c$, and case columns blank and write
the reason in the "why not?" column.

| function | fits $aT(n/b)+f(n)$? | why not? | a | b | c = log_b a | f(n) | case | Θ(·) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bsearch` | | | | | | | | |
| `merge_sort` | | | | | | | | |
| `quick_sort` | | | | | | | | |
| `quick_select` | | | | | | | | |
| `sequential_search_rec` | | | | | | | | |
| `power` | | | | | | | | |
| `fib` | | | | | | | | |
| `hanoi` | | | | | | | | |
| `binom` | | | | | | | | |
| `grid_paths` | | | | | | | | |
| `edit_distance` | | | | | | | | |
| `subsets` | | | | | | | | |
| `foo` | | | | | | | | |

> **NOTE:**
> There are three common reasons a recurrence does *not* fit the
> master theorem:
>
> 1. The split is **subtractive** (the input size decreases by a
>    constant, e.g. $T(n) = T(n-1) + \Theta(1)$), so $b$ does not
>    exist.
> 2. The subproblems have **unequal sizes** (e.g. quicksort on a
>    sorted list, where one side is empty and the other has $n-1$
>    elements), so there is no single $b$.
> 3. The number of subproblems is **not constant** (e.g. `subsets`,
>    where the branching factor depends on $n$).
>
> Deciding which (if any) of these applies is the actual skill being
> tested here.  Getting the answer "the master theorem doesn't
> apply, because ___" is just as important as getting the right
> value of $c$.

> **HINT:**
> The "predicted runtime" column from Parts 2 and 3 should match the
> $\Theta(\cdot)$ column here *where the master theorem applies*.
> Where it does not apply, you can still write a $\Theta(\cdot)$
> using a different method (the substitution method, the recursion
> tree method, or just reading off the tree you drew).

## Part 5: Memoization

One of the most useful decorators in python is `functools.lru_cache`.
It caches the return value of a function keyed by its arguments, so
that repeated calls with the same arguments return instantly.

Consider `fib`:
```
>>> import timeit
>>> timeit.timeit('fib(30)', setup='from recurrences import fib', number=1)
```
The naive `fib` computes the same subproblems over and over.
If we wrap it in `lru_cache`, the repeated subproblems become
$O(1)$ lookups:
```python
from functools import lru_cache
from recurrences import fib

@lru_cache
def fast_fib(n):
    return fib(n)
```
Measure the runtime:
```
>>> timeit.timeit('fast_fib(30)', setup='from demo import fast_fib', number=1)
```

Compare the two times.
You should observe a speedup of many orders of magnitude.

Now look at the recursion trees you drew in Part 3.
In the `fib` tree, the same `args` value appears many times.
If we could color each node by its `args` tuple, we would see that
most of the tree consists of *duplicate* subtrees that the cache
would eliminate.

> **NOTE:**
> We are not going to explain how `lru_cache` works in this lab.
> (That is the topic of next week's lab on decorators.)
> For now, treat it as another black box.
> The important observation is that **a decorator can change the
> asymptotic runtime of a function without changing its behavior.**

Fill in the following table by running `timeit` on each function
with and without `@lru_cache`:

| function | input | runtime without cache | runtime with cache | speedup |
| --- | --- | --- | --- | --- |
| `fib` | `fib(30)` | | | |
| `binom` | `binom(30, 15)` | | | |
| `edit_distance` | `edit_distance('abcdefghij', 'klmnopqrst')` | | | |
| `grid_paths` | `grid_paths(15, 15)` | | | |
| `power` | `power(2, 1000)` | | | |
| `merge_sort` | `merge_sort(list(range(1000)))` | | | |

> **NOTE:**
> Some of these will get a huge speedup and some will get none at
> all.  Why?  Think about which functions in Part 3 recompute the
> same subproblems, and which ones have all-distinct subproblems.
> This is the same distinction you drew in the trees.

## Submission

Upload your changes to github and submit the url to canvas.
