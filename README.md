# Lab: Recursion Trees and the Master Theorem

<img src=img/meme.jpg width=400px />

When you look at a recursive function, you see a few lines of code.
What the computer actually does is build a *tree* of function calls.
The shape and size of that tree determines how long the function
takes to run, and the master theorem is a shortcut for computing
that runtime without having to draw the tree.

This lab teaches three things.

1. **A graph is just data.**  A picture of a tree is not the tree.
   graphviz separates "describe the graph" (the DOT language, a
   small text format) from "render the graph" (the `dot` program,
   which draws a PNG).  You will write DOT by hand and render it
   from the command line.  This is the same pattern as a compiler
   emitting assembly and an *assembler* turning that assembly into
   a binary.

2. **Functions are objects.**  You can pass them to other functions
   and get them back.  A *decorator* is just a function that takes
   a function and returns another function.  The `trace` decorator
   in this lab writes a DOT file every time you call the function
   it wraps.

3. **The master theorem summarizes a picture.**  When a recurrence
   has the form T(n) = a T(n/b) + f(n), the master theorem gives
   you Θ(·) directly.  Understanding the picture makes the theorem
   easier to remember and easier to apply.

You will finish the lab by seeing how a single decorator,
`functools.lru_cache`, can change the *asymptotic runtime* of a
function without changing its observable behavior.

## Part 0: Setup

Fork this repo and clone your fork on the lambda server.
The instructions below ask you to directly edit the README of your
fork.

Install the python dependencies:
```
$ pip3 install -r requirements.txt
```

> **NOTE:**
> This lab does not use the `graphviz` python package.  Instead, it
> renders DOT files by calling the `dot` program directly.  The
> binary is preinstalled on the lambda server, but on your own
> computer you will need to install it yourself.  See
> <https://graphviz.org/download/>.

Verify that the supporting files are correct by running the
doctests:
```
$ python3 -m doctest recurrences.py
$ python3 -m doctest trace.py
```

You should see no output if all the tests pass.

## Part 1: The DOT language

This part introduces the *intermediate language* that graphviz
uses to describe graphs.

### A hello world graph

Create a file called `hello.dot` with the following contents:
```
digraph {
    a [label="root"]
    b [label="left"]
    c [label="right"]
    a -> b
    a -> c
}
```

A DOT file describes a graph as a list of statements between
braces.  The keyword `digraph` means "directed graph" (use `graph`
for undirected).  Each statement is one of:

- `a [label="root"]` — a *node* named `a`, with an attribute.
- `a -> b` — a *directed edge* from `a` to `b`.  (In an undirected
  graph the arrow is `--` instead of `->`.)

That is the entire language you need for this lab.  Everything
else is attributes you can set with `key=value` inside `[...]`.

### Rendering with the `dot` program

The `dot` program reads a DOT file and writes a picture.  To render
your file to a PNG:
```
$ dot -Tpng hello.dot -o hello.png
```

The `-T` flag selects the output format.  Try a few:
```
$ dot -Tsvg hello.dot -o hello.svg
$ dot -Tpdf hello.dot -o hello.pdf
$ dot -Tpng hello.dot -o hello.png
```
The same DOT source produces the same graph in three different file
formats.  This is exactly the pattern of a compiler: a frontend
emits an intermediate language (assembly, DOT), and a backend turns
that intermediate language into a target (a binary, a PNG).  The
intermediate language is the *useful* artifact: it is text,
readable, diffable, and editable.  The PNG is just one possible
rendering.

The `dot` program also provides several layout engines.  By default
`dot` draws *hierarchical* layouts (good for trees).  The `neato`,
`circo`, and `fdp` programs use different layout algorithms, and
you can pick one with the `-K` flag:
```
$ dot -Kneato -Tpng hello.dot -o hello_neato.png
```
You will not need these for this lab, but they are one reason the
separation between DOT (the description) and rendering (the
picture) is useful.

### Viewing PNGs on the lambda server

You cannot view images in a terminal.  The simplest way to view
them on the lambda server is to commit and push to github, and
then reference them from this README:
```html
<img src=hello.png width=400px>
```
Try it now: copy the HTML line above into your README, commit,
push, and refresh this page on github.  You should see your
three-node graph.

## Part 2: Functions are objects

In python, functions are *first-class objects*.  That means you can
store them in variables, pass them to other functions, and return
them from other functions.  You have already used this in earlier
labs:
```
>>> xs = ['hello', 'hi', 'howdy']
>>> xs.sort(key=len)
```
The `key=len` argument passes the function `len` as a value to
`sort`.

Python's `inspect` module lets you look at any live function object.
Try this in a python interpreter:
```
>>> import inspect
>>> from recurrences import fib
>>> print(inspect.getsource(fib))
def fib(n):
    '''
    Return the n-th fibonacci number.
    ...
    '''
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```
You can now read the source of any function in the lab without
leaving the interpreter.  Try it on `bsearch`, `merge_sort`, and
`quick_select`.

A few related functions in the same module:

| call | what it returns |
| --- | --- |
| `inspect.getsource(f)` | the source code of `f` |
| `inspect.getdoc(f)` | the docstring of `f` (same as `f.__doc__`) |
| `inspect.signature(f)` | the parameter list of `f` |
| `inspect.getsourcefile(f)` | which `.py` file `f` came from |

> **NOTE:**
> `inspect.getsource` fails with `OSError` on built-in functions
> like `print` and `len`, because there is no source file to read.
> It works on functions defined in `.py` files.

### A decorator is a function that takes a function

The simplest decorator I can think of:
```python
def twice(f):
    def g(*args, **kwargs):
        return f(f(*args, **kwargs))
    return g
```
Apply it by hand:
```
>>> def inc(x):
...     return x + 1
>>> inc2 = twice(inc)
>>> inc2(0)
2
>>> inc2(10)
12
```
The following code does exactly the same thing:
```python
@twice
def inc(x):
    return x + 1
```
The `@twice` line is *syntactic sugar*.  The python interpreter
takes the function object defined on the next lines, passes it to
`twice`, and rebinds the name `inc` to the result.  In other words,
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

The file `trace.py` defines a decorator with the signature
```python
trace(f, outputfile=None)
```
It returns a wrapper of `f` that:

1. behaves *identically* to `f` (same inputs, same output, same
   exceptions), and
2. as a side effect, writes a graphviz DOT file describing the
   *call tree* of `f`.

Unlike earlier labs, `trace` does **not** render a PNG for you.
It writes the DOT source and stops there.  You render the picture
yourself:
```
$ dot -Tpng fib.dot -o fib.png
```
This is deliberate.  The DOT file is the intermediate language,
and it is more useful than the PNG for debugging: you can read
it, diff it, edit it by hand, and feed it to the other graphviz
tools you saw in Part 1.

### Prove transparency by example

The first thing every good scientist does with a new instrument is
verify that it does not perturb what it measures.  Do the same
here:
```
>>> from trace import trace
>>> from recurrences import fib
>>> traced_fib = trace(fib)
>>> traced_fib(10) == fib(10)
True
```
The two calls return the same value, so the decorator has not
changed the behavior of `fib`.

> **NOTE:**
> There is a subtlety here.  `trace` works by rebinding the name
> `fib` in the *module* `recurrences` to the wrapper.  This is
> what makes the recursive calls inside `fib`'s body go through
> the wrapper (python resolves those calls by name lookup at call
> time).  If you want to keep both versions around, save a
> reference first:
>
>     original_fib = fib
>     traced_fib = trace(fib)

### The `@trace` sugar

Once you trust the decorator, you can use the `@` sugar anywhere:
```python
@trace(outputfile='fib.dot')
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```
Now every call to `fib` writes a DOT file.  Try it on a small
input:
```
>>> fib(5)
```
You should see a file `fib.dot` appear.  Render it with:
```
$ dot -Tpng fib.dot -o fib.png
```

### `functools.wraps` and introspection

Look at the wrapper's name:
```
>>> traced_fib.__name__
'fib'
```
This works because `trace` uses `functools.wraps`, which copies the
name, docstring, and other metadata from `f` onto the wrapper.
Without it, `traced_fib.__name__` would be `'wrapper'`, and
`inspect.getsource(traced_fib)` would show you the wrapper's code
instead of `fib`'s.  Every well-written decorator uses
`functools.wraps`.

You can always see through the wrapper using the `__wrapped__`
attribute:
```
>>> traced_fib.__wrapped__ is fib
True
```
The same trick works on functions decorated with
`functools.lru_cache`, which is the last decorator we will see in
this lab.

## Part 3: Trees for algorithms you already know

You have already seen several recursive algorithms this semester.
For each function below, trace it, look at the recursion tree, and
fill in the table.

The functions live in `recurrences.py`.  To trace one:
```
>>> from trace import trace
>>> from recurrences import bsearch
>>> traced = trace(bsearch, 'bsearch.dot')
>>> traced(list(range(64)), 17)
```
Then render the DOT file:
```
$ dot -Tpng bsearch.dot -o bsearch.png
```

You will need to choose a value of n that is small enough for the
tree to be legible and large enough to show the shape.  For
balanced splits, n = 8 works well; for exponential functions, you
may need to go as small as n = 4.

> **WARNING:**
> The trace decorator builds a python object for every call.
> The recursion tree of `fib(30)` has about a million nodes.
> Start with tiny inputs.

| function | tree shape | depth | # recursive calls | recurrence T(n) | predicted runtime |
| --- | --- | --- | --- | --- | --- |
| `bsearch` | | | | | |
| `merge_sort` | | | | | |
| `quick_sort` | | | | | |
| `quick_select` | | | | | |
| `sequential_search_rec` | | | | | |

For the "tree shape" column, use one of: *path* (each call has one
child), *balanced binary* (each call has two children and halves
the input), *uneven binary* (each call has two children but the
halves are unequal), *subtractive* (each call has children but the
input size decreases by a constant rather than a factor), or
*other*.

> **HINT:**
> The "# recursive calls" column is what we really care about.
> The runtime of a recursive function is approximately the number
> of calls times the work done inside each call.  Since we are not
> measuring wall-clock time in this lab, "# calls" is our proxy
> for "runtime".

## Part 4: New functions

Now do the same for the following functions, which you have not
seen before.

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

`foo` is the function from class, rewritten with an explicit index
so the tracer can label the nodes:
```python
def foo(xs, i=0):
    if i >= len(xs):
        return 1
    return xs[i] + foo(xs, i + 1) + foo(xs, i + 3)
```
Trace `foo((1, 2, 3, 4))` and compare the tree you drew by hand in
class to the one the tracer produces.  Do they match?

> **NOTE:**
> The shapes here are more varied than in Part 3.  Some are paths,
> some are balanced, some are uneven, and some grow so fast you
> will barely see the leaves.  That variation is the whole point.

## Part 5: The master theorem

Now we are ready for the master theorem.

> **The Master Theorem.**
> Suppose T(n) satisfies
> $$T(n) = a \, T(n/b) + f(n)$$
> where a ≥ 1, b > 1, and f is asymptotically positive.  Let
> c = log_b(a).  Then:
>
> 1. If f(n) = O(n^(c − ε)) for some ε > 0, then T(n) = Θ(n^c).
> 2. If f(n) = Θ(n^c), then T(n) = Θ(n^c log n).
> 3. If f(n) = Ω(n^(c + ε)) for some ε > 0, and if the
>    *regularity condition* a f(n/b) ≤ k f(n) holds for some
>    k < 1, then T(n) = Θ(f(n)).

The master theorem only applies to recurrences of the specific
form T(n) = a T(n/b) + f(n).  Many of the functions in this lab do
*not* have that form.  Your job is to figure out which ones do, and
for those, which case applies.

For each function from Parts 3 and 4, fill in the following table.
If the recurrence does not have the form required by the master
theorem, leave the a, b, c, and case columns blank and explain why
in the "why not?" column.

| function | fits a T(n/b) + f(n)? | why not? | a | b | c = log_b a | f(n) | case | Θ(·) |
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
> There are two common reasons a recurrence does not fit the
> master theorem:
>
> 1. The split is **subtractive**, so no b exists
>    (e.g. T(n) = T(n−1) + Θ(1)).
> 2. The subproblems have **unequal sizes**, so no single b exists
>    (e.g. quicksort on a sorted list).
>
> Deciding which (if any) of these applies is the skill being
> tested.  Writing "does not apply, because ___" is just as
> important as writing the right value of c.

> **HINT:**
> The "predicted runtime" column from Parts 3 and 4 should match
> the "Θ(·)" column here *where the master theorem applies*.
> Where it does not, you can still write a Θ(·) using another
> method: the substitution method, the recursion tree method, or
> just reading the tree you drew.

## Part 6: Memoization

Look back at the recursion tree of `fib`.  The same subproblem
appears in many different branches: `fib(3)` is computed once, then
again, then again.  If we could cache the return value of `fib`
keyed by its argument, every duplicate subtree would become a
single O(1) lookup.

Python provides exactly this as a decorator:
```python
import functools

@functools.lru_cache
def fast_fib(n):
    return fib(n)
```
`lru_cache` stands for *least-recently-used cache*.  It stores the
return value of the function keyed by its arguments, and returns
the cached value on subsequent calls with the same arguments:
```
>>> @functools.lru_cache
... def square(x):
...     print(f'computing {x}**2')
...     return x * x
>>> square(3)
computing 3**2
9
>>> square(3)
9
```
We are not going to explain how `lru_cache` works.  (That is the
topic of next week's lab on decorators.)  For now, treat it as
another black box.

The important observation is that **a decorator can change the
asymptotic runtime of a function without changing its behavior.**

Measure the speedup using `timeit`.  First add `fast_fib` (and
versions of the other functions below wrapped in `lru_cache`) to
`recurrences.py`:
```python
import functools

@functools.lru_cache
def fast_fib(n):
    return fib(n)
```
Then run the timed comparisons:
```
$ python3 -m timeit -s 'from recurrences import fib' 'fib(30)'
$ python3 -m timeit -s 'from recurrences import fast_fib' 'fast_fib(30)'
```
Fill in the following table:

| function | input | runtime without cache | runtime with cache | speedup |
| --- | --- | --- | --- | --- |
| `fib` | `fib(30)` | | | |
| `binom` | `binom(30, 15)` | | | |
| `edit_distance` | `edit_distance('abcdefghij', 'klmnopqrst')` | | | |
| `grid_paths` | `grid_paths(15, 15)` | | | |
| `power` | `power(2, 1000)` | | | |
| `merge_sort` | `merge_sort(tuple(range(1000)))` | | | |

> **NOTE:**
> Some of these get a huge speedup, and some get none at all.
> Why?  Think about which functions recompute the same
> subproblems, and which ones have all-distinct subproblems.
> This is the same distinction you drew in the trees.

You have now seen that the asymptotic runtime of a function can be
understood in two ways: by deriving a recurrence and applying the
master theorem, or by looking at the number of nodes in the
recursion tree.  The two should always agree — and where the
master theorem does not apply, the tree is still there to tell you
the answer.

## Submission

Upload your changes to github and submit the url to canvas.
