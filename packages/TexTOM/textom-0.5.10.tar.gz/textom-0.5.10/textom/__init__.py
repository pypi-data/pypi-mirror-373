# textom/__init__.py
import pkgutil
import importlib
from .version import __version__
import psutil

__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if module_name == 'textom':  # Restrict to the textom module
        module = importlib.import_module(f"{__name__}.{module_name}")
        for name in dir(module):
            if not name.startswith("_"):  # Skip private attributes
                globals()[name] = getattr(module, name)
                __all__.append(name)

# Optional: Set package metadata
__author__ = "Moritz Frewein"
__email__ = "textom@fresnel.fr"

# initialize numba
import os
from numba import set_num_threads
from .config import n_threads
n_threads = min(psutil.cpu_count(), n_threads) # make sure the number of threads doesn't exceed the possible ones
set_num_threads(n_threads)
