"""Tests for class-based FreyjaCLI functionality."""
import enum
from pathlib import Path

import pytest

from freyja import FreyjaCLI
from freyja.cli import TargetMode


class SampleEnum(enum.Enum):
  """Sample enum for class-based FreyjaCLI testing."""
  OPTION_A = "a"
  OPTION_B = "b"


class SampleClass:
  """Sample class for testing FreyjaCLI generation."""

  def __init__(self):
    """Initialize sample class."""
    self.state = "initialized"

  def simple_method(self, name: str = "world"):
    """Simple method with default parameter.

    :param name: Name to use in greeting
    """
    return f"Hello {name} from method!"

  def method_with_types(self, text: str, number: int = 42,
                        active: bool = False, choice: SampleEnum = SampleEnum.OPTION_A,
                        file_path: Path = None):
    """Method with various type annotations.

    :param text: Required text parameter
    :param number: Optional number parameter
    :param active: Boolean flag parameter
    :param choice: Enum choice parameter
    :param file_path: Optional file path parameter
    """
    return {
      'text': text,
      'number': number,
      'active': active,
      'choice': choice,
      'file_path': file_path,
      'state': self.state
    }

  def hierarchical__nested__command(self, value: str):
    """Nested hierarchical method.

    :param value: Value to process
    """
    return f"Hierarchical: {value} (state: {self.state})"

  def method_without_docstring(self, param: str):
    """Method without parameter docstrings for testing."""
    return f"No docstring method: {param}"


class SampleClassWithComplexInit:
  """Class that requires constructor parameters (should fail)."""

  def __init__(self, required_param: str):
    """Initialize with required parameter."""
    self.required_param = required_param

  def some_method(self):
    """Some method that won't be accessible via FreyjaCLI."""
    return "This shouldn't work"


class TestClassBasedCLI:
  """Test class-based FreyjaCLI functionality."""

  def test_from_class_creation(self):
    """Test FreyjaCLI creation from class."""
    cli = FreyjaCLI(SampleClass)

    assert cli.target_mode == TargetMode.CLASS
    assert cli.target_class == SampleClass
    assert cli.title == "Sample class for testing FreyjaCLI generation."  # From docstring
    assert 'simple-method' in cli.commands
    assert 'method-with-types' in cli.commands
    assert cli.target_module is None

  def test_from_class_with_custom_title(self):
    """Test FreyjaCLI creation with custom title."""
    cli = FreyjaCLI(SampleClass, title="Custom Title")
    assert cli.title == "Custom Title"

  def test_from_class_without_docstring(self):
    """Test FreyjaCLI creation from class without docstring."""

    class NoDocClass:
      def __init__(self):
        pass

      def method(self):
        return "test"

    cli = FreyjaCLI(NoDocClass)
    assert cli.title == "NoDocClass"  # Falls back to class name

  def test_method_discovery(self):
    """Test automatic method discovery."""
    cli = FreyjaCLI(SampleClass)

    # Should include public methods (converted to kebab-case)
    assert 'simple-method' in cli.commands
    assert 'method-with-types' in cli.commands
    assert 'method-without-docstring' in cli.commands

    # Should not include private methods or special methods
    command_names = list(cli.commands.keys())
    
    # Check that cmd_tree have proper structure
    for command_name, command_info in cli.commands.items():
      if command_info.get('type') == 'command':
        assert callable(command_info.get('function'))
      assert not command_name.startswith('_')  # No private methods in cmd_tree  # Methods should be callable

  def test_method_execution(self):
    """Test method execution through FreyjaCLI."""
    cli = FreyjaCLI(SampleClass)

    result = cli.run(['simple-method', '--name', 'Alice'])
    assert result == "Hello Alice from method!"

  def test_method_execution_with_defaults(self):
    """Test method execution with default parameters."""
    cli = FreyjaCLI(SampleClass)

    result = cli.run(['simple-method'])
    assert result == "Hello world from method!"

  def test_method_with_types_execution(self):
    """Test method execution with type annotations."""
    cli = FreyjaCLI(SampleClass)

    result = cli.run(['method-with-types', '--text', 'test'])
    assert result['text'] == 'test'
    assert result['number'] == 42  # default
    assert result['active'] is False  # default
    assert result['choice'] == SampleEnum.OPTION_A  # default
    assert result['state'] == 'initialized'  # From class instance

  def test_method_with_all_parameters(self):
    """Test method execution with all parameters specified."""
    cli = FreyjaCLI(SampleClass)

    result = cli.run([
      'method-with-types',
      '--text', 'hello',
      '--number', '123',
      '--active',
      '--choice', 'OPTION_B',
      '--file-path', '/tmp/test.txt'
    ])

    assert result['text'] == 'hello'
    assert result['number'] == 123
    assert result['active'] is True
    assert result['choice'] == SampleEnum.OPTION_B
    assert isinstance(result['file_path'], Path)
    assert str(result['file_path']) == '/tmp/test.txt'

  def test_hierarchical_methods(self):
    """Test that dunder notation is converted to flat command for class methods."""
    cli = FreyjaCLI(SampleClass)

    # Dunder notation should now create a flat command with underscores converted to dashes
    result = cli.run(['hierarchical--nested--command', '--value', 'test'])
    assert "Hierarchical: test" in result
    assert "(state: initialized)" in result

  def test_parser_creation_from_class(self):
    """Test parser creation from class methods."""
    cli = FreyjaCLI(SampleClass)
    parser = cli.create_parser()

    help_text = parser.format_help()
    assert "Sample class for testing FreyjaCLI generation." in help_text
    assert "simple-method" in help_text
    assert "method-with-types" in help_text

  def test_class_instantiation_error(self):
    """Test error handling for classes that can't be instantiated."""
    with pytest.raises(ValueError, match="parameters without default values"):
      FreyjaCLI(SampleClassWithComplexInit)

  def test_custom_method_filter(self):
    """Test custom method filter functionality."""

    def only_simple_method(target_class, name, obj):
      return name == 'simple_method'

    cli = FreyjaCLI(SampleClass, method_filter=only_simple_method)
    # Should only have simple-method (converted to kebab-case)
    assert 'simple-method' in cli.commands
    # Count actual command entries (filter out groups)
    command_count = len([k for k, v in cli.commands.items() if v.get('type') == 'command'])
    assert command_count == 1

  def test_theme_tuner_integration(self):
    """Test that theme tuner is now provided by System class."""
    # Theme tuner functionality is now in System class, not injected into FreyjaCLI
    from freyja.cli.system import System
    cli = FreyjaCLI(System)

    # System class uses inner class pattern, so should have hierarchical cmd_tree
    assert 'tune-theme' in cli.commands
    assert cli.commands['tune-theme']['type'] == 'group'
    assert 'increase-adjustment' in cli.commands['tune-theme']['cmd_tree']

  def test_completion_integration(self):
    """Test that completion works with class-based FreyjaCLI."""
    cli = FreyjaCLI(SampleClass, completion=True)

    assert cli.enable_completion is True

  def test_method_without_docstring_parameters(self):
    """Test method without parameter docstrings."""
    cli = FreyjaCLI(SampleClass)

    result = cli.run(['method-without-docstring', '--param', 'test'])
    assert result == "No docstring method: test"



class TestClassVsModuleComparison:
  """Test that class and module modes have feature parity."""

  def test_type_annotation_parity(self):
    """Test that type annotations work the same for classes and modules."""
    import freyja.tests.conftest as sample_module

    # Module-based FreyjaCLI
    cli_module = FreyjaCLI(sample_module, "Module FreyjaCLI")

    # Class-based FreyjaCLI
    cli_class = FreyjaCLI(SampleClass, "Class FreyjaCLI")

    # Both should handle types correctly
    module_result = cli_module.run(['function-with-types', '--text', 'test', '--number', '456'])
    class_result = cli_class.run(['method-with-types', '--text', 'test', '--number', '456'])

    assert module_result['text'] == class_result['text']
    assert module_result['number'] == class_result['number']

  def test_hierarchical_command_parity(self):
    """Test that dunder notation creates flat cmd_tree for both classes and modules."""
    # Dunder notation should create flat cmd_tree with double dashes
    cli = FreyjaCLI(SampleClass)

    result = cli.run(['hierarchical--nested--command', '--value', 'test'])
    assert "Hierarchical: test" in result

  def test_help_generation_parity(self):
    """Test that help generation works similarly for classes and modules."""
    import freyja.tests.conftest as sample_module

    cli_module = FreyjaCLI(sample_module, "Module FreyjaCLI")
    cli_class = FreyjaCLI(SampleClass, "Class FreyjaCLI")

    module_help = cli_module.create_parser().format_help()
    class_help = cli_class.create_parser().format_help()

    # Both should contain their respective titles
    assert "Module FreyjaCLI" in module_help
    assert "Class FreyjaCLI" in class_help

    # Both should have similar structure
    assert "COMMANDS" in module_help
    assert "COMMANDS" in class_help


class TestErrorHandling:
  """Test error handling for class-based FreyjaCLI."""

  def test_missing_required_parameter(self):
    """Test error handling for missing required parameters."""
    cli = FreyjaCLI(SampleClass)

    # Should raise SystemExit for missing required parameter
    with pytest.raises(SystemExit):
      cli.run(['method-with-types'])  # Missing required --text

  def test_invalid_enum_value(self):
    """Test error handling for invalid enum values."""
    cli = FreyjaCLI(SampleClass)

    with pytest.raises(SystemExit):
      cli.run(['method-with-types', '--text', 'test', '--choice', 'INVALID'])

  def test_invalid_type_conversion(self):
    """Test error handling for invalid type conversions."""
    cli = FreyjaCLI(SampleClass)

    with pytest.raises(SystemExit):
      cli.run(['method-with-types', '--text', 'test', '--number', 'not_a_number'])


class TestEdgeCases:
  """Test edge cases for class-based FreyjaCLI."""

  def test_empty_class(self):
    """Test FreyjaCLI creation from class with no public methods."""

    class EmptyClass:
      def __init__(self):
        pass

    cli = FreyjaCLI(EmptyClass)
    # Should have no cmd_tree (only __init__ is excluded)
    command_count = len([k for k, v in cli.commands.items() if v.get('type') == 'command'])
    assert command_count == 0

  def test_class_with_only_private_methods(self):
    """Test class with only private methods."""

    class PrivateMethodsClass:
      def __init__(self):
        pass

      def _private_method(self):
        return "private"

      def __special_method__(self):
        return "special"

    cli = FreyjaCLI(PrivateMethodsClass)
    # Should have no public methods
    command_count = len([k for k, v in cli.commands.items() if v.get('type') == 'command'])
    assert command_count == 0

  def test_class_with_property(self):
    """Test that properties are not included as methods."""

    class ClassWithProperty:
      def __init__(self):
        self._value = 42

      @property
      def value(self):
        return self._value

      def method(self):
        return "method"

    cli = FreyjaCLI(ClassWithProperty)
    assert 'method' in cli.commands
    assert 'value' not in cli.commands  # Property should not be included


class SampleClassWithDefaults:
  """Class with constructor parameters that have defaults (should work)."""

  def __init__(self, config_file: str = "config.json", debug: bool = False):
    """Initialize with parameters that have defaults."""
    self.config_file = config_file
    self.debug = debug

  def test_method(self, message: str = "hello"):
    """Test method."""
    return f"Config: {self.config_file}, Debug: {self.debug}, Message: {message}"


class SampleClassWithInnerClasses:
  """Class with inner classes for hierarchical cmd_tree."""

  def __init__(self, base_config: str = "base.json"):
    """Initialize with base configuration."""
    self.base_config = base_config

  class GoodInnerClass:
    """Inner class with parameters that have defaults (should work)."""

    def __init__(self, database_url: str = "sqlite:///test.db"):
      self.database_url = database_url

    def create_item(self, name: str):
      """Create an item."""
      return f"Creating {name} with DB: {self.database_url}"


class TestConstructorParameterValidation:
  """Test constructor parameter validation for both patterns."""

  def test_direct_method_class_with_defaults_succeeds(self):
    """Test that class with default constructor parameters works for direct method pattern."""
    # Should work because all parameters have defaults
    cli = FreyjaCLI(SampleClassWithDefaults)
    assert cli.target_mode == TargetMode.CLASS
    # Should have the test method available as a command
    assert 'test-method' in cli.commands

  def test_direct_method_class_without_defaults_fails(self):
    """Test that class with required constructor parameters fails for direct method pattern."""
    # Should fail because constructor has required parameter
    with pytest.raises(ValueError, match="parameters without default values"):
      FreyjaCLI(SampleClassWithComplexInit)

  def test_inner_class_pattern_with_good_constructors_succeeds(self):
    """Test that inner class pattern works when all constructors have default parameters."""
    # Should work because both main class and inner class have defaults
    cli = FreyjaCLI(SampleClassWithInnerClasses)
    assert cli.target_mode == TargetMode.CLASS
    # Inner class methods become hierarchical cmd_tree with proper nesting
    assert 'good-inner-class' in cli.commands
    assert cli.commands['good-inner-class']['type'] == 'group'
    assert 'create-item' in cli.commands['good-inner-class']['cmd_tree']

  def test_inner_class_pattern_with_bad_inner_class_fails(self):
    """Test that inner class pattern fails when inner class has required parameters."""

    # Create a class with bad inner class
    class ClassWithBadInner:
      def __init__(self, config: str = "test.json"):
        pass

      class BadInner:
        def __init__(self, required: str):  # No default!
          pass

        def method(self):
          pass

    # Should fail because inner class constructor has required parameter
    with pytest.raises(ValueError, match="Constructor for inner class.*parameters without default values"):
      FreyjaCLI(ClassWithBadInner)

  def test_inner_class_pattern_with_bad_main_class_fails(self):
    """Test that inner class pattern fails when main class has required parameters."""

    # Create a class with bad main constructor
    class ClassWithBadMain:
      def __init__(self, required: str):  # No default!
        pass

      class GoodInner:
        def __init__(self, config: str = "test.json"):
          pass

        def method(self):
          pass

    # Should fail because main class constructor has required parameter
    with pytest.raises(ValueError, match="Constructor for main class.*parameters without default values"):
      FreyjaCLI(ClassWithBadMain)
