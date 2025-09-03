import inspect
from typing import Dict, Type, List, Tuple, Optional, Any

"""Multi-class FreyjaCLI command handling and collision detection.

Provides services for managing cmd_tree from multiple classes in a single FreyjaCLI,
including collision detection, command ordering, and source tracking.
"""



class ClassHandler:
  """Handles cmd_tree from multiple classes with collision detection and ordering."""

  def __init__(self):
    """Initialize multi-class handler."""
    self.command_sources: Dict[str, Type] = {}  # command_name -> source_class
    self.class_commands: Dict[Type, List[str]] = {}  # source_class -> [command_names]
    self.collision_tracker: Dict[str, List[Type]] = {}  # command_name -> [source_classes]

  def track_command(self, command_name: str, source_class: Type) -> None:
    """
    Track a command and its source class for collision detection.

    :param command_name: FreyjaCLI command name (e.g., 'file-operations--process-single')
    :param source_class: Source class that defines this command
    """
    # Track which class this command comes from
    if command_name in self.command_sources:
      # Collision detected - track all sources
      if command_name not in self.collision_tracker:
        self.collision_tracker[command_name] = [self.command_sources[command_name]]
      self.collision_tracker[command_name].append(source_class)
    else:
      self.command_sources[command_name] = source_class

    # Track cmd_tree per class for ordering
    if source_class not in self.class_commands:
      self.class_commands[source_class] = []
    self.class_commands[source_class].append(command_name)

  def detect_collisions(self) -> List[Tuple[str, List[Type]]]:
    """
    Detect and return command name collisions.

    :return: List of (command_name, [conflicting_classes]) tuples
    """
    return [(cmd, classes) for cmd, classes in self.collision_tracker.items()]

  def has_collisions(self) -> bool:
    """
    Check if any command name collisions exist.

    :return: True if collisions detected, False otherwise
    """
    return len(self.collision_tracker) > 0

  def get_ordered_commands(self, class_order: List[Type]) -> List[str]:
    """
    Get cmd_tree ordered by class sequence, then alphabetically within each class.

    :param class_order: Desired order of classes
    :return: List of command names in proper order
    """
    ordered_commands = []

    # Process classes in the specified order
    for cls in class_order:
      if cls in self.class_commands:
        # Sort cmd_tree within this class alphabetically
        class_commands = sorted(self.class_commands[cls])
        ordered_commands.extend(class_commands)

    return ordered_commands

  def get_command_source(self, command_name: str) -> Optional[Type]:
    """
    Get the source class for a command.

    :param command_name: FreyjaCLI command name
    :return: Source class or None if not found
    """
    return self.command_sources.get(command_name)

  def format_collision_error(self) -> str:
    """
    Format collision error message for user display.

    :return: Formatted error message describing all collisions
    """
    if not self.has_collisions():
      return ""

    error_lines = ["Command name collisions detected:"]

    for command_name, conflicting_classes in self.collision_tracker.items():
      class_names = [cls.__name__ for cls in conflicting_classes]
      error_lines.append(f"  '{command_name}' conflicts between: {', '.join(class_names)}")

    error_lines.append("")
    error_lines.append("Solutions:")
    error_lines.append("1. Rename methods in one of the conflicting classes")
    error_lines.append("2. Use different inner class names to create unique command paths")
    error_lines.append("3. Use separate FreyjaCLI instances for conflicting classes")

    return "\n".join(error_lines)

  def validate_classes(self, classes: List[Type]) -> None:
    """Validate that classes can be used together without collisions.

    :param classes: List of classes to validate
    :raises ValueError: If command collisions are detected"""
    # Simulate command discovery to detect collisions
    temp_handler = ClassHandler()

    for cls in classes:
      # Simulate the command discovery process
      self._simulate_class_commands(temp_handler, cls)

    # Check for collisions
    if temp_handler.has_collisions():
      raise ValueError(temp_handler.format_collision_error())

  def _simulate_class_commands(self, handler: 'ClassHandler', cls: Type) -> None:
    """Simulate command discovery for collision detection.

    :param handler: Handler to track cmd_tree in
    :param cls: Class to simulate cmd_tree for"""
    from freyja.utils.text_util import TextUtil

    # Check for inner classes (hierarchical cmd_tree)
    inner_classes = self._discover_inner_classes(cls)

    if inner_classes:
      # Inner class pattern - track both direct methods and inner class methods
      # Direct methods
      for name, obj in inspect.getmembers(cls):
        if self._is_valid_method(name, obj, cls):
          cli_name = TextUtil.kebab_case(name)
          handler.track_command(cli_name, cls)

      # Inner class methods
      for class_name, inner_class in inner_classes.items():
        command_name = TextUtil.kebab_case(class_name)

        for method_name, method_obj in inspect.getmembers(inner_class):
          if (not method_name.startswith('_') and
              callable(method_obj) and
              method_name != '__init__' and
              inspect.isfunction(method_obj)):
            # Create hierarchical command name
            cli_name = f"{command_name}--{TextUtil.kebab_case(method_name)}"
            handler.track_command(cli_name, cls)
    else:
      # Direct methods only
      for name, obj in inspect.getmembers(cls):
        if self._is_valid_method(name, obj, cls):
          cli_name = TextUtil.kebab_case(name)
          handler.track_command(cli_name, cls)

  def _discover_inner_classes(self, cls: Type) -> Dict[str, Type]:
    """Discover inner classes for a given class.

    :param cls: Class to check for inner classes
    :return: Dictionary of inner class name -> inner class"""
    inner_classes = {}

    for name, obj in inspect.getmembers(cls):
      if (inspect.isclass(obj) and
          not name.startswith('_') and
          obj.__qualname__.endswith(f'{cls.__name__}.{name}')):
        inner_classes[name] = obj

    return inner_classes

  def _is_valid_method(self, name: str, obj: Any, cls: Type) -> bool:
    """Check if a method should be included as a FreyjaCLI command.

    :param name: Method name
    :param obj: Method object
    :param cls: Containing class
    :return: True if method should be included"""
    return (
        not name.startswith('_') and
        callable(obj) and
        (inspect.isfunction(obj) or inspect.ismethod(obj)) and
        hasattr(obj, '__qualname__') and
        cls.__name__ in obj.__qualname__
    )
