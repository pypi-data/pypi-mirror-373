# Command discovery functionality extracted from FreyjaCLI class.
import inspect
from types import ModuleType
from typing import *

from freyja.cli import TargetMode, SystemClassBuilder
from freyja.utils import TextUtil
from freyja.parser import DocStringParser
from .command_info import CommandInfo
from .command_tree import CommandTree
from .validation import ValidationService

TargetType = ModuleType | type | list[type]


class CommandDiscovery:
  """
  Discovers cmd_tree from modules or classes using introspection.

  Handles both flat command structures (direct functions/methods) and
  hierarchical structures (inner classes with methods).
  """

  def __init__(
      self,
      target: TargetType,
      function_filter: Optional[Callable[[str, Any], bool]] = None,
      method_filter: Optional[Callable[[type, str, Any], bool]] = None,
      completion: bool = True,
      theme_tuner: bool = False
  ):
    """
    Initialize command discovery.

    :param target: Module, class, or list of classes to discover from
    :param function_filter: Optional filter for module functions
    :param method_filter: Optional filter for class methods
    """
    self.target = target
    self.function_filter = function_filter or self._default_function_filter
    self.method_filter = method_filter or self._default_method_filter

    self.completion: bool = completion
    self.theme_tuner: bool = theme_tuner

    self.target_classes: Optional[list[type]] = None
    self.target_module: Optional[ModuleType] = None
    self.mode: TargetMode = TargetMode.CLASS
    self.primary_class: Optional[type] = None

    # Determine target mode with unified class handling
    if isinstance(target, list):
      self.target_classes = target
      self._validate_classes(self.target_classes)
      self.primary_class = self.target_classes[-1]
    elif inspect.isclass(target):
      self.primary_class = target
      self.target_classes = [target]
    elif inspect.ismodule(target):
      self.mode = TargetMode.MODULE
      self.target_module = target
    else:
      raise ValueError(f"Target must be module, class, or list of classes, got {type(target).__name__}")

    self.cmd_tree:CommandTree = self.discover_commands()
    print(self.cmd_tree)

  def discover_commands(self) -> CommandTree:
    """
    Discover all cmd_tree from the target.

    :return: CommandTree with hierarchical command structure
    """
    # Import CommandTree here to avoid circular imports
    command_tree:CommandTree = CommandTree()

    if self.mode == TargetMode.MODULE:
      self._discover_from_module(command_tree)
    elif self.mode == TargetMode.CLASS:
      # Unified class handling: always use multi-class logic for consistency
      self.discover_classes(command_tree)

    return command_tree

  def _discover_from_module(self, command_tree) -> None:
    """Discover functions from a module and add to command tree."""
    for name, obj in inspect.getmembers(self.target_module):
      if self.function_filter(name, obj):
        command_info = CommandInfo(
          name=TextUtil.kebab_case(name),
          original_name=name,
          function=obj,
          signature=inspect.signature(obj),
          docstring=inspect.getdoc(obj)
        )
        command_tree.add_command(command_info.name, command_info)

  def _discover_from_class(self, target_cls: type, command_tree, is_namespaced: bool = False) -> None:
    """Discover methods from a single class and add to command tree."""
    # Check for inner classes first (hierarchical pattern)
    inner_classes = self._discover_inner_classes(target_cls)

    if inner_classes:
      # Mixed pattern: direct methods + inner class methods
      ValidationService.validate_constructor_parameters(
        target_cls, "main class"
      )

      # Validate inner class constructors
      for class_name, inner_class in inner_classes.items():
        ValidationService.validate_inner_class_constructor_parameters(
          inner_class, f"inner class '{class_name}'"
        )
    else:
      # Direct methods only (flat pattern)
      ValidationService.validate_constructor_parameters(
        target_cls, "class", allow_parameterless_only=True
      )

    # Create top-level group for namespaced classes (whether they have inner classes or not)
    if is_namespaced:
      class_namespace = TextUtil.kebab_case(target_cls.__name__)
      class_description = self._get_class_description(target_cls)
      command_tree.add_group(
        class_namespace, 
        class_description,
        is_system_command=self.is_system(target_cls)
      )

    # Discover direct methods
    self._discover_direct_methods(target_cls, command_tree, is_namespaced)

    # Discover inner class methods (if any)
    if inner_classes:
      self._discover_methods_from_inner_classes(target_cls, inner_classes, command_tree, is_namespaced)

  @staticmethod
  def _validate_classes(targets: list[type]) -> None:
    if not targets:
      raise ValueError("Passed a list, but no target classes were found.")

    if invalid_items := [item for item in targets if not isinstance(item, type)]:
      invalid_type = type(invalid_items[0]).__name__
      raise ValueError(f"All items in list must be classes, got {invalid_type}")

  def discover_classes(self, command_tree) -> None:
    """Discover methods from classes (single or multiple) and add to command tree.
    
    For single class: methods get no namespace prefix (global namespace).
    For multiple classes: last class gets global namespace, others get kebab-cased class name prefixes.
    """
    if self.completion or self.theme_tuner:
      System = SystemClassBuilder.build(self.completion, self.theme_tuner)
      self.target_classes.insert(0, System)  # SystemClassBuilder.build(self.completion, self.theme_tuner))

    # Separate last class (global) from others (namespaced)
    namespaced_classes = self.target_classes[:-1] if len(self.target_classes) > 1 else []

    # Process namespaced classes first (with class name prefixes)
    for target_class in namespaced_classes:
      # Discover cmd_tree for this class and add to tree
      self._discover_from_class(target_class, command_tree, is_namespaced=True)

    # Discover cmd_tree for primary class (no namespace)
    self._discover_from_class(self.primary_class, command_tree, is_namespaced=False)

  def _discover_inner_classes(self, target_class: Type) -> Dict[str, Type]:
    """Discover inner classes that should be treated as command groups."""
    inner_classes = {}

    for name, obj in inspect.getmembers(target_class):
      if (inspect.isclass(obj) and not name.startswith('_')):  # and obj.__qualname__.endswith(f'{target_class.__name__}.{name}')):
        inner_classes[name] = obj

    return inner_classes

  def _discover_direct_methods(self, target_class, command_tree, is_namespaced: bool = False) -> None:
    """Discover methods directly from the target class and add to command tree."""
    for name, obj in inspect.getmembers(target_class):
      if self.method_filter(target_class, name, obj):
        command_info = CommandInfo(
          name=TextUtil.kebab_case(name),
          original_name=name,
          function=obj,
          signature=inspect.signature(obj),
          docstring=inspect.getdoc(obj)
        )
        
        # Add metadata for execution
        command_info.metadata['source_class'] = target_class
        command_info.metadata['is_namespaced'] = is_namespaced
        if is_namespaced:
          command_info.metadata['class_namespace'] = TextUtil.kebab_case(target_class.__name__)
          # Add command to the parent class group
          class_namespace = TextUtil.kebab_case(target_class.__name__)
          command_tree.add_command_to_group(class_namespace, command_info.name, command_info)
        else:
          command_info.metadata['class_namespace'] = None
          command_tree.add_command(command_info.name, command_info)

  def _discover_methods_from_inner_classes(self, target_cls: type, inner_classes: Dict[str, Type], command_tree, is_namespaced: bool = False) -> None:
    """Discover methods from inner classes for hierarchical cmd_tree and add to tree."""
    for class_name, inner_class in inner_classes.items():
      command_name = TextUtil.kebab_case(class_name)
      
      # Get group description from inner class docstring
      description = self._get_group_description(inner_class, command_name)
      
      if is_namespaced:
        # Create subgroup under the parent class group
        class_namespace = TextUtil.kebab_case(target_cls.__name__)
        command_tree.add_subgroup_to_group(
          class_namespace,
          command_name, 
          description,
          inner_class=inner_class,
          is_system_command=self.is_system(target_cls)
        )
        full_group_path = f"{class_namespace}.{command_name}"
      else:
        # Create top-level group
        command_tree.add_group(
          command_name, 
          description,
          inner_class=inner_class,
          is_system_command=self.is_system(target_cls)
        )
        full_group_path = command_name

      for method_name, method_obj in inspect.getmembers(inner_class):
        if (not method_name.startswith('_') and
            callable(method_obj) and
            method_name != '__init__' and
            inspect.isfunction(method_obj)):
          # Use kebab-cased method name as command name (no dunder notation)
          method_kebab = TextUtil.kebab_case(method_name)

          command_info = CommandInfo(
            name=method_kebab,  # Just the method name, not group__method
            original_name=method_name,
            function=method_obj,
            signature=inspect.signature(method_obj),
            docstring=inspect.getdoc(method_obj),
            is_hierarchical=True,
            parent_class=class_name,
            command_path=full_group_path,
            inner_class=inner_class,
            is_system_command=self.is_system(target_cls),
            group_name=command_name,  # Just the inner class name
            method_name=method_kebab  # Kebab-cased method name
          )

          # Store metadata for execution
          command_info.metadata.update({
            'inner_class': inner_class,
            'inner_class_name': class_name,
            'command_name': command_name,
            'method_name': method_name,
            'source_class': target_cls,
            'is_namespaced': is_namespaced
          })
          
          if is_namespaced:
            command_info.metadata['class_namespace'] = TextUtil.kebab_case(target_cls.__name__)
            # Add command to subgroup
            command_tree.add_command_to_subgroup(
              TextUtil.kebab_case(target_cls.__name__),
              command_name,
              method_kebab, 
              command_info,
              method_name=method_kebab
            )
          else:
            command_info.metadata['class_namespace'] = None
            # Add command to top-level group
            command_tree.add_command_to_group(
              command_name, 
              method_kebab, 
              command_info,
              method_name=method_kebab
            )
          
  def _get_group_description(self, inner_class: type, group_name: str) -> str:
    """Get description for command group from inner class docstring."""
    if inner_class and inner_class.__doc__:
      from freyja.parser import DocStringParser
      description, _ = DocStringParser.parse_docstring(inner_class.__doc__)
      return description
    
    # Fallback to generating description from group name
    return f"{group_name.title().replace('-', ' ')} operations"

  def _get_class_description(self, target_cls: type) -> str:
    """Get description for class group from class docstring."""
    if target_cls and target_cls.__doc__:
      description, _ = DocStringParser.parse_docstring(target_cls.__doc__)
      return description
    
    # Fallback to generating description from class name
    class_name = TextUtil.kebab_case(target_cls.__name__)
    return f"{class_name.title().replace('-', ' ')} cmd_tree and utilities"

  def is_system(self, cls: type) -> bool:
    return cls.__name__ == 'System'

  def _default_function_filter(self, name: str, obj: Any) -> bool:
    """Default filter for module functions."""
    if self.target_module is None:
      return False
    
    if name.startswith('_'):
      return False
    
    if not callable(obj) or inspect.isclass(obj) or not inspect.isfunction(obj):
      return False
    
    # Exclude imported functions
    return obj.__module__ == self.target_module.__name__

  def _default_method_filter(self, target_class: type, name: str, obj: Any) -> bool:
    """Default filter for class methods."""
    if target_class is None:
      return False
    
    if name.startswith('_'):
      return False
    
    if not callable(obj):
      return False
    
    if not (inspect.isfunction(obj) or inspect.ismethod(obj)):
      return False
    
    if not hasattr(obj, '__qualname__'):
      return False
    
    return target_class.__name__ in obj.__qualname__

  def generate_title(self) -> str:
    """Generate FreyjaCLI title based on target type."""
    if self.mode == TargetMode.MODULE and hasattr(self.target_module, '__name__'):
      module_name = self.target_module.__name__.split('.')[-1]
      return f"{module_name.title()} FreyjaCLI"
    
    if self.mode == TargetMode.CLASS and self.primary_class:
      if self.primary_class.__doc__:
        main_desc, _ = DocStringParser.parse_docstring(self.primary_class.__doc__)
        return main_desc or self.primary_class.__name__
      return self.primary_class.__name__
    
    return "FreyjaCLI Application"
