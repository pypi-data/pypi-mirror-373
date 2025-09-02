import os
import sys
from typing import Optional

class Completion:
  """Shell completion management."""

  def __init__(self, shell: str = "bash", cli_instance=None):
    """Initialize completion manager.

    :param shell: Default shell type
    :param cli_instance: FreyjaCLI instance for completion functionality (set by FreyjaCLI class)
    """
    self.shell = shell
    self._cli_instance = cli_instance
    self._completion_handler = None

  def install(self, shell: Optional[str] = None, force: bool = False) -> bool:
    """Install shell completion for the current FreyjaCLI.

    :param shell: Shell type (bash/zsh/fish) or auto-detect
    :param force: Force overwrite existing completion
    :return: True if installation successful
    """
    target_shell = shell or self.shell
    result = False

    if not self._cli_instance or not self._cli_instance.enable_completion:
      print("Completion is disabled for this FreyjaCLI.", file=sys.stderr)
    elif not self._completion_handler:
      self.init_completion(target_shell)
      if not self._completion_handler:
        print("Completion handler not available.", file=sys.stderr)

    if self._completion_handler:
      try:
        from freyja.completion.installer import CompletionInstaller

        # Extract program name from sys.argv[0]
        prog_name = os.path.basename(sys.argv[0])
        if prog_name.endswith('.py'):
          prog_name = prog_name[:-3]

        installer = CompletionInstaller(self._completion_handler, prog_name)
        result = installer.install(target_shell, force)
      except ImportError:
        print("Completion installer not available.", file=sys.stderr)

    return result

  def show(self, shell: Optional[str] = None) -> None:
    """Show shell completion script.

    :param shell: Shell type (bash/zsh/fish)
    """
    target_shell = shell or self.shell

    if not self._cli_instance or not self._cli_instance.enable_completion:
      print("Completion is disabled for this FreyjaCLI.", file=sys.stderr)
    else:
      # Initialize completion handler for specific shell
      self.init_completion(target_shell)

      if not self._completion_handler:
        print("Completion handler not available.", file=sys.stderr)
      else:
        # Extract program name from sys.argv[0]
        prog_name = os.path.basename(sys.argv[0])
        if prog_name.endswith('.py'):
          prog_name = prog_name[:-3]

        try:
          script = self._completion_handler.generate_script(prog_name)
          print(script)
        except Exception as e:
          print(f"Error generating completion script: {e}", file=sys.stderr)

  def handle_completion(self) -> None:
    """Handle completion request and exit."""
    exit_code = 0

    if not self._completion_handler:
      self.init_completion()

    if not self._completion_handler:
      exit_code = 1
    else:
      # Parse completion context from command line and environment
      try:
        from freyja.completion.base import CompletionContext

        # Get completion context
        words = sys.argv[:]
        current_word = ""
        cursor_pos = 0

        # Handle --_complete flag
        if '--_complete' in words:
          complete_idx = words.index('--_complete')
          words = words[:complete_idx]  # Remove --_complete and after
          if complete_idx < len(sys.argv) - 1:
            current_word = sys.argv[complete_idx + 1] if complete_idx + 1 < len(sys.argv) else ""

        # Extract command group path
        command_group_path = []
        if len(words) > 1:
          for word in words[1:]:
            if not word.startswith('-'):
              command_group_path.append(word)

        # Create parser for context
        parser = self._cli_instance.create_parser(no_color=True) if self._cli_instance else None

        # Create completion context
        context = CompletionContext(
          words=words,
          current_word=current_word,
          cursor_position=cursor_pos,
          command_group_path=command_group_path,
          parser=parser,
          cli=self._cli_instance
        )

        # Get completions and output them
        completions = self._completion_handler.get_completions(context)
        for completion in completions:
          print(completion)

      except ImportError:
        pass  # Completion module not available

    sys.exit(exit_code)

  def init_completion(self, shell: str = None):
    """Initialize completion handler if enabled.

    :param shell: Target shell (auto-detect if None)
    """
    if not self._cli_instance or not self._cli_instance.enable_completion:
      return

    try:
      from freyja.completion.base import get_completion_handler
      self._completion_handler = get_completion_handler(self._cli_instance, shell)
    except ImportError:
      # Completion module not available
      if self._cli_instance:
        self._cli_instance.enable_completion = False

  def is_completion_request(self) -> bool:
    """Check if this is a completion request."""
    return (
        '--_complete' in sys.argv or
        os.environ.get('_FREYA_COMPLETE') is not None
    )
