import sys
import inspect

is_debugger = sys.gettrace() is not None


def class_vars(cls):
    """Return the class variables of a class."""
    all_vars = dict()
    for name in dir(cls):
        # Filter out magic methods
        if name.startswith('__'):
            continue
        try:
            attr = getattr(cls, name)
            # Check if it's a property or variable
            if not inspect.ismethod(attr) and not inspect.isfunction(attr):
                all_vars[name] = attr
        except Exception:
            pass
    return all_vars


def is_notebook():
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
        return False
    except ImportError:
        return False
