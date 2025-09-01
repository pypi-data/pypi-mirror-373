from importlib import import_module


def load_class(path, package=None):
    """Load class by path

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.
    """
    module_name, class_name = path.rsplit(".", 1)
    module = import_module(module_name, package)
    class_ref = getattr(module, class_name, None)
    if not class_ref:
        raise ImportError()
    return class_ref
