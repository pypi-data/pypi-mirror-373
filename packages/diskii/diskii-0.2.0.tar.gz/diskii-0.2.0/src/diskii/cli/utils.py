"""Shared utilities for CLI commands."""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

from ..exceptions import DiskiiError


def format_bytes(bytes_count: int) -> str:
    """Format byte count in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            if unit == 'B':
                return f"{bytes_count} {unit}"
            else:
                return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"


def format_file_type(file_type, variant: str = "prodos") -> str:
    """Format file type for display."""
    # Handle enum types - convert to string representation
    if hasattr(file_type, 'name'):
        # This is likely an enum, extract the name part
        enum_name = str(file_type.name)
        # Convert from APPLESOFT_BASIC to "Applesoft"
        if enum_name == "APPLESOFT_BASIC":
            return "Applesoft"
        elif enum_name == "INTEGER_BASIC":
            return "Integer"
        elif enum_name == "BINARY":
            return "Binary"
        elif enum_name == "TEXT":
            return "Text"
        else:
            return enum_name.replace('_', ' ').title()
    
    if variant == "prodos":
        type_map = {
            0x00: "UNK", 0x01: "BAD", 0x04: "TXT", 0x06: "BIN", 0x0F: "DIR",
            0x19: "ADB", 0x1A: "AWP", 0x1B: "ASP", 0xB0: "SRC", 0xB3: "OBJ",
            0xB5: "LIB", 0xB8: "S16", 0xB9: "RTL", 0xBA: "EXE", 0xBF: "SYS",
            0xC0: "PIF", 0xC1: "TIF", 0xC2: "ANI", 0xC5: "PAL", 0xC6: "OOG",
            0xC7: "SCR", 0xC8: "CDV", 0xC9: "FON", 0xCA: "FND", 0xCB: "ICN",
            0xF0: "P8C", 0xFA: "INT", 0xFB: "IVR", 0xFC: "BAS", 0xFD: "VAR",
            0xFE: "REL", 0xFF: "SYS"
        }
        if isinstance(file_type, int):
            return type_map.get(file_type, f"${file_type:02X}")
        return str(file_type)
    else:  # DOS
        if isinstance(file_type, str):
            type_map = {"T": "Text", "I": "Integer", "A": "Applesoft", 
                       "B": "Binary", "S": "Special", "R": "Relocatable"}
            return type_map.get(file_type, file_type)
        return str(file_type)


def create_backup(file_path: Path) -> Path:
    """Create a backup of a file."""
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
    counter = 1
    while backup_path.exists():
        backup_path = file_path.with_suffix(f'{file_path.suffix}.bak{counter}')
        counter += 1
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    suffix = " [Y/n]" if default else " [y/N]"
    
    while True:
        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            if response in ('y', 'yes'):
                return True
            if response in ('n', 'no'):
                return False
            print("Please respond with 'y' or 'n'")
        except EOFError:
            return False


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print warning message to stderr."""
    print(f"Warning: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print success message."""
    print(f"✓ {message}")


def detect_file_type_from_extension(file_path: Path, is_prodos: bool = True) -> Optional[str]:
    """Detect Apple II file type from file extension.
    
    Args:
        file_path: Path to the file
        is_prodos: True for ProDOS format, False for DOS format
        
    Returns:
        File type string appropriate for the disk format
    """
    extension = file_path.suffix.lower()
    
    if is_prodos:
        # ProDOS style file types
        ext_map = {
            '.txt': 'TXT',
            '.bas': 'BAS', 
            '.bin': 'BIN',
            '.obj': 'BIN',
            '.sys': 'SYS',
            '.int': 'INT',  # Integer BASIC
        }
    else:
        # DOS style file types (single letter)
        ext_map = {
            '.txt': 'T',    # Text
            '.bas': 'A',    # Applesoft BASIC
            '.bin': 'B',    # Binary
            '.obj': 'B',    # Binary
            '.sys': 'S',    # System
            '.int': 'I',    # Integer BASIC
        }
    
    return ext_map.get(extension)


def get_terminal_width() -> int:
    """Get terminal width, with fallback."""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


def truncate_filename(filename: str, max_width: int) -> str:
    """Truncate filename if too long."""
    if len(filename) <= max_width:
        return filename
    
    if max_width <= 3:
        return "..."[:max_width]
    
    return filename[:max_width-3] + "..."