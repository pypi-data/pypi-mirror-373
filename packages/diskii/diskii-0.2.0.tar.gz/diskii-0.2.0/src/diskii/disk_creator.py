#!/usr/bin/env python3
"""Disk image creation utilities for diskii library."""

import struct
from datetime import datetime
from pathlib import Path

from .exceptions import DiskiiError


def create_blank_dos33_image(
    file_path: str | Path, volume_number: int = 254
) -> None:
    """Create a blank DOS 3.3 disk image.

    Args:
        file_path: Path where the disk image will be created
        volume_number: DOS volume number (default 254)
    """
    file_path = Path(file_path)

    # DOS 3.3 specifications
    TRACKS = 35
    SECTORS_PER_TRACK = 16
    BYTES_PER_SECTOR = 256
    TOTAL_SIZE = TRACKS * SECTORS_PER_TRACK * BYTES_PER_SECTOR  # 143,360 bytes

    # Create blank disk image file
    with open(file_path, "wb") as f:
        f.write(b"\x00" * TOTAL_SIZE)

    # Use DOSImage to write sectors with proper ordering
    from .image import DOSImage

    with DOSImage(file_path, read_only=False) as img:
        # Create VTOC (Volume Table of Contents) at track 17, sector 0
        vtoc_data = _create_dos33_vtoc(volume_number)
        img.write_sector(17, 0, vtoc_data)

        # Create initial catalog at track 17, sector 15
        catalog_data = _create_dos33_catalog()
        img.write_sector(17, 15, catalog_data)


def create_blank_prodos_image(
    file_path: str | Path,
    volume_name: str = "BLANK.DISK",
    total_blocks: int = 280,
) -> None:
    """Create a blank ProDOS disk image.

    Args:
        file_path: Path where the disk image will be created
        volume_name: ProDOS volume name (15 chars max)
        total_blocks: Total blocks in the disk (default 280 for 140K disk)
                     Maximum 65535 blocks (32MB)
    """
    file_path = Path(file_path)

    # Validate parameters
    if len(volume_name) > 15:
        raise DiskiiError(f"Volume name too long: {volume_name} (max 15 chars)")
    if total_blocks > 65535:
        raise DiskiiError(f"Too many blocks: {total_blocks} (max 65535)")
    if total_blocks < 5:
        raise DiskiiError(f"Too few blocks: {total_blocks} (min 5)")

    # ProDOS specifications
    BYTES_PER_BLOCK = 512
    total_size = total_blocks * BYTES_PER_BLOCK

    # Create blank disk image
    with open(file_path, "wb") as f:
        # Initialize with zeros
        f.write(b"\x00" * total_size)

        # Create boot blocks (blocks 0-1) - minimal boot code
        f.seek(0)
        boot_block = _create_prodos_boot_blocks()
        f.write(boot_block)

        # Create volume directory (block 2)
        f.seek(2 * BYTES_PER_BLOCK)
        volume_dir = _create_prodos_volume_directory(volume_name, total_blocks)
        f.write(volume_dir)

        # Create volume bitmap (block 6 and following)
        bitmap_start_block = 6
        bitmap_blocks_needed = (
            total_blocks + 4095
        ) // 4096  # Each block covers 4096 blocks

        f.seek(bitmap_start_block * BYTES_PER_BLOCK)
        volume_bitmap = _create_prodos_volume_bitmap(
            total_blocks, bitmap_start_block, bitmap_blocks_needed
        )
        f.write(volume_bitmap)


def create_blank_dos32_image(
    file_path: str | Path, volume_number: int = 254
) -> None:
    """Create a blank DOS 3.2 disk image (13-sector format).

    Args:
        file_path: Path where the disk image will be created
        volume_number: DOS volume number (default 254)
    """
    file_path = Path(file_path)

    # DOS 3.2 specifications
    TRACKS = 35
    SECTORS_PER_TRACK = 13
    BYTES_PER_SECTOR = 256
    TOTAL_SIZE = TRACKS * SECTORS_PER_TRACK * BYTES_PER_SECTOR  # 116,480 bytes

    # Create blank disk image file
    with open(file_path, "wb") as f:
        f.write(b"\x00" * TOTAL_SIZE)

    # Use DOS32Image to write sectors with proper ordering
    from .image import DOS32Image

    with DOS32Image(file_path, read_only=False) as img:
        # Create VTOC at track 17, sector 0
        vtoc_data = _create_dos32_vtoc(volume_number)
        img.write_sector(17, 0, vtoc_data)

        # Create initial catalog at track 17, sector 12 (different from DOS 3.3)
        catalog_data = _create_dos32_catalog()
        img.write_sector(17, 12, catalog_data)


def _get_dos_sector_offset(track: int, sector: int) -> int:
    """Get file offset for DOS 3.3 track/sector."""
    return (track * 16 + sector) * 256


def _get_dos32_sector_offset(track: int, sector: int) -> int:
    """Get file offset for DOS 3.2 track/sector."""
    return (track * 13 + sector) * 256


def _create_dos33_vtoc(volume_number: int) -> bytes:
    """Create DOS 3.3 VTOC (Volume Table of Contents)."""
    vtoc = bytearray(256)

    # VTOC header
    vtoc[0x01] = 17  # Catalog track
    vtoc[0x02] = 15  # Catalog sector (first catalog sector)
    vtoc[0x03] = 3  # Release number
    vtoc[0x27] = 122  # Maximum track/sector list sectors
    vtoc[0x30] = 1  # Last track where sectors were allocated
    vtoc[0x31] = 1  # Direction of track allocation (+1)
    vtoc[0x34] = 35  # Number of tracks per disk
    vtoc[0x35] = 16  # Number of sectors per track
    vtoc[0x36] = 0  # Number of bytes per sector (low byte)
    vtoc[0x37] = 1  # Number of bytes per sector (high byte) -> 256 bytes

    # Track allocation bitmap - mark most sectors as free
    # Each track has 2 bytes for sector allocation (16 bits for 16 sectors)
    for track in range(35):
        offset = 0x38 + track * 4  # Track allocation starts at 0x38

        if track == 0:
            # Boot track - mark sectors 0-2 as used, rest free
            vtoc[offset] = 0xF8  # Low byte: 11111000 (sectors 0-2 used)
            vtoc[offset + 1] = 0xFF  # High byte: all free
        elif track == 17:
            # VTOC/Catalog track - mark VTOC and catalog sectors as used
            vtoc[offset] = 0x00  # Sector 0 (VTOC) used
            vtoc[offset + 1] = 0x7F  # Sector 15 (catalog) used, others free
        else:
            # All other tracks - all sectors free
            vtoc[offset] = 0xFF
            vtoc[offset + 1] = 0xFF

    return bytes(vtoc)


def _create_dos32_vtoc(volume_number: int) -> bytes:
    """Create DOS 3.2 VTOC."""
    vtoc = bytearray(256)

    # VTOC header for DOS 3.2
    vtoc[0x01] = 17  # Catalog track
    vtoc[0x02] = 12  # Catalog sector (DOS 3.2 uses sector 12)
    vtoc[0x03] = 2  # Release number (DOS 3.2)
    vtoc[0x27] = 122  # Maximum track/sector list sectors
    vtoc[0x30] = 1  # Last track where sectors were allocated
    vtoc[0x31] = 1  # Direction of track allocation
    vtoc[0x34] = 35  # Number of tracks per disk
    vtoc[0x35] = 13  # Number of sectors per track (DOS 3.2 difference)
    vtoc[0x36] = 0  # Number of bytes per sector (low)
    vtoc[0x37] = 1  # Number of bytes per sector (high)

    # Track allocation bitmap for 13 sectors per track
    for track in range(35):
        offset = 0x38 + track * 4

        if track == 0:
            # Boot track
            vtoc[offset] = 0xF8  # Sectors 0-2 used
            vtoc[offset + 1] = 0x1F  # Only 13 sectors total (bits 0-12)
        elif track == 17:
            # VTOC/Catalog track
            vtoc[offset] = 0x00  # Sector 0 (VTOC) used
            vtoc[offset + 1] = 0x0F  # Sector 12 (catalog) used, others free
        else:
            # All other tracks - all 13 sectors free
            vtoc[offset] = 0xFF
            vtoc[offset + 1] = 0x1F  # Only 13 bits set (0-12)

    return bytes(vtoc)


def _create_dos33_catalog() -> bytes:
    """Create initial empty DOS 3.3 catalog sector."""
    catalog = bytearray(256)

    # Catalog header
    catalog[0x00] = 0x00  # Next catalog track (0 = last catalog sector)
    catalog[0x01] = 0x00  # Next catalog sector

    # Mark all file entries as deleted (0x00 in track field)
    for i in range(7):  # 7 file entries per catalog sector
        offset = 0x0B + i * 35  # File entries start at 0x0B
        catalog[offset] = 0x00  # Track = 0x00 (deleted entry)

    return bytes(catalog)


def _create_dos32_catalog() -> bytes:
    """Create initial empty DOS 3.2 catalog sector."""
    # DOS 3.2 catalog structure is the same as DOS 3.3
    return _create_dos33_catalog()


def _create_prodos_boot_blocks() -> bytes:
    """Create minimal ProDOS boot blocks (blocks 0-1)."""
    boot_data = bytearray(1024)  # 2 blocks = 1024 bytes

    # Very minimal boot code - just enough to be recognized as ProDOS
    # Block 0 - Bootstrap loader
    boot_data[0x00] = 0x01  # ProDOS boot signature
    boot_data[0x01] = 0x38  # Load address low
    boot_data[0x02] = 0xB0  # Load address high ($B038)

    # Simple "UNABLE TO LOAD PRODOS" message routine
    message = b"UNABLE TO LOAD PRODOS"
    boot_data[0x2D : 0x2D + len(message)] = message

    # Block 1 - Additional boot code (can be minimal)
    boot_data[0x200] = 0x00  # Reserved

    return bytes(boot_data)


def _create_prodos_volume_directory(volume_name: str, total_blocks: int) -> bytes:
    """Create ProDOS volume directory (block 2)."""
    volume_dir = bytearray(512)

    # ProDOS directory block header (first 4 bytes)
    volume_dir[0x00] = 0x02  # Previous block pointer (low) - 0 for volume directory
    volume_dir[0x01] = 0x00  # Previous block pointer (high)  
    volume_dir[0x02] = 0x03  # Next block pointer (low) - 0 for no next block
    volume_dir[0x03] = 0x00  # Next block pointer (high)

    # Volume directory header entry starts at offset 4
    # Storage type (0xF in high nibble) and name length (low nibble)  
    volume_dir[0x04] = 0xF0 | len(volume_name)  # Storage type 0xF + name length
    volume_dir[0x05 : 0x05 + len(volume_name)] = volume_name.encode("ascii").upper()

    # Volume directory key block (adjusted offsets - add 4 to all)
    volume_dir[0x18] = 0x75  # Reserved
    volume_dir[0x19] = 0x00  # Reserved

    # Creation date/time (current time)
    now = datetime.now()
    date_time = _encode_prodos_datetime(now)
    volume_dir[0x1A:0x1E] = date_time

    # Version info
    volume_dir[0x1E] = 0x00  # Version
    volume_dir[0x1F] = 0x00  # Min version
    volume_dir[0x20] = 0xC3  # Access permissions (read/write/destroy)
    volume_dir[0x21] = 0x27  # Entry length (39 bytes)
    volume_dir[0x22] = 0x0D  # Entries per block (13)
    volume_dir[0x23] = 0x01  # File count (low)
    volume_dir[0x24] = 0x00  # File count (high)

    # Volume bitmap pointer (block 6)
    volume_dir[0x25] = 0x06  # Bitmap pointer (low)
    volume_dir[0x26] = 0x00  # Bitmap pointer (high)

    # Total blocks
    volume_dir[0x27] = total_blocks & 0xFF  # Total blocks (low)
    volume_dir[0x28] = (total_blocks >> 8) & 0xFF  # Total blocks (high)

    return bytes(volume_dir)


def _create_prodos_volume_bitmap(
    total_blocks: int, start_block: int, bitmap_blocks: int
) -> bytes:
    """Create ProDOS volume bitmap."""
    bitmap_size = bitmap_blocks * 512
    bitmap = bytearray(bitmap_size)

    # Mark system blocks as used (blocks 0-5 and bitmap blocks)
    system_blocks = set(range(6))  # Blocks 0-5
    system_blocks.update(
        range(start_block, start_block + bitmap_blocks)
    )  # Bitmap blocks

    # Set bits for all blocks (1 = free, 0 = used)
    for block in range(total_blocks):
        byte_offset = block // 8
        bit_offset = 7 - (block % 8)  # ProDOS uses big-endian bit ordering

        if byte_offset < len(bitmap):
            if block not in system_blocks:
                bitmap[byte_offset] |= 1 << bit_offset  # Mark as free
            # Used blocks remain 0 (already initialized)

    return bytes(bitmap)


def _encode_prodos_datetime(dt: datetime) -> bytes:
    """Encode datetime in ProDOS format."""
    # ProDOS date: bits 15-9 = year-1900, 8-5 = month, 4-0 = day
    # ProDOS time: bits 15-11 = hour, 10-5 = minute

    year = dt.year - 1900
    if year < 0:
        year = 0
    if year > 127:
        year = 127

    date_word = (year << 9) | (dt.month << 5) | dt.day
    time_word = (dt.hour << 11) | (dt.minute << 5)

    return struct.pack("<HH", date_word, time_word)


# Convenience functions for common disk sizes
def create_140k_dos_disk(file_path: str | Path) -> None:
    """Create standard 140K DOS 3.3 disk."""
    create_blank_dos33_image(file_path)


def create_140k_prodos_disk(
    file_path: str | Path, volume_name: str = "BLANK.DISK"
) -> None:
    """Create standard 140K ProDOS disk."""
    create_blank_prodos_image(file_path, volume_name, 280)  # 280 blocks = 140K


def create_800k_prodos_disk(
    file_path: str | Path, volume_name: str = "BLANK.DISK"
) -> None:
    """Create 800K ProDOS disk."""
    create_blank_prodos_image(file_path, volume_name, 1600)  # 1600 blocks = 800K


def create_32mb_prodos_disk(
    file_path: str | Path, volume_name: str = "BLANK.DISK"
) -> None:
    """Create maximum 32MB ProDOS disk."""
    create_blank_prodos_image(file_path, volume_name, 65535)  # Maximum ProDOS blocks
