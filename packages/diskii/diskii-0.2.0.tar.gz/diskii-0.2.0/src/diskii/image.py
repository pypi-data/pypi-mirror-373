"""Base classes for disk image handling."""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import BinaryIO, Optional

from .exceptions import (
    CorruptedImageError,
    UnsupportedOperationError,
    IOError as DiskiiIOError,
)


class SectorOrdering(Enum):
    """Sector ordering schemes for disk images."""

    DOS_ORDER = "dos_order"  # .dsk, .do files - DOS 3.3 sector interleaving
    PRODOS_ORDER = "prodos_order"  # .po files - ProDOS block ordering
    DOS32_ORDER = "dos32_order"  # .d13 files - DOS 3.2 13-sector format


class FilesystemType(Enum):
    """Filesystem types found on disk images."""

    DOS33 = "dos33"  # DOS 3.3 filesystem
    PRODOS = "prodos"  # ProDOS filesystem
    DOS32 = "dos32"  # DOS 3.2 filesystem


class ImageFormat:
    """Complete disk image format combining sector ordering and filesystem type."""

    def __init__(
        self,
        sector_ordering: SectorOrdering,
        filesystem: FilesystemType,
        size_bytes: int | None = None,
    ):
        self.sector_ordering = sector_ordering
        self.filesystem = filesystem
        self.size_bytes = size_bytes

    def __eq__(self, other):
        if isinstance(other, ImageFormat):
            return (
                self.sector_ordering == other.sector_ordering
                and self.filesystem == other.filesystem
            )
        return False

    def __repr__(self):
        return f"ImageFormat({self.sector_ordering.value}, {self.filesystem.value})"


class DiskImage(ABC):
    """Abstract base class for disk image readers."""

    def __init__(
        self,
        file_path: str | Path,
        image_format: Optional["ImageFormat"] = None,
        read_only: bool = True,
    ):
        self.file_path = Path(file_path)
        self._file_handle: BinaryIO | None = None
        self._image_format = image_format
        self._read_only = read_only

    def __enter__(self):
        mode = "rb" if self._read_only else "r+b"
        self._file_handle = open(self.file_path, mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    @property
    def is_open(self) -> bool:
        """Check if the image file is currently open."""
        return self._file_handle is not None and not self._file_handle.closed

    @abstractmethod
    def read_block(self, block_num: int) -> bytes:
        """Read a logical block from the disk image."""
        pass

    @abstractmethod
    def read_sector(self, track: int, sector: int) -> bytes:
        """Read a physical sector from the disk image."""
        pass

    def write_block(self, block_num: int, data: bytes) -> None:
        """Write a logical block to the disk image."""
        if self._read_only:
            raise UnsupportedOperationError("write", "read-only image")
        self._write_block_impl(block_num, data)

    def write_sector(self, track: int, sector: int, data: bytes) -> None:
        """Write a physical sector to the disk image."""
        if self._read_only:
            raise UnsupportedOperationError("write", "read-only image")
        self._write_sector_impl(track, sector, data)

    @abstractmethod
    def _write_block_impl(self, block_num: int, data: bytes) -> None:
        """Implementation-specific block writing."""
        pass

    @abstractmethod
    def _write_sector_impl(self, track: int, sector: int, data: bytes) -> None:
        """Implementation-specific sector writing."""
        pass

    @abstractmethod
    def get_volume_name(self) -> str:
        """Get the volume name from the disk image."""
        pass

    @abstractmethod
    def get_file_list(self) -> list:
        """Get a list of files on the disk image."""
        pass

    def create_file(self, filename: str, file_type: int | str, data: bytes, **kwargs) -> None:
        """Create a new file on the disk image.
        
        Args:
            filename: Name of the file to create
            file_type: File type (int for ProDOS, int or str for DOS)
            data: File content bytes
            **kwargs: Additional arguments (aux_type, etc.)
        """
        if self._read_only:
            raise UnsupportedOperationError("create_file", "read-only image")
        self._create_file_impl(filename, file_type, data, **kwargs)

    def delete_file(self, filename: str) -> None:
        """Delete a file from the disk image."""
        if self._read_only:
            raise UnsupportedOperationError("delete_file", "read-only image")
        self._delete_file_impl(filename)

    @abstractmethod
    def _create_file_impl(
        self, filename: str, file_type: int | str, data: bytes, **kwargs
    ) -> None:
        """Implementation-specific file creation."""
        pass

    @abstractmethod
    def _delete_file_impl(self, filename: str) -> None:
        """Implementation-specific file deletion."""
        pass

    @property
    def format(self) -> "ImageFormat":
        """Get the image format type."""
        if self._image_format is None:
            # Fallback: detect format if not provided
            from .detection import detect_format

            self._image_format = detect_format(self.file_path)
        return self._image_format

    @property
    @abstractmethod
    def total_blocks(self) -> int:
        """Get the total number of blocks in the image."""
        pass

    @property
    @abstractmethod
    def total_sectors(self) -> int:
        """Get the total number of sectors in the image."""
        pass


class ProDOSImage(DiskImage):
    """ProDOS disk image handler."""

    BLOCK_SIZE = 512

    def __init__(
        self,
        file_path: str | Path,
        image_format: Optional["ImageFormat"] = None,
        read_only: bool = True,
    ):
        super().__init__(file_path, image_format, read_only)
        self._volume_name: str | None = None

    def read_block(self, block_num: int) -> bytes:
        """Read a 512-byte ProDOS block."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")

        if block_num < 0 or block_num >= self.total_blocks:
            raise ValueError(
                f"Block {block_num} out of range (0-{self.total_blocks - 1})"
            )

        try:
            self._file_handle.seek(block_num * self.BLOCK_SIZE)
            data = self._file_handle.read(self.BLOCK_SIZE)
            if len(data) != self.BLOCK_SIZE:
                raise CorruptedImageError(
                    f"Block {block_num} incomplete: got {len(data)} bytes, expected {self.BLOCK_SIZE}",
                    str(self.file_path),
                )
            return data
        except OSError as e:
            raise DiskiiIOError(f"Error reading block {block_num}: {e}") from e

    def read_sector(self, track: int, sector: int) -> bytes:
        """Read sector by converting to block address."""
        # ProDOS uses blocks, so convert track/sector to block
        block_num = track * 8 + (sector // 2)
        block_data = self.read_block(block_num)

        # Return first or second half of block based on sector
        if sector % 2 == 0:
            return block_data[:256]
        else:
            return block_data[256:]

    def get_volume_name(self) -> str:
        """Get the ProDOS volume name from block 2."""
        if self._volume_name is None:
            from .prodos import parse_prodos_directory

            directory = parse_prodos_directory(self)
            self._volume_name = directory.volume_name

        return self._volume_name

    def get_file_list(self) -> list:
        """Get a list of files on the ProDOS volume."""
        from .prodos import parse_prodos_directory

        directory = parse_prodos_directory(self)
        return directory.parse()

    def get_all_files(self, recursive: bool = True) -> list:
        """Get all files from the ProDOS volume, optionally including subdirectories.

        Args:
            recursive: If True, recursively traverse subdirectories

        Returns:
            List of ProDOSFileEntry objects from entire directory tree
        """
        from .prodos import parse_prodos_directory

        directory = parse_prodos_directory(self)
        return directory.get_all_files(recursive=recursive)

    @property
    def total_blocks(self) -> int:
        """Calculate total blocks from file size."""
        return self.file_path.stat().st_size // self.BLOCK_SIZE

    @property
    def total_sectors(self) -> int:
        """Calculate total sectors (2 per block)."""
        return self.total_blocks * 2

    def _write_block_impl(self, block_num: int, data: bytes) -> None:
        """Write a 512-byte ProDOS block."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")

        if block_num < 0 or block_num >= self.total_blocks:
            raise ValueError(
                f"Block {block_num} out of range (0-{self.total_blocks - 1})"
            )

        if len(data) != self.BLOCK_SIZE:
            raise ValueError(
                f"Block data must be exactly {self.BLOCK_SIZE} bytes, got {len(data)}"
            )

        try:
            self._file_handle.seek(block_num * self.BLOCK_SIZE)
            self._file_handle.write(data)
            self._file_handle.flush()
        except OSError as e:
            raise DiskiiIOError(f"Error writing block {block_num}: {e}") from e

    def _write_sector_impl(self, track: int, sector: int, data: bytes) -> None:
        """Write sector by converting to block address."""
        if len(data) != 256:
            raise ValueError(f"Sector data must be exactly 256 bytes, got {len(data)}")

        # ProDOS uses blocks, so convert track/sector to block
        block_num = track * 8 + (sector // 2)

        # Read current block, modify the appropriate half, write back
        block_data = bytearray(self.read_block(block_num))

        if sector % 2 == 0:
            block_data[:256] = data
        else:
            block_data[256:] = data

        self._write_block_impl(block_num, bytes(block_data))

    def _create_file_impl(
        self, filename: str, file_type: int | str, data: bytes, **kwargs
    ) -> None:
        """Create a new ProDOS file."""
        from .prodos_writer import create_prodos_file
        from .file_type_conversion import normalize_prodos_file_type, get_prodos_aux_type_for_basic

        # Normalize file type to ProDOS integer format
        prodos_file_type = normalize_prodos_file_type(file_type)
        
        # Set default aux_type for BASIC programs if not specified
        if 'aux_type' not in kwargs:
            aux_type = get_prodos_aux_type_for_basic(file_type)
            if aux_type != 0:
                kwargs['aux_type'] = aux_type

        create_prodos_file(self, filename, prodos_file_type, data, **kwargs)

    def _delete_file_impl(self, filename: str) -> None:
        """Delete a ProDOS file."""
        from .prodos_writer import delete_prodos_file

        delete_prodos_file(self, filename)


class DOSOrderedProDOSImage(ProDOSImage):
    """ProDOS filesystem stored in DOS sector-ordered disk image (.dsk file).
    
    This class provides transparent access to ProDOS filesystems that are
    stored in DOS sector-ordered disk images. It uses a block translation
    layer to handle the sector-to-block mapping and automatically locates
    volume directories in non-standard locations.
    """
    
    def __init__(
        self,
        file_path: str | Path,
        image_format: Optional["ImageFormat"] = None,
        read_only: bool = True,
    ):
        super().__init__(file_path, image_format, read_only)
        self._block_reader = None  # Initialized when file is opened
    
    def __enter__(self):
        """Context manager entry - initialize block reader."""
        result = super().__enter__()
        if self._file_handle:
            from .dos_ordered_block_reader import DOSOrderedBlockReader
            self._block_reader = DOSOrderedBlockReader(self._file_handle, self.file_path)
        return result
    
    def read_block(self, block_num: int) -> bytes:
        """Read a 512-byte ProDOS block using transparent DOS sector translation."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")
        
        if self._block_reader is None:
            raise RuntimeError("Block reader not initialized")
        
        return self._block_reader.read_block(block_num)
    
    def _write_block_impl(self, block_num: int, data: bytes) -> None:
        """Write a 512-byte ProDOS block using transparent DOS sector translation."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")
        
        if self._block_reader is None:
            raise RuntimeError("Block reader not initialized")
        
        self._block_reader.write_block(block_num, data)
    
    @property
    def total_blocks(self) -> int:
        """Get total number of blocks, using block reader if available."""
        if self._block_reader is not None:
            return self._block_reader.total_blocks
        else:
            # Fallback calculation for when block reader isn't initialized
            return self.file_path.stat().st_size // self.BLOCK_SIZE
    
    @property
    def total_sectors(self) -> int:
        """Get total number of sectors, using block reader if available."""
        if self._block_reader is not None:
            return self._block_reader.total_sectors
        else:
            # Fallback calculation for when block reader isn't initialized  
            return self.file_path.stat().st_size // 256


class DOSImage(DiskImage):
    """DOS 3.3 disk image handler."""

    SECTOR_SIZE = 256
    SECTORS_PER_TRACK = 16

    def __init__(
        self,
        file_path: str | Path,
        image_format: Optional["ImageFormat"] = None,
        read_only: bool = True,
    ):
        super().__init__(file_path, image_format, read_only)
        self._volume_name: str | None = None

    def read_sector(self, track: int, sector: int) -> bytes:
        """Read a 256-byte DOS sector."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")

        if track < 0 or sector < 0 or sector >= self.SECTORS_PER_TRACK:
            raise ValueError(f"Invalid track/sector: {track}/{sector}")

        total_sectors = self.total_sectors
        linear_sector = track * self.SECTORS_PER_TRACK + sector
        if linear_sector >= total_sectors:
            raise ValueError(
                f"Sector {track}/{sector} out of range (max {total_sectors - 1})"
            )

        try:
            offset = linear_sector * self.SECTOR_SIZE
            self._file_handle.seek(offset)
            data = self._file_handle.read(self.SECTOR_SIZE)
            if len(data) != self.SECTOR_SIZE:
                raise CorruptedImageError(
                    f"Sector {track}/{sector} incomplete: got {len(data)} bytes, expected {self.SECTOR_SIZE}",
                    str(self.file_path),
                )
            return data
        except OSError as e:
            raise DiskiiIOError(f"Error reading sector {track}/{sector}: {e}") from e

    def read_block(self, block_num: int) -> bytes:
        """Read block by combining two sectors."""
        # DOS uses sectors, so convert block to track/sector
        sector_num = block_num * 2
        track = sector_num // self.SECTORS_PER_TRACK
        sector = sector_num % self.SECTORS_PER_TRACK

        sector1 = self.read_sector(track, sector)
        sector2 = self.read_sector(track, sector + 1) if sector < 15 else b"\x00" * 256

        return sector1 + sector2

    def get_volume_name(self) -> str:
        """Get the DOS 3.3 volume name from VTOC."""
        if self._volume_name is None:
            try:
                # DOS 3.3 VTOC is at track 17, sector 0
                vtoc = self.read_sector(17, 0)
                # DOS doesn't really have volume names, but we can use a default
                self._volume_name = "DOS 3.3"
            except Exception as e:
                raise CorruptedImageError(
                    f"Cannot read DOS VTOC: {e}", str(self.file_path)
                ) from e

        return self._volume_name

    def get_file_list(self) -> list:
        """Get a list of files on the DOS 3.3 disk."""
        from .dos33 import parse_dos33_catalog

        catalog = parse_dos33_catalog(self)
        return catalog.parse()

    @property
    def total_sectors(self) -> int:
        """Calculate total sectors from file size."""
        return self.file_path.stat().st_size // self.SECTOR_SIZE

    @property
    def total_blocks(self) -> int:
        """Calculate total blocks (sectors / 2)."""
        return self.total_sectors // 2

    def _write_sector_impl(self, track: int, sector: int, data: bytes) -> None:
        """Write a 256-byte DOS sector."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")

        if track < 0 or sector < 0 or sector >= self.SECTORS_PER_TRACK:
            raise ValueError(f"Invalid track/sector: {track}/{sector}")

        if len(data) != self.SECTOR_SIZE:
            raise ValueError(
                f"Sector data must be exactly {self.SECTOR_SIZE} bytes, got {len(data)}"
            )

        total_sectors = self.total_sectors
        linear_sector = track * self.SECTORS_PER_TRACK + sector
        if linear_sector >= total_sectors:
            raise ValueError(
                f"Sector {track}/{sector} out of range (max {total_sectors - 1})"
            )

        try:
            offset = linear_sector * self.SECTOR_SIZE
            self._file_handle.seek(offset)
            self._file_handle.write(data)
            self._file_handle.flush()
        except OSError as e:
            raise DiskiiIOError(f"Error writing sector {track}/{sector}: {e}") from e

    def _write_block_impl(self, block_num: int, data: bytes) -> None:
        """Write a block by converting to track/sector."""
        if len(data) != 512:
            raise ValueError(f"Block data must be exactly 512 bytes, got {len(data)}")

        # Convert block to track/sector and write both sectors
        track = block_num // 8
        base_sector = (block_num % 8) * 2

        # Write first sector (first 256 bytes)
        self._write_sector_impl(track, base_sector, data[:256])
        # Write second sector (last 256 bytes)
        self._write_sector_impl(track, base_sector + 1, data[256:])

    def _create_file_impl(
        self, filename: str, file_type: int | str, data: bytes, **kwargs
    ) -> None:
        """Create a new DOS file."""
        from .dos_writer import create_dos_file
        from .file_type_conversion import normalize_dos_file_type

        # Normalize file type to DOS string format
        dos_file_type = normalize_dos_file_type(file_type)
        
        create_dos_file(self, filename, dos_file_type, data, **kwargs)

    def _delete_file_impl(self, filename: str) -> None:
        """Delete a DOS file."""
        from .dos_writer import delete_dos_file

        delete_dos_file(self, filename)


class DOS32Image(DOSImage):
    """DOS 3.2 disk image handler (13 sectors per track)."""

    SECTORS_PER_TRACK = 13

    def __init__(
        self, 
        file_path: str | Path, 
        image_format: Optional["ImageFormat"] = None, 
        read_only: bool = True
    ):
        super().__init__(file_path, image_format, read_only)

    def get_volume_name(self) -> str:
        """Get the DOS 3.2 volume name."""
        if self._volume_name is None:
            self._volume_name = "DOS 3.2"
        return self._volume_name

    def get_file_list(self) -> list:
        """Get a list of files on the DOS 3.2 disk."""
        from .dos32 import parse_dos32_catalog

        catalog = parse_dos32_catalog(self)
        return catalog.parse()


class ProDOSOrderedDOSImage(DOSImage):
    """DOS filesystem stored in ProDOS block-ordered disk image (.po file).
    
    This class provides transparent access to DOS filesystems that are
    stored in ProDOS block-ordered disk images. It uses a sector translation
    layer to handle the block-to-sector mapping and automatically locates
    the VTOC in non-standard locations.
    """
    
    def __init__(
        self,
        file_path: str | Path,
        image_format: Optional["ImageFormat"] = None,
        read_only: bool = True,
    ):
        super().__init__(file_path, image_format, read_only)
        self._sector_reader = None  # Initialized when file is opened
    
    def __enter__(self):
        """Context manager entry - initialize sector reader."""
        result = super().__enter__()
        if self._file_handle:
            from .prodos_ordered_sector_reader import ProDOSOrderedSectorReader
            self._sector_reader = ProDOSOrderedSectorReader(self._file_handle, self.file_path)
        return result
    
    def read_sector(self, track: int, sector: int) -> bytes:
        """Read a 256-byte DOS sector using transparent ProDOS block translation."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")
        
        if self._sector_reader is None:
            raise RuntimeError("Sector reader not initialized")
        
        return self._sector_reader.read_sector(track, sector)
    
    def _write_sector_impl(self, track: int, sector: int, data: bytes) -> None:
        """Write a 256-byte DOS sector using transparent ProDOS block translation."""
        if not self.is_open:
            raise RuntimeError("Image file is not open")
        
        if self._sector_reader is None:
            raise RuntimeError("Sector reader not initialized")
        
        self._sector_reader.write_sector(track, sector, data)
    
    @property
    def total_blocks(self) -> int:
        """Get total number of blocks, using sector reader if available."""
        if self._sector_reader is not None:
            return self._sector_reader.total_blocks
        else:
            # Fallback calculation for when sector reader isn't initialized
            return self.file_path.stat().st_size // 512
    
    @property
    def total_sectors(self) -> int:
        """Get total number of sectors, using sector reader if available."""
        if self._sector_reader is not None:
            return self._sector_reader.total_sectors
        else:
            # Fallback calculation for when sector reader isn't initialized  
            return self.file_path.stat().st_size // self.SECTOR_SIZE
