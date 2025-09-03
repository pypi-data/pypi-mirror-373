"""Tests for mod_example.py functionality."""
import subprocess
import sys
from pathlib import Path


class TestModuleExample:
  """Test cases for the mod_example.py file."""

  def test_examples_help(self):
    """Test that mod_example.py shows help without errors."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "mod_example.py"
    result = subprocess.run(
      [sys.executable, str(examples_path), "--help"],
      capture_output=True,
      text=True,
      timeout=10
    )

    assert result.returncode == 0
    assert "Usage:" in result.stdout or "usage:" in result.stdout

  def test_examples_generate_report_command(self):
    """Test the generate-report command in mod_example.py."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "mod_example.py"
    # Create a test file for the command
    test_file = Path("test_data.txt")
    test_file.write_text("line 1\nline 2\nline 3\n")
    
    try:
      result = subprocess.run(
        [sys.executable, str(examples_path), "generate-report", "--data-file", str(test_file)],
        capture_output=True,
        text=True,
        timeout=10
      )

      assert result.returncode == 0
      assert "lines" in result.stdout
    finally:
      # Clean up test file
      if test_file.exists():
        test_file.unlink()

  def test_examples_calculate_statistics_help(self):
    """Test the calculate-statistics command help in mod_example.py."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "mod_example.py"
    result = subprocess.run(
      [sys.executable, str(examples_path), "calculate-statistics", "--help"],
      capture_output=True,
      text=True,
      timeout=10
    )

    assert result.returncode == 0
    assert "numbers" in result.stdout
    assert "precision" in result.stdout

  def test_examples_verify_file_hash_help(self):
    """Test the verify-file-hash command help in mod_example.py."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "mod_example.py"
    result = subprocess.run(
      [sys.executable, str(examples_path), "verify-file-hash", "--help"],
      capture_output=True,
      text=True,
      timeout=10
    )

    assert result.returncode == 0
    assert "file-path" in result.stdout
    assert "algorithm" in result.stdout


class TestClassExample:
  """Test cases for the cls_example.py file."""

  def test_class_example_help(self):
    """Test that cls_example.py shows help without errors."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "cls_example.py"
    result = subprocess.run(
      [sys.executable, str(examples_path), "--help"],
      capture_output=True,
      text=True,
      timeout=10
    )

    assert result.returncode == 0
    assert "Usage:" in result.stdout or "usage:" in result.stdout
    assert "Enhanced data processing utility" in result.stdout

  def test_class_example_process_file(self):
    """Test the file-operations process-single command group in cls_example.py."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "cls_example.py"
    result = subprocess.run(
      [sys.executable, str(examples_path), "file-operations", "process-single", "--input-file", "test.txt"],
      capture_output=True,
      text=True,
      timeout=10
    )

    assert result.returncode == 0
    assert "Processing file: test.txt" in result.stdout

  def test_class_example_config_command(self):
    """Test config-management set-default-mode command group in cls_example.py."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "cls_example.py"
    result = subprocess.run(
      [sys.executable, str(examples_path), "config-management", "set-default-mode", "--mode", "FAST"],
      capture_output=True,
      text=True,
      timeout=10
    )

    assert result.returncode == 0
    assert "Setting default processing mode to: fast" in result.stdout

  def test_class_example_config_help(self):
    """Test that config management cmd_tree are listed in main help."""
    examples_path = Path(__file__).parent.parent.parent / "examples" / "cls_example.py"
    result = subprocess.run(
      [sys.executable, str(examples_path), "--help"],
      capture_output=True,
      text=True,
      timeout=10
    )

    assert result.returncode == 0
    assert "config-management" in result.stdout  # Command group should appear
    assert "set-default-mode" in result.stdout   # Command group command should appear
