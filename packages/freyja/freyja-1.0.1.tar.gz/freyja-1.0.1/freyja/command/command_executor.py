"""Command execution service for FreyjaCLI applications.

Handles the execution of different command types (direct methods, inner class methods, module functions)
by creating appropriate instances and invoking methods with parsed arguments.
"""

import inspect
from typing import Any, Dict, Type, Optional


class CommandExecutor:
  """Centralized service for executing FreyjaCLI cmd_tree with different patterns."""

  def __init__(self, target_class: Optional[Type] = None, target_module: Optional[Any] = None):
    """Initialize command executor with target information.

    :param target_class: Class containing methods to execute (for class-based FreyjaCLI)
    :param target_module: Module containing functions to execute (for module-based FreyjaCLI)
    """
    self.target_class = target_class
    self.target_module = target_module

  def _execute_inner_class_command(self, parsed) -> Any:
    """Execute command using inner class pattern.

    Creates main class instance, inner class instance, then invokes method.
    """
    method = parsed._cli_function
    original_name = parsed._function_name
    command_path = parsed._command_path

    # Extract inner class information from the method object
    # The method qualname can be:
    # - "OuterClass.InnerClass.method_name" (normal case, 3 parts)
    # - "InnerClass.method_name" (System class case, 2 parts)
    qualname_parts = method.__qualname__.split('.')
    if len(qualname_parts) < 2:
      raise RuntimeError(f"Invalid method qualname for inner class method: {method.__qualname__}")
    
    # For both cases, the inner class name is the second-to-last part
    inner_class_name = qualname_parts[-2]  # Get the inner class name
    
    # Find the actual inner class object from the main target class
    if not hasattr(self.target_class, inner_class_name):
      raise RuntimeError(f"Inner class {inner_class_name} not found in {self.target_class.__name__}")
    
    inner_class_obj = getattr(self.target_class, inner_class_name)

    # 1. Create main class instance with global arguments
    main = self._create_main(parsed)

    # 2. Create inner class instance with sub-global arguments
    inner_instance = self._create_inner_instance(inner_class_obj, command_path, parsed, main)

    # 3. Execute method with command arguments
    return self._execute_method(inner_instance, original_name, parsed)

  def _execute_direct_method_command(self, parsed) -> Any:
    """Execute command using direct method from class.

    Creates class instance with parameterless constructor, then invokes method.
    """
    method = parsed._cli_function

    # Create class instance (requires parameterless constructor or all defaults)
    try:
      class_instance = self.target_class()
    except TypeError as e:
      raise RuntimeError(
        f"Cannot instantiate {self.target_class.__name__}: constructor parameters must have default values") from e

    # Execute method with arguments
    return self._execute_method(class_instance, method.__name__, parsed)

  def _execute_module_function(self, parsed) -> Any:
    """Execute module function directly.

    Invokes function from module with parsed arguments.
    """
    function = parsed._cli_function
    return self._execute_function(function, parsed)

  def _create_main(self, parsed) -> Any:
    """Create main class instance with global arguments."""
    main_kwargs = {}
    main_sig = inspect.signature(self.target_class.__init__)

    for param_name, param in main_sig.parameters.items():
      if param_name == 'self':
        continue
      if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
        continue

      # Look for global argument
      global_attr = f'_global_{param_name}'
      if hasattr(parsed, global_attr):
        value = getattr(parsed, global_attr)
        main_kwargs[param_name] = value

    try:
      return self.target_class(**main_kwargs)
    except TypeError as e:
      raise RuntimeError(f"Cannot instantiate {self.target_class.__name__} with global args: {e}") from e

  def _create_inner_instance(self, inner_class: Type, command_name: str, parsed, main: Any) -> Any:
    """Create inner class instance with sub-global arguments."""
    inner_kwargs = {}
    inner_sig = inspect.signature(inner_class.__init__)

    for param_name, param in inner_sig.parameters.items():
      if param_name == 'self':
        continue
      if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
        continue

      # Look for sub-global argument
      subglobal_attr = f'_subglobal_{command_name}_{param_name}'
      if hasattr(parsed, subglobal_attr):
        value = getattr(parsed, subglobal_attr)
        inner_kwargs[param_name] = value

    try:
      return inner_class(main, **inner_kwargs)
    except TypeError as e:
      raise RuntimeError(f"Cannot instantiate {inner_class.__name__} with sub-global args: {e}") from e

  def _execute_method(self, instance: Any, method_name: str, parsed) -> Any:
    """Execute method on instance with parsed arguments."""
    bound_method = getattr(instance, method_name)
    method_kwargs = self._extract_method_arguments(bound_method, parsed)
    return bound_method(**method_kwargs)

  def _execute_function(self, function: Any, parsed) -> Any:
    """Execute function directly with parsed arguments."""
    function_kwargs = self._extract_method_arguments(function, parsed)
    return function(**function_kwargs)

  def _extract_method_arguments(self, method_or_function: Any, parsed) -> Dict[str, Any]:
    """Extract method/function arguments from parsed FreyjaCLI arguments."""
    sig = inspect.signature(method_or_function)
    kwargs = {}

    for param_name, param in sig.parameters.items():
      if param_name == 'self':
        continue
      if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
        continue

      # Look for method argument (no prefix, just the parameter name)
      attr_name = param_name.replace('-', '_')
      if hasattr(parsed, attr_name):
        value = getattr(parsed, attr_name)
        kwargs[param_name] = value

    return kwargs

  def execute_command(self, parsed, target_mode) -> Any:
    """Main command execution dispatcher - determines execution strategy based on target mode."""
    result = None

    match target_mode.value:
      case 'module':
        result = self._execute_module_function(parsed)
      case 'class':
        # Check if this is a hierarchical command with command path
        if hasattr(parsed, '_command_path'):
          # Execute inner class method
          result = self._execute_inner_class_command(parsed)
        else:
          # Execute direct method from class
          result = self._execute_direct_method_command(parsed)
      case _:
        raise RuntimeError(f"Unknown target mode: {target_mode}")

    return result

  def _handle_execution_error(self, parsed, error: Exception) -> int:
    """Handle execution errors with appropriate logging and return codes."""
    import sys
    import traceback

    function_name = getattr(parsed, '_function_name', 'unknown')
    print(f"Error executing {function_name}: {error}", file=sys.stderr)

    if getattr(parsed, 'verbose', False):
      traceback.print_exc()

    return 1
