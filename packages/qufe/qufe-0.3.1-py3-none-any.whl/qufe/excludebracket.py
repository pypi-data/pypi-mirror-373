"""
Bracket content removal utilities.

This module provides functions to validate and remove content within brackets
from text strings with proper bracket pairing validation.
"""

import re


def check_eb(text, open_bracket, close_bracket):
    """
    Validate bracket pairing in text.
    
    Args:
        text (str): The input text to validate
        open_bracket (str): The opening bracket character
        close_bracket (str): The closing bracket character
        
    Returns:
        int: 1 if brackets are valid and properly paired, 0 otherwise
        
    Raises:
        None: Returns 0 for any validation failure
    """
    brackets = ('(', ')', '[', ']', '{', '}', '<', '>')
    
    # Fail if not valid bracket characters
    if (open_bracket not in brackets) or (close_bracket not in brackets):
        return 0
        
    # Check if brackets form a valid pair
    if not (0 < (ord(close_bracket) - ord(open_bracket)) < 3):
        return 0
        
    # Check if bracket counts match
    if text.count(open_bracket) != text.count(close_bracket):
        return 0
        
    # Check if closing bracket appears before opening bracket
    if text.find(close_bracket) < text.find(open_bracket):
        return 0
        
    return 1


def eb2(text, open_bracket, close_bracket):
    """
    Remove content within brackets from text.
    
    Args:
        text (str): The input text
        open_bracket (str): The opening bracket character
        close_bracket (str): The closing bracket character
        
    Returns:
        str: Text with bracket content removed, or 0 if validation fails
        
    Example:
        >>> eb2("Hello (world) test", "(", ")")
        'Hello  test'
    """
    if not check_eb(text, open_bracket, close_bracket):
        return 0
    
    # Escape brackets for regex
    escaped_open = '\\' + open_bracket
    escaped_close = '\\' + close_bracket
    
    # Find all bracket positions
    re_open = re.compile(escaped_open)
    re_close = re.compile(escaped_close)
    
    open_positions = [m.start() for m in re.finditer(re_open, text)]
    close_positions = [m.start() for m in re.finditer(re_close, text)]
    
    # Check if any closing bracket appears before its opening bracket
    invalid_order = [1 for (x, y) in zip(open_positions, close_positions) if x > y]
    if sum(invalid_order):
        return 0
    
    # Create position pairs for text extraction
    close_positions.insert(0, -1)
    open_positions.append(len(text))
    
    # Extract text outside brackets
    result = [text[start+1:end] for (start, end) in zip(close_positions, open_positions) 
              if (end - start) > 1]
    
    return ''.join(result)


def exclude_bracket_content(text, open_bracket='(', close_bracket=')'):
    """
    Convenience function to remove bracket content with default parentheses.
    
    Args:
        text (str): The input text
        open_bracket (str): The opening bracket character (default: '(')
        close_bracket (str): The closing bracket character (default: ')')
        
    Returns:
        str: Text with bracket content removed, or original text if validation fails
    """
    result = eb2(text, open_bracket, close_bracket)
    return result if result != 0 else text
