# textom/src/__init__.py
import pkgutil
import importlib

# Dynamically import all submodules and expose their contents
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    for name in dir(module):
        if not name.startswith("_"):  # Skip private attributes
            globals()[name] = getattr(module, name)
            __all__.append(name)

