'''
The trace decorator renders the recursion tree of a function to a PNG.

The decorator is transparent: the traced function behaves exactly
like the original function (same inputs, same output, same
exceptions).  It additionally records every call to the function --
including recursive calls, provided the function calls itself by
name -- and renders them to a graphviz PNG.

Doctests:

    >>> from recurrences import binom
    >>> binom3 = trace(binom)
    >>> binom3(5, 2) == binom(5, 2)
    True
    >>> binom3.__name__
    'binom'
    >>> binom3.__wrapped__ is binom
    True
'''
import functools
import os

import graphviz


def trace(f, outputfile=None):
    '''
    Return a version of f that renders its recursion tree to outputfile.

    The wrapper is transparent: it returns the same value as f and
    propagates the same exceptions.  As a side effect, it records
    the calls made to the wrapped function and, when outputfile is
    given, renders them to a PNG using graphviz.

    >>> from recurrences import binom
    >>> binom3 = trace(binom)
    >>> binom3(5, 2) == binom(5, 2)
    True
    '''
    nodes = []     # list of (node_id, label, parent_id)
    stack = []     # current call stack of node_ids
    counter = [0]  # mutable counter of node_ids

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        node_id = counter[0]
        counter[0] += 1
        label = _label(args, kwargs)
        parent = stack[-1] if stack else None
        nodes.append((node_id, label, parent))
        stack.append(node_id)
        try:
            return f(*args, **kwargs)
        finally:
            stack.pop()
            # When the outermost call returns, render the tree and
            # reset the state so the next top-level call starts fresh.
            if not stack:
                if outputfile is not None:
                    _render(nodes, outputfile)
                counter[0] = 0
                del nodes[:]

    # Rebind f's name in its defining module to the wrapper.  This is
    # what makes recursive calls inside f's body reach the wrapper:
    # when f's body evaluates `f(...)`, it looks up `f` in its
    # module's global namespace, which now points at the wrapper.
    f.__globals__[f.__name__] = wrapper

    return wrapper


def _label(args, kwargs):
    '''
    Format the arguments of a call as a short string.

    >>> _label((1, 2), {})
    '(1, 2)'
    >>> _label((1,), {'y': 3})
    '(1, y=3)'
    '''
    parts = [repr(a) for a in args]
    parts += ['{}={!r}'.format(k, v) for k, v in kwargs.items()]
    return '(' + ', '.join(parts) + ')'


def _render(nodes, outputfile):
    '''
    Render a list of (node_id, label, parent_id) tuples to a PNG.

    graphviz writes two files: the DOT source (a text description
    of the graph) and the rendered PNG.  We keep both because the
    DOT source is useful for debugging.
    '''
    dot = graphviz.Digraph()
    dot.attr('node', shape='box', fontname='Courier', fontsize='10')
    for node_id, label, parent in nodes:
        dot.node(str(node_id), label)
        if parent is not None:
            dot.edge(str(parent), str(node_id))
    base = os.path.splitext(outputfile)[0]
    dot.render(base, format='png', cleanup=False)
