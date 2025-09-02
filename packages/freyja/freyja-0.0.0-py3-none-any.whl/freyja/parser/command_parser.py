# Command parsing functionality extracted from FreyjaCLI class.
import argparse
from typing import *

from freyja.help.help_formatter import HierarchicalHelpFormatter
from .docstring_parser import DocStringParser
from .argument_parser import ArgumentParser
from ..theme import create_default_theme


class CommandParser:
  """
  Creates and configures ArgumentParser instances for FreyjaCLI cmd_tree.

  Handles both flat command structures and hierarchical command groups
  with proper argument handling and help formatting.
  """

  def __init__(
      self,
      title: str,
      theme=None,
      alphabetize: bool = True,
      enable_completion: bool = False
  ):
    """
    Initialize command parser.

    :param title: FreyjaCLI application title
    :param theme: Optional theme for colored output
    :param alphabetize: Whether to alphabetize cmd_tree and options
    :param enable_completion: Whether to enable shell completion
    """
    self.title = title
    self.theme = theme or create_default_theme()
    self.alphabetize = alphabetize
    self.enable_completion = enable_completion

  def create_parser(
      self,
      command_tree: Dict[str, Any],
      target_mode: str,
      target_class: Optional[Type] = None,
      no_color: bool = False
  ) -> argparse.ArgumentParser:
    """
    Create ArgumentParser with all cmd_tree using pre-built command tree.

    :param command_tree: Pre-built nested command structure
    :param target_mode: Target mode ('module', 'class', or 'multi_class')
    :param target_class: Target class for inner class pattern
    :param no_color: Whether to disable colored output
    :return: Configured ArgumentParser
    """
    # Create effective theme (disable if no_color)
    effective_theme = None if no_color else self.theme

    # For multi-class mode, disable alphabetization to preserve class order
    effective_alphabetize = self.alphabetize and (target_mode != 'multi_class')

    # Create formatter factory
    def create_formatter_with_theme(*args, **kwargs):
      return HierarchicalHelpFormatter(
        *args,
        theme=effective_theme,
        alphabetize=effective_alphabetize,
        **kwargs
      )

    # Create main parser
    parser = argparse.ArgumentParser(
      description=self.title,
      formatter_class=create_formatter_with_theme
    )

    # Add global arguments
    self._add_global_arguments(parser, target_mode, target_class, command_tree)

    # Create subparsers for cmd_tree
    subparsers = parser.add_subparsers(
      title='COMMANDS',
      dest='command',
      required=False,
      help='Available cmd_tree',
      metavar=''
    )

    # Store theme reference
    subparsers._theme = effective_theme

    # Add cmd_tree to parser using command tree
    self._add_commands_from_tree(subparsers, command_tree, effective_theme)

    # Apply parser patches for styling and formatter access
    self._apply_parser_patches(parser, effective_theme)

    return parser

  def _add_global_arguments(
      self,
      parser: argparse.ArgumentParser,
      target_mode: str,
      target_class: Optional[Type],
      command_tree: Dict[str, Any]
  ):
    """Add global arguments to the parser."""
    # Add verbose flag for module-based CLIs
    if target_mode == 'module':
      parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
      )

    # Add global no-color flag
    parser.add_argument(
      "-n", "--no-color",
      action="store_true",
      help="Disable colored output"
    )

    # Add completion arguments
    if self.enable_completion:
      parser.add_argument(
        "--_complete",
        action="store_true",
        help=argparse.SUPPRESS
      )

    # Add global class arguments for hierarchical cmd_tree
    if (target_mode == 'class' and target_class and
        any(info.get('type') == 'group' for info in command_tree.values())):
      ArgumentParser.add_global_class_args(parser, target_class)

  def _add_commands_from_tree(
      self,
      subparsers,
      command_tree: Dict[str, Any],
      theme
  ):
    """Add cmd_tree to parser from pre-built command tree."""
    for command_name, command_info in command_tree.items():
      if command_info['type'] == 'command':
        # Add flat command
        self._add_flat_command_from_tree(subparsers, command_name, command_info, theme)
      elif command_info['type'] == 'group':
        # Add command group
        self._add_command_group_from_tree(subparsers, command_name, command_info, theme)

  def _add_flat_command_from_tree(self, subparsers, command_name: str, command_info: Dict[str, Any], theme):
    """Add a flat command from command tree."""
    desc, _ = DocStringParser.extract_function_help(command_info['function'])

    def create_formatter_with_theme(*args, **kwargs):
      return HierarchicalHelpFormatter(
        *args,
        theme=theme,
        alphabetize=self.alphabetize,
        **kwargs
      )

    sub = subparsers.add_parser(
      command_name,
      help=desc,
      description=desc,
      formatter_class=create_formatter_with_theme
    )
    sub._command_type = 'command'
    sub._theme = theme

    # Add function arguments
    ArgumentParser.add_function_args(sub, command_info['function'])

    # Set defaults
    defaults = {
      '_cli_function': command_info['function'],
      '_function_name': command_info['original_name']
    }

    # Add command path for hierarchical cmd_tree
    if command_info.get('group_name'):
      defaults['_command_path'] = command_info['group_name']

    if command_info.get('is_system_command'):
      defaults['_is_system_command'] = True

    sub.set_defaults(**defaults)

  def _add_command_group_from_tree(self, subparsers, group_name: str, group_info: Dict[str, Any], theme):
    """Add a command group from command tree."""
    group_help = group_info.get('description', f"{group_name.title().replace('-', ' ')} operations")
    inner_class = group_info.get('inner_class')

    def create_formatter_with_theme(*args, **kwargs):
      return HierarchicalHelpFormatter(
        *args,
        theme=theme,
        alphabetize=self.alphabetize,
        **kwargs
      )

    # Create group parser
    group_parser = subparsers.add_parser(
      group_name,
      help=group_help,
      formatter_class=create_formatter_with_theme
    )

    # Configure group parser
    group_parser._command_type = 'group'
    group_parser._theme = theme
    group_parser._command_group_description = group_help
    
    # Set system command flag if present
    if group_info.get('is_system_command'):
      group_parser._is_system_command = True

    # Add sub-global arguments from inner class
    if inner_class:
      ArgumentParser.add_subglobal_class_args(
        group_parser, inner_class, group_name
      )

    # Store command help information (only for cmd_tree, not subgroups)
    command_help = {}
    for cmd_name, cmd_info in group_info['cmd_tree'].items():
      if cmd_info.get('type') == 'command':
        desc, _ = DocStringParser.extract_function_help(cmd_info['function'])
        command_help[cmd_name] = desc
      elif cmd_info.get('type') == 'group':
        # For subgroups, use their description
        command_help[cmd_name] = cmd_info.get('description', 'Command group')

    group_parser._commands = command_help

    # Create subparsers for group cmd_tree
    dest_name = f'{group_name}_command'
    sub_subparsers = group_parser.add_subparsers(
      title=f'{group_name.title().replace("-", " ")} COMMANDS',
      dest=dest_name,
      required=False,
      help=f'Available {group_name} cmd_tree',
      metavar=''
    )

    sub_subparsers._enhanced_help = True
    sub_subparsers._theme = theme

    # Add individual cmd_tree and subgroups in the group
    for cmd_name, cmd_info in group_info['cmd_tree'].items():
      if cmd_info.get('type') == 'command':
        self._add_flat_command_from_tree(sub_subparsers, cmd_name, cmd_info, theme)
      elif cmd_info.get('type') == 'group':
        # Add nested command group
        self._add_command_group_from_tree(sub_subparsers, cmd_name, cmd_info, theme)

  def _apply_parser_patches(self, parser: argparse.ArgumentParser, theme):
    """Apply patches to parser for enhanced functionality."""

    # Patch formatter to have access to parser actions
    def patch_formatter_with_parser_actions():
      original_get_formatter = parser._get_formatter

      def patched_get_formatter():
        formatter = original_get_formatter()
        formatter._parser_actions = parser._actions
        return formatter

      parser._get_formatter = patched_get_formatter

    # Patch help formatting for title styling
    original_format_help = parser.format_help

    def patched_format_help():
      original_help = original_format_help()

      if theme and self.title in original_help:
        from freyja.theme import ColorFormatter
        color_formatter = ColorFormatter()
        styled_title = color_formatter.apply_style(self.title, theme.title)
        original_help = original_help.replace(self.title, styled_title)

      return original_help

    parser.format_help = patched_format_help

    # Apply formatter patch
    patch_formatter_with_parser_actions()
