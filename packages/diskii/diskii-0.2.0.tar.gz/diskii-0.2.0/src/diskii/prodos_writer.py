"""ProDOS file writing and allocation functionality."""

import struct
from datetime import UTC, datetime

from .exceptions import (
    FileNotFoundError,
    FilesystemError,
    InvalidFileError,
)
from .prodos import ProDOSVolumeBitmap, ProDOSVolumeDirectory


def datetime_to_prodos_date(dt: datetime | None) -> bytes:
    """Convert Python datetime to ProDOS date format (4 bytes).

    ProDOS date format:
    - 2 bytes for date: YYYYYYY MMMM DDDDD (year, month, day)
    - 2 bytes for time: unused HHHH HMMM MMM (hour, minute)
    """
    if dt is None:
        dt = datetime.now()

    # Handle year encoding (reverse of prodos_date_to_datetime)
    if dt.year >= 2000:
        if dt.year <= 2027:
            year_raw = dt.year - 2000 + 100  # 2000-2027 -> 100-127
        else:
            year_raw = dt.year - 2000  # 2028+ -> 28+, wrapping
    else:
        year_raw = dt.year - 1900  # 1940-1999 -> 40-99

    # Pack date word: year(7) + month(4) + day(5)
    date_word = (year_raw << 9) | (dt.month << 5) | dt.day

    # Pack time word: unused(1) + hour(5) + minute(6)
    time_word = (dt.hour << 8) | dt.minute

    return struct.pack("<HH", date_word, time_word)


class ProDOSBlockAllocator:
    """Manages ProDOS block allocation using the volume bitmap."""

    def __init__(self, image):
        self.image = image
        self.bitmap = ProDOSVolumeBitmap(image)

    def find_free_blocks(self, count: int, contiguous: bool = False) -> list[int]:
        """Find free blocks on the disk.

        Args:
            count: Number of blocks needed
            contiguous: If True, find contiguous blocks

        Returns:
            List of available block numbers

        Raises:
            FilesystemError: If not enough free blocks available
        """
        # Get actually used blocks from existing files to avoid corrupted bitmap issues
        actually_used_blocks = self._get_actually_used_blocks()
        
        free_blocks = []
        total_blocks = self.image.total_blocks

        if contiguous:
            # Find contiguous sequence
            consecutive_count = 0
            start_block = None

            for block_num in range(total_blocks):
                # Block is truly free if both bitmap says free AND it's not actually used by files
                if (self.bitmap.is_block_free(block_num) and 
                    block_num not in actually_used_blocks):
                    if consecutive_count == 0:
                        start_block = block_num
                    consecutive_count += 1

                    if consecutive_count >= count:
                        return list(range(start_block, start_block + count))
                else:
                    consecutive_count = 0
                    start_block = None

            raise FilesystemError(
                f"Cannot find {count} contiguous free blocks", str(self.image.file_path)
            )
        else:
            # Find any free blocks
            for block_num in range(total_blocks):
                # Block is truly free if both bitmap says free AND it's not actually used by files
                if (self.bitmap.is_block_free(block_num) and 
                    block_num not in actually_used_blocks):
                    free_blocks.append(block_num)
                    if len(free_blocks) >= count:
                        return free_blocks[:count]

        raise FilesystemError(
            f"Not enough free blocks: need {count}, found {len(free_blocks)}",
            str(self.image.file_path),
        )
        
    def _get_actually_used_blocks(self) -> set[int]:
        """Get blocks that are actually in use by existing files, ignoring corrupted bitmap.
        
        This protects against corrupted volume bitmaps that incorrectly mark allocated
        blocks as free, which would cause file corruption.
        """
        used_blocks = set()
        
        # Always reserve system blocks
        used_blocks.update(range(6))  # Blocks 0-5: boot, volume directory, bitmap
        
        try:
            # Get all existing files and their block usage
            files = self.image.get_file_list()
            for file_entry in files:
                # Add the key block (index block for sapling/tree, data block for seedling)
                used_blocks.add(file_entry.key_block)
                
                if file_entry.is_sapling or file_entry.is_tree:
                    # Read index block to get data blocks
                    try:
                        index_block = self.image.read_block(file_entry.key_block)
                        
                        # Extract data block pointers (ProDOS split-block format)
                        for i in range(256):
                            low_byte = index_block[i]
                            high_byte = index_block[i + 256] if i + 256 < len(index_block) else 0
                            block_num = (high_byte << 8) | low_byte
                            if block_num != 0:
                                used_blocks.add(block_num)
                        
                        # For tree files, we need to read each index block to get data blocks
                        if file_entry.is_tree:
                            for i in range(256):
                                low_byte = index_block[i]
                                high_byte = index_block[i + 256] if i + 256 < len(index_block) else 0
                                index_block_num = (high_byte << 8) | low_byte
                                if index_block_num != 0:
                                    try:
                                        sub_index_block = self.image.read_block(index_block_num)
                                        for j in range(256):
                                            low_byte = sub_index_block[j]
                                            high_byte = sub_index_block[j + 256] if j + 256 < len(sub_index_block) else 0
                                            data_block_num = (high_byte << 8) | low_byte
                                            if data_block_num != 0:
                                                used_blocks.add(data_block_num)
                                    except Exception:
                                        pass  # Skip corrupted index blocks
                    except Exception:
                        pass  # Skip files we can't read
        except Exception:
            pass  # If we can't read file list, just use system blocks
            
        return used_blocks

    def allocate_blocks(self, block_numbers: list[int]) -> None:
        """Mark blocks as allocated in the volume bitmap."""
        bitmap_start_block = self.bitmap._find_bitmap_block()
        blocks_per_bitmap = 512 * 8

        # Group blocks by which bitmap block they belong to
        bitmap_updates = {}

        for block_num in block_numbers:
            bitmap_block_index = block_num // blocks_per_bitmap
            if bitmap_block_index not in bitmap_updates:
                bitmap_block_num = bitmap_start_block + bitmap_block_index
                bitmap_updates[bitmap_block_index] = {
                    "block_num": bitmap_block_num,
                    "data": bytearray(self.image.read_block(bitmap_block_num)),
                    "changes": [],
                }

            block_within_bitmap = block_num % blocks_per_bitmap
            byte_offset = block_within_bitmap // 8
            bit_pos = block_within_bitmap % 8

            bitmap_updates[bitmap_block_index]["changes"].append((byte_offset, bit_pos))

        # Apply changes and write bitmap blocks
        for bitmap_info in bitmap_updates.values():
            data = bitmap_info["data"]
            for byte_offset, bit_pos in bitmap_info["changes"]:
                # Clear the bit (0 = allocated, 1 = free)
                data[byte_offset] &= ~(1 << bit_pos)

            self.image.write_block(bitmap_info["block_num"], bytes(data))

    def deallocate_blocks(self, block_numbers: list[int]) -> None:
        """Mark blocks as free in the volume bitmap."""
        bitmap_start_block = self.bitmap._find_bitmap_block()
        blocks_per_bitmap = 512 * 8

        bitmap_updates = {}

        for block_num in block_numbers:
            bitmap_block_index = block_num // blocks_per_bitmap
            if bitmap_block_index not in bitmap_updates:
                bitmap_block_num = bitmap_start_block + bitmap_block_index
                bitmap_updates[bitmap_block_index] = {
                    "block_num": bitmap_block_num,
                    "data": bytearray(self.image.read_block(bitmap_block_num)),
                    "changes": [],
                }

            block_within_bitmap = block_num % blocks_per_bitmap
            byte_offset = block_within_bitmap // 8
            bit_pos = block_within_bitmap % 8

            bitmap_updates[bitmap_block_index]["changes"].append((byte_offset, bit_pos))

        # Apply changes and write bitmap blocks
        for bitmap_info in bitmap_updates.values():
            data = bitmap_info["data"]
            for byte_offset, bit_pos in bitmap_info["changes"]:
                # Set the bit (1 = free, 0 = allocated)
                data[byte_offset] |= 1 << bit_pos

            self.image.write_block(bitmap_info["block_num"], bytes(data))


def create_prodos_file(
    image,
    filename: str,
    file_type: int,
    data: bytes,
    aux_type: int = 0,
    created: datetime | None = None,
) -> None:
    """Create a new file on a ProDOS disk image.

    Args:
        image: ProDOSImage instance
        filename: Name of the file to create
        file_type: ProDOS file type (e.g., 0x04 for text, 0x06 for binary)
        data: File content bytes
        aux_type: Auxiliary type information
        created: Creation date (defaults to current time)

    Raises:
        InvalidFileError: If filename already exists or is invalid
        FilesystemError: If not enough free space
    """
    if created is None:
        created = datetime.now(UTC)

    # Validate filename
    if not filename or len(filename) > 15:
        raise InvalidFileError(f"Invalid filename: {filename}")

    # Check if file already exists
    existing_files = image.get_file_list()
    for existing_file in existing_files:
        if existing_file.filename.upper() == filename.upper():
            raise InvalidFileError(f"File already exists: {filename}")

    # Determine storage type based on file size
    file_size = len(data)

    if file_size <= 512:
        # Seedling file - single data block
        storage_type = 1
        blocks_needed = 1
    elif file_size <= 131072:  # 256 blocks * 512 bytes
        # Sapling file - index block + data blocks
        storage_type = 2
        data_blocks_needed = (file_size + 511) // 512
        blocks_needed = data_blocks_needed + 1  # +1 for index block
    else:
        # Tree file - master index + index blocks + data blocks
        storage_type = 3
        data_blocks_needed = (file_size + 511) // 512
        index_blocks_needed = (data_blocks_needed + 255) // 256
        blocks_needed = (
            data_blocks_needed + index_blocks_needed + 1
        )  # +1 for master index

    # Allocate blocks (but don't mark them as allocated yet)
    allocator = ProDOSBlockAllocator(image)
    allocated_blocks = allocator.find_free_blocks(blocks_needed)

    # Pre-validate directory space is available before making any changes
    try:
        _validate_directory_space(image, filename)
    except FilesystemError as e:
        raise FilesystemError(f"Cannot create file {filename}: {e}") from e

    # Save original directory state for rollback
    original_directory_block = image.read_block(2)

    try:
        # Write file data based on storage type
        if storage_type == 1:
            # Seedling: write data directly to block
            key_block = allocated_blocks[0]
            padded_data = data.ljust(512, b"\x00")
            image.write_block(key_block, padded_data)

        elif storage_type == 2:
            # Sapling: create index block pointing to data blocks
            key_block = allocated_blocks[0]
            data_blocks = allocated_blocks[1:]

            # Create index block using ProDOS split-block format
            # Low bytes in first half (0-255), high bytes in second half (256-511)
            index_data = bytearray(512)
            for i, data_block in enumerate(data_blocks):
                if i < 256:  # Max 256 pointers per index block
                    low_byte = data_block & 0xFF
                    high_byte = (data_block >> 8) & 0xFF
                    index_data[i] = low_byte        # Low byte in first half
                    index_data[i + 256] = high_byte # High byte in second half

            image.write_block(key_block, bytes(index_data))

            # Write data blocks
            for i, data_block in enumerate(data_blocks):
                start_offset = i * 512
                end_offset = min(start_offset + 512, len(data))
                block_data = data[start_offset:end_offset].ljust(512, b"\x00")
                image.write_block(data_block, block_data)

        else:  # storage_type == 3
            # Tree: create master index pointing to index blocks pointing to data blocks
            key_block = allocated_blocks[0]
            remaining_blocks = allocated_blocks[1:]

            data_blocks_needed = (file_size + 511) // 512
            index_blocks_needed = (data_blocks_needed + 255) // 256

            index_blocks = remaining_blocks[:index_blocks_needed]
            data_blocks = remaining_blocks[index_blocks_needed:]

            # Create master index block using ProDOS split-block format
            master_index = bytearray(512)
            for i, index_block in enumerate(index_blocks):
                if i < 256:
                    low_byte = index_block & 0xFF
                    high_byte = (index_block >> 8) & 0xFF
                    master_index[i] = low_byte        # Low byte in first half
                    master_index[i + 256] = high_byte # High byte in second half

            image.write_block(key_block, bytes(master_index))

            # Create index blocks and write data
            data_block_index = 0
            for i, index_block in enumerate(index_blocks):
                index_data = bytearray(512)

                for j in range(256):  # Each index block can point to 256 data blocks
                    if data_block_index < len(data_blocks):
                        # Use ProDOS split-block format
                        data_block_num = data_blocks[data_block_index]
                        low_byte = data_block_num & 0xFF
                        high_byte = (data_block_num >> 8) & 0xFF
                        index_data[j] = low_byte        # Low byte in first half
                        index_data[j + 256] = high_byte # High byte in second half

                        # Write data block
                        start_offset = data_block_index * 512
                        end_offset = min(start_offset + 512, len(data))
                        block_data = data[start_offset:end_offset].ljust(512, b"\x00")
                        image.write_block(data_blocks[data_block_index], block_data)

                        data_block_index += 1
                    else:
                        break

                image.write_block(index_block, bytes(index_data))

        # Create directory entry first (before marking blocks allocated)
        _add_directory_entry(
            image,
            filename,
            file_type,
            file_size,
            storage_type,
            key_block,
            len(allocated_blocks),
            aux_type,
            created,
        )
        
        # Only mark blocks as allocated after directory entry is successfully created
        allocator.allocate_blocks(allocated_blocks)

    except Exception as e:
        # Comprehensive rollback on any failure
        try:
            # Restore original directory state
            image.write_block(2, original_directory_block)
        except Exception as restore_error:
            # If directory restore fails, this is a critical filesystem corruption
            raise FilesystemError(f"CRITICAL: Failed to restore directory after error in {filename}: {restore_error}. Original error: {e}") from e
        
        # Note: We don't need to deallocate blocks since we never marked them as allocated
        # The bitmap remains unchanged if we failed before allocate_blocks()
        
        raise FilesystemError(f"Failed to create file {filename}: {e}") from e


def _validate_directory_space(image, filename: str) -> None:
    """Validate that directory space is available and won't corrupt volume directory."""
    volume_block = image.read_block(2)
    volume_data = bytearray(volume_block)
    
    # Validate volume directory structure first
    if len(volume_data) != 512:
        raise FilesystemError(f"Invalid volume directory block size: {len(volume_data)}")
    
    volume_storage_type = (volume_data[4] >> 4) & 0x0F
    if volume_storage_type != 0x0F:
        raise FilesystemError(f"Invalid volume directory signature: expected 0xF, got 0x{volume_storage_type:X}")
    
    # Find if there's an empty directory entry slot available
    entry_size = 39
    entries_per_block = 13
    found_empty_slot = False
    
    for i in range(1, entries_per_block):
        offset = 4 + 39 + ((i - 1) * entry_size)
        
        if offset + entry_size > len(volume_data):
            break
            
        storage_and_length = volume_data[offset]
        existing_storage_type = (storage_and_length >> 4) & 0x0F
        
        if existing_storage_type == 0:
            found_empty_slot = True
            break
    
    if not found_empty_slot:
        raise FilesystemError("Directory is full - no empty slots available")


def _add_directory_entry(
    image,
    filename: str,
    file_type: int,
    file_size: int,
    storage_type: int,
    key_block: int,
    blocks_used: int,
    aux_type: int,
    created: datetime,
) -> None:
    """Add a directory entry for a new file."""

    # Read volume directory header block
    volume_block = image.read_block(2)
    volume_data = bytearray(volume_block)

    # Validate volume directory block structure
    if len(volume_data) != 512:
        raise FilesystemError(f"Invalid volume directory block size: {len(volume_data)}")
    
    # Check volume directory header signature (storage type = 0xF at offset 4)
    volume_storage_type = (volume_data[4] >> 4) & 0x0F
    if volume_storage_type != 0x0F:
        raise FilesystemError(f"Invalid volume directory signature: expected 0xF, got 0x{volume_storage_type:X}")
    
    # Verify this is actually a volume directory by checking the volume name length
    volume_name_length = volume_data[4] & 0x0F
    if volume_name_length == 0 or volume_name_length > 15:
        raise FilesystemError(f"Invalid volume name length: {volume_name_length}")

    # Find an empty directory entry (storage type = 0)
    entry_size = 39
    entries_per_block = 13

    # Skip the volume header entry (first 39 bytes after prev/next pointers)
    # ProDOS directory block layout: [prev/next: 4 bytes] [volume header: 39 bytes] [file entries: 12 × 39 bytes]
    for i in range(1, entries_per_block):  # Start from 1 to skip volume header
        offset = 4 + 39 + ((i - 1) * entry_size)  # 4 bytes prev/next + 39 bytes volume header + file entries

        if offset + entry_size > len(volume_data):
            break

        # Check if entry is empty (storage type = 0)
        storage_and_length = volume_data[offset]
        existing_storage_type = (storage_and_length >> 4) & 0x0F

        if existing_storage_type == 0:
            # Found empty entry, create new file entry
            name_bytes = filename.upper().encode("ascii")
            if len(name_bytes) > 15:
                name_bytes = name_bytes[:15]

            # Build directory entry
            entry_data = bytearray(entry_size)

            # Byte 0: Storage type + name length
            entry_data[0] = (storage_type << 4) | len(name_bytes)

            # Bytes 1-15: Filename (padded with spaces)
            entry_data[1 : 1 + len(name_bytes)] = name_bytes

            # Byte 16: File type
            entry_data[16] = file_type

            # Bytes 17-18: Key block (little endian)
            struct.pack_into("<H", entry_data, 17, key_block)

            # Bytes 19-20: Blocks used (little endian)
            struct.pack_into("<H", entry_data, 19, blocks_used)

            # Bytes 21-23: End of file (file size, 3 bytes little endian)
            entry_data[21] = file_size & 0xFF
            entry_data[22] = (file_size >> 8) & 0xFF
            entry_data[23] = (file_size >> 16) & 0xFF

            # Bytes 24-27: Creation date/time
            date_bytes = datetime_to_prodos_date(created)
            entry_data[24:28] = date_bytes

            # Byte 30: Access permissions (default: read/write/rename)
            entry_data[30] = 0xE3

            # Bytes 31-32: Auxiliary type
            struct.pack_into("<H", entry_data, 31, aux_type)

            # Bytes 33-36: Last modified date/time (same as creation)
            entry_data[33:37] = date_bytes

            # Copy entry to volume directory
            volume_data[offset : offset + entry_size] = entry_data

            # Write updated directory block
            image.write_block(2, bytes(volume_data))
            return

    # TODO: Handle directory continuation blocks if main block is full
    raise FilesystemError("Directory is full", str(image.file_path))


def delete_prodos_file(image, filename: str) -> None:
    """Delete a file from a ProDOS disk image.

    Args:
        image: ProDOSImage instance
        filename: Name of the file to delete

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    # Find the file in directory
    directory = ProDOSVolumeDirectory(image)
    files = directory.parse()

    target_file = None
    for file_entry in files:
        if file_entry.filename.upper() == filename.upper():
            target_file = file_entry
            break

    if target_file is None:
        raise FileNotFoundError(filename, str(image.file_path))

    # Collect blocks to deallocate
    blocks_to_free = []

    # Add key block
    blocks_to_free.append(target_file.key_block)

    # Add data blocks based on storage type
    if target_file.storage_type == 1:
        # Seedling: only the key block (already added)
        pass
    elif target_file.storage_type == 2:
        # Sapling: read index block and add data blocks using ProDOS split-block format
        index_data = image.read_block(target_file.key_block)
        for i in range(256):
            # ProDOS split-block format: low byte at offset i, high byte at offset i+256
            low_byte = index_data[i]
            high_byte = index_data[i + 256] if i + 256 < len(index_data) else 0
            data_block = low_byte | (high_byte << 8)
            if data_block != 0:
                blocks_to_free.append(data_block)
    elif target_file.storage_type == 3:
        # Tree: read master index, then index blocks, then data blocks using ProDOS split-block format
        master_index = image.read_block(target_file.key_block)
        for i in range(256):
            # ProDOS split-block format for master index
            low_byte = master_index[i]
            high_byte = master_index[i + 256] if i + 256 < len(master_index) else 0
            index_block = low_byte | (high_byte << 8)
            
            if index_block != 0:
                blocks_to_free.append(index_block)

                # Read index block and add data blocks using ProDOS split-block format
                index_data = image.read_block(index_block)
                for j in range(256):
                    # ProDOS split-block format for data block pointers
                    low_byte = index_data[j]
                    high_byte = index_data[j + 256] if j + 256 < len(index_data) else 0
                    data_block = low_byte | (high_byte << 8)
                    if data_block != 0:
                        blocks_to_free.append(data_block)

    # Deallocate blocks
    allocator = ProDOSBlockAllocator(image)
    allocator.deallocate_blocks(blocks_to_free)

    # Remove directory entry
    _remove_directory_entry(image, filename)


def _remove_directory_entry(image, filename: str) -> None:
    """Remove a directory entry by setting its storage type to 0."""

    # Read volume directory header block
    volume_block = image.read_block(2)
    volume_data = bytearray(volume_block)

    entry_size = 39
    entries_per_block = 13

    # Find the directory entry  
    for i in range(1, entries_per_block):  # Skip volume header
        offset = 4 + 39 + ((i - 1) * entry_size)  # 4 bytes prev/next + 39 bytes volume header + file entries

        if offset + entry_size > len(volume_data):
            break

        # Check storage type and name
        storage_and_length = volume_data[offset]
        storage_type = (storage_and_length >> 4) & 0x0F
        name_length = storage_and_length & 0x0F

        if storage_type != 0 and name_length > 0:
            entry_filename = volume_data[offset + 1 : offset + 1 + name_length].decode(
                "ascii"
            )

            if entry_filename.upper() == filename.upper():
                # Found the entry, mark as deleted (storage type = 0)
                volume_data[offset] = 0  # Clear storage type and name length

                # Clear the entire entry
                volume_data[offset : offset + entry_size] = bytes(entry_size)

                # Write updated directory block
                image.write_block(2, bytes(volume_data))
                return

    # TODO: Handle directory continuation blocks
    raise FileNotFoundError(filename, str(image.file_path))
