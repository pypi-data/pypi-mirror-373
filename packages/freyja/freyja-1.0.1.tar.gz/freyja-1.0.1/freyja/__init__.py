"""
Freyja: Zero-configuration FreyjaCLI generator from classes/module introspection.
Uses class/method/function introspection, typehints, and docstrings to build
a fully functional FreyjaCLI.  Command groups can be made with inner-classes,
effectively making subclasses.
"""
from .freyja_cli import FreyjaCLI
__all__ = [FreyjaCLI]
