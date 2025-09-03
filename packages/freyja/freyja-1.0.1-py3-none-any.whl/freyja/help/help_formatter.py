# Refactored Help Formatter with reduced duplication and single return points
import argparse
import itertools
import os
import re
import textwrap

from .help_formatting_engine import HelpFormattingEngine


class FormatPatterns:
  """Common formatting patterns extracted to eliminate duplication."""

  @staticmethod
  def format_section_title(title: str, style_func=None) -> str:
    """Format section title consistently."""
    return style_func(title) if style_func else title

  @staticmethod
  def format_indented_line(content: str, indent: int) -> str:
    """Format line with consistent indentation."""
    return f"{' ' * indent}{content}"

  @staticmethod
  def calculate_spacing(name_width: int, target_column: int, min_spacing: int = 4) -> int:
    """Calculate spacing needed to reach target column."""
    return min_spacing if name_width >= target_column else target_column - name_width

  @staticmethod
  def create_text_wrapper(width: int, initial_indent: str = "", subsequent_indent: str = "") -> textwrap.TextWrapper:
    """Create TextWrapper with consistent parameters."""
    return textwrap.TextWrapper(
      width=width,
      break_long_words=False,
      break_on_hyphens=False,
      initial_indent=initial_indent,
      subsequent_indent=subsequent_indent
    )


class HierarchicalHelpFormatter(argparse.RawDescriptionHelpFormatter):
  """Refactored formatter with reduced duplication and single return points."""

  def __init__(self, *args, theme=None, alphabetize=True, **kwargs):
    super().__init__(*args, **kwargs)
    self._console_width = self._get_console_width()
    self._cmd_indent = 2
    self._arg_indent = 4
    self._desc_indent = 8

    # Initialize formatting engine
    self._formatting_engine = HelpFormattingEngine(
      console_width=self._console_width,
      theme=theme,
      color_formatter=getattr(self, '_color_formatter', None)
    )

    # Theme support
    self._theme = theme
    self._color_formatter = None
    if theme:
      from freyja.theme import ColorFormatter
      self._color_formatter = ColorFormatter()

    self._alphabetize = alphabetize
    self._global_desc_column = None

  def _get_console_width(self) -> int:
    """Get console width with fallback."""
    try:
      return os.get_terminal_size().columns
    except (OSError, ValueError):
      return int(os.environ.get('COLUMNS', 80))

  def _format_actions(self, actions):
    """Override to capture parser actions for unified column calculation."""
    self._parser_actions = actions
    return super()._format_actions(actions)

  def _format_action(self, action):
    """Format actions with proper indentation for command groups."""
    result = None

    if isinstance(action, argparse._SubParsersAction):
      result = self._format_command_groups(action)
    elif action.option_strings and not isinstance(action, argparse._SubParsersAction):
      result = self._format_global_option_aligned(action)
    else:
      result = super()._format_action(action)

    return result

  def _ensure_global_column_calculated(self):
    """Calculate and cache the unified description column if not already done."""
    if self._global_desc_column is not None:
      return self._global_desc_column

    subparsers_action = self._find_subparsers_action()

    self._global_desc_column = (
      self._calculate_unified_command_description_column(subparsers_action)
      if subparsers_action else 40
    )

    return self._global_desc_column

  def _find_subparsers_action(self):
    """Find subparsers action from parser actions."""
    parser_actions = getattr(self, '_parser_actions', [])

    for action in parser_actions:
      if isinstance(action, argparse._SubParsersAction):
        return action
    return None

  def _format_global_option_aligned(self, action):
    """Format global options with consistent alignment using existing alignment logic."""
    option_strings = action.option_strings
    result = None

    if not option_strings:
      result = super()._format_action(action)
    else:
      option_display = self._build_option_display(action, option_strings)
      help_text = self._build_help_text(action)
      global_desc_column = self._ensure_global_column_calculated()

      formatted_lines = self._format_inline_description(
        name=option_display,
        description=help_text,
        name_indent=self._arg_indent + 2,
        description_column=global_desc_column + 4,
        style_name='option_name',
        style_description='option_description',
        add_colon=False
      )

      result = '\n'.join(formatted_lines) + '\n'

    return result

  def _build_option_display(self, action, option_strings):
    """Build option display string with metavar."""
    option_name = option_strings[-1] if option_strings else ""

    if action.nargs != 0:
      if hasattr(action, 'metavar') and action.metavar:
        return f"{option_name} {action.metavar}"
      elif hasattr(action, 'choices') and action.choices:
        return option_name
      else:
        metavar = action.dest.upper().replace('_', '-')
        return f"{option_name} {metavar}"

    return option_name

  def _build_help_text(self, action):
    """Build help text including choices if present."""
    help_text = action.help or ""

    if hasattr(action, 'choices') and action.choices and action.nargs != 0:
      choices_str = ", ".join(str(c) for c in action.choices)
      help_text = f"{help_text} (choices: {choices_str})"

    return help_text

  def _calculate_unified_command_description_column(self, action):
    """Calculate unified description column for ALL elements."""
    if not action:
      return 40

    max_width = self._cmd_indent

    # Include global options in calculation
    max_width = max(max_width, self._calculate_global_options_width())

    # Scan all cmd_tree
    for choice, subparser in action.choices.items():
      max_width = max(max_width, self._calculate_command_width(choice, subparser))

    unified_desc_column = max_width + 4
    return min(unified_desc_column, self._console_width // 2)

  def _calculate_global_options_width(self):
    """Calculate width needed for global options."""
    max_width = 0
    parser_actions = getattr(self, '_parser_actions', [])

    for action in parser_actions:
      if (action.option_strings and
          action.dest != 'help' and
          not isinstance(action, argparse._SubParsersAction)):
        opt_width = self._calculate_option_width(action)
        max_width = max(max_width, opt_width)

    return max_width

  def _calculate_option_width(self, action):
    """Calculate width for a single option."""
    opt_name = action.option_strings[-1]
    opt_display = self._build_option_display(action, action.option_strings)
    return len(opt_display) + self._arg_indent

  def _calculate_command_width(self, choice, subparser):
    """Calculate width for cmd_tree and their options."""
    max_width = self._cmd_indent + len(choice) + 1  # +1 for colon

    # Check options in this command
    _, optional_args = self._analyze_arguments(subparser)
    for arg_name, _ in optional_args:
      opt_width = len(arg_name) + self._arg_indent
      max_width = max(max_width, opt_width)

    # Handle nested cmd_tree
    if hasattr(subparser, '_commands'):
      command_indent = self._cmd_indent + 2
      for cmd_name in subparser._commands.keys():
        cmd_width = command_indent + len(cmd_name) + 1
        max_width = max(max_width, cmd_width)

        cmd_parser = self._find_subparser(subparser, cmd_name)
        if cmd_parser:
          _, nested_args = self._analyze_arguments(cmd_parser)
          for arg_name, _ in nested_args:
            nested_width = len(arg_name) + self._arg_indent
            max_width = max(max_width, nested_width)

    return max_width

  def _format_command_groups(self, action):
    """Format command groups with clean list-based display."""
    parts = []
    has_required_args = False

    unified_cmd_desc_column = self._calculate_unified_command_description_column(action)

    all_commands = self._collect_all_commands(action)

    grouped=itertools.groupby(all_commands, key=lambda c: c[-1])

    # Sort system cmd_tree first, then alphabetize the rest
    if self._alphabetize:
      all_commands.sort(key=lambda x: (not x[3], x[0]))  # x[3] is is_system, x[0] is command name

    for choice, subparser, command_type, is_system in all_commands:
      command_section = self._format_single_command(
        choice, subparser, self._cmd_indent, unified_cmd_desc_column
      )
      parts.extend(command_section)

      if self._command_has_required_args(subparser):
        has_required_args = True

    if has_required_args:
      parts.extend(self._format_required_footnote())

    return "\n".join(parts)

  def _collect_all_commands(self, action):
    """Collect all cmd_tree with their metadata."""
    all_commands = []

    for choice, subparser in action.choices.items():
      command_type = 'flat'
      is_system = False

      if hasattr(subparser, '_command_type'):
        if subparser._command_type == 'group':
          command_type = 'group'
          if hasattr(subparser, '_is_system_command'):
            is_system = getattr(subparser, '_is_system_command', False)

      all_commands.append((choice, subparser, command_type, is_system))

    return all_commands

  def _format_single_command(self, choice, subparser, base_indent, unified_cmd_desc_column):
    """Format a single command (either flat or group)."""
    return self._format_group_with_command_groups_global(
      choice, subparser, base_indent, unified_cmd_desc_column, unified_cmd_desc_column
    )

  def _command_has_required_args(self, subparser):
    """Check if command or its nested cmd_tree have required arguments."""
    required_args, _ = self._analyze_arguments(subparser)
    if required_args:
      return True

    if hasattr(subparser, '_command_details'):
      return any(
        cmd_info.get('type') == 'command' and 'function' in cmd_info
        for cmd_info in subparser._command_details.values()
      )

    return False

  def _format_required_footnote(self):
    """Format the required arguments footnote."""
    footnote_text = "* - required"

    if self._theme:
      from freyja.theme import ColorFormatter
      color_formatter = ColorFormatter()
      styled_footnote = color_formatter.apply_style(footnote_text, self._theme.required_asterisk)
      return ["", styled_footnote]

    return ["", footnote_text]

  def _format_group_with_command_groups_global(self, name, parser, base_indent,
                                               unified_cmd_desc_column, global_option_column):
    """Format a command group with unified command description column alignment."""
    lines = []

    # Group header
    group_description = (getattr(parser, '_command_group_description', None) or
                         parser.description or
                         getattr(parser, 'help', ''))

    if group_description:
      formatted_lines = self._format_inline_description(
        name=name,
        description=group_description,
        name_indent=base_indent,
        description_column=unified_cmd_desc_column,
        style_name='grouped_command_name',
        style_description='command_description',
        add_colon=True
      )
      lines.extend(formatted_lines)
    else:
      styled_name = self._apply_style(name, 'grouped_command_name')
      lines.append(f"{' ' * base_indent}{styled_name}")

    # Add arguments
    lines.extend(self._format_command_arguments(parser, unified_cmd_desc_column))

    # Add nested cmd_tree
    if hasattr(parser, '_commands'):
      lines.extend(self._format_nested_commands(parser, base_indent, unified_cmd_desc_column))

    return lines

  def _format_command_arguments(self, parser, unified_cmd_desc_column):
    """Format command arguments (both required and optional)."""
    lines = []
    required_args, optional_args = self._analyze_arguments(parser)

    # Format required arguments
    for arg_name, arg_help in required_args:
      arg_lines = self._format_single_argument(
        arg_name, arg_help, unified_cmd_desc_column,
        'command_group_option_name', 'command_group_option_description',
        required=True
      )
      lines.extend(arg_lines)

    # Format optional arguments
    for arg_name, arg_help in optional_args:
      arg_lines = self._format_single_argument(
        arg_name, arg_help, unified_cmd_desc_column,
        'command_group_option_name', 'command_group_option_description',
        required=False
      )
      lines.extend(arg_lines)

    return lines

  def _format_single_argument(self, arg_name, arg_help, unified_cmd_desc_column,
                              name_style, desc_style, required=False):
    """Format a single argument with consistent styling."""
    lines = []

    if arg_help:
      arg_lines = self._format_inline_description(
        name=arg_name,
        description=arg_help,
        name_indent=self._arg_indent,
        description_column=unified_cmd_desc_column + 2,
        style_name=name_style,
        style_description=desc_style
      )
      lines.extend(arg_lines)

      if required and arg_lines:
        styled_asterisk = self._apply_style(" *", 'required_asterisk')
        lines[-1] += styled_asterisk
    else:
      styled_arg = self._apply_style(arg_name, name_style)
      asterisk = self._apply_style(" *", 'required_asterisk') if required else ""
      lines.append(f"{' ' * self._arg_indent}{styled_arg}{asterisk}")

    return lines

  def _format_nested_commands(self, parser, base_indent, unified_cmd_desc_column):
    """Format nested cmd_tree within a group."""
    lines = []
    command_indent = base_indent + 2

    command_items = (sorted(parser._commands.items())
                     if self._alphabetize
                     else list(parser._commands.items()))

    for cmd, cmd_help in command_items:
      cmd_parser = self._find_subparser(parser, cmd)
      if cmd_parser:
        if (hasattr(cmd_parser, '_command_type') and
            getattr(cmd_parser, '_command_type') == 'group' and
            hasattr(cmd_parser, '_commands') and
            cmd_parser._commands):
          # Nested group
          cmd_section = self._format_group_with_command_groups_global(
            cmd, cmd_parser, command_indent, unified_cmd_desc_column, unified_cmd_desc_column
          )
        else:
          # Final command
          cmd_section = self._format_final_command(
            cmd, cmd_parser, command_indent, unified_cmd_desc_column
          )
        lines.extend(cmd_section)
      else:
        # Fallback
        lines.append(f"{' ' * command_indent}{cmd}")
        if cmd_help:
          wrapped_help = self._wrap_text(cmd_help, command_indent + 2, self._console_width)
          lines.extend(wrapped_help)

    return lines

  def _format_final_command(self, name, parser, base_indent, unified_cmd_desc_column):
    """Format a final command with its arguments."""
    lines = []

    # Command description
    help_text = parser.description or getattr(parser, 'help', '')

    if help_text:
      formatted_lines = self._format_inline_description(
        name=name,
        description=help_text,
        name_indent=base_indent,
        description_column=unified_cmd_desc_column + 2,
        style_name='command_group_name',
        style_description='grouped_command_description',
        add_colon=True
      )
      lines.extend(formatted_lines)
    else:
      styled_name = self._apply_style(name, 'command_group_name')
      lines.append(f"{' ' * base_indent}{styled_name}")

    # Command arguments
    lines.extend(self._format_final_command_arguments(parser, unified_cmd_desc_column))

    return lines

  def _format_final_command_arguments(self, parser, unified_cmd_desc_column):
    """Format arguments for final cmd_tree."""
    lines = []
    required_args, optional_args = self._analyze_arguments(parser)

    # Required arguments
    for arg_name, arg_help in required_args:
      arg_lines = self._format_single_argument(
        arg_name, arg_help, unified_cmd_desc_column,
        'option_name', 'option_description', required=True
      )
      # Adjust indentation for command group options
      adjusted_lines = [line.replace(' ' * self._arg_indent, ' ' * (self._arg_indent + 2), 1)
                        for line in arg_lines]
      lines.extend(adjusted_lines)

    # Optional arguments
    for arg_name, arg_help in optional_args:
      arg_lines = self._format_single_argument(
        arg_name, arg_help, unified_cmd_desc_column,
        'option_name', 'option_description', required=False
      )
      # Adjust indentation for command group options
      adjusted_lines = [line.replace(' ' * self._arg_indent, ' ' * (self._arg_indent + 2), 1)
                        for line in arg_lines]
      lines.extend(adjusted_lines)

    return lines

  def _analyze_arguments(self, parser):
    """Analyze parser arguments and return required and optional separately."""
    if not parser:
      return [], []

    required_args = []
    optional_args = []

    for action in parser._actions:
      if action.dest == 'help':
        continue

      arg_name, arg_help = self._extract_argument_info(action)

      if hasattr(action, 'required') and action.required:
        required_args.append((arg_name, arg_help))
      elif action.option_strings:
        optional_args.append((arg_name, arg_help))

    if self._alphabetize:
      required_args.sort(key=lambda x: x[0])
      optional_args.sort(key=lambda x: x[0])

    return required_args, optional_args

  def _extract_argument_info(self, action):
    """Extract argument name and help from action."""
    # Handle sub-global arguments
    clean_param_name = None
    if action.dest.startswith('_subglobal_'):
      parts = action.dest.split('_', 3)
      if len(parts) >= 4:
        clean_param_name = parts[3]
        arg_name = f"--{clean_param_name.replace('_', '-')}"
      else:
        arg_name = f"--{action.dest.replace('_', '-')}"
    else:
      arg_name = f"--{action.dest.replace('_', '-')}"

    arg_help = getattr(action, 'help', '')

    # Add metavar for value arguments
    if hasattr(action, 'required') and action.required:
      if hasattr(action, 'metavar') and action.metavar:
        arg_name = f"{arg_name} {action.metavar}"
      else:
        metavar_base = clean_param_name if clean_param_name else action.dest
        arg_name = f"{arg_name} {metavar_base.upper()}"
    elif action.option_strings and action.nargs != 0 and getattr(action, 'action', None) != 'store_true':
      if hasattr(action, 'metavar') and action.metavar:
        arg_name = f"{arg_name} {action.metavar}"
      else:
        metavar_base = clean_param_name if clean_param_name else action.dest
        arg_name = f"{arg_name} {metavar_base.upper()}"

    return arg_name, arg_help

  def _wrap_text(self, text: str, indent: int, width: int) -> list[str]:
    """Wrap text with proper indentation using textwrap."""
    if not text:
      return []

    available_width = max(width - indent, 20)
    wrapper = FormatPatterns.create_text_wrapper(
      width=available_width,
      initial_indent=" " * indent,
      subsequent_indent=" " * indent
    )
    return wrapper.wrap(text)

  def _apply_style(self, text: str, style_name: str) -> str:
    """Apply theme style to text if theme is available."""
    if not self._theme or not self._color_formatter:
      return text

    style_map = {
      'title': self._theme.title,
      'subtitle': self._theme.subtitle,
      'command_name': self._theme.command_name,
      'command_description': self._theme.command_description,
      'command_group_name': getattr(self._theme, 'command_group_name', self._theme.command_name),
      'command_group_description': getattr(self._theme, 'command_group_description', self._theme.command_description),
      'command_group_option_name': getattr(self._theme, 'command_group_option_name', self._theme.option_name),
      'command_group_option_description': getattr(self._theme, 'command_group_option_description',
                                                  self._theme.option_description),
      'grouped_command_name': getattr(self._theme, 'grouped_command_name', self._theme.command_name),
      'grouped_command_description': getattr(self._theme, 'grouped_command_description',
                                             self._theme.command_description),
      'grouped_command_option_name': getattr(self._theme, 'grouped_command_option_name', self._theme.option_name),
      'grouped_command_option_description': getattr(self._theme, 'grouped_command_option_description',
                                                    self._theme.option_description),
      'option_name': self._theme.option_name,
      'option_description': self._theme.option_description,
      'required_asterisk': self._theme.required_asterisk
    }

    style = style_map.get(style_name)
    return self._color_formatter.apply_style(text, style) if style else text

  def _get_display_width(self, text: str) -> int:
    """Get display width of text, handling ANSI color codes."""
    if not text:
      return 0

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', text)
    return len(clean_text)

  def _format_inline_description(self, name: str, description: str, name_indent: int,
                                 description_column: int, style_name: str, style_description: str,
                                 add_colon: bool = False) -> list[str]:
    """Format name and description inline with consistent wrapping."""
    lines = []

    if not description:
      styled_name = self._apply_style(name, style_name)
      display_name = f"{styled_name}:" if add_colon else styled_name
      lines = [f"{' ' * name_indent}{display_name}"]
    else:
      lines = self._format_description_with_wrapping(
        name, description, name_indent, description_column,
        style_name, style_description, add_colon
      )

    return lines

  def _format_description_with_wrapping(self, name, description, name_indent,
                                        description_column, style_name, style_description, add_colon):
    """Format description with proper wrapping logic."""
    styled_name = self._apply_style(name, style_name)
    styled_description = self._apply_style(description, style_description)

    display_name = f"{styled_name}:" if add_colon else styled_name
    name_part = f"{' ' * name_indent}{display_name}"
    name_display_width = name_indent + self._get_display_width(name) + (1 if add_colon else 0)

    spacing_needed = FormatPatterns.calculate_spacing(name_display_width, description_column)

    if name_display_width >= description_column:
      spacing_needed = 4

    first_line = f"{name_part}{' ' * spacing_needed}{styled_description}"

    if self._get_display_width(first_line) <= self._console_width:
      return [first_line]

    return self._format_wrapped_description(
      name_part, description, name_display_width, spacing_needed,
      description_column, style_description
    )

  def _format_wrapped_description(self, name_part, description, name_display_width,
                                  spacing_needed, description_column, style_description):
    """Format description with wrapping when it doesn't fit on one line."""
    available_width_first_line = self._console_width - name_display_width - spacing_needed

    if available_width_first_line >= 20:
      wrapper = FormatPatterns.create_text_wrapper(width=available_width_first_line)
      desc_lines = wrapper.wrap(description)

      if desc_lines:
        styled_first_desc = self._apply_style(desc_lines[0], style_description)
        lines = [f"{name_part}{' ' * spacing_needed}{styled_first_desc}"]

        if len(desc_lines) > 1:
          desc_start_position = name_display_width + spacing_needed
          continuation_indent = " " * desc_start_position
          for desc_line in desc_lines[1:]:
            styled_desc_line = self._apply_style(desc_line, style_description)
            lines.append(f"{continuation_indent}{styled_desc_line}")
        return lines

    # Fallback: put description on separate lines
    return self._format_separate_line_description(
      name_part, description, description_column, style_description
    )

  def _format_separate_line_description(self, name_part, description, description_column, style_description):
    """Format description on separate lines when inline doesn't work."""
    lines = [name_part]

    desc_indent = description_column
    available_width = max(self._console_width - desc_indent, 20)

    if available_width < 20:
      available_width = 20
      desc_indent = self._console_width - available_width

    wrapper = FormatPatterns.create_text_wrapper(width=available_width)
    desc_lines = wrapper.wrap(description)
    indent_str = " " * desc_indent

    for desc_line in desc_lines:
      styled_desc_line = self._apply_style(desc_line, style_description)
      lines.append(f"{indent_str}{styled_desc_line}")

    return lines

  def _format_usage(self, usage, actions, groups, prefix):
    """Override to add color to usage line and potentially title."""
    usage_text = super()._format_usage(usage, actions, groups, prefix)

    if (prefix == 'usage: ' and
        hasattr(self, '_root_section')):
      parser = getattr(self._root_section, 'formatter', None)
      if parser:
        parser_obj = getattr(parser, '_parser', None)
        if (parser_obj and
            hasattr(parser_obj, 'description') and
            parser_obj.description):
          styled_title = self._apply_style(parser_obj.description, 'title')
          return f"{styled_title}\n\n{usage_text}"

    return usage_text

  def start_section(self, heading):
    """Override to customize section headers with theming and capitalization."""
    styled_heading = heading

    if heading:
      if heading.lower() == 'options':
        styled_heading = self._apply_style('OPTIONS', 'subtitle')
      elif heading == 'COMMANDS':
        styled_heading = self._apply_style('COMMANDS', 'subtitle')
      elif self._theme:
        styled_heading = self._apply_style(heading, 'subtitle')

    super().start_section(styled_heading)

  def _find_subparser(self, parent_parser, subcmd_name):
    """Find a subparser by name in the parent parser."""
    result = None
    for action in parent_parser._actions:
      if isinstance(action, argparse._SubParsersAction):
        if subcmd_name in action.choices:
          result = action.choices[subcmd_name]
          break
    return result
