"""Comprehensive tests for DataStructUtil."""

import pytest
from freyja.utils.data_struct_util import DataStructUtil


class TestDataStructUtil:
    """Test DataStructUtil.simplify() method comprehensively."""

    def test_primitive_types(self):
        """Test handling of primitive types."""
        # None
        assert DataStructUtil.simplify(None) is None
        
        # Boolean
        assert DataStructUtil.simplify(True) is True
        assert DataStructUtil.simplify(False) is False
        
        # Integer
        assert DataStructUtil.simplify(42) == 42
        assert DataStructUtil.simplify(0) == 0
        assert DataStructUtil.simplify(-123) == -123
        
        # Float
        assert DataStructUtil.simplify(3.14) == 3.14
        assert DataStructUtil.simplify(0.0) == 0.0
        assert DataStructUtil.simplify(-2.5) == -2.5
        
        # String
        assert DataStructUtil.simplify("hello") == "hello"
        assert DataStructUtil.simplify("") == ""
        assert DataStructUtil.simplify("multi\nline") == "multi\nline"
        
        # Bytes
        test_bytes = b"test bytes"
        assert DataStructUtil.simplify(test_bytes) == test_bytes

    def test_empty_collections(self):
        """Test handling of empty collections."""
        assert DataStructUtil.simplify([]) == []
        assert DataStructUtil.simplify(()) == []
        assert DataStructUtil.simplify(set()) == []
        assert DataStructUtil.simplify(frozenset()) == []
        assert DataStructUtil.simplify({}) == {}

    def test_list_types(self):
        """Test handling of list-like collections."""
        # Regular list
        assert DataStructUtil.simplify([1, 2, 3]) == [1, 2, 3]
        
        # Mixed types list
        assert DataStructUtil.simplify([1, "test", True, None]) == [1, "test", True, None]
        
        # Tuple (converted to list)
        assert DataStructUtil.simplify((1, 2, 3)) == [1, 2, 3]
        
        # Set (order may vary, so check contents)
        result = DataStructUtil.simplify({1, 2, 3})
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}
        
        # Frozenset
        result = DataStructUtil.simplify(frozenset([1, 2, 3]))
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}

    def test_nested_lists(self):
        """Test handling of nested list structures."""
        nested = [1, [2, 3], [[4, 5], 6]]
        expected = [1, [2, 3], [[4, 5], 6]]
        assert DataStructUtil.simplify(nested) == expected
        
        # Mixed nested
        mixed_nested = [1, {"key": [2, 3]}, (4, 5)]
        expected = [1, {"key": [2, 3]}, [4, 5]]
        assert DataStructUtil.simplify(mixed_nested) == expected

    def test_dict_types(self):
        """Test handling of dictionary types."""
        # Simple dict
        assert DataStructUtil.simplify({"a": 1, "b": 2}) == {"a": 1, "b": 2}
        
        # Mixed value types
        mixed_dict = {"str": "value", "int": 42, "bool": True, "null": None}
        assert DataStructUtil.simplify(mixed_dict) == mixed_dict
        
        # Non-string keys (converted to string)
        # Note: True and 1 are equivalent in Python dicts, so True overwrites 1
        numeric_keys = {1: "one", 2.5: "two-five", True: "boolean"}
        result = DataStructUtil.simplify(numeric_keys)
        # True overwrites 1 in the original dict, so we expect "boolean" not "one"
        assert result == {"1": "boolean", "2.5": "two-five"}
        
        # Test separate numeric keys that don't conflict
        separate_keys = {2: "two", 3.5: "three-five", "str": "string"}
        result = DataStructUtil.simplify(separate_keys)
        assert result == {"2": "two", "3.5": "three-five", "str": "string"}

    def test_nested_dicts(self):
        """Test handling of nested dictionary structures."""
        nested = {
            "level1": {
                "level2": {
                    "level3": "deep_value"
                },
                "list": [1, 2, 3]
            },
            "simple": "value"
        }
        assert DataStructUtil.simplify(nested) == nested

    def test_max_depth_primitive(self):
        """Test max depth handling with primitive conversion."""
        # Create deeply nested structure
        deep = {"level1": {"level2": {"level3": {"level4": {"level5": "deep"}}}}}
        
        # Test with depth limit of 3
        result = DataStructUtil.simplify(deep, max_depth=3)
        
        # At depth 3, the level4 dict should be converted to string
        assert result["level1"]["level2"]["level3"] == str({"level4": {"level5": "deep"}})

    def test_circular_references(self):
        """Test handling of circular references."""
        # Create circular reference
        circular_dict = {"key": "value"}
        circular_dict["self"] = circular_dict
        
        result = DataStructUtil.simplify(circular_dict)
        assert result["key"] == "value"
        assert result["self"].startswith("<circular reference: dict>")

    def test_circular_references_complex(self):
        """Test complex circular reference scenarios."""
        # Create more complex circular structure
        parent = {"name": "parent", "children": []}
        child = {"name": "child", "parent": parent}
        parent["children"].append(child)
        
        result = DataStructUtil.simplify(parent)
        assert result["name"] == "parent"
        assert len(result["children"]) == 1
        assert result["children"][0]["name"] == "child"
        assert result["children"][0]["parent"].startswith("<circular reference:")

    def test_object_with_dict(self):
        """Test objects with __dict__ attribute."""
        class SimpleClass:
            def __init__(self):
                self.public_attr = "visible"
                self._private_attr = "hidden"
                self.number = 42
        
        obj = SimpleClass()
        result = DataStructUtil.simplify(obj)
        
        # Only public attributes should be included
        assert "public_attr" in result
        assert result["public_attr"] == "visible"
        assert result["number"] == 42
        assert "_private_attr" not in result

    def test_object_with_slots(self):
        """Test objects with __slots__ attribute."""
        class SlottedClass:
            __slots__ = ["public_slot", "_private_slot", "value"]
            
            def __init__(self):
                self.public_slot = "slot_value"
                self._private_slot = "private"
                self.value = 123
        
        obj = SlottedClass()
        result = DataStructUtil.simplify(obj)
        
        # Only public slots should be included
        assert "public_slot" in result
        assert result["public_slot"] == "slot_value"
        assert result["value"] == 123
        assert "_private_slot" not in result

    def test_object_with_to_dict(self):
        """Test objects with to_dict() method."""
        class CustomClass:
            def __init__(self):
                self.attr1 = "value1"
                self.attr2 = "value2"
            
            def to_dict(self):
                return {"custom_key": "custom_value", "attr1": self.attr1}
        
        obj = CustomClass()
        result = DataStructUtil.simplify(obj)
        
        # Should use to_dict() method
        assert result == {"custom_key": "custom_value", "attr1": "value1"}

    def test_object_fallback_string(self):
        """Test objects that fall back to string representation."""
        # Object with __dict__ but empty (most classes have __dict__)
        class MinimalClass:
            pass
        
        obj = MinimalClass()
        result = DataStructUtil.simplify(obj)
        
        # MinimalClass has __dict__ (empty), so it returns empty dict
        assert result == {}
        
        # Test with object that truly has no __dict__ or __slots__
        # Use a built-in type that doesn't have __dict__
        import datetime
        obj = datetime.time(12, 30)  # time objects don't have __dict__ or __slots__
        result = DataStructUtil.simplify(obj)
        
        # Should be converted to string representation
        assert isinstance(result, str)
        assert "12:30" in result

    def test_object_str_exception(self):
        """Test objects that raise exception during str() conversion."""
        # For objects with __dict__ (even empty), they return empty dict
        class ProblematicClass:
            def __str__(self):
                raise ValueError("Cannot convert to string")
        
        obj = ProblematicClass()
        result = DataStructUtil.simplify(obj)
        
        # ProblematicClass has __dict__ (empty), so it returns empty dict
        assert result == {}
        
        # Test actual safe_str exception handling by mocking an object that triggers it
        # This tests the safe_str function's exception handling within DataStructUtil
        import types
        
        # Create a mock object that has no __dict__ or __slots__ but can have str() fail
        # We'll test this by using the max_depth limit to force string conversion
        def create_bad_str_obj():
            class BadStr:
                def __str__(self):
                    raise ValueError("String conversion failed")
            return BadStr()
        
        # Create nested structure that will hit max_depth and try to convert to string
        deep_obj = create_bad_str_obj()
        for i in range(15):  # Create deeper than max_depth (10)
            deep_obj = {"level": deep_obj}
        
        result = DataStructUtil.simplify(deep_obj)
        
        # Navigate to the deep level where str() conversion should have been attempted
        temp = result
        while isinstance(temp, dict) and "level" in temp and isinstance(temp["level"], dict):
            temp = temp["level"]
        
        # At some point, the BadStr object should be converted to safe string
        # Navigate to find the stringified bad object
        found_safe_string = False
        def find_safe_string(obj):
            if isinstance(obj, str) and "BadStr" in obj:
                return True
            elif isinstance(obj, dict):
                return any(find_safe_string(v) for v in obj.values())
            elif isinstance(obj, list):
                return any(find_safe_string(item) for item in obj)
            return False
        
        # The result should contain a safe string representation
        assert find_safe_string(result)

    def test_complex_nested_structure(self):
        """Test complex nested structure with mixed types."""
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age
                self._id = "private"
        
        complex_data = {
            "users": [
                Person("Alice", 30),
                Person("Bob", 25)
            ],
            "settings": {
                "theme": "dark",
                "features": ["feature1", "feature2"],
                "metadata": {
                    "version": 1.0,
                    "enabled": True
                }
            },
            "mixed_list": [
                1, "string", {"nested": "dict"}, [1, 2, 3]
            ]
        }
        
        result = DataStructUtil.simplify(complex_data)
        
        # Verify structure
        assert "users" in result
        assert len(result["users"]) == 2
        assert result["users"][0]["name"] == "Alice"
        assert result["users"][0]["age"] == 30
        assert "_id" not in result["users"][0]  # Private attribute excluded
        
        assert result["settings"]["theme"] == "dark"
        assert result["settings"]["features"] == ["feature1", "feature2"]
        assert result["settings"]["metadata"]["version"] == 1.0
        
        assert result["mixed_list"][0] == 1
        assert result["mixed_list"][1] == "string"
        assert result["mixed_list"][2] == {"nested": "dict"}
        assert result["mixed_list"][3] == [1, 2, 3]

    def test_very_deep_nesting(self):
        """Test very deep nesting beyond max depth."""
        # Create structure deeper than default max_depth (10)
        current = "final_value"
        for i in range(15):
            current = {"level": current}
        
        result = DataStructUtil.simplify(current)
        
        # Should not crash and should convert deep levels to string
        # Navigate down to max depth
        temp = result
        depth = 0
        while isinstance(temp, dict) and "level" in temp and isinstance(temp["level"], dict):
            temp = temp["level"]
            depth += 1
        
        # Should hit max depth before reaching the end
        assert depth < 15

    def test_custom_max_depth(self):
        """Test custom max depth parameter."""
        nested = {"l1": {"l2": {"l3": {"l4": "deep"}}}}
        
        # With max_depth=2
        result = DataStructUtil.simplify(nested, max_depth=2)
        assert result["l1"]["l2"] == str({"l3": {"l4": "deep"}})
        
        # With max_depth=5 (deeper than structure)
        result = DataStructUtil.simplify(nested, max_depth=5)
        assert result["l1"]["l2"]["l3"]["l4"] == "deep"

    def test_mixed_collection_types(self):
        """Test structures with mixed collection types."""
        mixed = {
            "list": [1, 2, 3],
            "tuple": (4, 5, 6),
            "set": {7, 8, 9},
            "frozenset": frozenset([10, 11, 12]),
            "dict": {"inner": "value"}
        }
        
        result = DataStructUtil.simplify(mixed)
        
        assert result["list"] == [1, 2, 3]
        assert result["tuple"] == [4, 5, 6]  # Converted to list
        assert set(result["set"]) == {7, 8, 9}  # Converted to list, order may vary
        assert set(result["frozenset"]) == {10, 11, 12}  # Converted to list
        assert result["dict"] == {"inner": "value"}

    def test_performance_large_structure(self):
        """Test performance with reasonably large structure."""
        # Create a moderately large structure
        large_data = {
            "items": [{"id": i, "value": f"item_{i}"} for i in range(100)],
            "metadata": {
                "count": 100,
                "categories": {f"cat_{i}": list(range(10)) for i in range(10)}
            }
        }
        
        # Should complete without issues
        result = DataStructUtil.simplify(large_data)
        
        assert len(result["items"]) == 100
        assert result["items"][0]["id"] == 0
        assert result["items"][99]["value"] == "item_99"
        assert result["metadata"]["count"] == 100
        assert len(result["metadata"]["categories"]) == 10

    def test_edge_case_empty_slots(self):
        """Test object with empty slots."""
        class EmptySlots:
            __slots__ = []
        
        obj = EmptySlots()
        result = DataStructUtil.simplify(obj)
        
        # Should return empty dict for object with empty slots
        assert result == {}

    def test_edge_case_none_values_in_collections(self):
        """Test collections containing None values."""
        data_with_nones = {
            "list_with_none": [1, None, 3],
            "dict_with_none": {"key": None, "other": "value"},
            "none_key": None
        }
        
        result = DataStructUtil.simplify(data_with_nones)
        
        assert result["list_with_none"] == [1, None, 3]
        assert result["dict_with_none"]["key"] is None
        assert result["dict_with_none"]["other"] == "value"
        assert result["none_key"] is None

    def test_bytes_in_collections(self):
        """Test bytes objects in collections."""
        data_with_bytes = {
            "bytes_list": [b"test", b"bytes"],
            "bytes_value": b"single_bytes",
            "mixed": ["string", b"bytes", 42]
        }
        
        result = DataStructUtil.simplify(data_with_bytes)
        
        assert result["bytes_list"] == [b"test", b"bytes"]
        assert result["bytes_value"] == b"single_bytes"
        assert result["mixed"] == ["string", b"bytes", 42]