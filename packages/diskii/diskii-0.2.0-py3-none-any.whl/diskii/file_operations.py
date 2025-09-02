"""High-level file operation utilities for diskii.

This module provides convenient functions for copying files between different
disk images and formats, with automatic type conversion and error handling.
"""

from pathlib import Path
from typing import Any, Dict

from .detection import open_disk_image
from .exceptions import FileNotFoundError, FilesystemError, UnsupportedOperationError
from .image import DiskImage


def copy_file(
    source_image: DiskImage | str | Path,
    dest_image: DiskImage | str | Path, 
    filename: str,
    dest_filename: str = None,
    **kwargs
) -> None:
    """Copy a file from one disk image to another.
    
    This function handles copying files between different disk image formats
    (DOS 3.2/3.3 ↔ ProDOS) with automatic file type conversion.
    
    Args:
        source_image: Source disk image (DiskImage instance or file path)
        dest_image: Destination disk image (DiskImage instance or file path)  
        filename: Name of file to copy from source
        dest_filename: Name for file in destination (defaults to original name)
        **kwargs: Additional arguments passed to dest_image.create_file()
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        FilesystemError: If copy operation fails
        UnsupportedOperationError: If destination is read-only
        
    Examples:
        # Copy between disk image files
        copy_file("source.dsk", "dest.po", "HELLO")
        
        # Copy with rename
        copy_file("source.dsk", "dest.po", "HELLO", "GREETING")
        
        # Copy between opened images
        with open_disk_image("source.dsk") as src:
            with open_disk_image("dest.po", read_only=False) as dst:
                copy_file(src, dst, "HELLO")
    """
    if dest_filename is None:
        dest_filename = filename
    
    # Handle string/Path arguments by opening the images
    source_opened = False
    dest_opened = False
    
    try:
        if isinstance(source_image, (str, Path)):
            source_image = open_disk_image(source_image)
            source_opened = True
            
        if isinstance(dest_image, (str, Path)):
            dest_image = open_disk_image(dest_image, read_only=False)
            dest_opened = True
        
        # Enter context managers if needed
        if source_opened:
            source_image = source_image.__enter__()
        if dest_opened:
            dest_image = dest_image.__enter__()
            
        # Find source file
        source_files = source_image.get_file_list()
        source_file = None
        for file_entry in source_files:
            if file_entry.filename == filename:
                source_file = file_entry
                break
        
        if source_file is None:
            raise FileNotFoundError(filename, str(source_image.file_path))
        
        # Read source file data
        file_data = source_file.read_data(source_image)
        
        # Convert file type for cross-format copying
        file_type, converted_kwargs = _convert_file_type(
            source_file, source_image, dest_image, kwargs
        )
        
        # Create file in destination
        dest_image.create_file(dest_filename, file_type, file_data, **converted_kwargs)
        
    finally:
        # Clean up opened images
        if dest_opened and hasattr(dest_image, '__exit__'):
            dest_image.__exit__(None, None, None)
        if source_opened and hasattr(source_image, '__exit__'):  
            source_image.__exit__(None, None, None)


def copy_all_files(
    source_image: DiskImage | str | Path,
    dest_image: DiskImage | str | Path,
    overwrite: bool = False,
    **kwargs
) -> int:
    """Copy all files from source disk image to destination.
    
    Args:
        source_image: Source disk image (DiskImage instance or file path)
        dest_image: Destination disk image (DiskImage instance or file path)
        overwrite: If True, overwrite existing files in destination
        **kwargs: Additional arguments passed to dest_image.create_file()
        
    Returns:
        Number of files copied
        
    Raises:
        FilesystemError: If copy operation fails
        UnsupportedOperationError: If destination is read-only
    """
    copied_count = 0
    
    # Handle string/Path arguments
    source_opened = False
    dest_opened = False
    
    try:
        if isinstance(source_image, (str, Path)):
            source_image = open_disk_image(source_image)
            source_opened = True
            
        if isinstance(dest_image, (str, Path)):
            dest_image = open_disk_image(dest_image, read_only=False)
            dest_opened = True
            
        # Enter context managers if needed
        if source_opened:
            source_image = source_image.__enter__()
        if dest_opened:
            dest_image = dest_image.__enter__()
            
        # Get all files from source
        source_files = source_image.get_file_list()
        
        # Get existing files in destination to check for conflicts
        dest_files = dest_image.get_file_list() if not overwrite else []
        existing_names = {f.filename for f in dest_files}
        
        for source_file in source_files:
            # Skip if file exists and overwrite is False
            if source_file.filename in existing_names and not overwrite:
                continue
                
            try:
                copy_file(source_image, dest_image, source_file.filename, **kwargs)
                copied_count += 1
            except (FileNotFoundError, FilesystemError):
                # Continue with other files if one fails
                continue
                
    finally:
        # Clean up opened images  
        if dest_opened and hasattr(dest_image, '__exit__'):
            dest_image.__exit__(None, None, None)
        if source_opened and hasattr(source_image, '__exit__'):
            source_image.__exit__(None, None, None)
            
    return copied_count


def _convert_file_type(
    source_file, source_image: DiskImage, dest_image: DiskImage, kwargs: Dict[str, Any]
) -> tuple[int | str, Dict[str, Any]]:
    """Convert file type between different disk image formats.
    
    Args:
        source_file: Source file entry
        source_image: Source disk image
        dest_image: Destination disk image  
        kwargs: Additional arguments for create_file
        
    Returns:
        Tuple of (converted_file_type, converted_kwargs)
    """
    # Get format types
    source_fs = source_image.format.filesystem.value
    dest_fs = dest_image.format.filesystem.value
    
    converted_kwargs = kwargs.copy()
    
    # If same filesystem, use original file type
    if source_fs == dest_fs:
        return source_file.file_type, converted_kwargs
    
    # Convert between ProDOS and DOS formats
    if hasattr(source_file, 'prodos_type'):
        # Source is ProDOS
        prodos_type = source_file.prodos_type
        if dest_fs in ['dos33', 'dos32']:
            # ProDOS -> DOS conversion
            dos_type_map = {
                0x04: 'T',  # TEXT -> Text
                0x06: 'B',  # BIN -> Binary  
                0xFC: 'B',  # BAS -> Binary (tokenized BASIC)
                0xFA: 'I',  # INT -> Integer BASIC
                0xFF: 'S',  # SYS -> System
            }
            return dos_type_map.get(prodos_type, 'B'), converted_kwargs
        else:
            return prodos_type, converted_kwargs
            
    elif hasattr(source_file, 'dos_type'):
        # Source is DOS
        dos_type = source_file.dos_type
        if dest_fs == 'prodos':
            # DOS -> ProDOS conversion
            prodos_type_map = {
                'T': 0x04,  # Text -> TEXT
                'B': 0x06,  # Binary -> BIN
                'A': 0xFC,  # Applesoft -> BAS  
                'I': 0xFA,  # Integer -> INT
                'S': 0xFF,  # System -> SYS
                'R': 0xFE,  # Relocatable -> REL
            }
            file_type = prodos_type_map.get(dos_type, 0x06)
            # Set auxiliary type for BASIC programs
            if dos_type == 'A':
                converted_kwargs['aux_type'] = 0x0801  # Standard Applesoft load address
            elif dos_type == 'I':
                converted_kwargs['aux_type'] = 0x0800  # Standard Integer BASIC load address
            return file_type, converted_kwargs
        else:
            return dos_type, converted_kwargs
    
    # Fallback - use binary type
    if dest_fs == 'prodos':
        return 0x06, converted_kwargs  # ProDOS BIN
    else:
        return 'B', converted_kwargs   # DOS Binary