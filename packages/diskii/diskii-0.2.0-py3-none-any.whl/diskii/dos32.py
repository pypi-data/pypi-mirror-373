"""DOS 3.2 filesystem parsing and manipulation."""

import struct

from .exceptions import CorruptedImageError
from .fileentry import DOSFileEntry
from .image import DOS32Image


class DOS32TrackSectorList:
    """DOS 3.2 Track/Sector list parser."""

    def __init__(self, image: DOS32Image, track: int, sector: int):
        self.image = image
        self.track = track
        self.sector = sector

    def read_sectors(self) -> list[bytes]:
        """Read all data sectors for this track/sector list."""
        data_sectors = []
        current_track = self.track
        current_sector = self.sector

        while current_track != 0 or current_sector != 0:
            try:
                # Read the track/sector list sector
                ts_list = self.image.read_sector(current_track, current_sector)

                # First byte is track of next T/S list (0 if last)
                # Second byte is sector of next T/S list (0 if last)
                next_track = ts_list[1]
                next_sector = ts_list[2]

                # Bytes 5-6: sector offset (which sector number in this T/S list)
                sector_offset = struct.unpack("<H", ts_list[5:7])[0]

                # Bytes 12-255: track/sector pairs (122 pairs max)
                for i in range(12, 256, 2):
                    if i + 1 >= len(ts_list):
                        break

                    data_track = ts_list[i]
                    data_sector = ts_list[i + 1]

                    if data_track == 0:
                        # End of data sectors for this T/S list
                        break

                    # Read the actual data sector
                    try:
                        data = self.image.read_sector(data_track, data_sector)
                        data_sectors.append(data)
                    except Exception:
                        # Bad sector - add empty data
                        data_sectors.append(b"\x00" * 256)

                # Move to next T/S list
                current_track = next_track
                current_sector = next_sector

            except Exception:
                # If we can't read a T/S list, stop here
                break

        return data_sectors


class DOS32VTOC:
    """DOS 3.2 Volume Table of Contents parser."""

    def __init__(self, image: DOS32Image):
        self.image = image
        self._vtoc_data: bytes | None = None
        self._dos_version: int | None = None
        self._catalog_track: int | None = None
        self._catalog_sector: int | None = None
        self._sectors_per_track: int | None = None
        self._last_allocated_track: int | None = None
        self._track_allocation_direction: int | None = None
        self._num_tracks: int | None = None
        self._free_sector_count: int | None = None

    def _parse_vtoc(self) -> None:
        """Parse the VTOC from track 17, sector 0."""
        try:
            self._vtoc_data = self.image.read_sector(17, 0)
        except Exception as e:
            raise CorruptedImageError(
                f"Cannot read VTOC at track 17, sector 0: {e}",
                str(self.image.file_path),
            ) from e

        if len(self._vtoc_data) < 256:
            raise CorruptedImageError(
                "VTOC sector too short", str(self.image.file_path)
            )

        # Parse VTOC structure according to DOS 3.2 documentation
        # Same as DOS 3.3 but with 13 sectors per track
        # Byte 1: Track number of first catalog sector (normally 17)
        self._catalog_track = self._vtoc_data[1]

        # Byte 2: Sector number of first catalog sector (normally 12 for DOS 3.2)
        self._catalog_sector = self._vtoc_data[2]

        # Byte 3: Release number of DOS used to INIT this disk
        self._dos_version = self._vtoc_data[3]

        # Byte 6: Number of sectors per track (normally 13 for DOS 3.2)
        self._sectors_per_track = self._vtoc_data[6]

        # Byte 48: Last track where sectors were allocated
        self._last_allocated_track = self._vtoc_data[48]

        # Byte 49: Direction of track allocation (+1 or -1)
        direction_byte = self._vtoc_data[49]
        self._track_allocation_direction = 1 if direction_byte >= 128 else -1

        # Bytes 52-53: Number of tracks per disk (normally 35)
        self._num_tracks = struct.unpack("<H", self._vtoc_data[52:54])[0]

        # Calculate free sectors
        self._calculate_free_sectors()

    def _calculate_free_sectors(self) -> None:
        """Calculate number of free sectors from bitmap."""
        if not self._vtoc_data:
            return

        free_count = 0

        # Track allocation bitmaps start at byte 56
        # Each track gets 4 bytes (32 bits) for its sectors
        for track in range(self._num_tracks or 35):
            bitmap_offset = 56 + (track * 4)
            if bitmap_offset + 4 > len(self._vtoc_data):
                break

            # Read 4-byte bitmap for this track
            bitmap = struct.unpack(
                "<I", self._vtoc_data[bitmap_offset : bitmap_offset + 4]
            )[0]

            # Count free sectors (bits set to 1)
            # DOS 3.2 has 13 sectors per track
            sectors_per_track = self._sectors_per_track or 13
            for sector in range(sectors_per_track):
                if bitmap & (1 << sector):
                    free_count += 1

        self._free_sector_count = free_count

    def is_sector_free(self, track: int, sector: int) -> bool:
        """Check if a specific sector is free."""
        if not self._vtoc_data:
            self._parse_vtoc()

        if track >= (self._num_tracks or 35):
            return False

        bitmap_offset = 56 + (track * 4)
        if bitmap_offset + 4 > len(self._vtoc_data):
            return False

        bitmap = struct.unpack(
            "<I", self._vtoc_data[bitmap_offset : bitmap_offset + 4]
        )[0]
        return bool(bitmap & (1 << sector))

    def get_free_sector_list(self) -> list[tuple[int, int]]:
        """Get list of all free sectors as (track, sector) tuples."""
        if not self._vtoc_data:
            self._parse_vtoc()

        free_sectors = []

        for track in range(self._num_tracks or 35):
            bitmap_offset = 56 + (track * 4)
            if bitmap_offset + 4 > len(self._vtoc_data):
                break

            bitmap = struct.unpack(
                "<I", self._vtoc_data[bitmap_offset : bitmap_offset + 4]
            )[0]

            # DOS 3.2 has 13 sectors per track
            sectors_per_track = self._sectors_per_track or 13
            for sector in range(sectors_per_track):
                if bitmap & (1 << sector):
                    free_sectors.append((track, sector))

        return free_sectors

    @property
    def catalog_track(self) -> int:
        """Get catalog starting track."""
        if self._catalog_track is None:
            self._parse_vtoc()
        return self._catalog_track or 17

    @property
    def catalog_sector(self) -> int:
        """Get catalog starting sector."""
        if self._catalog_sector is None:
            self._parse_vtoc()
        return self._catalog_sector or 12  # DOS 3.2 typically uses sector 12

    @property
    def dos_version(self) -> int:
        """Get DOS version number."""
        if self._dos_version is None:
            self._parse_vtoc()
        return self._dos_version or 2  # DOS 3.2

    @property
    def sectors_per_track(self) -> int:
        """Get sectors per track."""
        if self._sectors_per_track is None:
            self._parse_vtoc()
        return self._sectors_per_track or 13  # DOS 3.2 has 13 sectors per track

    @property
    def num_tracks(self) -> int:
        """Get number of tracks."""
        if self._num_tracks is None:
            self._parse_vtoc()
        return self._num_tracks or 35

    @property
    def free_sectors(self) -> int:
        """Get number of free sectors."""
        if self._free_sector_count is None:
            self._parse_vtoc()
        return self._free_sector_count or 0


class DOS32Catalog:
    """DOS 3.2 catalog parser."""

    def __init__(self, image: DOS32Image):
        self.image = image
        self.vtoc = DOS32VTOC(image)
        self._entries: list[DOSFileEntry] | None = None

    def _parse_catalog_sector(
        self, track: int, sector: int
    ) -> tuple[list[DOSFileEntry], tuple[int, int] | None]:
        """Parse a single catalog sector and return entries plus next sector info."""
        try:
            catalog_data = self.image.read_sector(track, sector)
        except Exception as e:
            raise CorruptedImageError(
                f"Cannot read catalog sector {track},{sector}: {e}",
                str(self.image.file_path),
            ) from e

        entries = []

        # First byte: track of next catalog sector (0 if last)
        # Second byte: sector of next catalog sector (0 if last)
        next_track = catalog_data[1] if len(catalog_data) > 1 else 0
        next_sector = catalog_data[2] if len(catalog_data) > 2 else 0

        next_catalog = (next_track, next_sector) if next_track != 0 else None

        # Parse catalog entries (7 entries per sector, 35 bytes each)
        for i in range(7):
            entry_offset = 11 + (i * 35)  # Skip 11-byte header
            if entry_offset + 35 > len(catalog_data):
                break

            entry_data = catalog_data[entry_offset : entry_offset + 35]
            entry = self._parse_catalog_entry(entry_data)
            if entry:
                entries.append(entry)

        return entries, next_catalog

    def _parse_catalog_entry(self, entry_data: bytes) -> DOSFileEntry | None:
        """Parse a single DOS 3.2 catalog entry."""
        if len(entry_data) < 35:
            return None

        # First byte: track of first track/sector list sector
        ts_list_track = entry_data[0]

        # Skip deleted files (track = 255) only. Track 0 is valid for files.
        if ts_list_track == 255:
            return None

        # Second byte: sector of first track/sector list sector
        ts_list_sector = entry_data[1]

        # Third byte: file type and flags
        type_byte = entry_data[2]

        # Extract file type (bits 0-6) - same as DOS 3.3
        dos_type_map = {
            0x00: "T",  # Text
            0x01: "I",  # Integer BASIC
            0x02: "A",  # Applesoft BASIC
            0x04: "B",  # Binary
            0x08: "S",  # Special/Typeless
            0x10: "R",  # Relocatable
            0x20: "B",  # New B type
            0x40: "B",  # New B type
        }

        # Find the file type
        dos_type = "B"  # Default to binary
        for type_code, type_char in dos_type_map.items():
            if type_byte & type_code:
                dos_type = type_char
                break

        # Check if file is locked (bit 7)
        locked = bool(type_byte & 0x80)

        # Bytes 3-32: filename (30 characters, high ASCII, space padded)
        filename_bytes = entry_data[3:33]

        # Convert from high ASCII and strip spaces
        filename = ""
        for b in filename_bytes:
            if b == 0xA0:  # High ASCII space
                break
            elif b >= 0x80:  # High ASCII
                filename += chr(b - 0x80)
            else:
                filename += chr(b) if 32 <= b <= 126 else ""

        filename = filename.strip()
        if not filename:
            return None

        # Bytes 33-34: file length in sectors
        length_sectors = struct.unpack("<H", entry_data[33:35])[0]

        # Calculate approximate file size (sectors * 256 bytes)
        # This is approximate because DOS doesn't store exact byte count
        file_size = length_sectors * 256

        entry = DOSFileEntry(
            filename=filename,
            file_type=dos_type,
            size=file_size,
            locked=locked,
            track=ts_list_track,
            sector=ts_list_sector,
            length_sectors=length_sectors,
            dos_type=dos_type,
        )

        # Add image reference for file reading
        entry._image = self.image
        return entry

    def parse(self) -> list[DOSFileEntry]:
        """Parse the DOS 3.2 catalog and return list of file entries."""
        if self._entries is not None:
            return self._entries

        entries = []
        current_track = self.vtoc.catalog_track
        current_sector = self.vtoc.catalog_sector

        try:
            while current_track != 0:
                sector_entries, next_catalog = self._parse_catalog_sector(
                    current_track, current_sector
                )
                entries.extend(sector_entries)

                if next_catalog:
                    current_track, current_sector = next_catalog
                else:
                    break

        except Exception as e:
            raise CorruptedImageError(
                f"Error parsing DOS 3.2 catalog: {e}", str(self.image.file_path)
            ) from e

        self._entries = entries
        return entries


def parse_dos32_catalog(image: DOS32Image) -> DOS32Catalog:
    """Parse a DOS 3.2 catalog from an image."""
    return DOS32Catalog(image)
