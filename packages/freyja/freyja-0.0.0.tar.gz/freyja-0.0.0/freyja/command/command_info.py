import inspect
from dataclasses import dataclass, field
from typing import Callable as CallableABC, Optional, Type, Dict, Any


@dataclass
class CommandInfo:
  """Information about a discovered command."""
  name: str
  original_name: str
  function: CallableABC
  signature: inspect.Signature
  docstring: Optional[str] = None
  is_hierarchical: bool = False
  parent_class: Optional[str] = None
  command_path: Optional[str] = None
  is_system_command: bool = False
  inner_class: Optional[Type] = None
  metadata: Dict[str, Any] = field(default_factory=dict)
  # New fields for nested command structure
  group_name: Optional[str] = None  # For hierarchical cmd_tree (kebab-cased inner class name)
  method_name: Optional[str] = None  # For hierarchical cmd_tree (kebab-cased method name)
