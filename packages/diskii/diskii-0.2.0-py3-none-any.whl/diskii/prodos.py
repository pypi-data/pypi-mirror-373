"""ProDOS filesystem parsing and manipulation."""

import struct
from datetime import UTC, datetime

from .exceptions import (
    CorruptedImageError,
    InvalidHeaderError,
)
from .fileentry import ProDOSFileEntry
from .image import ProDOSImage


def prodos_date_to_datetime(date_bytes: bytes) -> datetime | None:
    """Convert ProDOS date format to Python datetime.

    ProDOS date format:
    - 2 bytes for date: YYYYYYY MMMM DDDDD (year, month, day)
    - 1 byte for time: HHHHH MMM (hour, minute/8)

    Year encoding: 0-39 = 2000-2039, 40-99 = 1940-1999, 100-127 = 2000-2027
    """
    if len(date_bytes) < 4:
        return None

    date_word = struct.unpack("<H", date_bytes[:2])[0]
    time_word = struct.unpack("<H", date_bytes[2:4])[0]

    # Extract date components
    day = date_word & 0x1F
    month = (date_word >> 5) & 0x0F
    year_raw = (date_word >> 9) & 0x7F

    # Extract time components
    minute = time_word & 0x3F
    hour = (time_word >> 8) & 0x1F

    # Handle year encoding
    if year_raw == 0:
        return None  # Invalid date
    elif year_raw <= 39:
        year = 2000 + year_raw
    elif year_raw <= 99:
        year = 1900 + year_raw
    else:
        year = 2000 + (year_raw - 100)

    # Validate components
    if month == 0 or month > 12 or day == 0 or day > 31 or hour > 23 or minute > 59:
        return None

    try:
        return datetime(year, month, day, hour, minute, tzinfo=UTC)
    except ValueError:
        return None


class ProDOSVolumeBitmap:
    """ProDOS volume bitmap parser for free space tracking."""

    def __init__(self, image: ProDOSImage):
        self.image = image
        self._bitmap_blocks: list[int] | None = None
        self._free_blocks: int | None = None
        self._used_blocks: int | None = None

    def _find_bitmap_block(self) -> int:
        """Find the volume bitmap block (usually block 6)."""
        # The volume bitmap immediately follows the volume directory
        # For most disks, this is block 6 (blocks 2-5 are directory)
        # But we should read from the volume directory to be sure

        # For now, assume standard layout - bitmap starts at block 6
        return 6

    def parse_bitmap(self) -> dict:
        """Parse the volume bitmap and return free/used block information."""
        if self._free_blocks is not None:
            return {
                "free_blocks": self._free_blocks,
                "used_blocks": self._used_blocks,
                "total_blocks": self.image.total_blocks,
            }

        bitmap_start_block = self._find_bitmap_block()
        total_blocks = self.image.total_blocks

        # Calculate how many bitmap blocks we need
        # Each bitmap block can track 512 * 8 = 4096 blocks
        blocks_per_bitmap = 512 * 8
        bitmap_blocks_needed = (
            total_blocks + blocks_per_bitmap - 1
        ) // blocks_per_bitmap

        free_count = 0
        used_count = 0

        try:
            for bitmap_block_num in range(bitmap_blocks_needed):
                bitmap_block = self.image.read_block(
                    bitmap_start_block + bitmap_block_num
                )

                # Each byte represents 8 blocks
                for byte_offset, byte_val in enumerate(bitmap_block):
                    for bit_pos in range(8):
                        block_num = (
                            (bitmap_block_num * blocks_per_bitmap)
                            + (byte_offset * 8)
                            + bit_pos
                        )

                        if block_num >= total_blocks:
                            break

                        if byte_val & (1 << bit_pos):
                            free_count += 1
                        else:
                            used_count += 1

        except Exception as e:
            raise CorruptedImageError(
                f"Error reading volume bitmap: {e}", str(self.image.file_path)
            ) from e

        self._free_blocks = free_count
        self._used_blocks = used_count

        return {
            "free_blocks": free_count,
            "used_blocks": used_count,
            "total_blocks": total_blocks,
        }

    def is_block_free(self, block_num: int) -> bool:
        """Check if a specific block is free."""
        if block_num < 0 or block_num >= self.image.total_blocks:
            return False

        bitmap_start_block = self._find_bitmap_block()
        blocks_per_bitmap = 512 * 8

        # Find which bitmap block contains this block's bit
        bitmap_block_index = block_num // blocks_per_bitmap
        block_within_bitmap = block_num % blocks_per_bitmap

        byte_offset = block_within_bitmap // 8
        bit_pos = block_within_bitmap % 8

        try:
            bitmap_block = self.image.read_block(
                bitmap_start_block + bitmap_block_index
            )
            byte_val = bitmap_block[byte_offset]
            return bool(byte_val & (1 << bit_pos))
        except Exception:
            return False


class ProDOSVolumeDirectory:
    """ProDOS volume directory parser."""

    def __init__(self, image: ProDOSImage):
        self.image = image
        self._entries: list[ProDOSFileEntry] | None = None
        self._volume_name: str | None = None
        self._creation_date: datetime | None = None
        self._total_blocks: int | None = None
        self._entries_per_block: int = 13  # ProDOS standard
        self._entry_size: int = 39  # ProDOS directory entry size
        self._bitmap: ProDOSVolumeBitmap | None = None

    def _parse_volume_header(self, block_data: bytes) -> None:
        """Parse the volume directory header block."""
        if len(block_data) < 512:
            raise CorruptedImageError(
                "Volume directory block too short", str(self.image.file_path)
            )

        # First entry (offset 4) is the volume directory header
        header_start = 4

        # Byte 0: Storage type (0xF) + name length
        storage_type_and_length = block_data[header_start]
        storage_type = (storage_type_and_length >> 4) & 0x0F
        name_length = storage_type_and_length & 0x0F

        if storage_type != 0x0F:
            raise InvalidHeaderError(
                f"Invalid volume directory storage type: 0x{storage_type:X}",
                str(self.image.file_path),
                2,
            )

        if name_length > 15:
            raise InvalidHeaderError(
                f"Invalid volume name length: {name_length}",
                str(self.image.file_path),
                2,
            )

        # Extract volume name
        name_start = header_start + 1
        name_bytes = block_data[name_start : name_start + name_length]
        try:
            self._volume_name = name_bytes.decode("ascii")
        except UnicodeDecodeError as e:
            raise CorruptedImageError(
                f"Invalid volume name encoding: {e}", str(self.image.file_path)
            ) from e

        # Skip reserved bytes and get creation date (offset 28-31)
        date_start = header_start + 28 - 4  # Adjust for header start offset
        if date_start + 4 <= len(block_data):
            date_bytes = block_data[date_start : date_start + 4]
            self._creation_date = prodos_date_to_datetime(date_bytes)

        # Get total blocks from offset 35-36
        blocks_start = header_start + 35 - 4
        if blocks_start + 2 <= len(block_data):
            self._total_blocks = struct.unpack(
                "<H", block_data[blocks_start : blocks_start + 2]
            )[0]

    def _parse_directory_entry(
        self, entry_data: bytes, entry_offset: int
    ) -> ProDOSFileEntry | None:
        """Parse a single ProDOS directory entry."""
        if len(entry_data) < self._entry_size:
            return None

        # Byte 0: Storage type + name length
        storage_type_and_length = entry_data[0]
        storage_type = (storage_type_and_length >> 4) & 0x0F
        name_length = storage_type_and_length & 0x0F

        # Skip unused entries
        if storage_type == 0 or name_length == 0:
            return None

        # Extract filename
        try:
            filename = entry_data[1 : 1 + name_length].decode("ascii")
        except UnicodeDecodeError:
            # Skip entries with invalid names
            return None

        # File type (byte 16)
        file_type = entry_data[16] if len(entry_data) > 16 else 0

        # Key block pointer (bytes 17-18)
        key_block = (
            struct.unpack("<H", entry_data[17:19])[0] if len(entry_data) > 18 else 0
        )

        # Blocks used (bytes 19-20)
        blocks_used = (
            struct.unpack("<H", entry_data[19:21])[0] if len(entry_data) > 20 else 0
        )

        # EOF (file size, bytes 21-23)
        eof_bytes = entry_data[21:24] if len(entry_data) > 23 else b"\x00\x00\x00"
        file_size = (
            struct.unpack("<I", eof_bytes + b"\x00")[0] & 0xFFFFFF
        )  # 24-bit value

        # Creation date (bytes 24-27)
        creation_date = None
        if len(entry_data) > 27:
            date_bytes = entry_data[24:28]
            creation_date = prodos_date_to_datetime(date_bytes)

        # Access permissions (byte 30)
        access = entry_data[30] if len(entry_data) > 30 else 0

        # Aux type (bytes 31-32)
        aux_type = (
            struct.unpack("<H", entry_data[31:33])[0] if len(entry_data) > 32 else 0
        )

        # Last modification date (bytes 33-36)
        modification_date = None
        if len(entry_data) > 36:
            date_bytes = entry_data[33:37]
            modification_date = prodos_date_to_datetime(date_bytes)

        entry = ProDOSFileEntry(
            filename=filename,
            file_type=file_type,
            size=file_size,
            locked=(access & 0x01) == 0,  # Locked if destroy bit is clear
            storage_type=storage_type,
            key_block=key_block,
            blocks_used=blocks_used,
            aux_type=aux_type,
            created=creation_date,
            modified=modification_date,
            access=access,
        )

        # Add reference to image for file reading
        entry._image = self.image
        return entry

    def parse(self) -> list[ProDOSFileEntry]:
        """Parse the volume directory and return list of file entries."""
        if self._entries is not None:
            return self._entries

        entries = []

        try:
            # Read volume directory header (block 2)
            volume_block = self.image.read_block(2)
            self._parse_volume_header(volume_block)

            # Parse entries in volume directory block
            # Skip first 4 bytes (previous/next pointers), then volume header (39 bytes)
            entry_start = 4 + 39

            for i in range(
                self._entries_per_block - 1
            ):  # -1 because first entry is volume header
                offset = entry_start + (i * self._entry_size)
                if offset + self._entry_size > len(volume_block):
                    break

                entry_data = volume_block[offset : offset + self._entry_size]
                entry = self._parse_directory_entry(entry_data, offset)
                if entry:
                    entries.append(entry)

            # TODO: Follow directory continuation blocks if needed
            # This would involve reading blocks linked by the next pointer at offset 2-3

        except Exception as e:
            raise CorruptedImageError(
                f"Error parsing volume directory: {e}", str(self.image.file_path)
            ) from e

        self._entries = entries
        return entries

    @property
    def volume_name(self) -> str:
        """Get the volume name."""
        if self._volume_name is None:
            self.parse()  # This will populate _volume_name
        return self._volume_name or "UNKNOWN"

    @property
    def creation_date(self) -> datetime | None:
        """Get the volume creation date."""
        if self._creation_date is None:
            self.parse()
        return self._creation_date

    @property
    def total_blocks(self) -> int | None:
        """Get the total blocks from volume header."""
        if self._total_blocks is None:
            self.parse()
        return self._total_blocks

    @property
    def bitmap(self) -> ProDOSVolumeBitmap:
        """Get the volume bitmap parser."""
        if self._bitmap is None:
            self._bitmap = ProDOSVolumeBitmap(self.image)
        return self._bitmap

    def get_free_space_info(self) -> dict:
        """Get free space information from the volume bitmap."""
        return self.bitmap.parse_bitmap()

    def parse_subdirectory(
        self, directory_entry: ProDOSFileEntry
    ) -> "ProDOSSubdirectory":
        """Parse a subdirectory entry."""
        if not directory_entry.is_directory:
            raise ValueError(f"{directory_entry.filename} is not a directory")

        return ProDOSSubdirectory(
            self.image, directory_entry.key_block, directory_entry.filename
        )

    def get_all_files(
        self, recursive: bool = True, _path_prefix: str = ""
    ) -> list[ProDOSFileEntry]:
        """Get all files from this directory, optionally recursing into subdirectories.

        Args:
            recursive: If True, recursively traverse subdirectories
            _path_prefix: Internal parameter for tracking directory path

        Returns:
            List of all ProDOSFileEntry objects, with full paths for nested files
        """
        all_files = []
        entries = self.parse()

        for entry in entries:
            # Set the full path for this entry
            if _path_prefix:
                entry._full_path = f"{_path_prefix}/{entry.filename}"
            else:
                entry._full_path = entry.filename

            if entry.is_directory and recursive:
                # Recursively get files from subdirectory
                try:
                    subdirectory = self.parse_subdirectory(entry)
                    subdir_files = subdirectory.get_all_files(
                        recursive=True, _path_prefix=entry._full_path
                    )
                    all_files.extend(subdir_files)
                except Exception:
                    # If subdirectory can't be read, still include the directory entry
                    all_files.append(entry)
            else:
                # Regular file or directory (if not recursing)
                all_files.append(entry)

        return all_files


class ProDOSSubdirectory:
    """ProDOS subdirectory parser."""

    def __init__(self, image: ProDOSImage, header_block: int, directory_name: str):
        self.image = image
        self.header_block = header_block
        self.directory_name = directory_name
        self._entries: list[ProDOSFileEntry] | None = None
        self._parent_pointer: int | None = None
        self._entry_length: int = 39
        self._entries_per_block: int = 13

    def _parse_subdirectory_header(self, block_data: bytes) -> None:
        """Parse subdirectory header block."""
        if len(block_data) < 512:
            raise CorruptedImageError(
                "Subdirectory header block too short", str(self.image.file_path)
            )

        # Previous block pointer (bytes 0-1)
        # Next block pointer (bytes 2-3)

        # First entry (offset 4) is the subdirectory header
        header_start = 4

        # Byte 0: Storage type (0xE) + name length
        storage_type_and_length = block_data[header_start]
        storage_type = (storage_type_and_length >> 4) & 0x0F
        name_length = storage_type_and_length & 0x0F

        if storage_type != 0x0E:
            raise InvalidHeaderError(
                f"Invalid subdirectory header storage type: 0x{storage_type:X}",
                str(self.image.file_path),
                self.header_block,
            )

        # Extract directory name (should match what we expect)
        name_start = header_start + 1
        name_bytes = block_data[name_start : name_start + name_length]
        try:
            actual_name = name_bytes.decode("ascii")
            if actual_name != self.directory_name:
                # This is informational, not an error
                pass
        except UnicodeDecodeError:
            pass

        # Parent directory pointer (bytes 35-36 in header entry)
        parent_start = header_start + 35
        if parent_start + 2 <= len(block_data):
            self._parent_pointer = struct.unpack(
                "<H", block_data[parent_start : parent_start + 2]
            )[0]

    def _parse_directory_entry(self, entry_data: bytes) -> ProDOSFileEntry | None:
        """Parse a directory entry (same format as volume directory)."""
        if len(entry_data) < self._entry_length:
            return None

        # Use the same parsing logic as volume directory
        volume_dir = ProDOSVolumeDirectory(self.image)
        entry = volume_dir._parse_directory_entry(entry_data, 0)

        # Add image reference for file reading
        if entry:
            entry._image = self.image

        return entry

    def parse(self) -> list[ProDOSFileEntry]:
        """Parse the subdirectory and return list of file entries."""
        if self._entries is not None:
            return self._entries

        entries = []
        current_block = self.header_block

        try:
            while current_block != 0:
                # Read directory block
                block_data = self.image.read_block(current_block)

                if current_block == self.header_block:
                    # Parse header for first block
                    self._parse_subdirectory_header(block_data)
                    # Skip header entry, start from second entry
                    entry_start = 4 + self._entry_length
                    entries_to_parse = self._entries_per_block - 1
                else:
                    # Regular directory continuation block
                    entry_start = 4  # Skip prev/next pointers
                    entries_to_parse = self._entries_per_block

                # Parse entries in this block
                for i in range(entries_to_parse):
                    offset = entry_start + (i * self._entry_length)
                    if offset + self._entry_length > len(block_data):
                        break

                    entry_data = block_data[offset : offset + self._entry_length]
                    entry = self._parse_directory_entry(entry_data)
                    if entry:
                        entries.append(entry)

                # Get next block pointer
                if len(block_data) >= 4:
                    current_block = struct.unpack("<H", block_data[2:4])[0]
                else:
                    break

        except Exception as e:
            raise CorruptedImageError(
                f"Error parsing subdirectory {self.directory_name}: {e}",
                str(self.image.file_path),
            ) from e

        self._entries = entries
        return entries

    @property
    def parent_pointer(self) -> int | None:
        """Get parent directory block pointer."""
        if self._parent_pointer is None:
            self.parse()  # This will populate _parent_pointer
        return self._parent_pointer

    def get_full_path(self, parent_path: str = "") -> str:
        """Get full path of this directory."""
        if parent_path:
            return f"{parent_path}/{self.directory_name}"
        return self.directory_name

    def get_all_files(
        self, recursive: bool = True, _path_prefix: str = ""
    ) -> list[ProDOSFileEntry]:
        """Get all files from this subdirectory, optionally recursing into nested subdirectories.

        Args:
            recursive: If True, recursively traverse subdirectories
            _path_prefix: Internal parameter for tracking directory path

        Returns:
            List of all ProDOSFileEntry objects, with full paths for nested files
        """
        all_files = []
        entries = self.parse()

        for entry in entries:
            # Set the full path for this entry
            if _path_prefix:
                entry._full_path = f"{_path_prefix}/{entry.filename}"
            else:
                entry._full_path = entry.filename

            if entry.is_directory and recursive:
                # Recursively get files from nested subdirectory
                try:
                    # Create a new ProDOSSubdirectory instance for the nested directory
                    nested_subdir = ProDOSSubdirectory(
                        self.image, entry.key_block, entry.filename
                    )
                    subdir_files = nested_subdir.get_all_files(
                        recursive=True, _path_prefix=entry._full_path
                    )
                    all_files.extend(subdir_files)
                except Exception:
                    # If subdirectory can't be read, still include the directory entry
                    all_files.append(entry)
            else:
                # Regular file or directory (if not recursing)
                all_files.append(entry)

        return all_files


def parse_prodos_directory(image: ProDOSImage) -> ProDOSVolumeDirectory:
    """Parse a ProDOS volume directory from an image."""
    return ProDOSVolumeDirectory(image)
