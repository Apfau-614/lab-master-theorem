'''
The trace decorator writes the recursion tree of a function to a DOT file.

The decorator is transparent: the traced function behaves exactly
like the original function (same inputs, same output, same
exceptions).  It additionally records every call to the function --
including recursive calls, provided the function calls itself by
name -- and writes them to a graphviz DOT file.

The DOT source is generated directly, without the graphviz library.
If outputfile ends in .png, the decorator shells out to the `dot`
program with subprocess.run to render the picture; otherwise it
writes the DOT source and stops there:

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
import os
import subprocess
import types


def trace(f, outputfile=None, highlight_duplicates=True):
    '''
    Return a version of f that writes its recursion tree to outputfile.

    The wrapper is transparent: it returns the same value as f and
    propagates the same exceptions.  As a side effect, it records
    the calls made to the wrapped function and, when outputfile is
    given, writes them as graphviz DOT source to that file.  Each
    node is labelled with the name of the function and the
    arguments of the call.

    If outputfile ends in .png, the DOT source is written to the
    matching .dot file and the `dot` program is run to render the
    PNG.  If highlight_duplicates is true, any call whose arguments
    have been seen before is filled light blue; the first call with
    a given set of arguments stays white.

    >>> from recurrences import binom
    >>> binom3 = trace(binom)
    >>> binom3(5, 2) == binom(5, 2)
    True
    '''
    nodes = []     # list of (node_id, label, parent_id, duplicate)
    stack = []     # current call stack of node_ids
    counter = [0]  # mutable counter of node_ids
    seen = set()   # labels of calls already made

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        node_id = counter[0]
        counter[0] += 1
        label = f.__name__ + _label(args, kwargs)
        dup = highlight_duplicates and label in seen
        seen.add(label)
        parent = stack[-1] if stack else None
        nodes.append((node_id, label, parent, dup))
        stack.append(node_id)
        try:
            return traced_f(*args, **kwargs)
        finally:
            stack.pop()
            # When the outermost call returns, write the tree and
            # reset the state so the next top-level call starts fresh.
            if not stack:
                if outputfile is not None:
                    _render(nodes, outputfile)
                counter[0] = 0
                del nodes[:]
                seen.clear()

    # Follow the __wrapped__ chain (functools.lru_cache and friends
    # expose the function they wrap this way) down to the underlying
    # function whose code contains the recursive calls.
    code_f = f
    while not hasattr(code_f, '__code__') and hasattr(code_f, '__wrapped__'):
        code_f = code_f.__wrapped__

    # Duplicate code_f with a private copy of its globals in which its
    # own name points at the wrapper.  Recursive calls inside the body
    # then reach the wrapper, while the original module's globals stay
    # untouched.
    g = dict(code_f.__globals__)
    g[code_f.__name__] = wrapper
    code_copy = types.FunctionType(
        code_f.__code__, g, code_f.__name__,
        code_f.__defaults__, code_f.__closure__,
    )
    code_copy.__kwdefaults__ = code_f.__kwdefaults__

    # Rebuild any outer wrapper (e.g. functools.lru_cache) on top of
    # the copy, so that calls from the wrapper go through it.
    if code_f is f:
        traced_f = code_copy
    elif hasattr(f, 'cache_info'):
        traced_f = functools.lru_cache(code_copy)
    else:
        traced_f = code_copy

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


def _render(nodes, outputfile):
    '''
    Write the tree as DOT source and, for a .png name, a PNG too.

    If outputfile ends in .png, the DOT source is written to the
    matching .dot file and the `dot` program is run with
    subprocess.run to produce the picture; otherwise outputfile is
    itself the DOT file.
    '''
    base, ext = os.path.splitext(outputfile)
    dotfile = base + '.dot' if ext == '.png' else outputfile
    _write_dot(nodes, dotfile)
    if ext == '.png':
        subprocess.run(['dot', '-Tpng', dotfile, '-o', outputfile], check=True)


def _write_dot(nodes, dotfile):
    '''
    Write a list of (node_id, label, parent_id, duplicate) tuples as DOT.

    Duplicate calls (where duplicate is true) are filled light blue;
    the first call with a given set of arguments stays white.

    The DOT language is a small text format, so we format it by hand
    instead of pulling in the graphviz library.  The resulting file
    can be rendered by any of the graphviz layout programs:

        $ dot -Tpng fib.dot -o fib.png
    '''
    lines = ['digraph {']
    lines.append('    node [shape=box fontname="Courier" fontsize="10"]')
    for node_id, label, parent, dup in nodes:
        attrs = 'label="{}"'.format(_escape(label))
        if dup:
            attrs += ' fillcolor="lightblue" style="filled"'
        lines.append('    {} [{}]'.format(node_id, attrs))
    for node_id, label, parent, dup in nodes:
        if parent is not None:
            lines.append('    {} -> {}'.format(parent, node_id))
    lines.append('}')
    with open(dotfile, 'w') as fp:
        fp.write('\n'.join(lines) + '\n')
