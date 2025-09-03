import enum


class TargetMode(enum.Enum):
    """Target mode enum for command discovery."""
    MODULE = 'module'
    CLASS = 'class'
