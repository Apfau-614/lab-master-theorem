# lab: master theorem
<!-- byexample: +ellipsis -->

In this lab we will practice working with recursive functions and the master theorem.
You will also see some new functional programming techniques for debugging,
and a technique called *memoization* for making recursive code faster.

## Part 0: Setup

Fork this repo, clone it onto the lambda server, and cd into the cloned repo.
You'll have to make changes to the README and push them to github later.

## Part 1: functions as variables

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
<...>
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

Read that source now.
Everything below modifies `merge_sorted`,
and once a function has been modified, `getsource` shows you the modified function
instead of the original one.

### modifying a function

Sometimes, we write functions that modify the behavior of other functions in order to make them faster or easier to debug.
The `trace.py` file contains a function called `add_trace` that modifies the function you pass to it
so that it prints a picture of its *call tree*.

Notice that `add_trace` does not return a new function for you to assign;
it modifies `merge_sorted` itself.
Try it with the code below:
```
>>> from trace import add_trace
>>> add_trace(merge_sorted)
>>> merge_sorted(xs)
merge_sorted([1, 5, 4, 2, 7, 9, 8, 3, 6, 10])
  merge_sorted([1, 5, 4, 2, 7])
    merge_sorted([1, 5])
      merge_sorted([1])
      merge_sorted([5])
    merge_sorted([4, 2, 7])
      merge_sorted([4])
      merge_sorted([2, 7])
        merge_sorted([2])
        merge_sorted([7])
  merge_sorted([9, 8, 3, 6, 10])
    merge_sorted([9, 8])
      merge_sorted([9])
      merge_sorted([8])
    merge_sorted([3, 6, 10])
      merge_sorted([3])
      merge_sorted([6, 10])
        merge_sorted([6])
        merge_sorted([10])
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

Each call is printed on its own line, indented by the depth of the call stack
at the moment that the call was made,
so the indented output above is a picture of the *call tree* of `merge_sorted`.

How does `add_trace` change a function that it did not write?
Python resolves the name of a recursive function every time the function calls itself,
by looking that name up in the globals of the module that defines it.
`add_trace` rebinds that name to a new function that records the call
and then calls the original one.
Every reference to `merge_sorted` -- including the one that `merge_sorted` itself
uses to make its recursive calls -- now reaches the new function.

The change is permanent, and nothing kept a copy of the original function:
```
>>> merge_sorted(xs)
merge_sorted([...])
...
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```
The only way to get the original `merge_sorted` back is to exit the python interpreter
and start a new one:
```
$ python3
>>> from recurrences import merge_sorted
>>> merge_sorted(xs)
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

### drawing a picture

The indented output is convenient for a small function,
but for a bigger one it is hard to read,
so `trace.py` contains a second function called `add_trace_png`.
It modifies the function in the same way,
but it writes the call tree as graphviz DOT source to a `.dot` file
and runs the `dot` program to render that file as a `.png` image.
```
>>> from trace import add_trace_png
>>> add_trace_png(merge_sorted, 'merge_sorted.png')
>>> merge_sorted(xs)
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```
Add/commit/push the file to github so that the image below displays.

<img src=merge_sorted.png />

Observe that the *call graph* contains a node for each call and an
edge from each call to the calls it makes.

## Part 2: memoization

### The same subproblem, twice

Look at the `power` function from `recurrences.py`:
```
>>> from recurrences import power
>>> print(inspect.getsource(power))
<...>
```
When `n` is even, the branch `if n % 2 == 0` calls `power(x, n // 2)`
**twice** with exactly the same arguments, so the second call
recomputes a value we already have.

Trace the function to see the duplication in the call graph:
```
>>> add_trace_png(power, 'power.png')
>>> power(2, 8)
256
```
Add/commit/push the file to github so that the image below displays.
<img src=power.png />

Every call with an even exponent appears twice in the graph.
Counting the calls gives the recurrence
$$T(n) = 2T(n/2) + \Theta(1).$$

### Computing each subproblem once

We can avoid the recomputation by storing the result in a variable:
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
>>> add_trace_png(modified_pow, 'modified_pow.png')
>>> modified_pow(2, 8)
256
```
Add/commit/push the file to github so that the image below displays.
<img src=modified_pow.png />

The call graph is now linear (instead of a tree).
The recurrence is
$$T(n) = T(n/2) + \Theta(1).$$

### Automatic memoization

Storing a repeated subproblem and reusing it is called *memoization*.
(Note that the spelling is correct---this is not a typo for the more common word memorization!)

For the `modified_pow` function, memoization was easy to do by hand.
But for most recursive functions it is more difficult.

A famous example is a function that computes the Fibonacci numbers
```python
>>> from recurrences import fib
>>> print(inspect.getsource(fib))
<...>
```
Observe that the recurrence relation for `fib` is
$$T(n) = T(n-1) + T(n-2) + \Theta(1).$$
The recurrence is not of the form $a\,T(n/b) + f(n)$ that the master theorem requires,
and so we do not have a tool to solve this recurrence.
But the actual solution is $\Omega(1.61^n)$, which is *very* bad.
Even trying to compute `fib(40)` is already impossible.

Trace the runtime on a small value and observe:
```
>>> add_trace_png(fib, 'fib.png')
>>> fib(8)
21
```
Add/commit/push the file to github so that the image below displays.
<img src=fib.png />

Looking at the graph, it is easy to see that `fib` is called with the same number of arguments many times.
And so we should be able to speed up `fib` by memoizing.
But refactoring `fib` the way we refactored `power` is harder,
because the two recursive calls have different arguments.
There is no single subproblem to store in a variable.

### `functools.lru_cache`

Python provides a function that memoizes for us automatically called `lru_cache` in the `functools` module.
We apply it to `fib`, and then ask `add_trace_png` for a second picture:
```
>>> import functools
>>> fib = functools.lru_cache(fib)
>>> add_trace_png(fib, 'fast_fib.png')
>>> fib(8)
21
>>> fib(40)
102334155
```
Add/commit/push the file to github so that the image below displays.
<img src=fast_fib.png />

Notice the order of the two calls.
The cache ends up on the *outside* of the trace:

    fib(8) -> cache -> trace -> the original fib

A call whose answer is already in the cache never reaches the trace,
so the picture contains a node for each *distinct* call that had to be computed,
and the blue nodes from the previous picture have all disappeared.
The recurrence is
$$T(n) = T(n-1) + \Theta(1).$$
Like the original `fib` recurrence, this is not of the form that the master theorem requires,
but it simplifies to $T(n) = \Theta(n)$.

## Part 3: the big table

Your last task of this lab is to fill out the table below.
For each function:
1. View the code with the `inspect.getsource` function.
    Then determine the recurrence and write it in the second column.
    Do this step for *all* of the functions before you do step 3 for any of them,
    because after a function has been traced `getsource` shows you the traced version.
2. If the recurrence has a form suitable for the master theorem,
    write `yes` in the third column and the solution in the fourth column.
    Otherwise, write `no` in the third column and `---` in the fourth column.
3. For the final column, plot the call graph with the `add_trace_png` function.
    If there are repeated calls (blue cells), then memoization will improve runtime,
    and write `yes`.
    Otherwise, write `no`.

| function | recurrence $T(n)$ | master theorem? | solution $\Theta(\cdot)$ | does memoization help? |
| --- | --- | --- | --- | --- |
| `binary_search`   | | | | |
| `merge_sorted`    | $T(n) = 2T(n/2) + \Theta(n)$ | yes | $T(n) = \Theta(n\log n)$ | no |
| `quick_sorted`    | $T(n) = 2T(n/2) + \Theta(n)$ | yes | $T(n) = \Theta(n\log n)$ | |
| `quick_select`    | $T(n) =  T(n/2) + \Theta(n)$ | yes | | |
| `sequential_search_rec` | | | | |
| `power`           | $T(n) = 2T(n/2) + \Theta(1)$ | yes | | yes |
| `modified_pow`    | $T(n) =  T(n/2) + \Theta(1)$ | yes | | no (already memoized) |
| `fib`             | $T(n) =  T(n-1) + T(n-2) + \Theta(1)$ | no  | --- | yes |
| `fast_fib` (memoized `fib`) | $T(n) =  T(n-1) + \Theta(1)$ | no  | --- | no (already memoized) |
| `grid_paths`      | | | | |
| `foo1`            | | | | |
| `foo2`            | | | | |
| `foo3`            | | | | |

## Submission

Ensure that all your images and completed table are pushed to github.
Then submit your repo url to canvas.
