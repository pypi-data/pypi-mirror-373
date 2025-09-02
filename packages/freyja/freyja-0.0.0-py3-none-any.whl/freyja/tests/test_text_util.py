"""Comprehensive tests for TextUtil."""

import json
import pytest
from freyja.utils import TextUtil


class TestTextUtil:
    """Comprehensive test cases for TextUtil class."""

    def setup_method(self):
        """Clear cache before each test for isolation."""
        TextUtil.clear_cache()

    # ========================================
    # kebab_case() tests
    # ========================================

    def test_kebab_case_pascal_case(self):
        """Test conversion of PascalCase strings."""
        assert TextUtil.kebab_case("FooBarBaz") == "foo-bar-baz"
        assert TextUtil.kebab_case("XMLHttpRequest") == "xml-http-request"
        assert TextUtil.kebab_case("HTMLParser") == "html-parser"

    def test_kebab_case_camel_case(self):
        """Test conversion of camelCase strings."""
        assert TextUtil.kebab_case("fooBarBaz") == "foo-bar-baz"
        assert TextUtil.kebab_case("getUserName") == "get-user-name"
        assert TextUtil.kebab_case("processDataFiles") == "process-data-files"

    def test_kebab_case_single_word(self):
        """Test single word inputs."""
        assert TextUtil.kebab_case("simple") == "simple"
        assert TextUtil.kebab_case("SIMPLE") == "simple"
        assert TextUtil.kebab_case("Simple") == "simple"

    def test_kebab_case_with_numbers(self):
        """Test strings containing numbers."""
        assert TextUtil.kebab_case("foo2Bar") == "foo2-bar"
        assert TextUtil.kebab_case("getV2APIResponse") == "get-v2-api-response"
        assert TextUtil.kebab_case("parseHTML5Document") == "parse-html5-document"

    def test_kebab_case_already_kebab_case(self):
        """Test strings that are already in kebab-case."""
        assert TextUtil.kebab_case("foo-bar-baz") == "foo-bar-baz"
        assert TextUtil.kebab_case("simple-case") == "simple-case"

    def test_kebab_case_edge_cases(self):
        """Test edge cases."""
        assert TextUtil.kebab_case("") == ""
        assert TextUtil.kebab_case("A") == "a"
        assert TextUtil.kebab_case("AB") == "ab"
        assert TextUtil.kebab_case("ABC") == "abc"

    def test_kebab_case_consecutive_capitals(self):
        """Test strings with consecutive capital letters."""
        assert TextUtil.kebab_case("JSONParser") == "json-parser"
        assert TextUtil.kebab_case("XMLHTTPRequest") == "xmlhttp-request"
        assert TextUtil.kebab_case("PDFDocument") == "pdf-document"

    def test_kebab_case_mixed_separators(self):
        """Test strings with existing separators."""
        assert TextUtil.kebab_case("foo_bar_baz") == "foo-bar-baz"
        assert TextUtil.kebab_case("FooBar_Baz") == "foo-bar-baz"

    def test_kebab_case_snake_case_input(self):
        """Test conversion from snake_case."""
        assert TextUtil.kebab_case("snake_case_string") == "snake-case-string"
        assert TextUtil.kebab_case("long_snake_case_name") == "long-snake-case-name"
        assert TextUtil.kebab_case("_leading_underscore") == "-leading-underscore"
        assert TextUtil.kebab_case("trailing_underscore_") == "trailing-underscore-"

    def test_kebab_case_special_characters(self):
        """Test strings with special characters."""
        assert TextUtil.kebab_case("foo-bar") == "foo-bar"  # Already kebab
        assert TextUtil.kebab_case("foo--bar") == "foo--bar"  # Double dash preserved
        assert TextUtil.kebab_case("foo__bar") == "foo--bar"  # Double underscore to double dash

    # ========================================
    # snake_case() tests  
    # ========================================

    def test_snake_case_kebab_input(self):
        """Test conversion from kebab-case to snake_case."""
        assert TextUtil.snake_case("foo-bar-baz") == "foo_bar_baz"
        assert TextUtil.snake_case("simple-case") == "simple_case"
        assert TextUtil.snake_case("get-user-name") == "get_user_name"

    def test_snake_case_already_snake(self):
        """Test strings already in snake_case."""
        assert TextUtil.snake_case("already_snake") == "already_snake"
        assert TextUtil.snake_case("simple_case") == "simple_case"

    def test_snake_case_mixed_input(self):
        """Test mixed format input."""
        assert TextUtil.snake_case("CamelCase") == "camelcase"  # No dashes to convert
        assert TextUtil.snake_case("mixed-Format_String") == "mixed_format_string"

    def test_snake_case_edge_cases(self):
        """Test edge cases for snake_case."""
        assert TextUtil.snake_case("") == ""
        assert TextUtil.snake_case("single") == "single"
        assert TextUtil.snake_case("UPPER") == "upper"
        assert TextUtil.snake_case("Multiple-Dash-String") == "multiple_dash_string"

    def test_snake_case_special_characters(self):
        """Test snake_case with special characters."""
        assert TextUtil.snake_case("foo--bar") == "foo__bar"  # Double dash to double underscore
        assert TextUtil.snake_case("-leading-dash") == "_leading_dash"
        assert TextUtil.snake_case("trailing-dash-") == "trailing_dash_"

    # ========================================
    # json_pretty() tests
    # ========================================

    def test_json_pretty_simple_dict(self):
        """Test json_pretty with simple dictionary."""
        data = {"name": "Alice", "age": 30}
        result = TextUtil.json_pretty(data)
        
        # Parse back to verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == data
        
        # Check formatting (should be indented)
        assert "    " in result  # Should have 4-space indentation
        assert "\n" in result    # Should have newlines

    def test_json_pretty_complex_structure(self):
        """Test json_pretty with complex nested structure."""
        data = {
            "users": [
                {"name": "Alice", "active": True},
                {"name": "Bob", "active": False}
            ],
            "settings": {
                "theme": "dark",
                "count": 42
            }
        }
        
        result = TextUtil.json_pretty(data)
        parsed = json.loads(result)
        
        assert parsed["users"][0]["name"] == "Alice"
        assert parsed["settings"]["theme"] == "dark"
        assert parsed["settings"]["count"] == 42

    def test_json_pretty_primitive_values(self):
        """Test json_pretty with primitive values."""
        assert json.loads(TextUtil.json_pretty(42)) == 42
        assert json.loads(TextUtil.json_pretty("string")) == "string"
        assert json.loads(TextUtil.json_pretty(True)) is True
        assert json.loads(TextUtil.json_pretty(None)) is None

    def test_json_pretty_custom_object(self):
        """Test json_pretty with custom objects (uses DataStructUtil)."""
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age
                self._private = "hidden"
        
        person = Person("Alice", 30)
        result = TextUtil.json_pretty(person)
        parsed = json.loads(result)
        
        # Should use DataStructUtil.simplify()
        assert parsed["name"] == "Alice"
        assert parsed["age"] == 30
        assert "_private" not in parsed  # Private attributes excluded

    def test_json_pretty_empty_collections(self):
        """Test json_pretty with empty collections."""
        assert json.loads(TextUtil.json_pretty([])) == []
        assert json.loads(TextUtil.json_pretty({})) == {}

    def test_json_pretty_sorted_keys(self):
        """Test that json_pretty sorts keys."""
        data = {"z": 1, "a": 2, "m": 3}
        result = TextUtil.json_pretty(data)
        
        # Keys should be sorted alphabetically in output
        lines = result.split('\n')
        key_lines = [line for line in lines if '"' in line and ':' in line]
        
        # Extract keys and verify order
        keys = []
        for line in key_lines:
            key = line.split('"')[1]  # Extract key from "key": value
            keys.append(key)
        
        assert keys == sorted(keys)

    # ========================================
    # Cache functionality tests
    # ========================================

    def test_cache_behavior_kebab_case(self):
        """Test that kebab_case uses LRU cache."""
        # Clear cache first
        TextUtil.clear_cache()
        
        # First call should cache the result
        result1 = TextUtil.kebab_case("TestString")
        cache_info = TextUtil.kebab_case.cache_info()
        assert cache_info.hits == 0
        assert cache_info.misses == 1
        
        # Second call should hit cache
        result2 = TextUtil.kebab_case("TestString")
        cache_info = TextUtil.kebab_case.cache_info()
        assert cache_info.hits == 1
        assert cache_info.misses == 1
        assert result1 == result2

    def test_cache_behavior_snake_case(self):
        """Test that snake_case uses LRU cache."""
        # Clear cache first  
        TextUtil.clear_cache()
        
        # First call should cache the result
        result1 = TextUtil.snake_case("test-string")
        cache_info = TextUtil.snake_case.cache_info()
        assert cache_info.hits == 0
        assert cache_info.misses == 1
        
        # Second call should hit cache
        result2 = TextUtil.snake_case("test-string")
        cache_info = TextUtil.snake_case.cache_info()
        assert cache_info.hits == 1
        assert cache_info.misses == 1
        assert result1 == result2

    def test_clear_cache_functionality(self):
        """Test clear_cache() method."""
        # Generate some cache entries
        TextUtil.kebab_case("TestString1")
        TextUtil.kebab_case("TestString2")
        TextUtil.snake_case("test-string-1")
        TextUtil.snake_case("test-string-2")
        
        # Verify cache has entries
        kebab_info = TextUtil.kebab_case.cache_info()
        snake_info = TextUtil.snake_case.cache_info()
        assert kebab_info.misses > 0
        assert snake_info.misses > 0
        
        # Clear cache
        TextUtil.clear_cache()
        
        # Verify cache is cleared
        kebab_info = TextUtil.kebab_case.cache_info()
        snake_info = TextUtil.snake_case.cache_info()
        assert kebab_info.hits == 0
        assert kebab_info.misses == 0
        assert snake_info.hits == 0 
        assert snake_info.misses == 0

    def test_get_cache_info(self):
        """Test get_cache_info() method."""
        # Clear and populate cache
        TextUtil.clear_cache()
        TextUtil.kebab_case("TestString")
        TextUtil.snake_case("test-string")
        
        cache_info = TextUtil.get_cache_info()
        
        # Should return dictionary with cache statistics
        assert isinstance(cache_info, dict)
        assert "kebab_case" in cache_info
        assert "kebab_to_snake" in cache_info
        assert "conversion_cache_size" in cache_info
        
        # Verify structure of cache info
        assert "hits" in cache_info["kebab_case"]
        assert "misses" in cache_info["kebab_case"]
        assert "hits" in cache_info["kebab_to_snake"]
        assert "misses" in cache_info["kebab_to_snake"]
        
        # Verify counts
        assert cache_info["kebab_case"]["misses"] == 1
        assert cache_info["kebab_to_snake"]["misses"] == 1

    def test_cache_isolation_between_methods(self):
        """Test that different methods have separate caches."""
        TextUtil.clear_cache()
        
        # Call each method
        TextUtil.kebab_case("TestString")
        TextUtil.snake_case("test-string")
        
        # Each should have separate cache entries
        kebab_info = TextUtil.kebab_case.cache_info()
        snake_info = TextUtil.snake_case.cache_info()
        
        assert kebab_info.misses == 1
        assert snake_info.misses == 1
        assert kebab_info.hits == 0
        assert snake_info.hits == 0

    # ========================================
    # Integration and cross-method tests
    # ========================================

    def test_kebab_to_snake_roundtrip(self):
        """Test converting kebab to snake and back."""
        original = "getUserData"
        kebab = TextUtil.kebab_case(original)
        snake = TextUtil.snake_case(kebab)
        
        assert kebab == "get-user-data"
        assert snake == "get_user_data"

    def test_json_pretty_integration_with_data_struct_util(self):
        """Test json_pretty integration with complex objects."""
        class NestedClass:
            def __init__(self):
                self.public = "visible"
                self._private = "hidden"
                self.nested_list = [1, 2, {"inner": "value"}]
        
        obj = NestedClass()
        result = TextUtil.json_pretty(obj)
        parsed = json.loads(result)
        
        # Verify DataStructUtil integration
        assert parsed["public"] == "visible"
        assert "_private" not in parsed
        assert parsed["nested_list"][2]["inner"] == "value"

    def test_edge_case_unicode_strings(self):
        """Test handling of unicode strings."""
        unicode_string = "café_naïve_résumé"
        
        kebab_result = TextUtil.kebab_case(unicode_string)
        snake_result = TextUtil.snake_case(kebab_result)
        
        assert kebab_result == "café-naïve-résumé"
        assert snake_result == "café_naïve_résumé"

    def test_very_long_strings(self):
        """Test handling of very long strings."""
        long_string = "very" + "Long" * 100 + "StringName"
        
        kebab_result = TextUtil.kebab_case(long_string)
        assert kebab_result.startswith("very-long")
        assert kebab_result.endswith("-string-name")
        assert len(kebab_result) > 400  # Should be quite long

    def test_performance_cache_benefits(self):
        """Test that cache provides performance benefits."""
        TextUtil.clear_cache()
        
        # Perform many operations with repeated strings
        test_strings = ["TestString", "AnotherTest", "ThirdTest"] * 10
        
        for s in test_strings:
            TextUtil.kebab_case(s)
        
        cache_info = TextUtil.kebab_case.cache_info()
        
        # Should have more hits than misses due to repetition
        assert cache_info.hits > cache_info.misses
        assert cache_info.hits > 20  # Many repeated calls should hit cache

    def test_all_methods_with_empty_string(self):
        """Test all methods handle empty strings properly."""
        assert TextUtil.kebab_case("") == ""
        assert TextUtil.snake_case("") == ""
        assert TextUtil.json_pretty("") == '""'  # JSON string

    def test_all_methods_with_none_handling(self):
        """Test methods that might receive None (json_pretty only)."""
        # Only json_pretty should handle None input (via DataStructUtil)
        assert TextUtil.json_pretty(None) == "null"
        
        # kebab_case returns None for None input (early return on falsy)
        assert TextUtil.kebab_case(None) is None
        
        # snake_case raises AttributeError for None input
        with pytest.raises(AttributeError):
            TextUtil.snake_case(None)
