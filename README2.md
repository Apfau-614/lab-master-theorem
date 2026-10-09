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

Observe that the *call graph* contains a node for each 
