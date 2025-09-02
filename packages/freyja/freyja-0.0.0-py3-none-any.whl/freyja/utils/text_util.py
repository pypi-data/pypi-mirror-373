"""Centralized string utilities for FreyjaCLI generation with caching."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Dict, Sequence
from .data_struct_util import DataStructUtil

class TextUtil:
  """Centralized string conversion utilities with performance optimizations."""

  # Cache for converted strings to avoid repeated operations
  _conversion_cache: Dict[str, str] = {}

  @classmethod
  def json_pretty(cls, obj: any) -> str:
    """ Format any object or collection as a pretty JSON string"""
    return json.dumps(DataStructUtil.simplify(obj), indent=4, sort_keys=True)


  @classmethod
  @lru_cache(maxsize=256)
  def kebab_case(cls, text: str) -> str:
    """
    Convert any string format to kebab-case.

    Handles camelCase, PascalCase, snake_case, and mixed formats.
    FreyjaCLI conventions favor kebab-case for better readability and consistency across shells.
    """
    if not text:
      return text

    # Handle snake_case to kebab-case
    result = text.replace('_', '-')

    # Insert dash before uppercase letters that follow lowercase letters or digits
    # This handles cases like "fooBar" -> "foo-Bar"
    result = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', result)

    # Insert dash before uppercase letters that are followed by lowercase letters
    # This handles cases like "XMLHttpRequest" -> "XML-Http-Request"
    result = re.sub(r'([A-Z])([A-Z][a-z])', r'\1-\2', result)

    return result.lower()

  @classmethod
  @lru_cache(maxsize=256)
  def snake_case(cls, text: str) -> str:
    """Map FreyjaCLI argument names back to Python function parameters.

    Enables seamless integration between FreyjaCLI parsing and function invocation.
    """
    return text.replace('-', '_').lower()

  @classmethod
  def clear_cache(cls) -> None:
    """Reset string conversion cache for testing isolation.

    Prevents test interdependencies by ensuring clean state between test runs.
    """
    TextUtil.kebab_case.cache_clear()
    TextUtil.snake_case.cache_clear()
    TextUtil._conversion_cache.clear()

  @classmethod
  def get_cache_info(cls, **kwarg) -> dict:
    """Get cache statistics for performance monitoring."""
    return {
      'kebab_case': cls.kebab_case.cache_info()._asdict(),
      'kebab_to_snake': cls.snake_case.cache_info()._asdict(),
      'conversion_cache_size': len(cls._conversion_cache)
    }
