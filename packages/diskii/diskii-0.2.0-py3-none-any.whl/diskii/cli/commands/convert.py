"""Convert command implementation."""

import argparse
from pathlib import Path

from ...detection import detect_sector_ordering, open_disk_image
from ...exceptions import DiskiiError
from ...image import SectorOrdering
from ..utils import confirm_action, create_backup, print_success, print_warning


def run_convert(args: argparse.Namespace) -> None:
    """Run the convert command to change sector ordering."""
    source_path = Path(args.source)
    dest_path = Path(args.dest)
    
    if not source_path.exists():
        raise DiskiiError(f"Source image not found: {source_path}")
    
    if dest_path.exists():
        if not confirm_action(f"Destination {dest_path} already exists. Overwrite?"):
            print("Cancelled")
            return
    
    # Detect source and destination sector orderings
    source_ordering = detect_sector_ordering(source_path)
    dest_ordering = detect_sector_ordering(dest_path)
    
    # Check if conversion is needed
    if source_ordering == dest_ordering:
        print_warning(f"Source and destination both use {source_ordering.value}")
        if not confirm_action("Continue anyway?"):
            print("Cancelled")
            return
    
    backup_path = None
    try:
        # Create backup if requested
        if getattr(args, 'backup', False):
            backup_path = create_backup(source_path)
            print_success(f"Created backup: {backup_path}")
        
        # Read entire source image
        source_data = source_path.read_bytes()
        
        # Convert sector ordering
        converted_data = _convert_sector_ordering(
            source_data, source_ordering, dest_ordering
        )
        
        # Write converted data to destination
        dest_path.write_bytes(converted_data)
        
        print_success(f"Converted {source_path} -> {dest_path}")
        print(f"Sector ordering: {source_ordering.value} -> {dest_ordering.value}")
        
    except Exception as e:
        if backup_path:
            print_warning(f"Error occurred, backup available at: {backup_path}")
        raise DiskiiError(f"Conversion failed: {e}") from e


def _convert_sector_ordering(
    data: bytes, source_ordering: SectorOrdering, dest_ordering: SectorOrdering
) -> bytes:
    """Convert disk image data between different sector orderings."""
    
    # If same ordering, just return the data
    if source_ordering == dest_ordering:
        return data
    
    # Determine disk geometry based on size
    data_size = len(data)
    
    # Standard 140KB disk (35 tracks, 16 sectors)
    if data_size == 35 * 16 * 256:
        tracks = 35
        sectors_per_track = 16
        sector_size = 256
    # DOS 3.2 disk (35 tracks, 13 sectors)
    elif data_size == 35 * 13 * 256:
        tracks = 35
        sectors_per_track = 13
        sector_size = 256
    # Larger ProDOS disks - assume 512-byte blocks
    elif data_size % 512 == 0 and data_size >= 35 * 16 * 512:
        # Convert from block-based to sector-based thinking
        # For larger disks, we'll treat them as having virtual tracks/sectors
        total_sectors = data_size // 256
        tracks = 35
        sectors_per_track = total_sectors // tracks
        sector_size = 256
        
        # If it doesn't divide evenly, it's probably a true block device
        if total_sectors % tracks != 0:
            # For true block devices, we can do a simpler conversion
            return _convert_block_ordering(data, source_ordering, dest_ordering)
    else:
        raise DiskiiError(f"Unsupported disk size: {data_size} bytes")
    
    # DOS sector interleave pattern (for DOS-ordered disks)
    dos_interleave = [0, 7, 14, 6, 13, 5, 12, 4, 11, 3, 10, 2, 9, 1, 8, 15]
    
    # Create output buffer
    output_data = bytearray(data_size)
    
    # Convert each sector
    for track in range(tracks):
        for logical_sector in range(min(sectors_per_track, 16)):  # DOS interleave only applies to 16-sector disks
            
            # Calculate source physical sector
            if source_ordering == SectorOrdering.DOS_ORDER and sectors_per_track == 16:
                source_physical_sector = dos_interleave[logical_sector]
            else:
                source_physical_sector = logical_sector
                
            # Calculate destination physical sector  
            if dest_ordering == SectorOrdering.DOS_ORDER and sectors_per_track == 16:
                dest_physical_sector = dos_interleave[logical_sector]
            else:
                dest_physical_sector = logical_sector
            
            # Calculate byte offsets
            source_offset = (track * sectors_per_track + source_physical_sector) * sector_size
            dest_offset = (track * sectors_per_track + dest_physical_sector) * sector_size
            
            # Copy sector data
            if source_offset + sector_size <= len(data):
                output_data[dest_offset:dest_offset + sector_size] = data[source_offset:source_offset + sector_size]
    
    return bytes(output_data)


def _convert_block_ordering(
    data: bytes, source_ordering: SectorOrdering, dest_ordering: SectorOrdering
) -> bytes:
    """Convert block-based disk images (simple byte-for-byte copy since blocks don't have interleaving)."""
    
    # For block-based images (.po files), there's no sector interleaving
    # The conversion is mainly about the file extension convention
    # The data itself remains the same
    
    if source_ordering == SectorOrdering.PRODOS_ORDER and dest_ordering == SectorOrdering.DOS_ORDER:
        # Converting .po to .dsk - data stays the same but represents different logical organization
        return data
    elif source_ordering == SectorOrdering.DOS_ORDER and dest_ordering == SectorOrdering.PRODOS_ORDER:
        # Converting .dsk to .po - data stays the same but represents different logical organization  
        return data
    else:
        # For other conversions, return as-is
        return data