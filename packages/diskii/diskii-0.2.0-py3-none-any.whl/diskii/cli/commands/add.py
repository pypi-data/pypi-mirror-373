"""Add command implementation."""

import argparse
from pathlib import Path
from typing import Optional

from ...detection import open_disk_image
from ...exceptions import DiskiiError
from ...basic import BasicTokenizer as BasicTokenizerFactory
from ...file_type_conversion import normalize_prodos_file_type, normalize_dos_file_type
from ..utils import (
    create_backup, confirm_action, detect_file_type_from_extension, 
    print_success, print_error, print_warning
)


def run_add(args: argparse.Namespace) -> None:
    """Run the add command."""
    image_path = Path(args.image)
    
    if not image_path.exists():
        raise DiskiiError(f"Image file not found: {image_path}")
    
    # Verify all source files exist first
    source_files = []
    for file_path_str in args.files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            raise DiskiiError(f"Source file not found: {file_path}")
        if file_path.is_dir():
            raise DiskiiError(f"Directory not supported: {file_path}")
        source_files.append(file_path)
    
    # Create backup if requested
    backup_path = None
    if args.backup:
        backup_path = create_backup(image_path)
        print_success(f"Created backup: {backup_path}")
    
    try:
        with open_disk_image(image_path, read_only=False) as image:
            is_prodos = image.format.filesystem.name == 'PRODOS'
            
            print(f"Adding {len(source_files)} file(s) to {image.get_volume_name()}")
            
            added_count = 0
            for source_file in source_files:
                try:
                    _add_file_to_image(image, source_file, args.type, is_prodos)
                    added_count += 1
                    print_success(f"Added {source_file.name}")
                except Exception as e:
                    print_error(f"Failed to add {source_file.name}: {e}")
            
            print(f"\nAdded {added_count} of {len(source_files)} files")
    
    except Exception as e:
        if backup_path:
            print_warning(f"Error occurred, backup available at: {backup_path}")
        raise


def _add_file_to_image(image, source_file: Path, type_override: Optional[str], is_prodos: bool) -> None:
    """Add a single file to the disk image."""
    # Determine target filename (Apple II filename constraints)
    target_filename = _make_apple_ii_filename(source_file.name, is_prodos)
    
    # Read file data
    data = source_file.read_bytes()
    
    # Determine file type
    file_type = _determine_file_type(source_file, type_override, is_prodos)
    
    # Handle BASIC file tokenization
    if _should_tokenize_basic(source_file, file_type, is_prodos):
        data = _tokenize_basic_file(source_file, file_type, is_prodos)
    
    # Add file to image
    if is_prodos:
        # ProDOS file creation
        prodos_type = normalize_prodos_file_type(file_type)
        aux_type = _determine_aux_type(source_file, prodos_type)
        
        image.create_file(target_filename, prodos_type, data, aux_type=aux_type)
    else:
        # DOS file creation
        dos_type = normalize_dos_file_type(file_type)
        # Use the create_dos_file function from dos_writer if available
        if hasattr(image, 'create_file'):
            image.create_file(target_filename, dos_type, data)
        else:
            # Fallback to the writer module functions
            from ...dos_writer import create_dos_file
            create_dos_file(image, target_filename, dos_type, data)


def _make_apple_ii_filename(filename: str, is_prodos: bool) -> str:
    """Convert filename to Apple II compatible format."""
    # Keep the full filename including extension (Apple II filesystems support extensions)
    name_part = Path(filename).name
    
    # Convert to uppercase
    name_part = name_part.upper()
    
    # Replace invalid characters
    valid_chars = []
    for char in name_part:
        if char.isalnum() or char in '.-':
            valid_chars.append(char)
        else:
            valid_chars.append('.')
    
    clean_name = ''.join(valid_chars)
    
    # Truncate to Apple II limits
    if is_prodos:
        return clean_name[:15]  # ProDOS 15 character limit
    else:
        return clean_name[:30]  # DOS 30 character limit


def _determine_file_type(source_file: Path, type_override: Optional[str], is_prodos: bool) -> str:
    """Determine the Apple II file type for the source file."""
    if type_override:
        return type_override.upper()
    
    # Try to detect from extension
    detected_type = detect_file_type_from_extension(source_file, is_prodos)
    if detected_type:
        return detected_type
    
    # Default file types
    if is_prodos:
        if _is_text_file(source_file):
            return 'TXT'
        else:
            return 'BIN'  # Binary default
    else:
        if _is_text_file(source_file):
            return 'T'
        else:
            return 'B'  # Binary default


def _is_text_file(file_path: Path) -> bool:
    """Check if file appears to be text."""
    try:
        # Try reading as text
        content = file_path.read_bytes()
        
        # Check for null bytes (binary indicator)
        if b'\x00' in content:
            return False
        
        # Try to decode as text
        content.decode('utf-8', errors='strict')
        return True
    except (UnicodeDecodeError, IOError):
        return False


def _should_tokenize_basic(source_file: Path, file_type: str, is_prodos: bool) -> bool:
    """Check if file should be tokenized as BASIC."""
    # Check if it's a BASIC type and appears to be text
    is_basic_type = False
    
    if is_prodos:
        is_basic_type = file_type in ['BAS', 'INT']
    else:
        is_basic_type = file_type in ['A', 'I']
    
    return is_basic_type and _is_text_file(source_file)


def _tokenize_basic_file(source_file: Path, file_type: str, is_prodos: bool) -> bytes:
    """Tokenize a BASIC text file."""
    try:
        text_content = source_file.read_text(encoding='utf-8')
        
        # Determine BASIC variant
        variant = "applesoft"
        if (is_prodos and file_type == 'INT') or (not is_prodos and file_type == 'I'):
            variant = "integer"
        
        tokenizer = BasicTokenizerFactory(variant)
        return tokenizer.tokenize(text_content)
    
    except Exception as e:
        print_warning(f"Failed to tokenize {source_file.name} as BASIC, treating as binary: {e}")
        return source_file.read_bytes()


def _determine_aux_type(source_file: Path, prodos_type: int) -> int:
    """Determine auxiliary type for ProDOS files."""
    # Standard aux types for common file types
    if prodos_type == 0x06:  # Binary
        return 0x0800  # Default load address
    elif prodos_type == 0xFC:  # Applesoft BASIC
        return 0x0801  # BASIC program aux type
    elif prodos_type == 0xFA:  # Integer BASIC
        return 0x2000  # Integer BASIC aux type
    else:
        return 0x0000  # Default