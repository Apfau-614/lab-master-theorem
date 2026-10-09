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

## Part 2: memoization

### The same subproblem, twice

Look at the `power` function from `recurrences.py`:
```
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
Add/commit/push the `power.png` file so that the image below displays.
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
>>> trace_modified_pow = trace(modified_pow, 'modified_pow.png')
>>> trace_modified_pow(2, 8)
256
```
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
>>> trace_fib = trace(fib, 'fib.png')
>>> trace_fib(8)
21
>>> trace_fast_fib(40) # will take years to finish; run it and press CTRL-C to stop
```
<img src=fib.png />

Looking at the graph, it is easy to see that `fib` is called with the same number of arguments many times.
And so we should be able to speed up `fib` by memoizing.
But refactoring `fib` the way we refactored `power` is harder,
because the two recursive calls have different arguments.
There is no single subproblem to store in a variable.

### `functools.lru_cache`

Python provides a function that memoizes for us automatically called `lru_cache` in the `functools` module.
We can apply it to the `fib` function like so:
```
>>> import functools
>>> fast_fib = functools.lru_cache(fib)
```
And now let's trace `fib` instead of `fast_fib`:
```
>>> trace_fast_fib = trace(fast_fib, 'fast_fib.png')
>>> trace_fast_fib(8)
21
>>> trace_fast_fib(40) # should now finish instantly
102334155
```
<img src=fast_fib.png />

The graph now has a node for each distinct call to `fib` and most of the duplicates have been eliminated.
The recurrence is
$$T(n) = T(n-1) + \Theta(1).$$
Like the original `fib` recurrence, it is not solvable by the master theorem does not apply.
But this recurrence simplifies to $T(n) = \Theta(n)$.

## Part 3: the big table

Your last task of this lab is to fill out the table below.
For each function:
1. View the code with the `inspect.getsource` function.
    Then determine the recurrence and write it in the second column.
2. If the recurrence has a form suitable for the master theorem,
    write `yes` in the third column and the solution in the fourth column.
    Otherwise, write `no` in the third column and `---` in the fourth column.
3. For the final column, plot the call graph with the `trace` function.
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
| `modified_power`  | $T(n) =  T(n/2) + \Theta(1)$ | yes | | no (already memoized) |
| `fib`             | $T(n) =  T(n-1) + T(n-2) + \Theta(1)$ | no  | --- | yes |
| `fast_fib`        | $T(n) =  T(n-1) + \Theta(1)$ | no  | --- | no (already memoized) |
| `foo1`            | | | | |
| `foo2`            | | | | |
| `foo3`            | | | | |

## Submission

Ensure that all your images and completed table are pushed to github.
Then submit your repo url to canvas.
