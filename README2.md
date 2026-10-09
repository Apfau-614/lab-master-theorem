<!-- byexample: +ellipsis -->

In python, functions are *first-class objects*.
This means that we can manipulate them just like any other type of variable.

The `recurrences.py` file contains a handful of recursive functions.
Some of them we have already studied, like `merge_sorted`.
We will first use this familiar function to learn some new debugging techniques;
then we will apply these debugging techniques to help us understand new programs.

First, observe what happens when we use the `merge_sorted` function without parentheses:
```
>>> from recurrences import merge_sorted
>>> merge_sorted
<function merge_sorted at 0x7ff9c1796840>
```
Recall that without parentheses, we are not *running* the function,
we are just holding a *reference* to the function.
This reference is what is displayed in the python repl above.

Because a python function is just an ordinary variable, we can assign it to other variables
```
>>> f = merge_sorted
>>> xs = [1, 5, 4, 2, 7, 9, 8, 3, 6, 10]
>>> f(xs)
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```
Above, both `f` and `merge_sorted` reference the same function object in python.

There are many useful built-in functions that take other functions as arguments.
One example is the `getsource` function in the `inspect` module,
which returns the function's source as a string.
```
>>> import inspect
>>> inspect.getsource(merge_sorted)
<...>
```
The output above is not particularly readable,
but you can make it more readable by printing the string:
```
>>> print(inspect.getsource(merge_sorted))
<...>
```

Sometimes, we write functions that modify the behavior of other functions in order to make them faster or easier to debug.
The `trace.py` file contains `trace` function inside of it that prints the *call graph* for a recursive function.
Try it with the code below:
```
>>> from trace import trace
>>> trace_merge_sorted = trace(merge_sorted, 'merge_sorted.png')
>>> trace_merge_sorted(xs)
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```
Add/commit/push it to github so that it appears in the picture below.

<img src=merge_sorted.png />

Observe that the *call graph* contains a node for each call and an
edge from each call to the calls it makes.

## Memoization

### The same subproblem, twice

Look at the `power` function from `recurrences.py`:
```
>>> import inspect
>>> from recurrences import power
>>> inspect.getsource(power)
<...>
```
When `n` is even, the branch `if n % 2 == 0` calls `power(x, n // 2)`
**twice** with exactly the same arguments, so the second call
recomputes a value we already have.

Trace the function to see the duplication in the call graph:
```
>>> from trace import trace
>>> trace_power = trace(power, 'power.png')
>>> trace_power(2, 8)
256
```
<img src=power.png />

Every call with an even exponent appears twice in the graph.  Counting
the calls gives the recurrence
$$T(n) = 2\,T(n/2) + \Theta(1),$$
which the master theorem solves as $\Theta(n)$.

### Computing each subproblem once

We can avoid the recomputation by storing the result in a variable and
using it twice:
```python
def modified_pow(x, n):
    if n == 0:
        return 1
    if n % 2 == 0:
        half = modified_pow(x, n // 2)
        return half * half
    return x * modified_pow(x, n - 1)
```
Trace it and compare the two call graphs:
```
>>> def modified_pow(x, n):
...     if n == 0:
...         return 1
...     if n % 2 == 0:
...         half = modified_pow(x, n // 2)
...         return half * half
...     return x * modified_pow(x, n - 1)
>>> trace_modified_pow = trace(modified_pow, 'modified_pow.png')
>>> trace_modified_pow(2, 8)
256
```
<img src=modified_pow.png />

The call graph is now a path, and the recurrence is
$$T(n) = T(n/2) + \Theta(1),$$
which the master theorem solves as $\Theta(\log n)$.

Fill in the solved recurrences:

| function | recurrence $T(n)$ | master theorem case | solution $\Theta(\cdot)$ |
| --- | --- | --- | --- |
| `power` | | | |
| `modified_pow` | | | |

### Automatic memoization

Storing a repeated subproblem and reusing it is called **memoization**.
It works for any function that recomputes the same subproblem, but
doing it by hand quickly gets tedious.

The poster child is `fib`:
```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```
Trace it:
```
>>> from recurrences import fib
>>> trace_fib = trace(fib, 'fib.png')
>>> trace_fib(6)
8
```
<img src=fib.png />

`fib(3)` is computed once, then again, then again, and the deeper
subproblems are recomputed even more.  The number of calls satisfies
$$T(n) = T(n-1) + T(n-2) + \Theta(1),$$
which is exponential, $\Theta(\varphi^n)$ for the golden ratio
$\varphi = (1 + \sqrt{5})/2$.  This is *very* bad: `fib(40)` already
requires billions of calls.  The recurrence is **not** of the form
$a\,T(n/b) + f(n)$ — the two subproblems are subtractive and have
different sizes — so the master theorem does not apply.

Refactoring `fib` the way we refactored `power` is harder, because the
two recursive calls have **different** arguments.  There is no single
subproblem to store in a variable.

### `functools.lru_cache`

Python provides memoization as a decorator:
```python
import functools

@functools.lru_cache
def fast_fib(n):
    if n < 2:
        return n
    return fast_fib(n - 1) + fast_fib(n - 2)
```
Recall from the first half of this lab that a decorator is just a
function that takes a function and returns a function.  `lru_cache`
stores the return value keyed by the arguments and returns the stored
value on a repeated call without running the body at all.  The result
is the same; each distinct subproblem is computed only once.

Trace the memoized version.  Here the cache sits *outside* the tracer,
so a cache hit does not add a node to the graph:
```
>>> import functools
>>> def fast_fib(n):
...     if n < 2:
...         return n
...     return fast_fib(n - 1) + fast_fib(n - 2)
>>> fast_fib = functools.lru_cache(trace(fast_fib, 'fast_fib.png'))
>>> fast_fib(6)
8
```
<img src=fast_fib.png />

The graph now has a node for each **distinct** subproblem — only
$n + 1$ of them — instead of an exponential number, and the runtime
drops from exponential to linear.  The recurrence is
$$T(n) = T(n-1) + \Theta(1),$$
so the solution is $\Theta(n)$.  Like the `fib` recurrence, it is
**not** of the form $a\,T(n/b) + f(n)$ — the split is subtractive — so
the master theorem does not apply.

## Table of all the functions

Fill in this table for every function in `recurrences.py`.  The
"master theorem?" column asks whether the recurrence has the form
$a\,T(n/b) + f(n)$; if it does not, explain why.

| function | recurrence $T(n)$ | master theorem? | solution $\Theta(\cdot)$ | does memoization help? |
| --- | --- | --- | --- | --- |
| `bsearch` | | | | |
| `merge_sorted` | | | | |
| `quick_sorted` | | | | |
| `quick_select` | | | | |
| `sequential_search_rec` | | | | |
| `power` | | | | |
| `fib` | | | | |
| `hanoi` | | | | |
| `binom` | | | | |
| `grid_paths` | | | | |
| `edit_distance` | | | | |
| `subsets` | | | | |
| `foo` | | | | |
