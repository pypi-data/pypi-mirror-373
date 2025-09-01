todo
====

* 支持更多特性.
def script_path():
    import inspect
    this_file = inspect.getfile(inspect.currentframe())
    return os.path.abspath(os.path.dirname(this_file)).replace('\\','/')