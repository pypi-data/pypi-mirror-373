from __future__ import annotations

Primitive = bool | int | float | str | bytes | None
SimpleType = dict | list | Primitive
Simple = dict[str, SimpleType] | list[SimpleType] | SimpleType

class DataStructUtil:
  """ Utility methods for collections (list, dict, set, etc) """

  @classmethod
  def simplify(cls, obj: any, max_depth: int = 10) -> Simple:
    """
    Recursively convert any class or collection to a "simple" representation.

    Args:
        obj: The object to convert
        max_depth: Maximum recursion depth (default 10)

    Returns: A dictionary, list, or primitive value representation of the object
    """

    # Inner methods:
    def safe_str(o: any) -> str:
      try:
        result = str(o)
      except Exception:
        result = f"<{type(o).__name__} object>"

      return result
    def to_prim(o: any, depth: int, seen: set) -> Simple:
      saw: set = seen.union({id(o)})

      if depth >= max_depth:
        # Convert to string at max depth
        result = safe_str(o)
      elif isinstance(o, Primitive):
        # Handle primitive types
        result = o
      elif id(o) in seen:
        # Handle circular references
        result = f"<circular reference: {type(o).__name__}>"
      elif isinstance(o, dict):
        # Handle dict-like objects:
        result = {str(k): to_prim(v, depth + 1, saw) for k, v in o.items()}
      elif isinstance(o, (list, tuple, set, frozenset)):
        # Handle list-like objects:
        result = [to_prim(item, depth + 1, saw) for item in o]
      elif hasattr(o, 'to_dict') and callable(getattr(o, 'to_dict')):
        # Handle Special case for when object has a "to_dict" method:
        result = {str(k): to_prim(v, depth + 1, saw) for k, v in o.to_dict().items()}
      elif hasattr(o, '__dict__') or hasattr(o, '__slots__'):
        # Handle objects with __dict__ or __slots__
        items = o.__dict__.items() \
          if hasattr(o, '__dict__') \
          else [(slot, getattr(o, slot, None)) for slot in o.__slots__ if hasattr(o, slot)]

        # Filter out private attributes and convert to dict:
        result = {str(k): to_prim(v, depth + 1, saw) for k, v in items if not k.startswith('_')}
      else:
        # Fallback for other types (convert to string representation)
        result = safe_str(o)

      return result

    # Call closure above:
    return to_prim(obj, depth=0, seen=set())
