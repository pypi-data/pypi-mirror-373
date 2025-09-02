"""Apple II BASIC tokenization and detokenization support.

This module provides tokenization and detokenization for Apple II BASIC variants:
- Applesoft BASIC (Apple II, II+, IIe, IIc, IIGS)
- Integer BASIC (original Apple II)

The module is organized into separate submodules for each variant to improve
maintainability and allow for variant-specific optimizations.
"""

# Import the main classes for backwards compatibility
from .applesoft.tokenizer import ApplesoftTokenizer
from .applesoft.detokenizer import ApplesoftDetokenizer
from .applesoft.validator import ApplesoftSyntaxValidator
from .integer.tokenizer import IntegerTokenizer
from .integer.detokenizer import IntegerDetokenizer
from .integer.validator import IntegerSyntaxValidator

# Legacy compatibility imports
def BasicTokenizer(variant: str = "applesoft"):
    """Create a tokenizer for the specified BASIC variant.
    
    Args:
        variant: Either "applesoft" or "integer"
        
    Returns:
        Appropriate tokenizer instance
    """
    if variant.lower() == "applesoft":
        return ApplesoftTokenizer()
    elif variant.lower() == "integer":
        return IntegerTokenizer()
    else:
        raise ValueError(f"Unknown BASIC variant: {variant}")


def BasicDetokenizer(variant: str = "applesoft"):
    """Create a detokenizer for the specified BASIC variant.
    
    Args:
        variant: Either "applesoft" or "integer"
        
    Returns:
        Appropriate detokenizer instance
    """
    if variant.lower() == "applesoft":
        return ApplesoftDetokenizer()
    elif variant.lower() == "integer":
        return IntegerDetokenizer()
    else:
        raise ValueError(f"Unknown BASIC variant: {variant}")


def BasicSyntaxValidator(variant: str = "applesoft"):
    """Create a syntax validator for the specified BASIC variant.
    
    Args:
        variant: Either "applesoft" or "integer"
        
    Returns:
        Appropriate syntax validator instance
    """
    if variant.lower() == "applesoft":
        return ApplesoftSyntaxValidator()
    elif variant.lower() == "integer":
        return IntegerSyntaxValidator()
    else:
        raise ValueError(f"Unknown BASIC variant: {variant}")


__all__ = [
    'BasicTokenizer',
    'BasicDetokenizer',
    'BasicSyntaxValidator',
    'ApplesoftTokenizer',
    'ApplesoftDetokenizer',
    'ApplesoftSyntaxValidator',
    'IntegerTokenizer',
    'IntegerDetokenizer',
    'IntegerSyntaxValidator',
]