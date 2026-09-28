"""Backends package"""
import importlib
import inspect
import pkgutil

__all__ = []

for _, module_name, _ in pkgutil.iter_modules(__path__):
    # Salta moduli privati o __init__
    if module_name.startswith("_"):
        continue

    module = importlib.import_module(f"{__name__}.{module_name}")

    # Trova tutte le classi definite DIRETTAMENTE in quel file (ignora quelle importate)
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            globals()[name] = obj
            __all__.append(name)