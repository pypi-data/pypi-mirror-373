"""Extract command implementation."""

import argparse
import fnmatch
from pathlib import Path
from typing import List

from ...detection import open_disk_image
from ...exceptions import DiskiiError, FileNotFoundError
from ...basic import BasicDetokenizer as BasicDetokenizerFactory
from ..utils import print_success, print_error, print_warning


def run_extract(args: argparse.Namespace) -> None:
    """Run the extract command."""
    image_path = Path(args.image)
    
    if not image_path.exists():
        raise DiskiiError(f"Image file not found: {image_path}")
    
    output_dir = args.output_dir or Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open_disk_image(image_path) as image:
        files = image.get_file_list()
        
        if not files:
            print("No files found in image")
            return
        
        # Determine which files to extract
        if args.files:
            files_to_extract = _find_matching_files(files, args.files)
            if not files_to_extract:
                print_error("No matching files found")
                return
        else:
            files_to_extract = files
            print(f"Extracting {len(files_to_extract)} files to {output_dir}")
        
        extracted_count = 0
        for file_entry in files_to_extract:
            try:
                _extract_file(file_entry, output_dir, args.convert, args.preserve_types)
                extracted_count += 1
                print_success(f"Extracted {file_entry.filename}")
            except Exception as e:
                print_error(f"Failed to extract {file_entry.filename}: {e}")
        
        print(f"\nExtracted {extracted_count} of {len(files_to_extract)} files")


def _find_matching_files(all_files, patterns: List[str]):
    """Find files matching the given patterns."""
    matching_files = []
    
    for pattern in patterns:
        pattern_matches = []
        
        # Try exact match first
        for file_entry in all_files:
            if file_entry.filename.upper() == pattern.upper():
                pattern_matches.append(file_entry)
        
        # If no exact match, try wildcard matching
        if not pattern_matches:
            for file_entry in all_files:
                if fnmatch.fnmatch(file_entry.filename.upper(), pattern.upper()):
                    pattern_matches.append(file_entry)
        
        if not pattern_matches:
            print_warning(f"No files match pattern: {pattern}")
        else:
            matching_files.extend(pattern_matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for file_entry in matching_files:
        if file_entry.filename not in seen:
            seen.add(file_entry.filename)
            unique_files.append(file_entry)
    
    return unique_files


def _extract_file(file_entry, output_dir: Path, convert_basic: bool, preserve_types: bool) -> None:
    """Extract a single file."""
    # Determine output filename
    output_name = file_entry.filename
    
    # Clean up filename for filesystem compatibility
    # Replace problematic characters
    safe_chars = []
    for char in output_name:
        if char.isalnum() or char in '.-_':
            safe_chars.append(char)
        else:
            safe_chars.append('_')
    output_name = ''.join(safe_chars)
    
    output_path = output_dir / output_name
    
    # Handle file type conversion and extension
    is_basic_file = _is_basic_file(file_entry)
    
    if convert_basic and is_basic_file:
        # Convert BASIC file to text
        output_path = output_path.with_suffix('.bas')
        _extract_basic_as_text(file_entry, output_path)
    else:
        # Extract as binary
        data = file_entry.read_data()
        output_path.write_bytes(data)
    
    # Preserve type information if requested
    if preserve_types:
        _write_type_info(file_entry, output_path)


def _is_basic_file(file_entry) -> bool:
    """Check if file is a BASIC program."""
    if not hasattr(file_entry, 'file_type'):
        return False
    
    file_type = file_entry.file_type
    
    # Handle enum types
    if hasattr(file_type, 'name'):
        return 'BASIC' in file_type.name
    
    # ProDOS BASIC types
    if isinstance(file_type, int):
        return file_type in [0xFC, 0xFA]  # Applesoft, Integer BASIC
    
    # DOS BASIC types
    if isinstance(file_type, str):
        return file_type in ['A', 'I']  # Applesoft, Integer BASIC
    
    return False


def _extract_basic_as_text(file_entry, output_path: Path) -> None:
    """Extract BASIC file as detokenized text."""
    try:
        data = file_entry.read_data()
        
        # Determine BASIC variant
        variant = "applesoft"
        if hasattr(file_entry, 'file_type'):
            file_type = file_entry.file_type
            # Handle enum types
            if hasattr(file_type, 'name') and 'INTEGER' in file_type.name:
                variant = "integer"
            # Handle int/str types
            elif (isinstance(file_type, int) and file_type == 0xFA) or \
                 (isinstance(file_type, str) and file_type == 'I'):
                variant = "integer"
        
        # Detokenize
        detokenizer = BasicDetokenizerFactory(variant)
        text = detokenizer.detokenize_program(data)
        
        # Write as text file
        output_path.write_text(text, encoding='utf-8')
        
    except Exception as e:
        print_warning(f"Could not detokenize {file_entry.filename}, saving as binary: {e}")
        # Fallback to binary
        data = file_entry.read_data()
        output_path.write_bytes(data)


def _write_type_info(file_entry, output_path: Path) -> None:
    """Write file type information to a companion file."""
    info_path = output_path.with_suffix(output_path.suffix + '.info')
    
    info_lines = [
        f"Filename: {file_entry.filename}",
        f"Size: {file_entry.size} bytes",
    ]
    
    if hasattr(file_entry, 'file_type'):
        info_lines.append(f"Type: {file_entry.file_type}")
    
    if hasattr(file_entry, 'aux_type'):
        info_lines.append(f"Aux Type: {file_entry.aux_type}")
    
    if hasattr(file_entry, 'created') and file_entry.created:
        info_lines.append(f"Created: {file_entry.created}")
    
    if hasattr(file_entry, 'modified') and file_entry.modified:
        info_lines.append(f"Modified: {file_entry.modified}")
    
    if hasattr(file_entry, 'storage_type'):
        info_lines.append(f"Storage Type: {file_entry.storage_type}")
    
    if hasattr(file_entry, 'blocks_used'):
        info_lines.append(f"Blocks Used: {file_entry.blocks_used}")
    elif hasattr(file_entry, 'sectors_used'):
        info_lines.append(f"Sectors Used: {file_entry.sectors_used}")
    
    info_path.write_text('\n'.join(info_lines), encoding='utf-8')