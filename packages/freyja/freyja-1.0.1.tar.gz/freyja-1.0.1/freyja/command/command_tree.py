"""Command tree structure for FreyjaCLI applications.

Provides a hierarchical command structure with convenience methods for efficient lookups.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Type

from freyja.utils import TextUtil
from .command_info import CommandInfo


@dataclass
class CommandTree:
  """
  Hierarchical command tree structure with convenience methods.

  Encapsulates the command tree dictionary and provides efficient lookup methods
  for cmd_tree, groups, and source classes.
  """

  tree: Dict[str, Dict[str, Any]] = field(default_factory=dict)
  _command_info_lookup: Dict[str, CommandInfo] = field(default_factory=dict, init=False)

  def __post_init__(self):
    """Initialize lookup structures after creation."""
    self._build_lookup_tables()

  # def __str__(self) -> str:
  #   """Format command tree"""
  #   print("GEtgingins itQ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
  #   return TextUtil.format_pretty("CommandTree: {tree}", tree=str(self.tree))

  def _build_lookup_tables(self):
    """Build internal lookup tables for efficient access."""
    self._command_info_lookup.clear()
    self._build_command_lookup(self.tree)

  def _build_command_lookup(self, tree_dict: Dict[str, Any], prefix: str = ""):
    """Recursively build command lookup table."""
    for name, info in tree_dict.items():
      full_name = f"{prefix}{name}" if prefix else name

      if info.get('type') == 'command' and 'command_info' in info:
        command_info = info['command_info']
        self._command_info_lookup[full_name] = command_info
        # Also add original name for lookup
        if original_name := info.get('original_name'):
          self._command_info_lookup[original_name] = command_info

      elif info.get('type') == 'group' and 'cmd_tree' in info:
        # Recursively process group cmd_tree
        self._build_command_lookup(info['cmd_tree'], f"{name} ")

  def add_command(self, name: str, command_info: CommandInfo, **kwargs):
    """Add a flat command to the tree."""
    self.tree[name] = {
      'type': 'command',
      'function': command_info.function,
      'original_name': command_info.original_name,
      'command_info': command_info,
      **kwargs
    }
    # Update lookup table
    self._command_info_lookup[name] = command_info
    if command_info.original_name != name:
      self._command_info_lookup[command_info.original_name] = command_info

  def add_group(self, group_name: str, description: str, inner_class: Optional[Type] = None, **kwargs):
    """Add a command group to the tree."""
    self.tree[group_name] = {
      'type': 'group',
      'description': description,
      'cmd_tree': {},
      'inner_class': inner_class,
      **kwargs
    }

  def add_command_to_group(self, group_name: str, command_name: str, command_info: CommandInfo, **kwargs):
    """Add a command to a specific group."""
    if group_name not in self.tree:
      raise ValueError(f"Group '{group_name}' not found")

    if self.tree[group_name].get('type') != 'group':
      raise ValueError(f"'{group_name}' is not a group")

    self.tree[group_name]['cmd_tree'][command_name] = {
      'type': 'command',
      'function': command_info.function,
      'original_name': command_info.original_name,
      'group_name': group_name,
      'command_info': command_info,
      **kwargs
    }

    # Update lookup table with full path
    full_name = f"{group_name} {command_name}"
    self._command_info_lookup[full_name] = command_info
    self._command_info_lookup[command_name] = command_info
    if command_info.original_name != command_name:
      self._command_info_lookup[command_info.original_name] = command_info

  def add_subgroup_to_group(self, parent_group_name: str, subgroup_name: str, description: str, inner_class: Optional[Type] = None,
                            **kwargs):
    """Add a subgroup to an existing group."""
    if parent_group_name not in self.tree:
      raise ValueError(f"Parent group '{parent_group_name}' not found")

    if self.tree[parent_group_name].get('type') != 'group':
      raise ValueError(f"'{parent_group_name}' is not a group")

    self.tree[parent_group_name]['cmd_tree'][subgroup_name] = {
      'type': 'group',
      'description': description,
      'cmd_tree': {},
      'inner_class': inner_class,
      **kwargs
    }

  def add_command_to_subgroup(self, parent_group_name: str, subgroup_name: str, command_name: str, command_info: CommandInfo, **kwargs):
    """Add a command to a subgroup within a parent group."""
    if parent_group_name not in self.tree:
      raise ValueError(f"Parent group '{parent_group_name}' not found")

    parent_group = self.tree[parent_group_name]
    if parent_group.get('type') != 'group':
      raise ValueError(f"'{parent_group_name}' is not a group")

    if subgroup_name not in parent_group['cmd_tree']:
      raise ValueError(f"Subgroup '{subgroup_name}' not found in '{parent_group_name}'")

    subgroup = parent_group['cmd_tree'][subgroup_name]
    if subgroup.get('type') != 'group':
      raise ValueError(f"'{subgroup_name}' is not a subgroup")

    subgroup['cmd_tree'][command_name] = {
      'type': 'command',
      'function': command_info.function,
      'original_name': command_info.original_name,
      'group_name': f"{parent_group_name}.{subgroup_name}",
      'command_info': command_info,
      **kwargs
    }

    # Update lookup table with full hierarchical path
    full_name = f"{parent_group_name} {subgroup_name} {command_name}"
    self._command_info_lookup[full_name] = command_info
    self._command_info_lookup[command_name] = command_info
    if command_info.original_name != command_name:
      self._command_info_lookup[command_info.original_name] = command_info

  def get_command(self, name: str) -> Optional[Dict[str, Any]]:
    """Get a command by name (supports both flat and hierarchical lookups)."""
    # Try direct lookup first
    if name in self.tree and self.tree[name].get('type') == 'command':
      return self.tree[name]

    # Try hierarchical lookup (group command)
    for group_name, group_info in self.tree.items():
      if group_info.get('type') == 'group' and 'cmd_tree' in group_info:
        if name in group_info['cmd_tree']:
          return group_info['cmd_tree'][name]

    return None

  def get_group(self, name: str) -> Optional[Dict[str, Any]]:
    """Get a command group by name."""
    if name in self.tree and self.tree[name].get('type') == 'group':
      return self.tree[name]
    return None

  def get_all_commands(self) -> List[CommandInfo]:
    """Get a flat list of all CommandInfo objects."""
    # Use a set to deduplicate CommandInfo objects (they should be unique by identity)
    seen = set()
    unique_commands = []
    for command_info in self._command_info_lookup.values():
      if id(command_info) not in seen:
        seen.add(id(command_info))
        unique_commands.append(command_info)
    return unique_commands

  def find_command_by_function(self, func_name: str) -> Optional[CommandInfo]:
    """Find a command by function name."""
    # Try exact matches first
    if func_name in self._command_info_lookup:
      return self._command_info_lookup[func_name]

    # Try partial matches (for hierarchical cmd_tree)
    for name, command_info in self._command_info_lookup.items():
      if (command_info.original_name == func_name or
          command_info.name == func_name or
          name.endswith(f" {func_name}") or
          name.endswith(f"--{func_name}")):
        return command_info

    return None

  def find_source_class(self, func_name: str) -> Optional[Type]:
    """Find the source class for a function name."""
    command_info = self.find_command_by_function(func_name)
    if command_info:
      return command_info.metadata.get('source_class')
    return None

  def to_dict(self) -> Dict[str, Dict[str, Any]]:
    """Return the raw hierarchical dictionary."""
    return self.tree

  def keys(self):
    """Return keys from the tree (for dict-like interface)."""
    return self.tree.keys()

  def __str__(self):
    return TextUtil.json_pretty(self.tree)

  def __getitem__(self, key: str):
    """Allow dict-like access to the tree."""
    return self.tree[key]

  def __contains__(self, key: str):
    """Check if key exists in the tree."""
    return key in self.tree

  def __len__(self):
    """Return the number of top-level items in the tree."""
    return len(self.tree)

  def __iter__(self):
    """Iterate over the tree keys."""
    return iter(self.tree)
