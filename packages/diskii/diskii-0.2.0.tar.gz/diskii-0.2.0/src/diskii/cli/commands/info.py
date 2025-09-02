"""Info command implementation."""

import argparse
from pathlib import Path

from ...detection import open_disk_image
from ...exceptions import DiskiiError
from ..utils import format_bytes, format_file_type, get_terminal_width, truncate_filename


def run_info(args: argparse.Namespace) -> None:
    """Run the info command."""
    image_path = Path(args.image)
    
    if not image_path.exists():
        raise DiskiiError(f"Image file not found: {image_path}")
    
    with open_disk_image(image_path) as image:
        # Basic disk information
        print(f"Disk Image: {image_path.name}")
        print(f"Format: {image.format.filesystem.name} on {image.format.sector_ordering.name}")
        print(f"Volume: {image.get_volume_name()}")
        print(f"Size: {format_bytes(image_path.stat().st_size)}")
        
        # Free space information
        try:
            if hasattr(image, 'get_free_blocks'):
                free_blocks = image.get_free_blocks()
                total_blocks = image.total_blocks
                used_blocks = total_blocks - free_blocks
                print(f"Used: {format_bytes(used_blocks * 512)} ({used_blocks} blocks)")
                print(f"Free: {format_bytes(free_blocks * 512)} ({free_blocks} blocks)")
            elif hasattr(image, 'get_free_sectors'):
                free_sectors = image.get_free_sectors()
                total_sectors = getattr(image, 'total_sectors', 0)
                used_sectors = total_sectors - free_sectors if total_sectors else 0
                print(f"Used: {format_bytes(used_sectors * 256)} ({used_sectors} sectors)")
                print(f"Free: {format_bytes(free_sectors * 256)} ({free_sectors} sectors)")
        except Exception:
            # Some images might not support free space calculation
            pass
        
        print()
        
        # File listing
        try:
            # Get all files including subdirectories recursively
            all_files = _get_all_files_recursive(image)
            print(f"Files: {len(all_files)}")
            
            if not all_files:
                print("  (no files)")
                return
                
            if args.tree:
                _print_tree_format(all_files, image, args.detailed)
            else:
                _print_table_format(all_files, image, args.detailed)
                
        except Exception as e:
            print(f"Error reading files: {e}")


def _get_all_files_recursive(image):
    """Get all files recursively, including files in subdirectories."""
    all_files = []
    
    def _collect_files(files, parent_path=""):
        for file_entry in files:
            # Add the current file/directory to the list
            all_files.append((file_entry, parent_path))
            
            # If this is a directory, recursively get its contents
            if file_entry.is_directory:
                try:
                    subdir = file_entry.read_subdirectory()
                    subfiles = subdir.get_all_files()
                    
                    # Recursively collect files with updated parent path
                    current_path = f"{parent_path}/{file_entry.filename}" if parent_path else file_entry.filename
                    _collect_files(subfiles, current_path)
                    
                except Exception as e:
                    # Some directories might not be readable, continue with others
                    pass
    
    # Start with root files
    root_files = image.get_file_list()
    _collect_files(root_files)
    
    return all_files


def _print_table_format(files, image, detailed: bool) -> None:
    """Print files in table format."""
    terminal_width = get_terminal_width()
    
    if detailed:
        # Detailed format with more columns
        print(f"{'Name':<20} {'Type':<8} {'Size':<10} {'Date':<12} {'Blocks/Sectors':<6}")
        print("-" * min(60, terminal_width))
        
        for item in files:
            # Handle both old and new formats
            if isinstance(item, tuple):
                file_entry, parent_path = item
                display_name = f"{parent_path}/{file_entry.filename}" if parent_path else file_entry.filename
            else:
                file_entry = item
                display_name = file_entry.filename
            # Format filename with truncation
            name = truncate_filename(display_name, 20)
            
            # Format file type
            file_type = format_file_type(file_entry.file_type, 
                                       "prodos" if hasattr(image, 'get_free_blocks') else "dos")
            
            # Format size
            size = format_bytes(file_entry.size)
            
            # Format date if available
            date_str = ""
            if hasattr(file_entry, 'created') and file_entry.created:
                date_str = file_entry.created.strftime("%Y-%m-%d")
            
            # Format blocks/sectors
            blocks_str = ""
            if hasattr(file_entry, 'blocks_used'):
                blocks_str = str(file_entry.blocks_used)
            elif hasattr(file_entry, 'sectors_used'):
                blocks_str = str(file_entry.sectors_used)
            
            print(f"{name:<20} {file_type:<8} {size:<10} {date_str:<12} {blocks_str:<6}")
    else:
        # Simple format - just names, types, and sizes
        name_width = min(30, terminal_width - 20)
        print(f"{'Name':<{name_width}} {'Type':<8} {'Size'}")
        print("-" * min(name_width + 18, terminal_width))
        
        for item in files:
            # Handle both old and new formats
            if isinstance(item, tuple):
                file_entry, parent_path = item
                display_name = f"{parent_path}/{file_entry.filename}" if parent_path else file_entry.filename
            else:
                file_entry = item
                display_name = file_entry.filename
            
            name = truncate_filename(display_name, name_width)
            file_type = format_file_type(file_entry.file_type,
                                       "prodos" if hasattr(image, 'get_free_blocks') else "dos")
            size = format_bytes(file_entry.size)
            
            print(f"{name:<{name_width}} {file_type:<8} {size}")


def _print_tree_format(files, image, detailed: bool) -> None:
    """Print files in tree format with proper subdirectory support."""
    volume_name = image.get_volume_name()
    print(f"{volume_name}/")
    
    # Build a directory tree structure from file paths
    tree = _build_directory_tree(files)
    
    # Print the tree recursively
    _print_tree_recursive(tree, "", True, detailed, image)


def _build_directory_tree(files):
    """Build a nested dictionary representing the directory tree."""
    tree = {}
    
    for item in files:
        if isinstance(item, tuple):
            # New format: (file_entry, parent_path)
            file_entry, parent_path = item
            if parent_path:
                full_path = f"{parent_path}/{file_entry.filename}"
            else:
                full_path = file_entry.filename
            path_parts = full_path.split('/')
        else:
            # Old format: just file_entry (for backward compatibility)
            file_entry = item
            # Use full_path if available (ProDOS), otherwise just filename (DOS)
            if hasattr(file_entry, 'full_path') and file_entry.full_path:
                path_parts = file_entry.full_path.split('/')
            else:
                # For DOS files, use just the filename
                path_parts = [file_entry.filename]
        
        current = tree
        
        # Navigate/create directory structure
        for i, part in enumerate(path_parts):
            if i == len(path_parts) - 1:
                # This is the file itself - only add if not a directory or if it has no contents
                if isinstance(current, dict):
                    if not file_entry.is_directory or part not in current:
                        current[part] = file_entry
                    elif file_entry.is_directory and isinstance(current[part], dict):
                        # Directory already exists as dict, don't overwrite
                        pass
            else:
                # This is a directory path component
                if isinstance(current, dict):
                    if part not in current:
                        current[part] = {}
                    elif not isinstance(current[part], dict):
                        # Replace file entry with directory dict if we have subdirectory contents
                        current[part] = {}
                    current = current[part]
                else:
                    # Current is not a dict, can't navigate further
                    break
    
    return tree


def _print_tree_recursive(tree, indent, is_root, detailed, image):
    """Recursively print the directory tree."""
    items = list(tree.items())
    
    for i, (name, content) in enumerate(items):
        is_last = i == len(items) - 1
        
        if is_root:
            # Root level files
            prefix = "└── " if is_last else "├── "
        else:
            # Nested files
            prefix = f"{indent}└── " if is_last else f"{indent}├── "
        
        if isinstance(content, dict):
            # This is a directory
            print(f"{prefix}{name}/")
            
            # Recurse into subdirectory
            next_indent = indent + ("    " if is_last else "│   ")
            _print_tree_recursive(content, next_indent, False, detailed, image)
        else:
            # This is a file
            file_entry = content
            
            if detailed:
                file_type = format_file_type(file_entry.file_type,
                                           "prodos" if hasattr(image, 'get_free_blocks') else "dos")
                size = format_bytes(file_entry.size)
                
                # Check if it's a directory file type
                is_dir = getattr(file_entry, 'is_directory', False)
                if callable(is_dir):
                    is_dir = is_dir()
                
                if is_dir:
                    print(f"{prefix}{file_entry.filename}/ ({file_type}, {size})")
                else:
                    print(f"{prefix}{file_entry.filename} ({file_type}, {size})")
            else:
                # Check if it's a directory file type
                is_dir = getattr(file_entry, 'is_directory', False)
                if callable(is_dir):
                    is_dir = is_dir()
                
                if is_dir:
                    print(f"{prefix}{file_entry.filename}/")
                else:
                    print(f"{prefix}{file_entry.filename}")