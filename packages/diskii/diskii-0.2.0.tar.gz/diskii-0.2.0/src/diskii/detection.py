"""Disk image format detection."""

from pathlib import Path

from .exceptions import (
    AccessError,
    CorruptedImageError,
    UnrecognizedFormatError,
    IOError as DiskiiIOError,
    PermissionError as DiskiiPermissionError,
)
from .image import (
    DiskImage,
    DOS32Image,
    DOSImage,
    DOSOrderedProDOSImage,
    FilesystemType,
    ImageFormat,
    ProDOSImage,
    ProDOSOrderedDOSImage,
    SectorOrdering,
)


def detect_sector_ordering(file_path: str | Path) -> SectorOrdering:
    """Detect sector ordering from file extension."""
    path = Path(file_path)
    extension = path.suffix.lower()

    extension_map = {
        ".dsk": SectorOrdering.DOS_ORDER,
        ".do": SectorOrdering.DOS_ORDER,
        ".po": SectorOrdering.PRODOS_ORDER,
        ".hdv": SectorOrdering.PRODOS_ORDER,
        ".d13": SectorOrdering.DOS32_ORDER,
    }

    ordering = extension_map.get(extension)
    if not ordering:
        # Default to DOS order for unknown extensions
        ordering = SectorOrdering.DOS_ORDER

    return ordering


def detect_filesystem(
    file_path: str | Path, sector_ordering: SectorOrdering
) -> FilesystemType:
    """Detect filesystem type by examining disk content."""
    path = Path(file_path)

    try:
        if not path.exists():
            raise AccessError(f"Image file does not exist: {path}")

        file_size = path.stat().st_size
    except PermissionError as e:
        raise DiskiiPermissionError(f"Permission denied accessing {path}") from e
    except OSError as e:
        raise DiskiiIOError(f"I/O error accessing {path}: {e}") from e

    # Check for zero-byte files (definitely corrupted)
    if file_size == 0:
        raise CorruptedImageError(f"Image file is empty: {path}", str(path))

    # Very small files are probably not disk images
    if file_size < 256:
        raise UnrecognizedFormatError(str(path))

    # Check for DOS 3.2 based on size
    dos32_sizes = [91 * 256, 35 * 13 * 256]  # 13-sector formats
    if file_size in dos32_sizes:
        return FilesystemType.DOS32

    # For standard 140KB disk images, need to examine content
    dos33_size = 35 * 16 * 256
    if file_size == dos33_size:
        return _detect_filesystem_140k(path, sector_ordering)

    # Larger files are likely ProDOS hard disk volumes, but check for DOS VTOC first
    if file_size > dos33_size and file_size % 512 == 0:
        # Check for DOS VTOC signature first (in case of DOS on ProDOS-ordered disk)
        if _has_dos_vtoc_signature(path, sector_ordering):
            return FilesystemType.DOS33
        # Then check for ProDOS signature
        if _has_prodos_signature(path, sector_ordering):
            return FilesystemType.PRODOS
        # If signatures can't be read (e.g., in tests), default to ProDOS for large files
        return FilesystemType.PRODOS

    # Check if it could be ProDOS based on block alignment
    if file_size % 512 == 0:
        # Check for DOS VTOC first (DOS on ProDOS-ordered disks)
        if _has_dos_vtoc_signature(path, sector_ordering):
            return FilesystemType.DOS33
        # Then check for ProDOS signature
        if _has_prodos_signature(path, sector_ordering):
            return FilesystemType.PRODOS
        # If signatures can't be read (e.g., in tests), default to ProDOS for block-aligned files
        return FilesystemType.PRODOS

    # If we reach here, the file size doesn't match any known format
    raise UnrecognizedFormatError(str(path))


def _detect_filesystem_140k(
    file_path: Path, sector_ordering: SectorOrdering
) -> FilesystemType:
    """Detect filesystem for standard 140KB disk images."""
    # Check for DOS VTOC signature first
    if _has_dos_vtoc_signature(file_path, sector_ordering):
        return FilesystemType.DOS33
    
    # Check for ProDOS volume directory signature
    if _has_prodos_signature(file_path, sector_ordering):
        return FilesystemType.PRODOS

    # Default to DOS 3.3 for 140KB images without clear signatures
    return FilesystemType.DOS33


def _has_prodos_signature(file_path: Path, sector_ordering: SectorOrdering) -> bool:
    """Check for ProDOS volume directory signature."""
    try:
        with open(file_path, "rb") as f:
            # ProDOS volume directory is at block 2
            # Need to find the correct physical location based on sector ordering
            if sector_ordering == SectorOrdering.PRODOS_ORDER:
                # In .po files, block 2 is at offset 2 * 512
                f.seek(2 * 512)
                block = f.read(512)
                return _is_prodos_volume_directory(block)
            elif sector_ordering == SectorOrdering.DOS_ORDER:
                # In .dsk files, search for ProDOS volume directory in multiple locations
                # Standard location: block 2 (sectors 4,5)
                # But some disks may have non-standard layouts, so search first several blocks
                try:
                    file_size = f.seek(0, 2)  # Get file size
                    f.seek(0)
                    
                    # Search blocks 0 through 7 for ProDOS volume directory
                    for block_num in range(8):
                        sector1_num = block_num * 2
                        sector2_num = block_num * 2 + 1
                        
                        # Convert to track/sector
                        track1 = sector1_num // 16
                        sector1 = sector1_num % 16
                        track2 = sector2_num // 16 
                        sector2 = sector2_num % 16
                        
                        sector1_offset = (track1 * 16 + sector1) * 256
                        sector2_offset = (track2 * 16 + sector2) * 256
                        
                        # Make sure we don't read past end of file
                        if sector2_offset + 256 <= file_size:
                            f.seek(sector1_offset)
                            sector1_data = f.read(256)
                            f.seek(sector2_offset)
                            sector2_data = f.read(256)
                            
                            if len(sector1_data) == 256 and len(sector2_data) == 256:
                                block = sector1_data + sector2_data
                                if _is_prodos_volume_directory(block):
                                    return True
                    
                    # Also check if it's stored sequentially (non-standard but possible)
                    for block_num in range(8):
                        f.seek(block_num * 512)
                        sequential_block = f.read(512)
                        if len(sequential_block) == 512 and _is_prodos_volume_directory(sequential_block):
                            return True
                        
                    return False
                except (OSError, IOError):
                    return False
            else:
                # DOS 3.2 format doesn't support ProDOS
                return False

    except (PermissionError, OSError):
        # If we can't read the file, assume it's not ProDOS
        return False

    return False


def _is_prodos_volume_directory(block: bytes) -> bool:
    """Check if a block contains a ProDOS volume directory header."""
    if len(block) < 20:
        return False

    # Check for ProDOS volume directory header at multiple offsets
    # Standard location: offset 4
    # Sometimes in DOS-ordered disks: offset 256+4 (second sector of block)
    offsets_to_check = [4]
    if len(block) >= 512:
        offsets_to_check.append(256 + 4)  # Second sector start + 4
    
    for offset in offsets_to_check:
        if offset + 15 < len(block):  # Ensure we have enough bytes to check
            # ProDOS volume directory header:
            # Byte offset+0: storage type (high nibble) + name length (low nibble)
            # Bytes offset+1 to offset+1+name_length: volume name
            storage_type_byte = block[offset]

            # Check storage type is 0xF (volume directory)
            if (storage_type_byte & 0xF0) == 0xF0:
                # Check name length is reasonable (1-15 characters)
                name_length = storage_type_byte & 0x0F
                if 1 <= name_length <= 15:
                    # Check that we have enough space for the name
                    if offset + 1 + name_length <= len(block):
                        # Check volume name contains reasonable characters
                        volume_name = block[offset + 1 : offset + 1 + name_length]
                        if all(32 <= b <= 126 for b in volume_name):
                            return True

    return False


def _has_dos_vtoc_signature(file_path: Path, sector_ordering: SectorOrdering) -> bool:
    """Check for DOS VTOC signature in the disk image."""
    try:
        with open(file_path, "rb") as f:
            # DOS VTOC is typically at track 17, sector 0
            # Need to find the correct physical location based on sector ordering
            
            if sector_ordering == SectorOrdering.PRODOS_ORDER:
                # In .po files, need to convert track/sector to block address
                # Track 17, sector 0 = linear sector 17*16 + 0 = 272
                # Block number = 272 // 2 = 136
                # Offset within block = 272 % 2 = 0 (first half)
                vtoc_block = 136
                f.seek(vtoc_block * 512)
                block_data = f.read(512)
                if len(block_data) >= 256:
                    vtoc_data = block_data[:256]  # First half of block
                    if _is_dos_vtoc_sector(vtoc_data):
                        return True
                        
                # Also check if VTOC is in second half of some block
                if len(block_data) >= 512:
                    vtoc_data = block_data[256:]  # Second half of block
                    if _is_dos_vtoc_sector(vtoc_data):
                        return True
                        
                # Search other common locations
                for track in range(15, 25):  # Search around track 17
                    linear_sector = track * 16  # sector 0 of each track
                    block_num = linear_sector // 2
                    sector_offset = linear_sector % 2
                    
                    f.seek(block_num * 512)
                    block = f.read(512)
                    if len(block) >= 512:
                        if sector_offset == 0:
                            vtoc_data = block[:256]
                        else:
                            vtoc_data = block[256:]
                        
                        if _is_dos_vtoc_sector(vtoc_data):
                            return True
                
            elif sector_ordering == SectorOrdering.DOS_ORDER:
                # In .dsk files, standard DOS sector ordering
                # Track 17, sector 0
                linear_sector = 17 * 16 + 0
                f.seek(linear_sector * 256)
                vtoc_data = f.read(256)
                if len(vtoc_data) >= 256 and _is_dos_vtoc_sector(vtoc_data):
                    return True
                    
                # Search nearby tracks in case VTOC is relocated
                for track in range(15, 25):
                    linear_sector = track * 16  # sector 0
                    f.seek(linear_sector * 256)
                    vtoc_data = f.read(256)
                    if len(vtoc_data) >= 256 and _is_dos_vtoc_sector(vtoc_data):
                        return True
                        
            else:
                # DOS32_ORDER - 13 sectors per track
                # Track 17, sector 0 
                linear_sector = 17 * 13 + 0
                f.seek(linear_sector * 256)
                vtoc_data = f.read(256)
                if len(vtoc_data) >= 256 and _is_dos_vtoc_sector(vtoc_data):
                    return True

    except (PermissionError, OSError, IOError):
        # If we can't read the file, assume it's not DOS
        return False

    return False


def _is_dos_vtoc_sector(sector_data: bytes) -> bool:
    """Check if sector contains a DOS VTOC signature."""
    if len(sector_data) < 256:
        return False
        
    # DOS 3.3 VTOC signature checks (same as in ProDOSOrderedSectorReader):
    # - Byte 1: Track number of first catalog sector (usually 17)  
    # - Byte 2: Sector number of first catalog sector (usually 15)
    # - Byte 3: DOS release number (3 for DOS 3.3)
    # - Byte 6: Volume number (usually 254)
    
    # Check for DOS 3.3 VTOC patterns
    if (sector_data[3] == 3 and  # DOS release 3
        sector_data[6] == 254 and  # Standard volume number
        sector_data[1] in range(10, 25) and  # Reasonable catalog track
        sector_data[2] in range(0, 16)):  # Valid catalog sector
        return True
        
    # Additional check: look for track allocation bitmap pattern
    # Bytes 56-195 contain the track allocation bitmap (DOS 3.3)
    if len(sector_data) >= 196:
        bitmap_start = 56
        bitmap_end = 196
        bitmap = sector_data[bitmap_start:bitmap_end]
        
        # Count tracks that appear to be in use (have any sectors allocated)
        tracks_in_use = sum(1 for byte_val in bitmap if byte_val != 0xFF)
        
        # DOS disk should have some tracks in use but not all
        if 5 <= tracks_in_use <= 30 and sector_data[3] == 3:  # Reasonable range + DOS 3.3
            return True
    
    return False


def detect_format(file_path: str | Path) -> ImageFormat:
    """Detect complete disk image format."""
    path = Path(file_path)

    # Phase 1: Get sector ordering hint from extension
    primary_ordering = detect_sector_ordering(file_path)

    # Phase 2: Try to detect filesystem with the primary ordering
    try:
        filesystem = detect_filesystem(file_path, primary_ordering)
        return ImageFormat(primary_ordering, filesystem)
    except UnrecognizedFormatError:
        # If detection failed with primary ordering, try alternatives
        pass

    # Phase 3: For .dsk files, also try ProDOS ordering (rare but exists)
    if path.suffix.lower() == ".dsk" and primary_ordering == SectorOrdering.DOS_ORDER:
        try:
            filesystem = detect_filesystem(file_path, SectorOrdering.PRODOS_ORDER)
            return ImageFormat(SectorOrdering.PRODOS_ORDER, filesystem)
        except UnrecognizedFormatError:
            pass

    # Phase 4: For .po files, also try DOS ordering (just in case)
    elif (
        path.suffix.lower() == ".po" and primary_ordering == SectorOrdering.PRODOS_ORDER
    ):
        try:
            filesystem = detect_filesystem(file_path, SectorOrdering.DOS_ORDER)
            return ImageFormat(SectorOrdering.DOS_ORDER, filesystem)
        except UnrecognizedFormatError:
            pass

    # If all attempts failed, raise the original error
    filesystem = detect_filesystem(file_path, primary_ordering)  # This will raise
    return ImageFormat(primary_ordering, filesystem)


def validate_image_file(file_path: str | Path) -> None:
    """Validate that an image file exists and is accessible."""
    path = Path(file_path)

    if not path.exists():
        raise AccessError(f"Image file does not exist: {path}")

    if not path.is_file():
        raise AccessError(f"Path is not a file: {path}")

    try:
        # Test if we can read the file
        with open(path, "rb") as f:
            f.read(1)  # Try to read just one byte
    except PermissionError as e:
        raise DiskiiPermissionError(f"Permission denied accessing {path}") from e
    except OSError as e:
        raise DiskiiIOError(f"I/O error accessing {path}: {e}") from e


def open_disk_image(file_path: str | Path, read_only: bool = True) -> DiskImage:
    """Open a disk image file and return appropriate DiskImage instance."""
    path = Path(file_path)

    # Validate the file first
    validate_image_file(path)

    try:
        image_format = detect_format(path)
    except (DiskiiPermissionError, DiskiiIOError, CorruptedImageError):
        # Re-raise diskii-specific errors as-is
        raise
    except Exception as e:
        raise UnrecognizedFormatError(str(path)) from e

    # Create appropriate image instance based on filesystem type and sector ordering
    if image_format.filesystem == FilesystemType.DOS32:
        return DOS32Image(path, image_format, read_only)
    elif image_format.filesystem == FilesystemType.DOS33:
        # Check if DOS is in ProDOS block ordering (special case for .po files)
        if image_format.sector_ordering == SectorOrdering.PRODOS_ORDER:
            return ProDOSOrderedDOSImage(path, image_format, read_only)
        else:
            return DOSImage(path, image_format, read_only)
    elif image_format.filesystem == FilesystemType.PRODOS:
        # Check if ProDOS is in DOS sector ordering (special case for .dsk files)
        if image_format.sector_ordering == SectorOrdering.DOS_ORDER:
            return DOSOrderedProDOSImage(path, image_format, read_only)
        else:
            return ProDOSImage(path, image_format, read_only)
    else:
        raise UnrecognizedFormatError(str(path))
