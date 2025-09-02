"""Apple II BASIC tokenization tables and utilities.

DEPRECATED: This module has been moved. Use diskii.basic.tokens instead.
This module is maintained for backward compatibility.
"""

# Import from the new location for backward compatibility
from .basic.tokens import *

# Re-export all symbols for complete compatibility
__all__ = [
    'APPLESOFT_TOKENS',
    'INTEGER_BASIC_TOKENS', 
    'APPLESOFT_KEYWORDS',
    'INTEGER_BASIC_KEYWORDS',
    'BasicTokenTable',
    'get_applesoft_table',
    'get_integer_basic_table'
]