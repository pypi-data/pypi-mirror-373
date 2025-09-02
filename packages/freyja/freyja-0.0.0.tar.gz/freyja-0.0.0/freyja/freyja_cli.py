# Refactored FreyjaCLI class - Simplified coordinator role only
from __future__ import annotations

import os
import types
from typing import *

from freyja.cli import ClassHandler, ExecutionCoordinator
from freyja.command import CommandDiscovery, CommandExecutor
from freyja.completion.base import get_completion_handler
from freyja.parser import CommandParser

Target = Union[types.ModuleType, Type[Any], Sequence[Type[Any]]]

class FreyjaCLI:
  """
  Simplified FreyjaCLI coordinator that orchestrates command discovery, parsing, and execution.
  """

  def __init__(self, target: Target, title: Optional[str] = None, function_filter: Optional[callable] = None,
               method_filter: Optional[callable] = None, theme=None, alphabetize: bool = True, completion: bool = True,
               theme_tuner=False):
    """
    Initialize FreyjaCLI with target and configuration.

    :param target: Module, class, or list of classes to generate FreyjaCLI from
    :param title: FreyjaCLI application title
    :param function_filter: Optional filter for functions (module mode)
    :param method_filter: Optional filter for methods (class mode)
    :param theme: Optional theme for colored output
    :param alphabetize: Whether to sort cmd_tree and options alphabetically
    :param completion: Whether to enable shell completion
    """

    # Initialize discovery service (replaces TargetAnalyzer)
    self.discovery = CommandDiscovery(target=target, function_filter=function_filter, method_filter=method_filter, completion=completion,
                                  theme_tuner=theme_tuner)
    
    # Get target mode and validation from discovery
    self.target_mode = self.discovery.mode
    
    # Validate class mode for command collisions when multiple classes are present
    if self.discovery.target_classes and len(self.discovery.target_classes) > 1:
      handler = ClassHandler()
      handler.validate_classes(self.discovery.target_classes)

    # Set title based on target
    self.title = title or self.discovery.generate_title()

    # Store only essential config
    self.enable_completion = completion

    # Discover cmd_tree
    # self.discovery.cmd_tree = discovery.cmd_tree

    # Initialize command executors
    executors = self._initialize_executors()

    # Initialize execution coordinator
    self.execution_coordinator = ExecutionCoordinator(self.target_mode, executors)

    # Initialize parser service
    self.parser_service = CommandParser(title=self.title, theme=theme, alphabetize=alphabetize, enable_completion=completion)

    # Set target_class and target_classes properties for compatibility
    if self.discovery.target_classes:
      # Class mode: set both for backward compatibility
      self.target_class = self.discovery.primary_class
      self.target_classes = self.discovery.target_classes
    else:
      # Module mode
      self.target_class = None
      self.target_classes = None

    # Get command structure from discovery (no need to build separately)
    self.commands = self.discovery.cmd_tree.to_dict()

    # Essential compatibility properties only
    self.target_module = self.discovery.target_module

  def run(self, args: List[str] = None) -> Any:
    """
    Parse arguments and execute the appropriate command.

    :param args: Optional command line arguments (uses sys.argv if None)
    :return: Command execution result
    """
    result = None

    # Handle completion requests early
    if self.enable_completion and self._is_completion_request():
      self._handle_completion()
    else:
      # Check for no-color flag
      no_color = ExecutionCoordinator.check_no_color_flag(args or [])

      # Create parser and parse arguments
      parser = self.create_parser(no_color=no_color)

      # Parse and execute with context  
      result = self._execute_with_context(parser, args)

    return result

  def _execute_with_context(self, parser, args) -> Any:
    """Execute command with FreyjaCLI context."""
    # Add context information to the execution coordinator
    self.execution_coordinator.command_tree = self.discovery.cmd_tree

    return self.execution_coordinator.parse_and_execute(parser, args)

  def _initialize_executors(self) -> dict:
    """Initialize command executors based on target mode."""
    if self.discovery.target_classes and len(self.discovery.target_classes) > 1:
      # Multiple classes: create executor for each class
      return {
        target_class: CommandExecutor(target_class=target_class, target_module=None)
        for target_class in self.discovery.target_classes
      }
    
    # Single class or module: create single primary executor
    return {
      'primary': CommandExecutor(
        target_class=self.discovery.primary_class,
        target_module=self.discovery.target_module
      )
    }

  def _is_completion_request(self) -> bool:
    """Check if this is a shell completion request."""
    return os.getenv('_FREYA_COMPLETE') is not None

  def _handle_completion(self):
    """Handle shell completion request."""
    try:
      completion_handler = get_completion_handler(self)
      completion_handler.complete()
    except ImportError:
      # Completion module    not available
      pass

  def create_parser(self, no_color: bool = False):
    """Create argument parser using pre-built command tree."""
    return self.parser_service.create_parser(
      command_tree=self.commands,
      target_mode=self.target_mode.value,
      target_class=self.target_class,
      no_color=no_color
    )
