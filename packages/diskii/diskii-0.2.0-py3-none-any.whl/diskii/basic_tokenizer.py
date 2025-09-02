"""Apple II BASIC tokenization and detokenization engine.

DEPRECATED: This module has been refactored. Use diskii.basic instead.
The classes in this module are maintained for backward compatibility.
"""

# Import from the new modular structure for backward compatibility
from .basic import BasicTokenizer, BasicDetokenizer

# Legacy function imports for complete compatibility
from .basic.tokens import get_applesoft_table, get_integer_basic_table


def tokenize_applesoft(text: str) -> bytes:
    """Tokenize Applesoft BASIC program text.
    
    Args:
        text: Plain text BASIC program
        
    Returns:
        Tokenized program as bytes
    """
    tokenizer = BasicTokenizer("applesoft")
    return tokenizer.tokenize_program(text)


def detokenize_applesoft(data: bytes) -> str:
    """Detokenize Applesoft BASIC program data.
    
    Args:
        data: Tokenized program data
        
    Returns:
        Plain text BASIC program
    """
    detokenizer = BasicDetokenizer("applesoft")
    return detokenizer.detokenize_program(data)


def tokenize_integer_basic(text: str) -> bytes:
    """Tokenize Integer BASIC program text.
    
    Args:
        text: Plain text BASIC program
        
    Returns:
        Tokenized program as bytes
    """
    tokenizer = BasicTokenizer("integer")
    return tokenizer.tokenize_program(text)


def detokenize_integer_basic(data: bytes) -> str:
    """Detokenize Integer BASIC program data.
    
    Args:
        data: Tokenized program data
        
    Returns:
        Plain text BASIC program
    """
    detokenizer = BasicDetokenizer("integer")
    return detokenizer.detokenize_program(data)


def auto_detect_variant(data) -> str | None:
    """Auto-detect BASIC variant from text or tokenized data.
    
    Args:
        data: Program data (plain text string or tokenized bytes)
        
    Returns:
        Detected variant ("applesoft" or "integer") or None if cannot determine
    """
    if isinstance(data, str):
        # Handle plain text detection first
        if not data.strip():
            return None  # Cannot determine variant from empty data
        
        # Look for Integer BASIC specific patterns
        text_upper = data.upper()
        
        # Integer BASIC specific commands/functions
        integer_only_patterns = [
            'COLOR=', 'HCOLOR=', 'VTAB', 'HTAB', 'HLIN', 'VLIN', 'PLOT', 'SCRN(',
            'TEXT', 'GR', 'HGR', 'HGR2', 'SCALE=', 'ROT=', 'SPEED='
        ]
        
        # Check for Integer BASIC patterns
        integer_score = 0
        for pattern in integer_only_patterns:
            if pattern in text_upper:
                integer_score += 1
        
        # Applesoft BASIC specific patterns
        applesoft_patterns = [
            'CHR$(', 'LEFT$(', 'RIGHT$(', 'MID$(', 'STR$(', 'VAL(', 'ASC(',
            'HOME', 'INVERSE', 'NORMAL', 'FLASH', '&'
        ]
        
        applesoft_score = 0
        for pattern in applesoft_patterns:
            if pattern in text_upper:
                applesoft_score += 1
        
        # Return best match
        if integer_score > applesoft_score:
            return "integer"
        elif applesoft_score > 0:
            return "applesoft"
        
        # No clear indicators, default to Applesoft for ambiguous cases
        # This matches historical behavior where Applesoft was more common
        return "applesoft"
    
    # Handle binary tokenized data
    try:
        data = data.encode('latin-1') if isinstance(data, str) else data
    except UnicodeEncodeError:
        # If string contains characters that can't be encoded to latin-1,
        # it's likely corrupted tokenized data
        return None
    
    if not data:
        return None  # Cannot determine variant from empty data
    
    # Need at least 4 bytes for a valid tokenized program
    if len(data) < 4:
        return None  # Insufficient data
    
    # Simple heuristics for variant detection
    # Integer BASIC starts with length byte, Applesoft with line pointer
    
    # Check for Applesoft pattern: next line pointer + line number + content + terminator
    first_two = data[0] | (data[1] << 8)
    if first_two == 0:
        # Check if this looks like Applesoft program terminator
        if len(data) >= 6:  # Need enough data for a line
            return "applesoft"
    elif first_two < 0x8000:  # Reasonable line pointer value
        return "applesoft"
    
    # Check for Integer BASIC pattern: length byte + line number + content
    line_length = data[0]
    if 0 < line_length < 100 and len(data) > line_length:
        # Validate that this could be a valid Integer BASIC line
        if len(data) >= line_length + 1:  # Need at least the claimed length
            return "integer"
    
    # Cannot determine variant from this data
    return None


# Re-export for backward compatibility
__all__ = [
    'BasicTokenizer', 
    'BasicDetokenizer', 
    'get_applesoft_table', 
    'get_integer_basic_table',
    'tokenize_applesoft',
    'detokenize_applesoft', 
    'tokenize_integer_basic',
    'detokenize_integer_basic',
    'auto_detect_variant'
]