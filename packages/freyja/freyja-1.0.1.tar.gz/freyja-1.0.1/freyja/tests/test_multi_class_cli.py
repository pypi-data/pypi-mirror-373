"""Test suite for multi-class FreyjaCLI functionality."""

import pytest

from freyja import FreyjaCLI
from freyja.cli import TargetMode, ClassHandler


class MockDataProcessor:
    """Mock data processor for testing."""

    def __init__(self, config_file: str = "config.json", verbose: bool = False):
        self.config_file = config_file
        self.verbose = verbose

    def process_data(self, input_file: str, format: str = "json") -> str:
        """Process data file."""
        return f"Processed {input_file} as {format} with config {self.config_file}"

    class FileOperations:
        """File operations for data processor."""

        def __init__(self, main, work_dir: str = "./data"):
            self.main = main
            self.work_dir = work_dir

        def cleanup(self, pattern: str = "*") -> str:
            """Clean up files."""
            return f"Cleaned {pattern} in {self.work_dir}"


class MockFileManager:
    """Mock file manager for testing."""

    def __init__(self, base_path: str = "/tmp"):
        self.base_path = base_path

    def list_files(self, directory: str = ".") -> str:
        """List files in directory."""
        return f"Listed files in {directory} from {self.base_path}"

    def process_data(self, input_file: str, format: str = "xml") -> str:
        """Process data file (collision with MockDataProcessor)."""
        return f"FileManager processed {input_file} as {format}"


class MockReportGenerator:
    """Mock report generator for testing."""

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir

    def generate_report(self, report_type: str = "summary") -> str:
        """Generate a report."""
        return f"Generated {report_type} report in {output_dir}"


class TestMultiClassHandler:
    """Test ClassHandler collision detection and command organization."""

    def test_collision_detection(self):
        """Test collision detection between classes with same command names."""
        handler = ClassHandler()

        # Track cmd_tree that will collide (same exact command name)
        handler.track_command("process-data", MockDataProcessor)
        handler.track_command("process-data", MockFileManager)

        # Should detect collision
        assert handler.has_collisions()
        collisions = handler.detect_collisions()
        assert len(collisions) == 1
        assert collisions[0][0] == "process-data"  # Command name that has collision
        assert len(collisions[0][1]) == 2

    def test_no_collision_different_names(self):
        """Test no collision when method names are different."""
        handler = ClassHandler()

        handler.track_command("process-data", MockDataProcessor)
        handler.track_command("list-files", MockFileManager)

        assert not handler.has_collisions()

    def test_command_ordering(self):
        """Test command ordering preserves class order then alphabetical."""
        handler = ClassHandler()

        # Track cmd_tree out of order using clean names
        handler.track_command("list-files", MockFileManager)
        handler.track_command("process-data", MockDataProcessor)
        handler.track_command("analyze", MockDataProcessor)
        handler.track_command("cleanup", MockFileManager)

        class_order = [MockDataProcessor, MockFileManager]
        ordered = handler.get_ordered_commands(class_order)

        # Should be: DataProcessor cmd_tree first (alphabetical), then FileManager cmd_tree (alphabetical)
        expected = [
            "analyze",
            "process-data",
            "cleanup",
            "list-files"
        ]
        assert ordered == expected

    def test_validation_success(self):
        """Test successful validation with no collisions."""
        handler = ClassHandler()

        # Should not raise exception
        handler.validate_classes([MockDataProcessor, MockReportGenerator])

    def test_validation_failure_with_collisions(self):
        """Test validation failure when collisions exist."""
        handler = ClassHandler()

        # Should raise ValueError due to process_data collision
        with pytest.raises(ValueError) as exc_info:
            handler.validate_classes([MockDataProcessor, MockFileManager])

        assert "Command name collisions detected" in str(exc_info.value)
        assert "process-data" in str(exc_info.value)


class TestMultiClassCLI:
    """Test multi-class FreyjaCLI functionality."""

    def test_single_class_in_list(self):
        """Test single class in list behaves like regular class mode."""
        cli = FreyjaCLI([MockDataProcessor], completion=False)

        assert cli.target_mode == TargetMode.CLASS
        assert cli.target_class == MockDataProcessor
        assert cli.target_classes == [MockDataProcessor]  # Unified handling: always a list for classes
        assert "process-data" in cli.commands

    def test_multi_class_mode_detection(self):
        """Test multi-class mode is detected correctly."""
        cli = FreyjaCLI([MockDataProcessor, MockReportGenerator], completion=False)

        assert cli.target_mode == TargetMode.CLASS  # Unified handling: always CLASS for classes
        assert cli.target_class == MockReportGenerator  # Last class is primary
        assert cli.target_classes == [MockDataProcessor, MockReportGenerator]

    def test_collision_detection_with_clean_names(self):
        """Test collision detection when classes have same method names."""
        # Should raise exception since both classes have process_data method
        with pytest.raises(ValueError) as exc_info:
            FreyjaCLI([MockDataProcessor, MockFileManager])

        assert "Command name collisions detected" in str(exc_info.value)
        assert "process-data" in str(exc_info.value)

    def test_multi_class_command_structure(self):
        """Test command structure for multi-class FreyjaCLI."""
        cli = FreyjaCLI([MockDataProcessor, MockReportGenerator])

        # Should have cmd_tree from both classes
        commands = cli.commands

        # Non-primary class (MockDataProcessor) should be in a hierarchical group
        assert "mock-data-processor" in commands
        dp_group = commands["mock-data-processor"]
        assert dp_group['type'] == 'group'
        assert "process-data" in dp_group['cmd_tree']

        # Primary class (MockReportGenerator) cmd_tree should be flat
        assert "generate-report" in commands

        # Commands should be properly structured
        dp_cmd = dp_group['cmd_tree']["process-data"]
        assert dp_cmd['type'] == 'command'
        assert dp_cmd['original_name'] == 'process_data'

    def test_multi_class_with_inner_classes(self):
        """Test multi-class FreyjaCLI with inner classes."""
        cli = FreyjaCLI([MockDataProcessor])

        # Should have both direct methods and inner class methods
        commands = cli.commands

        # Direct method should be present (single class doesn't need class prefix)
        assert "process-data" in commands

        # Inner class group should be present
        assert "file-operations" in commands
        inner_group = commands["file-operations"]
        assert inner_group['type'] == 'group'
        assert 'cleanup' in inner_group['cmd_tree']

    def test_multi_class_title_generation(self):
        """Test title generation for multi-class FreyjaCLI."""
        # Two classes - title should come from the last class (MockReportGenerator)
        cli2 = FreyjaCLI([MockDataProcessor, MockReportGenerator], completion=False)
        assert "Mock report generator for testing" in cli2.title

        # Single class (should use class name or docstring)
        cli1 = FreyjaCLI([MockDataProcessor], completion=False)
        assert "MockDataProcessor" in cli1.title or "mock data processor" in cli1.title.lower()

    def test_multi_class_command_execution(self):
        """Test command structure in multi-class mode."""
        cli = FreyjaCLI([MockDataProcessor, MockReportGenerator], completion=False)

        # Should have cmd_tree from both classes
        commands = cli.commands
        
        # Non-primary class should be in hierarchical group
        assert "mock-data-processor" in commands
        dp_group = commands["mock-data-processor"]
        assert "process-data" in dp_group['cmd_tree']  # From MockDataProcessor
        
        # Primary class should be flat
        assert "generate-report" in commands  # From MockReportGenerator

        # Unified handling: target mode is always CLASS for classes
        assert cli.target_mode.value == 'class'

        # Should be able to create parser successfully
        parser = cli.create_parser()
        assert parser is not None

    def test_backward_compatibility_single_class(self):
        """Test backward compatibility with single class (non-list)."""
        cli = FreyjaCLI(MockDataProcessor, completion=False)

        assert cli.target_mode == TargetMode.CLASS
        assert cli.target_class == MockDataProcessor
        assert cli.target_classes == [MockDataProcessor]  # Unified handling: always a list for classes

    def test_empty_list_validation(self):
        """Test validation of empty class list."""
        with pytest.raises((ValueError, IndexError)):
            FreyjaCLI([])

    def test_invalid_list_items(self):
        """Test validation of list with non-class items."""
        with pytest.raises(ValueError) as exc_info:
            FreyjaCLI([MockDataProcessor, "not_a_class"])

        assert "must be classes" in str(exc_info.value)


class TestCommandExecutorMultiClass:
    """Test multi-class FreyjaCLI functionality at a high level."""

    def test_multi_class_cli_initialization(self):
        """Test that multi-class CLIs initialize correctly."""
        cli = FreyjaCLI([MockDataProcessor, MockReportGenerator], completion=False)

        # Should properly identify target mode and classes
        assert cli.target_mode.value == 'class'
        assert cli.target_class == MockReportGenerator  # Last class is primary
        assert cli.target_classes == [MockDataProcessor, MockReportGenerator]

        # Should have cmd_tree from both classes
        commands = cli.commands
        
        # Non-primary class should be in hierarchical group
        assert "mock-data-processor" in commands
        dp_group = commands["mock-data-processor"]
        assert "process-data" in dp_group['cmd_tree']
        
        # Primary class should be flat
        assert "generate-report" in commands

    def test_single_class_compatibility(self):
        """Test that single class mode works correctly."""
        cli = FreyjaCLI(MockDataProcessor, completion=False)

        # Should properly handle single class
        assert cli.target_mode.value == 'class'
        assert cli.target_class == MockDataProcessor
        assert cli.target_classes == [MockDataProcessor]

        # Should have cmd_tree from the class
        commands = cli.commands
        assert "process-data" in commands


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
