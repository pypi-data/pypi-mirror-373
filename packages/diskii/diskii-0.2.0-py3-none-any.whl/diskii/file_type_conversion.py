"""File type conversion utilities for diskii.

This module provides utilities for converting file types between different
Apple II disk image formats (DOS 3.2/3.3 and ProDOS).
"""


def normalize_prodos_file_type(file_type: int | str) -> int:
    """Normalize file type to ProDOS integer format.
    
    Args:
        file_type: File type as integer (ProDOS) or string (DOS)
        
    Returns:
        ProDOS integer file type
        
    Raises:
        ValueError: If file type is invalid
        
    Examples:
        >>> normalize_prodos_file_type(0x04)
        4
        >>> normalize_prodos_file_type("T") 
        4
        >>> normalize_prodos_file_type("A")
        252
    """
    if isinstance(file_type, int):
        if 0 <= file_type <= 255:
            return file_type
        else:
            raise ValueError(f"ProDOS file type must be 0-255, got {file_type}")
    
    elif isinstance(file_type, str):
        file_type_upper = file_type.upper()
        
        # Convert DOS string types to ProDOS integer types
        dos_to_prodos_map = {
            "T": 0x04,  # Text -> TEXT
            "I": 0xFA,  # Integer BASIC -> INT
            "A": 0xFC,  # Applesoft BASIC -> BAS
            "B": 0x06,  # Binary -> BIN
            "S": 0xFF,  # System -> SYS
            "R": 0xFE,  # Relocatable -> REL
        }
        
        # Also handle ProDOS string types
        prodos_string_to_int_map = {
            "TXT": 0x04,  # TEXT
            "BIN": 0x06,  # Binary
            "BAS": 0xFC,  # Applesoft BASIC
            "INT": 0xFA,  # Integer BASIC
            "SYS": 0xFF,  # System
            "REL": 0xFE,  # Relocatable
        }
        
        if file_type_upper in dos_to_prodos_map:
            return dos_to_prodos_map[file_type_upper]
        elif file_type_upper in prodos_string_to_int_map:
            return prodos_string_to_int_map[file_type_upper]
        else:
            raise ValueError(f"Invalid file type string: '{file_type}'. Must be DOS type (T, I, A, B, S, R) or ProDOS type (TXT, BIN, BAS, INT, SYS, REL)")
    
    else:
        raise ValueError(f"File type must be int or str, got {type(file_type).__name__}")


def normalize_dos_file_type(file_type: int | str) -> str:
    """Normalize file type to DOS string format.
    
    Args:
        file_type: File type as integer (ProDOS) or string (DOS)
        
    Returns:
        DOS string file type (single character)
        
    Raises:
        ValueError: If file type is invalid
        
    Examples:
        >>> normalize_dos_file_type("T")
        'T'
        >>> normalize_dos_file_type(0x04)
        'T'
        >>> normalize_dos_file_type(0xFC)
        'A'
    """
    if isinstance(file_type, str):
        if len(file_type) == 1 and file_type.upper() in ["T", "I", "A", "B", "S", "R"]:
            return file_type.upper()
        else:
            raise ValueError(f"Invalid DOS file type string: '{file_type}'. Must be one of: T, I, A, B, S, R")
    
    elif isinstance(file_type, int):
        # Convert ProDOS integer types to DOS string types
        prodos_to_dos_map = {
            0x00: "T",  # Text (generic)
            0x01: "I",  # Integer BASIC (generic)
            0x02: "A",  # Applesoft BASIC (generic)
            0x04: "T",  # TEXT -> Text
            0x06: "B",  # BIN -> Binary
            0xFA: "I",  # INT -> Integer BASIC
            0xFC: "A",  # BAS -> Applesoft BASIC (tokenized)
            0xFE: "R",  # REL -> Relocatable
            0xFF: "S",  # SYS -> System
        }
        
        if file_type in prodos_to_dos_map:
            return prodos_to_dos_map[file_type]
        else:
            # Default unknown types to Binary
            return "B"
    
    else:
        raise ValueError(f"File type must be int or str, got {type(file_type).__name__}")


def get_prodos_aux_type_for_basic(file_type: int | str) -> int:
    """Get appropriate ProDOS auxiliary type for BASIC programs.
    
    Args:
        file_type: File type (will be normalized first)
        
    Returns:
        Auxiliary type value, or 0 if not a BASIC program
        
    Examples:
        >>> get_prodos_aux_type_for_basic("A")
        2049  # 0x0801 - Applesoft load address
        >>> get_prodos_aux_type_for_basic(0xFA)
        2048  # 0x0800 - Integer BASIC load address
        >>> get_prodos_aux_type_for_basic("T")
        0     # Not a BASIC program
    """
    try:
        normalized_prodos = normalize_prodos_file_type(file_type)
    except ValueError:
        return 0
    
    # Standard load addresses for BASIC programs
    if normalized_prodos == 0xFC:  # BAS (Applesoft BASIC)
        return 0x0801  # Standard Applesoft load address
    elif normalized_prodos == 0xFA:  # INT (Integer BASIC)
        return 0x0800  # Standard Integer BASIC load address
    elif isinstance(file_type, str) and file_type.upper() == "A":
        return 0x0801  # Applesoft
    elif isinstance(file_type, str) and file_type.upper() == "I":
        return 0x0800  # Integer BASIC
    
    return 0  # Not a BASIC program