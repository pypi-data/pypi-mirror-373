"""
Utility functions for text decoding operations.
"""


def safe_decode(data):
    """
    Safely decode bytes or text, handling UTF-8 errors.
    
    Args:
        data: Input data that can be bytes or text
        
    Returns:
        str: Decoded string with errors replaced if any
    """
    if isinstance(data, bytes):
        return data.decode('utf-8', errors='replace')
    return str(data) 