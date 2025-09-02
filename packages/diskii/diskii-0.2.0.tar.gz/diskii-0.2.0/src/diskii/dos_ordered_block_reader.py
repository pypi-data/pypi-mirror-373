"""DOS-ordered block reader for ProDOS filesystems in .dsk files."""

from typing import BinaryIO, Optional
from pathlib import Path

from .exceptions import CorruptedImageError, IOError as DiskiiIOError


class DOSOrderedBlockReader:
    """Handles reading ProDOS blocks from DOS sector-ordered disk images.
    
    This class provides a translation layer that makes DOS sector-ordered
    disk images appear as standard ProDOS block-ordered images to the
    ProDOS filesystem code.
    
    Key features:
    - Transparent sector-to-block translation
    - Automatic volume directory location detection
    - Logical block address remapping for non-standard layouts
    """
    
    SECTOR_SIZE = 256
    SECTORS_PER_TRACK = 16
    BLOCK_SIZE = 512
    
    def __init__(self, file_handle: BinaryIO, file_path: Path):
        """Initialize the DOS-ordered block reader.
        
        Args:
            file_handle: Open file handle to the disk image
            file_path: Path to the disk image file
        """
        self.file_handle = file_handle
        self.file_path = file_path
        self._total_sectors = None
        self._volume_directory_block = None
        self._block_mapping = {}  # Maps logical blocks to physical blocks
        
    @property 
    def total_sectors(self) -> int:
        """Get total number of sectors in the image."""
        if self._total_sectors is None:
            self._total_sectors = self.file_path.stat().st_size // self.SECTOR_SIZE
        return self._total_sectors
    
    @property
    def total_blocks(self) -> int:
        """Get total number of blocks in the image."""
        return self.total_sectors // 2
        
    def read_block(self, logical_block_num: int) -> bytes:
        """Read a ProDOS block, handling logical-to-physical mapping.
        
        Args:
            logical_block_num: Logical block number as expected by ProDOS code
            
        Returns:
            512-byte block data, normalized for ProDOS parsing
        """
        # Map logical block to physical block
        physical_block_num = self._map_logical_to_physical_block(logical_block_num)
        
        # Read the physical block using DOS sector translation
        block_data = self._read_physical_block(physical_block_num)
        
        # Special handling for volume directory block
        if logical_block_num == 2 and physical_block_num == self._volume_directory_block:
            # If volume directory is in second sector, normalize it
            if hasattr(self, '_volume_dir_offset') and self._volume_dir_offset == 260:
                # Volume directory is in second sector - rearrange so header is at offset 4
                block_data = self._normalize_volume_directory_block(block_data)
        
        return block_data
    
    def _map_logical_to_physical_block(self, logical_block: int) -> int:
        """Map logical block numbers to physical block numbers.
        
        This handles cases where the ProDOS volume directory is not at
        the standard block 2 location.
        """
        # Handle volume directory block (logical block 2)
        if logical_block == 2:
            volume_dir_block = self._find_volume_directory_block()
            if volume_dir_block != 2:
                # Volume directory is at non-standard location
                # Map logical block 2 to the actual physical location
                return volume_dir_block
        
        # For other blocks, check if we need any remapping
        if logical_block in self._block_mapping:
            return self._block_mapping[logical_block]
            
        # Default: no mapping needed
        return logical_block
    
    def _find_volume_directory_block(self) -> int:
        """Find the physical block containing the ProDOS volume directory.
        
        Returns:
            Physical block number containing the volume directory
        """
        if self._volume_directory_block is not None:
            return self._volume_directory_block
            
        # Search first 8 blocks for ProDOS volume directory signature
        for physical_block in range(min(8, self.total_blocks)):
            try:
                block_data = self._read_physical_block(physical_block)
                
                if self._is_volume_directory_block(block_data):
                    self._volume_directory_block = physical_block
                    return physical_block
                    
            except Exception:
                continue
        
        # Default to block 2 if not found
        self._volume_directory_block = 2
        return 2
    
    def _is_volume_directory_block(self, block_data: bytes) -> bool:
        """Check if block contains a ProDOS volume directory header.
        
        Returns True if found, also caches the offset where it was found.
        """
        if len(block_data) < 512:
            return False
            
        # Check standard location (offset 4) and second sector (offset 260)  
        offsets_to_check = [4, 260] if len(block_data) >= 512 else [4]
        
        for offset in offsets_to_check:
            if offset + 15 < len(block_data):
                storage_type_byte = block_data[offset]
                
                # Check for volume directory storage type (0xF?)
                if (storage_type_byte & 0xF0) == 0xF0:
                    name_length = storage_type_byte & 0x0F
                    if 1 <= name_length <= 15:
                        if offset + 1 + name_length <= len(block_data):
                            # Check volume name is valid ASCII
                            volume_name = block_data[offset + 1 : offset + 1 + name_length]
                            if all(32 <= b <= 126 for b in volume_name):
                                # Cache the offset where we found the volume directory
                                if not hasattr(self, '_volume_dir_offset'):
                                    self._volume_dir_offset = offset
                                return True
        
        return False
    
    def _normalize_volume_directory_block(self, block_data: bytes) -> bytes:
        """Normalize volume directory block so header appears at offset 4.
        
        When the volume directory is found in the second sector (offset 260),
        this method rearranges the block so the ProDOS parsing code can find
        the header at the expected offset 4.
        """
        if len(block_data) != 512:
            return block_data
            
        # Extract the second sector (which contains the volume directory)
        second_sector = block_data[256:512]
        
        # Create a normalized block with the volume directory at the start
        # Put directory header at offset 4 where ProDOS expects it
        normalized_block = bytearray(512)
        
        # Copy the volume directory header and entries from second sector
        # The volume directory starts at offset 4 within the sector
        if len(second_sector) >= 256:
            # Copy volume directory header (starts at offset 4 in second sector)
            # Place it at offset 4 in the normalized block
            dir_header_start = 4  # Offset within second sector
            dir_data = second_sector[dir_header_start:]
            
            # Place at offset 4 in normalized block
            copy_length = min(len(dir_data), 512 - 4)
            normalized_block[4:4 + copy_length] = dir_data[:copy_length]
        
        return bytes(normalized_block)
    
    def _read_physical_block(self, block_num: int) -> bytes:
        """Read a physical block using DOS sector-to-block translation.
        
        Args:
            block_num: Physical block number in the image
            
        Returns:
            512-byte block data
        """
        if block_num < 0 or block_num >= self.total_blocks:
            raise ValueError(
                f"Block {block_num} out of range (0-{self.total_blocks - 1})"
            )
        
        # Convert block to DOS sectors
        linear_sector1 = block_num * 2
        linear_sector2 = block_num * 2 + 1
        
        # Read both sectors
        sector1_data = self._read_dos_sector(linear_sector1)
        
        if linear_sector2 < self.total_sectors:
            sector2_data = self._read_dos_sector(linear_sector2)
        else:
            # Handle edge case where block spans beyond disk
            sector2_data = b"\x00" * self.SECTOR_SIZE
            
        return sector1_data + sector2_data
        
    def _read_dos_sector(self, linear_sector: int) -> bytes:
        """Read a DOS sector from linear sector number.
        
        Args:
            linear_sector: Linear sector number (0-based)
            
        Returns:
            256-byte sector data
        """
        if linear_sector >= self.total_sectors:
            raise ValueError(
                f"Sector {linear_sector} out of range (max {self.total_sectors - 1})"
            )
        
        try:
            offset = linear_sector * self.SECTOR_SIZE
            self.file_handle.seek(offset)
            data = self.file_handle.read(self.SECTOR_SIZE)
            
            if len(data) != self.SECTOR_SIZE:
                raise CorruptedImageError(
                    f"Sector {linear_sector} incomplete: got {len(data)} bytes, expected {self.SECTOR_SIZE}",
                    str(self.file_path),
                )
            return data
            
        except OSError as e:
            raise DiskiiIOError(f"Error reading sector {linear_sector}: {e}") from e
    
    def write_block(self, block_num: int, data: bytes) -> None:
        """Write a ProDOS block using DOS sector translation.
        
        Args:
            block_num: Logical block number
            data: 512 bytes of block data
        """
        if len(data) != self.BLOCK_SIZE:
            raise ValueError(
                f"Block data must be exactly {self.BLOCK_SIZE} bytes, got {len(data)}"
            )
        
        # Map logical to physical block
        physical_block_num = self._map_logical_to_physical_block(block_num)
        
        # Write using DOS sector translation
        linear_sector1 = physical_block_num * 2
        linear_sector2 = physical_block_num * 2 + 1
        
        self._write_dos_sector(linear_sector1, data[:256])
        if linear_sector2 < self.total_sectors:
            self._write_dos_sector(linear_sector2, data[256:])
    
    def _write_dos_sector(self, linear_sector: int, data: bytes) -> None:
        """Write a DOS sector.
        
        Args:
            linear_sector: Linear sector number
            data: 256 bytes of sector data
        """
        if len(data) != self.SECTOR_SIZE:
            raise ValueError(
                f"Sector data must be exactly {self.SECTOR_SIZE} bytes, got {len(data)}"
            )
        
        if linear_sector >= self.total_sectors:
            raise ValueError(
                f"Sector {linear_sector} out of range (max {self.total_sectors - 1})"
            )
        
        try:
            offset = linear_sector * self.SECTOR_SIZE
            self.file_handle.seek(offset)
            self.file_handle.write(data)
            self.file_handle.flush()
        except OSError as e:
            raise DiskiiIOError(f"Error writing sector {linear_sector}: {e}") from e