"""DOS 3.3 and DOS 3.2 file writing functionality."""

import struct

from .dos32 import DOS32VTOC, DOS32Catalog
from .dos33 import DOSVTOC, DOSCatalog
from .exceptions import (
    FileNotFoundError,
    FilesystemError,
    InvalidFileError,
)


class DOSTrackSectorAllocator:
    """Manages track/sector allocation using the DOS VTOC."""

    def __init__(self, image, vtoc_class=DOSVTOC):
        self.image = image
        self.vtoc_class = vtoc_class
        self._vtoc = None

    @property
    def vtoc(self):
        """Get or create VTOC instance."""
        if self._vtoc is None:
            self._vtoc = self.vtoc_class(self.image)
        return self._vtoc

    def find_free_sectors(self, count: int) -> list[tuple[int, int]]:
        """Find free track/sector pairs.

        Args:
            count: Number of sectors needed

        Returns:
            List of (track, sector) tuples

        Raises:
            FilesystemError: If not enough free sectors
        """
        free_sectors = []

        # Skip track 17 (VTOC track) and tracks used for catalog
        total_tracks = (
            35 if isinstance(self.vtoc, DOSVTOC) else 35
        )  # DOS 3.2 also has 35 tracks
        sectors_per_track = self.vtoc.sectors_per_track

        for track in range(total_tracks):
            # Skip VTOC track
            if track == self.vtoc.catalog_track:
                continue

            # Get free sector bitmap for this track
            if (
                hasattr(self.vtoc, "_track_sector_maps")
                and self.vtoc._track_sector_maps
            ):
                track_bitmap = self.vtoc._track_sector_maps.get(track, 0)
            else:
                # Read VTOC to get track bitmap
                vtoc_data = self.image.read_sector(
                    17, 0
                )  # VTOC is always at track 17, sector 0
                track_bitmap = struct.unpack_from("<H", vtoc_data, 56 + track * 4)[
                    0
                ]  # Track allocation map

            # Check each sector in the track
            for sector in range(sectors_per_track):
                if track_bitmap & (1 << sector):  # Bit set = free
                    free_sectors.append((track, sector))
                    if len(free_sectors) >= count:
                        return free_sectors[:count]

        raise FilesystemError(
            f"Not enough free sectors: need {count}, found {len(free_sectors)}",
            str(self.image.file_path),
        )

    def allocate_sectors(self, sector_list: list[tuple[int, int]]) -> None:
        """Mark sectors as allocated in the VTOC."""
        # Read current VTOC
        vtoc_data = bytearray(self.image.read_sector(17, 0))

        # Update track allocation maps
        for track, sector in sector_list:
            # Each track has a 4-byte entry in the allocation table starting at offset 56
            track_offset = 56 + track * 4

            # Read current bitmap for this track (first 2 bytes are bitmap, next 2 are unused)
            track_bitmap = struct.unpack_from("<H", vtoc_data, track_offset)[0]

            # Clear the bit for this sector (0 = allocated, 1 = free)
            track_bitmap &= ~(1 << sector)

            # Write back the updated bitmap
            struct.pack_into("<H", vtoc_data, track_offset, track_bitmap)

        # Write updated VTOC
        self.image.write_sector(17, 0, bytes(vtoc_data))

    def deallocate_sectors(self, sector_list: list[tuple[int, int]]) -> None:
        """Mark sectors as free in the VTOC."""
        # Read current VTOC
        vtoc_data = bytearray(self.image.read_sector(17, 0))

        # Update track allocation maps
        for track, sector in sector_list:
            track_offset = 56 + track * 4

            # Read current bitmap for this track
            track_bitmap = struct.unpack_from("<H", vtoc_data, track_offset)[0]

            # Set the bit for this sector (1 = free, 0 = allocated)
            track_bitmap |= 1 << sector

            # Write back the updated bitmap
            struct.pack_into("<H", vtoc_data, track_offset, track_bitmap)

        # Write updated VTOC
        self.image.write_sector(17, 0, bytes(vtoc_data))


def create_dos_file(
    image, filename: str, file_type: str, data: bytes, locked: bool = False
) -> None:
    """Create a new file on a DOS disk image.

    Args:
        image: DOSImage or DOS32Image instance
        filename: Name of the file to create (up to 30 chars)
        file_type: DOS file type ('T', 'I', 'A', 'B', 'S', 'R')
        data: File content bytes
        locked: Whether the file should be locked

    Raises:
        InvalidFileError: If filename already exists or is invalid
        FilesystemError: If not enough free space
    """
    # Validate filename
    if not filename or len(filename) > 30:
        raise InvalidFileError(f"Invalid filename: {filename}")

    if file_type not in ["T", "I", "A", "B", "S", "R"]:
        raise InvalidFileError(f"Invalid DOS file type: {file_type}")

    # Check if file already exists
    existing_files = image.get_file_list()
    for existing_file in existing_files:
        if existing_file.filename.upper() == filename.upper():
            raise InvalidFileError(f"File already exists: {filename}")

    # Determine VTOC class based on image type
    vtoc_class = (
        DOS32VTOC
        if hasattr(image, "SECTORS_PER_TRACK") and image.SECTORS_PER_TRACK == 13
        else DOSVTOC
    )

    # For binary files, prepend exact file size to preserve cross-format integrity
    actual_data = data
    if file_type == "B":
        # Check if this looks like it already has a DOS binary header
        has_dos_header = False
        if len(data) >= 4:
            start_addr = struct.unpack("<H", data[0:2])[0]
            file_length = struct.unpack("<H", data[2:4])[0]
            
            # Very strict validation for DOS binary header
            # Both address and length must be reasonable, and length must not exceed available data
            if (0x0800 <= start_addr <= 0xBFFF and 
                0 < file_length <= len(data) - 4 and
                file_length < 32768):  # Max reasonable size for Apple II program
                has_dos_header = True
        
        if not has_dos_header:
            # Add our own size metadata for cross-format integrity
            # Format: 4 bytes = original file length (little-endian 32-bit)
            size_header = struct.pack("<I", len(data))
            actual_data = size_header + data

    # Calculate sectors needed based on actual data (including any headers)
    sectors_per_ts = 256  # Bytes per track/sector list sector
    sectors_needed = (len(actual_data) + sectors_per_ts - 1) // sectors_per_ts

    if sectors_needed == 0:
        sectors_needed = 1  # Always need at least one sector

    # Add one extra sector for track/sector list if file is large
    ts_sectors_needed = 1
    if sectors_needed > 122:  # 122 entries fit in one T/S list sector
        ts_sectors_needed = (sectors_needed + 121) // 122  # Additional T/S list sectors

    total_sectors_needed = sectors_needed + ts_sectors_needed

    # Allocate sectors
    allocator = DOSTrackSectorAllocator(image, vtoc_class)
    allocated_sectors = allocator.find_free_sectors(total_sectors_needed)

    try:
        # First allocated sector is the track/sector list
        ts_track, ts_sector = allocated_sectors[0]
        data_sectors = allocated_sectors[1:]

        # Create track/sector list
        ts_data = _create_track_sector_list(data_sectors, sectors_needed)
        image.write_sector(ts_track, ts_sector, ts_data)

        # Write data sectors
        for i, (track, sector) in enumerate(data_sectors):
            start_offset = i * 256
            end_offset = min(start_offset + 256, len(actual_data))

            if start_offset < len(actual_data):
                sector_data = actual_data[start_offset:end_offset]
                # Pad sector to 256 bytes
                sector_data = sector_data.ljust(256, b"\x00")
                image.write_sector(track, sector, sector_data)
            else:
                # Empty sector for padding
                image.write_sector(track, sector, b"\x00" * 256)

        # Mark sectors as allocated
        allocator.allocate_sectors(allocated_sectors)

        # Add catalog entry
        _add_catalog_entry(
            image,
            filename,
            file_type,
            ts_track,
            ts_sector,
            len(actual_data),
            locked,
            vtoc_class,
        )

    except Exception as e:
        # If anything fails, deallocate sectors that were allocated
        try:
            allocator.deallocate_sectors(allocated_sectors)
        except:
            pass  # Best effort cleanup
        raise FilesystemError(f"Failed to create file {filename}: {e}") from e


def _create_track_sector_list(
    data_sectors: list[tuple[int, int]], sector_count: int
) -> bytes:
    """Create a DOS track/sector list sector."""
    ts_data = bytearray(256)

    # First byte is unused, second byte is sector count
    ts_data[1] = sector_count & 0xFF
    ts_data[2] = (sector_count >> 8) & 0xFF

    # Track/sector pairs start at offset 12
    for i, (track, sector) in enumerate(data_sectors[:122]):  # Max 122 entries
        offset = 12 + (i * 2)
        if offset < 254:  # Make sure we don't overflow
            ts_data[offset] = track
            ts_data[offset + 1] = sector

    return bytes(ts_data)


def _add_catalog_entry(
    image,
    filename: str,
    file_type: str,
    ts_track: int,
    ts_sector: int,
    file_size: int,
    locked: bool,
    vtoc_class,
) -> None:
    """Add a catalog entry for a new DOS file."""

    # Get catalog location from VTOC
    vtoc = vtoc_class(image)
    catalog_track = vtoc.catalog_track
    catalog_sector = vtoc.catalog_sector

    # Search through catalog sectors for an empty slot
    while True:
        try:
            catalog_data = bytearray(image.read_sector(catalog_track, catalog_sector))
        except:
            raise FilesystemError("Cannot read catalog sector", str(image.file_path))

        # Check for empty catalog entry (track = 0xFF or track = 0x00)
        for i in range(7):  # 7 entries per catalog sector
            offset = 0x0B + i * 35  # File entries start at 0x0B, each entry is 35 bytes

            if offset + 35 > len(catalog_data):
                break

            entry_track = catalog_data[offset]

            # Check if entry is truly empty (track=0 AND sector=0) or deleted (track=0xFF)
            entry_sector = (
                catalog_data[offset + 1] if offset + 1 < len(catalog_data) else 0
            )
            is_empty = (
                entry_track == 0x00 and entry_sector == 0x00
            ) or entry_track == 0xFF

            if is_empty:
                # Found empty entry
                _write_catalog_entry(
                    catalog_data,
                    offset,
                    filename,
                    file_type,
                    ts_track,
                    ts_sector,
                    file_size,
                    locked,
                )

                # Write updated catalog sector
                image.write_sector(catalog_track, catalog_sector, bytes(catalog_data))
                return

        # Check next catalog sector
        next_track = catalog_data[1]
        next_sector = catalog_data[2]

        if next_track == 0:
            # No more catalog sectors, need to add one (not implemented)
            raise FilesystemError("Catalog is full", str(image.file_path))

        catalog_track = next_track
        catalog_sector = next_sector


def _write_catalog_entry(
    catalog_data: bytearray,
    offset: int,
    filename: str,
    file_type: str,
    ts_track: int,
    ts_sector: int,
    file_size: int,
    locked: bool,
) -> None:
    """Write a DOS catalog entry at the specified offset."""

    # Byte 0: Track of first track/sector list
    catalog_data[offset] = ts_track

    # Byte 1: Sector of first track/sector list
    catalog_data[offset + 1] = ts_sector

    # Byte 2: File type and flags
    type_byte = 0x80  # Normal file
    if locked:
        type_byte |= 0x40

    type_mapping = {"T": 0x00, "I": 0x01, "A": 0x02, "B": 0x04, "S": 0x08, "R": 0x10}
    type_byte |= type_mapping.get(file_type, 0x00)

    catalog_data[offset + 2] = type_byte

    # Bytes 3-32: Filename (30 bytes, high ASCII, padded with spaces)
    name_bytes = filename.upper().encode("ascii")[:30]
    # Convert to high ASCII
    name_bytes = bytes(b | 0x80 for b in name_bytes)
    name_bytes = name_bytes.ljust(30, b"\xa0")  # Pad with high ASCII space

    catalog_data[offset + 3 : offset + 33] = name_bytes

    # Bytes 33-34: File size in sectors (little endian)
    sector_count = (file_size + 255) // 256
    struct.pack_into("<H", catalog_data, offset + 33, sector_count)


def delete_dos_file(image, filename: str) -> None:
    """Delete a file from a DOS disk image.

    Args:
        image: DOSImage or DOS32Image instance
        filename: Name of the file to delete

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    # Determine VTOC and catalog classes
    vtoc_class = (
        DOS32VTOC
        if hasattr(image, "SECTORS_PER_TRACK") and image.SECTORS_PER_TRACK == 13
        else DOSVTOC
    )
    catalog_class = DOS32Catalog if vtoc_class == DOS32VTOC else DOSCatalog

    # Find the file in catalog
    catalog = catalog_class(image)
    files = catalog.parse()

    target_file = None
    for file_entry in files:
        if file_entry.filename.upper() == filename.upper():
            target_file = file_entry
            break

    if target_file is None:
        raise FileNotFoundError(filename, str(image.file_path))

    # Collect sectors to deallocate
    sectors_to_free = []

    # Add track/sector list sector
    sectors_to_free.append((target_file.track, target_file.sector))

    # Read track/sector list to get data sector locations
    ts_data = image.read_sector(target_file.track, target_file.sector)

    # Parse track/sector list to find data sectors (starts at offset 12)
    for i in range(12, 256, 2):
        if i + 1 >= len(ts_data):
            break

        data_track = ts_data[i]
        data_sector = ts_data[i + 1]

        if data_track == 0:  # End of valid entries
            break

        sectors_to_free.append((data_track, data_sector))

    # Deallocate sectors
    allocator = DOSTrackSectorAllocator(image, vtoc_class)
    allocator.deallocate_sectors(sectors_to_free)

    # Remove catalog entry
    _remove_catalog_entry(image, filename, vtoc_class)


def _remove_catalog_entry(image, filename: str, vtoc_class) -> None:
    """Remove a DOS catalog entry by marking it as deleted."""

    # Get catalog location from VTOC
    vtoc = vtoc_class(image)
    catalog_track = vtoc.catalog_track
    catalog_sector = vtoc.catalog_sector

    # Search through catalog sectors
    while True:
        try:
            catalog_data = bytearray(image.read_sector(catalog_track, catalog_sector))
        except:
            raise FileNotFoundError(filename, str(image.file_path))

        # Check each catalog entry
        for i in range(7):  # 7 entries per sector
            offset = 0x0B + i * 35  # File entries start at 0x0B

            if offset + 35 > len(catalog_data):
                break

            entry_track = catalog_data[offset]

            # Check if entry is a valid file (not empty: track=0 AND sector=0, not deleted: track=0xFF)
            entry_sector = (
                catalog_data[offset + 1] if offset + 1 < len(catalog_data) else 0
            )
            is_valid_file = not (
                (entry_track == 0x00 and entry_sector == 0x00) or entry_track == 0xFF
            )

            if is_valid_file:
                # Read filename from entry
                name_bytes = catalog_data[offset + 3 : offset + 33]
                # Convert from high ASCII and strip padding
                entry_filename = (
                    bytes(b & 0x7F for b in name_bytes).decode("ascii").rstrip(" ")
                )

                if entry_filename.upper() == filename.upper():
                    # Found the entry, mark as deleted
                    catalog_data[offset] = 0xFF  # Mark as deleted

                    # Write updated catalog sector
                    image.write_sector(
                        catalog_track, catalog_sector, bytes(catalog_data)
                    )
                    return

        # Check next catalog sector
        next_track = catalog_data[1]
        next_sector = catalog_data[2]

        if next_track == 0:
            break

        catalog_track = next_track
        catalog_sector = next_sector
    
    # File not found in any catalog sector
    raise FileNotFoundError(filename, str(image.file_path))
