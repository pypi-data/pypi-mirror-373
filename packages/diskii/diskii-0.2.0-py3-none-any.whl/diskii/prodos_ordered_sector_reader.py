"""ProDOS-ordered sector reader for DOS filesystems in .po files."""

from typing import BinaryIO, Optional
from pathlib import Path

from .exceptions import CorruptedImageError, IOError as DiskiiIOError


class ProDOSOrderedSectorReader:
    """Handles reading DOS sectors from ProDOS block-ordered disk images.
    
    This class provides a translation layer that makes ProDOS block-ordered
    disk images appear as standard DOS sector-ordered images to the
    DOS filesystem code.
    
    Key features:
    - Transparent block-to-sector translation
    - DOS track/sector addressing from ProDOS block layout
    - Automatic VTOC location detection and remapping
    """
    
    SECTOR_SIZE = 256
    SECTORS_PER_TRACK = 16
    BLOCK_SIZE = 512
    
    def __init__(self, file_handle: BinaryIO, file_path: Path):
        """Initialize the ProDOS-ordered sector reader.
        
        Args:
            file_handle: Open file handle to the disk image
            file_path: Path to the disk image file
        """
        self.file_handle = file_handle
        self.file_path = file_path
        self._total_blocks = None
        self._vtoc_track = None
        self._vtoc_sector = None
        self._sector_mapping = {}  # Maps logical sectors to physical sectors
        
    @property 
    def total_blocks(self) -> int:
        """Get total number of blocks in the image."""
        if self._total_blocks is None:
            self._total_blocks = self.file_path.stat().st_size // self.BLOCK_SIZE
        return self._total_blocks
    
    @property
    def total_sectors(self) -> int:
        """Get total number of sectors in the image."""
        return self.total_blocks * 2
        
    def read_sector(self, track: int, sector: int) -> bytes:
        """Read a DOS sector, handling logical-to-physical mapping.
        
        Args:
            track: DOS track number
            sector: DOS sector number within track
            
        Returns:
            256-byte sector data, normalized for DOS parsing
        """
        # Map logical sector to physical sector
        physical_track, physical_sector = self._map_logical_to_physical_sector(track, sector)
        
        # Read the physical sector using ProDOS block translation
        sector_data = self._read_physical_sector(physical_track, physical_sector)
        
        # Special handling for VTOC (Volume Table of Contents)
        if track == 17 and sector == 0:
            # This is the DOS VTOC - check if we need to remap it
            vtoc_track, vtoc_sector = self._find_vtoc_location()
            if vtoc_track != 17 or vtoc_sector != 0:
                # VTOC is at non-standard location, read from actual location
                sector_data = self._read_physical_sector(vtoc_track, vtoc_sector)
        
        return sector_data
    
    def _map_logical_to_physical_sector(self, track: int, sector: int) -> tuple[int, int]:
        """Map logical DOS track/sector to physical track/sector in ProDOS layout.
        
        This handles cases where the DOS VTOC is not at the standard
        track 17, sector 0 location due to ProDOS block ordering.
        """
        # Handle VTOC mapping (track 17, sector 0)
        if track == 17 and sector == 0:
            vtoc_track, vtoc_sector = self._find_vtoc_location()
            if vtoc_track != 17 or vtoc_sector != 0:
                # VTOC is at non-standard location
                return vtoc_track, vtoc_sector
        
        # For other sectors, check if we have any custom remapping
        sector_key = (track, sector)
        if sector_key in self._sector_mapping:
            return self._sector_mapping[sector_key]
            
        # Default: no mapping needed
        return track, sector
    
    def _find_vtoc_location(self) -> tuple[int, int]:
        """Find the physical track/sector containing the DOS VTOC.
        
        Returns:
            Tuple of (track, sector) containing the VTOC
        """
        if self._vtoc_track is not None and self._vtoc_sector is not None:
            return self._vtoc_track, self._vtoc_sector
            
        # Search first few tracks for DOS VTOC signature
        # DOS 3.3 VTOC has specific patterns we can detect
        for track in range(min(20, self.total_sectors // self.SECTORS_PER_TRACK)):
            for sector in range(self.SECTORS_PER_TRACK):
                try:
                    sector_data = self._read_physical_sector(track, sector)
                    
                    if self._is_vtoc_sector(sector_data):
                        self._vtoc_track = track
                        self._vtoc_sector = sector
                        return track, sector
                        
                except Exception:
                    continue
        
        # Default to track 17, sector 0 if not found
        self._vtoc_track = 17
        self._vtoc_sector = 0
        return 17, 0
    
    def _is_vtoc_sector(self, sector_data: bytes) -> bool:
        """Check if sector contains a DOS VTOC.
        
        Returns True if this appears to be a DOS VTOC sector.
        """
        if len(sector_data) < 256:
            return False
            
        # DOS 3.3 VTOC signature checks:
        # - Byte 0: Reserved (usually 0x00)
        # - Byte 1: Track number of first catalog sector (usually 17)  
        # - Byte 2: Sector number of first catalog sector (usually 15)
        # - Byte 3: DOS release number (3 for DOS 3.3)
        # - Bytes 4-5: Reserved (usually 0x00)
        # - Byte 6: Volume number (usually 254)
        # - Byte 7: Reserved (usually 0x00)
        
        # Check for DOS 3.3 VTOC patterns
        if (sector_data[3] == 3 and  # DOS release 3
            sector_data[6] == 254 and  # Standard volume number
            sector_data[1] in range(10, 25) and  # Reasonable catalog track
            sector_data[2] in range(0, 16)):  # Valid catalog sector
            return True
            
        # Additional check: look for track allocation bitmap pattern
        # Bytes 56-195 contain the track allocation bitmap
        # Active tracks should have reasonable allocation patterns
        if len(sector_data) >= 196:
            bitmap_start = 56
            bitmap_end = 196
            bitmap = sector_data[bitmap_start:bitmap_end]
            
            # Count tracks that appear to be in use (have any sectors allocated)
            tracks_in_use = sum(1 for byte_val in bitmap if byte_val != 0xFF)
            
            # DOS disk should have some tracks in use but not all
            if 5 <= tracks_in_use <= 30:  # Reasonable range
                return True
        
        return False
    
    def _read_physical_sector(self, track: int, sector: int) -> bytes:
        """Read a physical sector using ProDOS block-to-sector translation.
        
        Args:
            track: Physical track number in the image
            sector: Physical sector number within track
            
        Returns:
            256-byte sector data
        """
        if track < 0 or sector < 0 or sector >= self.SECTORS_PER_TRACK:
            raise ValueError(f"Invalid track/sector: {track}/{sector}")
        
        # Convert DOS track/sector to linear sector number
        linear_sector = track * self.SECTORS_PER_TRACK + sector
        
        if linear_sector >= self.total_sectors:
            raise ValueError(
                f"Sector {track}/{sector} out of range (max {self.total_sectors - 1})"
            )
        
        # Convert linear sector to ProDOS block number and offset within block
        block_num = linear_sector // 2
        sector_offset = linear_sector % 2
        
        # Read the ProDOS block
        block_data = self._read_prodos_block(block_num)
        
        # Extract the requested sector (first or second half of block)
        if sector_offset == 0:
            return block_data[:256]  # First sector of block
        else:
            return block_data[256:]  # Second sector of block
            
    def _read_prodos_block(self, block_num: int) -> bytes:
        """Read a ProDOS block from the image.
        
        Args:
            block_num: ProDOS block number
            
        Returns:
            512-byte block data
        """
        if block_num < 0 or block_num >= self.total_blocks:
            raise ValueError(
                f"Block {block_num} out of range (0-{self.total_blocks - 1})"
            )
        
        try:
            offset = block_num * self.BLOCK_SIZE
            self.file_handle.seek(offset)
            data = self.file_handle.read(self.BLOCK_SIZE)
            
            if len(data) != self.BLOCK_SIZE:
                raise CorruptedImageError(
                    f"Block {block_num} incomplete: got {len(data)} bytes, expected {self.BLOCK_SIZE}",
                    str(self.file_path),
                )
            return data
            
        except OSError as e:
            raise DiskiiIOError(f"Error reading block {block_num}: {e}") from e
    
    def write_sector(self, track: int, sector: int, data: bytes) -> None:
        """Write a DOS sector using ProDOS block translation.
        
        Args:
            track: DOS track number
            sector: DOS sector number within track
            data: 256 bytes of sector data
        """
        if len(data) != self.SECTOR_SIZE:
            raise ValueError(
                f"Sector data must be exactly {self.SECTOR_SIZE} bytes, got {len(data)}"
            )
        
        # Map logical to physical sector
        physical_track, physical_sector = self._map_logical_to_physical_sector(track, sector)
        
        # Convert to linear sector and then to ProDOS block
        linear_sector = physical_track * self.SECTORS_PER_TRACK + physical_sector
        
        if linear_sector >= self.total_sectors:
            raise ValueError(
                f"Sector {track}/{sector} out of range (max {self.total_sectors - 1})"
            )
        
        block_num = linear_sector // 2
        sector_offset = linear_sector % 2
        
        # Read current block, modify the appropriate half, write back
        current_block = self._read_prodos_block(block_num)
        block_data = bytearray(current_block)
        
        if sector_offset == 0:
            block_data[:256] = data  # First sector of block
        else:
            block_data[256:] = data  # Second sector of block
        
        self._write_prodos_block(block_num, bytes(block_data))
    
    def _write_prodos_block(self, block_num: int, data: bytes) -> None:
        """Write a ProDOS block.
        
        Args:
            block_num: ProDOS block number
            data: 512 bytes of block data
        """
        if len(data) != self.BLOCK_SIZE:
            raise ValueError(
                f"Block data must be exactly {self.BLOCK_SIZE} bytes, got {len(data)}"
            )
        
        if block_num >= self.total_blocks:
            raise ValueError(
                f"Block {block_num} out of range (max {self.total_blocks - 1})"
            )
        
        try:
            offset = block_num * self.BLOCK_SIZE
            self.file_handle.seek(offset)
            self.file_handle.write(data)
            self.file_handle.flush()
        except OSError as e:
            raise DiskiiIOError(f"Error writing block {block_num}: {e}") from e