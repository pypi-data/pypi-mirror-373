"""ProDOS file reading implementation."""

import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fileentry import ProDOSFileEntry
    from .image import ProDOSImage

from .exceptions import InvalidFileError


def read_prodos_file_data(entry: "ProDOSFileEntry", image: "ProDOSImage") -> bytes:
    """Read ProDOS file data based on storage type."""
    if entry.is_seedling:
        return _read_seedling_file(entry, image)
    elif entry.is_sapling:
        return _read_sapling_file(entry, image)
    elif entry.is_tree:
        return _read_tree_file(entry, image)
    else:
        raise InvalidFileError(
            f"Cannot read file with storage type {entry.storage_type}", entry.filename
        )


def _read_seedling_file(entry: "ProDOSFileEntry", image: "ProDOSImage") -> bytes:
    """Read a seedling file (≤ 512 bytes, data stored directly in key block)."""
    try:
        block_data = image.read_block(entry.key_block)
        # Return only the actual file size, not the full block
        return block_data[: entry.size]
    except Exception as e:
        raise InvalidFileError(
            f"Error reading seedling file: {e}", entry.filename
        ) from e


def _read_sapling_file(entry: "ProDOSFileEntry", image: "ProDOSImage") -> bytes:
    """Read a sapling file (513-131,072 bytes, using index block).
    
    ProDOS stores block pointers in a split format:
    - First half of index block (bytes 0-255): Low bytes of block pointers
    - Second half of index block (bytes 256-511): High bytes of block pointers
    """
    try:
        # Read the index block
        index_block = image.read_block(entry.key_block)

        file_data = bytearray()
        bytes_remaining = entry.size

        # ProDOS index blocks can hold up to 256 block pointers
        max_pointers = min(256, (bytes_remaining + 511) // 512)

        for i in range(max_pointers):
            if bytes_remaining <= 0:
                break

            # Extract block number using ProDOS split-block format
            low_byte = index_block[i] if i < len(index_block) else 0
            high_byte = index_block[i + 256] if i + 256 < len(index_block) else 0
            block_num = (high_byte << 8) | low_byte

            # Block 0 means sparse/empty block
            if block_num == 0:
                # Add null bytes for sparse block
                sparse_size = min(512, bytes_remaining)
                file_data.extend(b"\x00" * sparse_size)
                bytes_remaining -= sparse_size
            else:
                # Read actual data block
                data_block = image.read_block(block_num)
                block_size = min(512, bytes_remaining)
                file_data.extend(data_block[:block_size])
                bytes_remaining -= block_size

        return bytes(file_data)

    except Exception as e:
        raise InvalidFileError(
            f"Error reading sapling file: {e}", entry.filename
        ) from e


def _read_tree_file(entry: "ProDOSFileEntry", image: "ProDOSImage") -> bytes:
    """Read a tree file (> 131,072 bytes, using master index block).
    
    ProDOS tree files use a master index block that points to sapling index blocks.
    All index blocks use the split-block format for storing block pointers.
    """
    try:
        # Read the master index block
        master_index = image.read_block(entry.key_block)

        file_data = bytearray()
        bytes_remaining = entry.size

        # Master index can hold up to 256 pointers to sapling index blocks
        max_sapling_indices = min(256, (bytes_remaining + 131071) // 131072)

        for i in range(max_sapling_indices):
            if bytes_remaining <= 0:
                break

            # Extract sapling index block number using split-block format
            low_byte = master_index[i] if i < 256 else 0
            high_byte = master_index[i + 256] if i + 256 < len(master_index) else 0
            index_block_num = (high_byte << 8) | low_byte

            if index_block_num == 0:
                # Sparse section - add null bytes
                sparse_size = min(131072, bytes_remaining)  # Max sapling size
                file_data.extend(b"\x00" * sparse_size)
                bytes_remaining -= sparse_size
            else:
                # Read the sapling index block
                index_block = image.read_block(index_block_num)

                # Process each data block referenced by this sapling index
                sapling_bytes_remaining = min(131072, bytes_remaining)
                max_data_blocks = min(256, (sapling_bytes_remaining + 511) // 512)
                
                for j in range(max_data_blocks):
                    if bytes_remaining <= 0:
                        break

                    # Extract data block number using split-block format
                    low_byte = index_block[j] if j < len(index_block) else 0
                    high_byte = index_block[j + 256] if j + 256 < len(index_block) else 0
                    block_num = (high_byte << 8) | low_byte

                    if block_num == 0:
                        # Sparse block
                        sparse_size = min(512, bytes_remaining)
                        file_data.extend(b"\x00" * sparse_size)
                        bytes_remaining -= sparse_size
                    else:
                        # Read actual data block
                        data_block = image.read_block(block_num)
                        block_size = min(512, bytes_remaining)
                        file_data.extend(data_block[:block_size])
                        bytes_remaining -= block_size

        return bytes(file_data)

    except Exception as e:
        raise InvalidFileError(f"Error reading tree file: {e}", entry.filename) from e
