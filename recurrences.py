'''
Recursive functions for the recursion trees lab.

Every function in this file calls itself by name (rather than
calling some helper), so that the @trace decorator can rebind the
name and see the recursive calls.

Run the doctests with:

    $ python3 -m doctest recurrences.py
'''


# ---------------------------------------------------------------------------
# Part 3: algorithms you already know
# ---------------------------------------------------------------------------

def bsearch(xs, y, lo=0, hi=None):
    '''
    Return True if y is in the sorted sequence xs.

    >>> bsearch([1, 3, 5, 7, 9, 11], 9)
    True
    >>> bsearch([1, 3, 5, 7, 9, 11], 8)
    False
    >>> bsearch(list(range(-1000, 1000, 2)), 9)
    False
    '''
    if hi is None:
        hi = len(xs) - 1
    if lo > hi:
        return False
    mid = (lo + hi) // 2
    if xs[mid] == y:
        return True
    if xs[mid] > y:
        return bsearch(xs, y, lo, mid - 1)
    return bsearch(xs, y, mid + 1, hi)


def merge_sorted(xs):
    '''
    Return a sorted copy of the list xs.

    >>> merge_sorted([3, 1, 4, 1, 5, 9, 2, 6])
    [1, 1, 2, 3, 4, 5, 6, 9]
    >>> merge_sorted([])
    []
    >>> merge_sorted([1])
    [1]
    '''
    if len(xs) <= 1:
        return xs
    mid = len(xs) // 2
    return _merge(merge_sorted(xs[:mid]), merge_sorted(xs[mid:]))


def _merge(a, b):
    '''
    Merge two sorted lists into a single sorted list.

    >>> _merge([1, 3], [2, 4])
    [1, 2, 3, 4]
    '''
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


def quick_sorted(xs):
    '''
    Return a sorted copy of the list xs.

    >>> quick_sorted([3, 1, 4, 1, 5, 9, 2, 6])
    [1, 1, 2, 3, 4, 5, 6, 9]
    >>> quick_sorted([])
    []
    '''
    if len(xs) <= 1:
        return xs
    pivot = xs[0]
    less = [x for x in xs[1:] if x < pivot]
    more = [x for x in xs[1:] if x >= pivot]
    return quick_sorted(less) + [pivot] + quick_sorted(more)


def quick_select(xs, k):
    '''
    Return the k-th smallest element of the tuple xs (0-indexed).

    >>> quick_select((3, 1, 4, 1, 5, 9, 2, 6), 0)
    1
    >>> quick_select((3, 1, 4, 1, 5, 9, 2, 6), 7)
    9
    '''
    pivot = xs[0]
    less = tuple(x for x in xs[1:] if x < pivot)
    more = tuple(x for x in xs[1:] if x >= pivot)
    if k < len(less):
        return quick_select(less, k)
    if k == len(less):
        return pivot
    return quick_select(more, k - len(less) - 1)


def sequential_search_rec(xs, y):
    '''
    Return True if y is in the sequence xs.

    >>> sequential_search_rec([1, 3, 5, 4, 2, 0], 2)
    True
    >>> sequential_search_rec([1, 3, 5, 4, 2, 0], 6)
    False
    '''
    if len(xs) == 0:
        return False
    if xs[0] == y:
        return True
    return sequential_search_rec(xs[1:], y)


# ---------------------------------------------------------------------------
# Part 4: new functions
# ---------------------------------------------------------------------------

def power(x, n):
    '''
    Return x raised to the n-th power.

    >>> power(2, 10)
    1024
    >>> power(3, 0)
    1
    '''
    if n == 0:
        return 1
    if n % 2 == 0:
        return power(x, n // 2) * power(x, n // 2)
    return x * power(x, n - 1)


def fib(n):
    '''
    Return the n-th fibonacci number.

    >>> fib(0)
    0
    >>> fib(1)
    1
    >>> fib(10)
    55
    '''
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def hanoi(n, a, b, c):
    '''
    Return the list of moves that solves the tower of hanoi.

    >>> hanoi(1, 'A', 'B', 'C')
    [('A', 'C')]
    >>> len(hanoi(3, 'A', 'B', 'C'))
    7
    '''
    if n == 0:
        return []
    return (hanoi(n - 1, a, c, b)
            + [(a, c)]
            + hanoi(n - 1, b, a, c))


def binom(n, k):
    '''
    Return the binomial coefficient C(n, k).

    >>> binom(5, 2)
    10
    >>> binom(10, 5)
    252
    '''
    if k == 0 or k == n:
        return 1
    return binom(n - 1, k - 1) + binom(n - 1, k)


def grid_paths(m, n):
    '''
    Return the number of monotone paths from (0, 0) to (m, n).

    >>> grid_paths(0, 0)
    1
    >>> grid_paths(2, 2)
    6
    >>> grid_paths(3, 3)
    20
    '''
    if m == 0 or n == 0:
        return 1
    return grid_paths(m - 1, n) + grid_paths(m, n - 1)


def edit_distance(a, b, i=None, j=None):
    '''
    Return the Levenshtein distance between strings a and b.

    >>> edit_distance('cat', 'bat')
    1
    >>> edit_distance('kitten', 'sitting')
    3
    '''
    if i is None:
        i = len(a)
    if j is None:
        j = len(b)
    if i == 0:
        return j
    if j == 0:
        return i
    if a[i - 1] == b[j - 1]:
        return edit_distance(a, b, i - 1, j - 1)
    return 1 + min(
        edit_distance(a, b, i - 1, j),
        edit_distance(a, b, i, j - 1),
        edit_distance(a, b, i - 1, j - 1),
    )


def subsets(xs, i=0):
    '''
    Return the list of all subsets of the tuple xs.

    >>> sorted(subsets((1, 2)))
    [(), (1,), (1, 2), (2,)]
    >>> len(subsets((1, 2, 3)))
    8
    '''
    if i == len(xs):
        return [()]
    without = subsets(xs, i + 1)
    with_x = [(xs[i],) + s for s in without]
    return without + with_x


def foo(xs, i=0):
    '''
    The function from class.

    >>> foo((1, 2, 3, 4))
    20
    >>> foo(())
    1
    '''
    if i >= len(xs):
        return 1
    return xs[i] + foo(xs, i + 1) + foo(xs, i + 3)
