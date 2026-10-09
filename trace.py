'''
The trace functions write the recursion tree of a function to a picture.

Unlike a decorator, these functions do not return a new function for
you to assign; they *modify* the function that you pass to them.
Python resolves the name of a recursive function in the globals of the
module that defines it every time the function makes a recursive call,
so rebinding that one name is enough to route every recursive call
through a wrapper:

    >>> from recurrences import merge_sorted
    >>> add_trace(merge_sorted)
    >>> merge_sorted([2, 1])
    merge_sorted([2, 1])
      merge_sorted([2])
      merge_sorted([1])
    [1, 2]

The change lasts for the rest of the python session.  There is no
remove_trace; to get the original function back you must restart the
interpreter.

Each traced function keeps its own state in the closure of its
wrapper, so tracing several functions at the same time is fine.

Run the doctests with:

    $ python3 -m doctest trace.py
'''
import functools
import os
import subprocess
import sys


def add_trace(f):
    '''
    Modify f so that it prints a picture of its call tree.

    Every call is printed on its own line, indented by the depth of
    the call stack at the moment the call was made.  The tree is
    printed when the outermost call returns, just before that call
    returns its value.

    >>> from recurrences import merge_sorted
    >>> add_trace(merge_sorted)
    >>> merge_sorted([2, 1])
    merge_sorted([2, 1])
      merge_sorted([2])
      merge_sorted([1])
    [1, 2]
    '''
    _install(f, _print_tree, sys._getframe(1).f_globals)


def add_trace_png(f, outputfile):
    '''
    Modify f so that its call tree is written to outputfile.

    The tree is written as graphviz DOT source to a file with the
    same name as outputfile but with a .dot extension, and then the
    `dot` program renders that file to the PNG named by outputfile.
    '''
    def render(nodes):
        _write_png(nodes, outputfile)
    _install(f, render, sys._getframe(1).f_globals)


def _install(f, render, caller_globals):
    '''
    Replace f with a version of itself that reports its calls to render.

    f is replaced in two places.  The globals of the module that
    defines f must be updated, because that is where python looks up
    the name of a recursive function when the function calls itself.
    The caller's globals are updated too, because a function that has
    been imported into the interactive interpreter is reachable under
    the same name from there.

    If f has already been memoized with functools.lru_cache, the
    memoization is kept and the cache ends up on the outside of the
    trace, so that a call which is answered from the cache never
    reaches the trace and never appears in the picture.
    '''
    root = _root(f)
    wrapper = _wrap(root, render)
    if hasattr(f, 'cache_info') and hasattr(f, 'cache_clear'):
        wrapper = functools.lru_cache(wrapper)
    root.__globals__[root.__name__] = wrapper
    if caller_globals.get(root.__name__) is f:
        caller_globals[root.__name__] = wrapper
    return wrapper


def _root(f):
    '''
    Follow the __wrapped__ chain down to the function with the code.

    The wrappers built by functools.lru_cache and by _install both
    point at the function they wrap through __wrapped__, so walking
    the chain reaches the function whose body contains the recursive
    calls.
    '''
    while hasattr(f, '__wrapped__'):
        f = f.__wrapped__
    return f


def _wrap(f, render):
    '''
    Return a version of f that records its calls and calls render.

    render is called once, with the list of (node_id, parent_id,
    label, duplicate) tuples of the outermost call, in the order in
    which the calls were made.  That order is preorder, so a parent
    always appears before its children.
    '''
    stack = []     # node_ids of the calls that are still running
    nodes = []     # (node_id, parent_id, label, duplicate) in call order
    counter = [0]  # mutable counter of node_ids
    seen = set()   # labels of the calls that have already been made

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        node_id = counter[0]
        counter[0] += 1
        label = f.__name__ + _label(args, kwargs)
        nodes.append((node_id, stack[-1] if stack else None,
                      label, label in seen))
        seen.add(label)
        stack.append(node_id)
        try:
            return f(*args, **kwargs)
        finally:
            stack.pop()
            # When the outermost call returns, draw the tree and
            # reset the state so the next top-level call starts fresh.
            if not stack:
                render(nodes)
                counter[0] = 0
                del nodes[:]
                seen.clear()

    return wrapper


def _print_tree(nodes):
    '''
    Print a list of (node_id, parent_id, label, duplicate) tuples as
    an indented tree.

    >>> _print_tree([(0, None, 'f(2)', False),
    ...              (1, 0, 'f(1)', False),
    ...              (2, 1, 'f(0)', True)])
    f(2)
      f(1)
        f(0)
    '''
    depth = {None: -1}
    for node_id, parent_id, label, dup in nodes:
        depth[node_id] = depth[parent_id] + 1
        print('  ' * depth[node_id] + label)


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


def _write_png(nodes, outputfile):
    '''
    Write the tree as DOT source and render it with the `dot` program.

    The DOT source goes to a file with the same name as outputfile
    but with a .dot extension, and subprocess.run is used to run the
    `dot` program on it:

        $ dot -Tpng fib.dot -o fib.png

    An outputfile that does not end in .png is written as DOT source
    and nothing else happens.
    '''
    base, ext = os.path.splitext(outputfile)
    dotfile = base + '.dot' if ext == '.png' else outputfile
    _write_dot(nodes, dotfile)
    if ext == '.png':
        subprocess.run(['dot', '-Tpng', dotfile, '-o', outputfile], check=True)


def _write_dot(nodes, dotfile):
    '''
    Write a list of (node_id, parent_id, label, duplicate) tuples as
    DOT source.

    A call whose arguments have been seen before is filled light
    blue; the first call with a given set of arguments stays white.
    A blue node is a call that recomputes a value the function has
    already computed once, which is exactly the kind of call that
    memoization removes.

    The DOT language is a small text format, so we format it by hand
    instead of pulling in the graphviz library.  Any of the graphviz
    layout programs can render the result:

        $ dot -Tpng fib.dot -o fib.png
    '''
    lines = ['digraph {']
    lines.append('    node [shape=box fontname="Courier" fontsize="10"]')
    for node_id, parent_id, label, dup in nodes:
        attrs = 'label="{}"'.format(_escape(label))
        if dup:
            attrs += ' fillcolor="lightblue" style="filled"'
        lines.append('    {} [{}]'.format(node_id, attrs))
    for node_id, parent_id, label, dup in nodes:
        if parent_id is not None:
            lines.append('    {} -> {}'.format(parent_id, node_id))
    lines.append('}')
    with open(dotfile, 'w') as fp:
        fp.write('\n'.join(lines) + '\n')
