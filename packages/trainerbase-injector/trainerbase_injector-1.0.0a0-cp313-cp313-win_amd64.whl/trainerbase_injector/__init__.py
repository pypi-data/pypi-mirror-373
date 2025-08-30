from .api import (
    inject,
    attach,
    PyInjectorError,
    LibraryNotFoundException,
    InjectorError,
)

from types import ModuleType


def legacy_trainerbase_injector_import():
    # A truly disgusting hack to cover for an import mistake in hypno<1.0.1
    from sys import modules

    trainerbase_injector = ModuleType("trainerbase_injector.trainerbase_injector")
    trainerbase_injector.__package__ = "trainerbase_injector"
    trainerbase_injector.InjectorError = InjectorError
    modules[trainerbase_injector.__name__] = trainerbase_injector


legacy_trainerbase_injector_import()

__all__ = [
    "inject",
    "attach",
    "PyInjectorError",
    "LibraryNotFoundException",
    "InjectorError",
]
