'''
The trace decorator writes the recursion tree of a function to a DOT file.

The decorator is transparent: the traced function behaves exactly
like the original function (same inputs, same output, same
exceptions).  It additionally records every call to the function --
including recursive calls, provided the function calls itself by
name -- and writes them to a graphviz DOT file.

The DOT source is generated directly, without the graphviz library,
and outputfile names a .dot file rather than a .png.  Render it
yourself with any graphviz layout program:

    $ dot -Tpng fib.dot -o fib.png

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


def trace(f, outputfile=None):
    '''
    Return a version of f that writes its recursion tree to outputfile.

    The wrapper is transparent: it returns the same value as f and
    propagates the same exceptions.  As a side effect, it records
    the calls made to the wrapped function and, when outputfile is
    given, writes them as graphviz DOT source to that file.  Each
    node is labelled with the name of the function and the
    arguments of the call.

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
        label = f.__name__ + _label(args, kwargs)
        parent = stack[-1] if stack else None
        nodes.append((node_id, label, parent))
        stack.append(node_id)
        try:
            return f(*args, **kwargs)
        finally:
            stack.pop()
            # When the outermost call returns, write the tree and
            # reset the state so the next top-level call starts fresh.
            if not stack:
                if outputfile is not None:
                    _write_dot(nodes, outputfile)
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


def _escape(s):
    r'''
    Escape a string so that it can appear inside a DOT label.

    >>> _escape('fib(5)')
    'fib(5)'
    >>> _escape('a"b')
    'a\\"b'
    '''
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def _write_dot(nodes, outputfile):
    '''
    Write a list of (node_id, label, parent_id) tuples as DOT source.

    The DOT language is a small text format, so we format it by hand
    instead of pulling in the graphviz library.  The resulting file
    can be rendered by any of the graphviz layout programs:

        $ dot -Tpng fib.dot -o fib.png
    '''
    lines = ['digraph {']
    lines.append('    node [shape=box fontname="Courier" fontsize="10"]')
    for node_id, label, parent in nodes:
        lines.append('    {} [label="{}"]'.format(node_id, _escape(label)))
    for node_id, label, parent in nodes:
        if parent is not None:
            lines.append('    {} -> {}'.format(parent, node_id))
    lines.append('}')
    with open(outputfile, 'w') as fp:
        fp.write('\n'.join(lines) + '\n')
