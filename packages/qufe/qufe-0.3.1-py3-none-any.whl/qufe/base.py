import os
import importlib.util as ut
from datetime import datetime
from zoneinfo import ZoneInfo
import difflib


class TS:
    """Timestamp handling utility class with timezone support."""
    
    def __init__(self, time_zone: str = 'Asia/Seoul'):
        """
        Initialize timestamp handler.
        
        Args:
            time_zone: Timezone string (default: 'Asia/Seoul')
        """
        self.time_zone = time_zone
        self.tz_info = ZoneInfo(time_zone)
        self.time_format = '%Y-%m-%d %H:%M:%S'

    def timestamp_to_datetime(self, timestamp) -> datetime:
        """
        Convert timestamp to datetime object with timezone.
        
        Args:
            timestamp: Unix timestamp (int/float) or datetime object
            
        Returns:
            datetime object with timezone or None if invalid input
            
        Example:
            >>> ts = TS()
            >>> dt = ts.timestamp_to_datetime(1640995200)  # 2022-01-01 00:00:00 UTC
        """
        match timestamp:
            case int() | float():
                return datetime.fromtimestamp(timestamp, tz=self.tz_info)
            case datetime():
                return timestamp
            case _:
                return None

    def get_ts_formatted(self, timestamp) -> str:
        """
        Get formatted timestamp string.
        
        Args:
            timestamp: Unix timestamp or datetime object
            
        Returns:
            Formatted timestamp string or None if invalid
            
        Example:
            >>> ts = TS()
            >>> formatted = ts.get_ts_formatted(1640995200)
            >>> print(formatted)  # '2022-01-01 09:00:00'
        """
        if isinstance(timestamp, int | float):
            timestamp = self.timestamp_to_datetime(timestamp)
        
        if isinstance(timestamp, datetime):
            return timestamp.strftime(self.time_format)
        else:
            return None


def diff_codes(left: str, right: str, mode: int = 0):
    """
    Compare two code strings with different diff formats.
    
    Args:
        left: Left code string to compare
        right: Right code string to compare  
        mode: Comparison mode (0=simple, 1=unified, 2=ndiff)
        
    Example:
        >>> diff_codes("line1\nline2", "line1\nmodified", mode=1)
    """
    left_lines = left.splitlines()
    right_lines = right.splitlines()

    match mode:
        case 0:
            print("\n=== simple mode ===\n")
            # Simple line-by-line comparison
            for i, (l, r) in enumerate(zip(left_lines, right_lines), start=1):
                if l != r:
                    print(f"Difference found at line {i}:")
                    print(f"Left: {l}")
                    print(f"Right: {r}")
                    print()
            # Handle different line counts
            if len(left_lines) > len(right_lines):
                print("Additional lines in left code:")
                for i, l in enumerate(left_lines[len(right_lines):], start=len(right_lines)+1):
                    print(f"Line {i}: {l}")
            elif len(right_lines) > len(left_lines):
                print("Additional lines in right code:")
                for i, r in enumerate(right_lines[len(left_lines):], start=len(left_lines)+1):
                    print(f"Line {i}: {r}")
        case 1:
            print("\n=== unified mode ===\n")
            # Unified diff format
            diff = difflib.unified_diff(
                left_lines, right_lines,
                fromfile='left', tofile='right',
                lineterm=''
            )
            print("\n".join(diff))
        case 2:
            print("\n=== ndiff mode ===")
            # Detailed ndiff format
            diff = difflib.ndiff(left_lines, right_lines)
            print("\n".join(diff))
        case _:
            print("Unsupported mode. Please choose 0 (simple), 1 (unified), or 2 (ndiff).")

 
def import_script(script_name: str, script_path: str):
    """
    Dynamically import a Python module from file path.
    
    Args:
        script_name: Name for the imported module
        script_path: Path to the Python file to import
        
    Returns:
        Imported module object
        
    Example:
        >>> module = import_script("my_module", "/path/to/script.py")
        >>> module.some_function()
    """
    module_spec = ut.spec_from_file_location(script_name, script_path)
    module = ut.module_from_spec(module_spec)
 
    module_dir = os.path.dirname(script_path)
    prev_cwd = os.getcwd()
    os.chdir(module_dir)
 
    try:
        module_spec.loader.exec_module(module)
    finally:
        os.chdir(prev_cwd)
 
    return module


def flatten(lst, max_depth=1, current_depth=0):
    """
    Flatten nested lists up to a specified depth.
    
    Args:
        lst: The list to flatten
        max_depth: Maximum depth to flatten (default: 1)
        current_depth: Current recursion depth (internal use)
        
    Returns:
        Flattened list
        
    Example:
        >>> flatten([1, [2, [3, 4], 5], [6, 7], 8])
        [1, 2, 3, 4, 5, 6, 7, 8]
    """
    result = []
    for item in lst:
        if isinstance(item, list) and current_depth < max_depth:
            result.extend(flatten(item, max_depth, current_depth + 1))
        else:
            result.append(item)
    return result


def flatten_gen(lst, max_depth=1, current_depth=0):
    """
    Flatten nested lists using generator (memory efficient).
    
    Args:
        lst: The list to flatten
        max_depth: Maximum depth to flatten (default: 1)
        current_depth: Current recursion depth (internal use)
        
    Yields:
        Flattened items one by one
        
    Example:
        >>> list(flatten_gen([1, [2, [3, [4]], 5]]))
        [1, 2, 3, 4, 5]
    """
    for item in lst:
        if isinstance(item, list) and current_depth < max_depth:
            yield from flatten_gen(item, max_depth, current_depth + 1)
        else:
            yield item


def flatten_any(nested, max_depth=1, current_depth=0):
    """
    Flatten nested collections (list, tuple, set) up to specified depth.
    
    Args:
        nested: The nested collection to flatten
        max_depth: Maximum depth to flatten (default: 1)
        current_depth: Current recursion depth (internal use)
        
    Yields:
        Flattened items one by one
        
    Example:
        >>> list(flatten_any([1, (2, [3, {4, 5}])]))
        [1, 2, 3, 4, 5]  # Order may vary for set items
    """
    for item in nested:
        if isinstance(item, (list, tuple, set)) and current_depth < max_depth:
            yield from flatten_any(item, max_depth, current_depth + 1)
        else:
            yield item


def flatten_three_levels_with_suffix(nested_dict: dict) -> dict:
    """
    Flatten 3-level nested dictionary by merging level2 into level1
    with suffix notation for original parent keys.
    
    Args:
        nested_dict: 3-level nested dictionary
        
    Returns:
        Flattened dictionary with suffix notation
        
    Example:
        >>> data = {'A': {'x': 1, 'y': {'p': 10, 'q': 20}, 'z': 3}}
        >>> flatten_three_levels_with_suffix(data)
        {'A': {'x': 1, 'p (y)': 10, 'q (y)': 20, 'z': 3}}
    """
    result = {}
    for (top_key, level1) in nested_dict.items():
        if not isinstance(level1, dict):
            result[top_key] = level1
            continue
    
        merged = {}
        for (k1, v1) in level1.items():
            if isinstance(v1, dict):
                # Level2 dict: extract items with suffix
                for (k2, v2) in v1.items():
                    new_key = f"{k2} ({k1})"
                    merged[new_key] = v2
            else:
                merged[k1] = v1
    
        result[top_key] = merged
    
    return result
