"""Utilities for loading `plugins' from python namespace and entrypoints"""

import importlib
import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

import inspect
import logging
import pkgutil
import types
import typing

log = logging.getLogger(__name__)


def flatten(lst):
    """Flatten a  list of lists
    Args:
      lst
    Returns:
      flatted list
    """
    for i in lst:
        if isinstance(i, list):
            yield from flatten(i)
        else:
            yield i


def iter_namespace(ns_pkg):
    """Iterate all entities in a python namespace
    Notes:
       https://docs.python.org/3/library/importlib.html
    Args:
      ns_pkg: is a dotted str ('package.plugins') or an imported namespace import package.plugins
    Returns:
      A list of (finder_class , module:types.ModuleType, is_pkg: bool)
    """
    if isinstance(ns_pkg, str):
        ns_pkg = importlib.import_module(ns_pkg)
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def find_plugins(module_ns: str, filter_plugins: typing.Callable = None, entry_point: str = None):
    """Find and load plugins in modules

    Default mode load module at a specific module path i.e. bq.service.plugins
    which will load each submodules at the path (bq.service.plugins.module_1, ...)

    If provided, filter_plugins is a callable that can take (name, module) and return
    a list of (name, Object) which are the plugins. Since each module may define
    more than one plugin (could be a set of classes or callables in the module)


    entry_point is a string for loading modules using setuptools entry_points
    Entrypoints are created using package metadata (see https://packaging.python.org/en/latest/specifications/entry-points/)

    Notes:
      Example filter for finding classes with a class attribute 'method'
      def transfer_plugins(name, module):
          "Filter for transfer plugins modules for classes with method attribute (signature)"
          return [(obj.method, obj) for name, obj in inspect.getmembers(module)
                if inspect.isclass(obj) and hasattr(obj, "method")]

    Args:
      Module: str i.e. "bq.service.plugins"  (A namespace package)
      entry_point: (load setuptools entrypoints
      filter_plugins : Callable (name:str,  module: module )  --> list of plugins i.e. classes, callables

    Returns:
       A list of plugins: modules, classes, callables

    Examples:
       find_plugins("my.package.plugins") -> dict of  modules in my.package.plugins
       find_plugins(".plugins", filter_classes)  dict classes in modules in relative .plugins
       find_plugins(".plugins", lambda nm, md: [ (n, fct) for n,fct in filter_functions(nm,md) if n.endswith("_plugin")])
                    dict of function in modules that are like def *_plugin (...) :

    """
    if module_ns.startswith("."):  # Relative import
        frm = inspect.stack()[1]
        module_info = inspect.getmodule(frm[0])
        if module_info:
            package, module = module_info.__name__.rsplit(".", 1)
            if module_ns == ".":
                module_ns = ""
            module_ns = package + module_ns

    def safe_import(name):
        try:
            return importlib.import_module(name)
        except (ImportError, ModuleNotFoundError) as exc:
            log.warn('Failed to import %s because "%s"', name, exc)
        except Exception:
            log.exception("while importing %s", name)

    modules = {name: safe_import(name) for finder, name, ispkg in iter_namespace(module_ns)}
    plugins = {}
    if filter_plugins:
        plugins.update(flatten(filter_plugins(name, value) for name, value in modules.items()))
    else:
        plugins.update(dict(modules.items()))

    if entry_point is not None:
        entry_plugins = entry_points(group=entry_point)
        # log.debug("Loading %s -> %s", entry_point, entry_plugins)
        if filter_plugins:
            plugins.update(flatten(filter_plugins(ep.name, ep.load()) for ep in entry_plugins))
        else:
            plugins.update({ep.name: ep.load() for ep in entry_plugins})

    return plugins


def filter_classes(name: str, module: types.ModuleType):
    """Filter module contents for classes"""
    return [(cls.__name__, cls) for name, cls in inspect.getmembers(module, inspect.isclass)]


def filter_functions(name: str, module: types.ModuleType):
    """Filter module contents for classes"""
    return [(name, fct) for name, fct in inspect.getmembers(module, inspect.isfunction)]
