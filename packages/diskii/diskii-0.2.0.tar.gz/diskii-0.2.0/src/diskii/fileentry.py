"""Common file entry interface for different filesystems."""

import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .exceptions import InvalidFileError


class FileType(Enum):
    """Common file types across DOS and ProDOS."""

    # DOS 3.3 types
    TEXT = "TXT"  # DOS: T
    INTEGER_BASIC = "INT"  # DOS: I
    APPLESOFT_BASIC = "BAS"  # DOS: A
    BINARY = "BIN"  # DOS: B
    SPECIAL = "SPC"  # DOS: S
    RELOCATABLE = "REL"  # DOS: R

    # ProDOS types (using hex values)
    PRODOS_UNK = 0x00  # Unknown
    PRODOS_BAD = 0x01  # Bad blocks
    PRODOS_PCD = 0x02  # Pascal code
    PRODOS_PTX = 0x03  # Pascal text
    PRODOS_TXT = 0x04  # ASCII text
    PRODOS_PDA = 0x05  # Pascal data
    PRODOS_BIN = 0x06  # Binary
    PRODOS_FNT = 0x07  # Font
    PRODOS_FOT = 0x08  # Foto
    PRODOS_BA3 = 0x09  # Business BASIC (3.0)
    PRODOS_DA3 = 0x0A  # Business BASIC data
    PRODOS_WPF = 0x0B  # Word processor
    PRODOS_SOS = 0x0F  # SOS system
    PRODOS_DIR = 0x0F  # Directory
    PRODOS_RPD = 0x10  # RPS data
    PRODOS_RPI = 0x11  # RPS index
    PRODOS_AFD = 0x12  # AppleFile discard
    PRODOS_AFM = 0x13  # AppleFile model
    PRODOS_AFR = 0x14  # AppleFile report
    PRODOS_SCL = 0x15  # Screen library
    PRODOS_PFS = 0x16  # PFS document
    PRODOS_ADB = 0x19  # AppleWorks database
    PRODOS_AWP = 0x1A  # AppleWorks word processor
    PRODOS_ASP = 0x1B  # AppleWorks spreadsheet


@dataclass
class FileEntry(ABC):
    """Abstract base class for file entries."""

    filename: str
    file_type: FileType | int | str
    size: int
    locked: bool

    @abstractmethod
    def read_data(self) -> bytes:
        """Read the file's data content."""
        pass

    @property
    @abstractmethod
    def is_directory(self) -> bool:
        """Check if this entry represents a directory."""
        pass

    @property
    @abstractmethod
    def creation_date(self) -> datetime | None:
        """Get file creation date if available."""
        pass

    @property
    @abstractmethod
    def modification_date(self) -> datetime | None:
        """Get file modification date if available."""
        pass


@dataclass
class DOSFileEntry(FileEntry):
    """DOS 3.3 file entry."""

    track: int
    sector: int
    length_sectors: int
    dos_type: str  # T, I, A, B, S, R

    def __post_init__(self):
        # Convert DOS type to common FileType
        dos_to_common = {
            "T": FileType.TEXT,
            "I": FileType.INTEGER_BASIC,
            "A": FileType.APPLESOFT_BASIC,
            "B": FileType.BINARY,
            "S": FileType.SPECIAL,
            "R": FileType.RELOCATABLE,
        }
        self.file_type = dos_to_common.get(self.dos_type, self.dos_type)

    @property
    def is_directory(self) -> bool:
        """DOS 3.3 doesn't have directories."""
        return False

    @property
    def creation_date(self) -> datetime | None:
        """DOS 3.3 doesn't store creation dates."""
        return None

    @property
    def modification_date(self) -> datetime | None:
        """DOS 3.3 doesn't store modification dates."""
        return None

    def read_data(self) -> bytes:
        """Read file data from the DOS 3.3 disk image."""
        if hasattr(self, "_image") and self._image:
            from .dos33 import DOSTrackSectorList

            ts_list = DOSTrackSectorList(self._image, self.track, self.sector)
            sectors = ts_list.read_sectors()

            # Combine all sectors into file data
            file_data = bytearray()
            for sector_data in sectors:
                file_data.extend(sector_data)

            # For DOS 3.3, trim file data based on file type
            if self.dos_type == "T":  # Text file
                # Text files often end with null byte or Ctrl+D (0x04)
                # Find first null byte and truncate there
                try:
                    null_pos = file_data.index(0x00)
                    file_data = file_data[:null_pos]
                except ValueError:
                    # No null byte found, try Ctrl+D
                    try:
                        ctrl_d_pos = file_data.index(0x04)
                        file_data = file_data[:ctrl_d_pos]
                    except ValueError:
                        # No terminator found, use all data but warn it might be padded
                        pass
            elif self.dos_type == "A":  # Applesoft BASIC
                # Applesoft BASIC files are plain text and should be trimmed like text files
                # Look for null byte terminator (common padding pattern)
                try:
                    null_pos = file_data.index(0x00)
                    file_data = file_data[:null_pos]
                except ValueError:
                    # No null byte found, keep all data
                    pass
            elif self.dos_type == "I":  # Integer BASIC  
                # Integer BASIC files are also text-based and should be trimmed
                try:
                    null_pos = file_data.index(0x00)
                    file_data = file_data[:null_pos]
                except ValueError:
                    # No null byte found, keep all data
                    pass
            elif self.dos_type == "B":  # Binary file
                # DOS 3.3 binary files can have different formats:
                # 1. Standard DOS binary: 2 bytes start addr + 2 bytes length + data
                # 2. Our cross-format binary: 4 bytes length + original data
                # 3. Raw binary data (preserve all allocated sectors)
                if hasattr(self, 'length_sectors') and self.length_sectors > 0:
                    expected_size = self.length_sectors * 256
                    if len(file_data) > expected_size:
                        file_data = file_data[:expected_size]
                
                if len(file_data) >= 4:
                    try:
                        # First, check if this has our cross-format size header
                        # (4-byte little-endian length at start)
                        potential_size = struct.unpack("<I", file_data[0:4])[0]
                        
                        if (potential_size > 0 and 
                            potential_size <= len(file_data) - 4 and
                            potential_size <= 65536):  # Reasonable size limit
                            # This looks like our cross-format size header
                            actual_data = file_data[4:4 + potential_size]
                            file_data = actual_data
                        else:
                            # Check if it's a standard DOS binary format
                            start_addr = struct.unpack("<H", file_data[0:2])[0]
                            file_length = struct.unpack("<H", file_data[2:4])[0]
                            
                            header_size = 4
                            max_possible_length = len(file_data) - header_size
                            
                            if (0x0800 <= start_addr <= 0xBFFF and 
                                4 <= file_length <= max_possible_length and
                                file_length < 32768):
                                # Standard DOS binary file
                                file_data = file_data[:header_size + file_length]
                            # Otherwise preserve all data
                    except (struct.error, IndexError):
                        # Error reading headers, preserve all data
                        pass
            else:
                # Other file types: return all sector data
                pass
            
            return bytes(file_data)

        raise InvalidFileError(
            "No image reference available for file reading", self.filename
        )

    def read_as_text(self) -> str:
        """Read BASIC file as plain text (detokenized if necessary).
        
        Returns:
            Plain text BASIC program
        """
        if self.dos_type not in ("A", "I"):
            raise InvalidFileError(
                f"Cannot read file type '{self.dos_type}' as BASIC text", self.filename
            )
        
        # Read raw file data
        data = self.read_data()
        
        # Import here to avoid circular imports
        from .basic_tokenizer import detokenize_applesoft, detokenize_integer_basic, auto_detect_variant
        
        # Detect if data is tokenized or already plain text
        if self._is_tokenized_data(data):
            # Detokenize based on file type
            if self.dos_type == "A":  # Applesoft
                return detokenize_applesoft(data)
            else:  # Integer BASIC
                return detokenize_integer_basic(data)
        else:
            # Already plain text
            try:
                return data.decode('ascii')
            except UnicodeDecodeError:
                # Fallback for non-ASCII data
                return data.decode('ascii', errors='replace')
    
    def read_as_tokens(self) -> bytes:
        """Read BASIC file as tokenized bytes.
        
        Returns:
            Tokenized BASIC program bytes
        """
        if self.dos_type not in ("A", "I"):
            raise InvalidFileError(
                f"Cannot read file type '{self.dos_type}' as BASIC tokens", self.filename
            )
        
        # Read raw file data
        data = self.read_data()
        
        # If already tokenized, return as-is
        if self._is_tokenized_data(data):
            return data
        
        # Need to tokenize plain text
        from .basic_tokenizer import tokenize_applesoft, tokenize_integer_basic
        
        try:
            text = data.decode('ascii')
            if self.dos_type == "A":  # Applesoft
                return tokenize_applesoft(text)
            else:  # Integer BASIC
                return tokenize_integer_basic(text)
        except UnicodeDecodeError:
            # Cannot tokenize non-ASCII data
            raise InvalidFileError(
                f"Cannot tokenize non-ASCII BASIC program", self.filename
            )
    
    def _is_tokenized_data(self, data: bytes) -> bool:
        """Check if data appears to be tokenized BASIC.
        
        Args:
            data: File data to check
            
        Returns:
            True if data appears tokenized, False if plain text
        """
        if len(data) < 4:
            return False
        
        # Check for BASIC program structure:
        # - First 2 bytes: next line pointer (usually 0 for single line)
        # - Next 2 bytes: line number (little-endian, should be reasonable)
        try:
            line_num = struct.unpack('<H', data[2:4])[0]
            
            # Reasonable line numbers are typically 1-63999
            if not (1 <= line_num <= 63999):
                return False
            
            # Look for tokens in the data (high bit set for Applesoft)
            token_count = sum(1 for b in data[4:min(len(data), 50)] if b >= 128)
            
            # If we have tokens, likely tokenized; if not, likely plain text
            return token_count > 0
            
        except (struct.error, IndexError):
            return False


@dataclass
class ProDOSFileEntry(FileEntry):
    """ProDOS file entry."""

    storage_type: int  # 1=seedling, 2=sapling, 3=tree, 0xD=subdirectory
    key_block: int
    blocks_used: int
    aux_type: int
    created: datetime | None = None
    modified: datetime | None = None
    access: int = 0  # Access permissions

    @property
    def is_directory(self) -> bool:
        """Check if this is a subdirectory."""
        return self.storage_type == 0x0D

    @property
    def creation_date(self) -> datetime | None:
        """Get creation date."""
        return self.created

    @property
    def modification_date(self) -> datetime | None:
        """Get modification date."""
        return self.modified

    @property
    def is_seedling(self) -> bool:
        """Check if this is a seedling file (≤ 512 bytes)."""
        return self.storage_type == 1

    @property
    def is_sapling(self) -> bool:
        """Check if this is a sapling file (513-131,072 bytes)."""
        return self.storage_type == 2

    @property
    def is_tree(self) -> bool:
        """Check if this is a tree file (> 131,072 bytes)."""
        return self.storage_type == 3

    @property
    def full_path(self) -> str:
        """Get the full path of this file (including directory path).

        Returns the full path if it has been set during directory traversal,
        otherwise returns just the filename.
        """
        return getattr(self, "_full_path", self.filename)

    def read_data(self) -> bytes:
        """Read file data from the ProDOS image."""
        if hasattr(self, "_image") and self._image:
            from .file_reading import read_prodos_file_data

            return read_prodos_file_data(self, self._image)
        raise InvalidFileError(
            "No image reference available for file reading",
            getattr(self, "filename", "unknown"),
        )

    def get_file_type_description(self) -> str:
        """Get human-readable description of the file type."""
        from .prodos_types import get_file_type_description

        return get_file_type_description(self.file_type)

    def get_aux_type_description(self) -> str | None:
        """Get human-readable description of the auxiliary type."""
        from .prodos_types import get_aux_type_description

        return get_aux_type_description(self.file_type, self.aux_type)

    def get_file_category(self) -> str:
        """Get general category of the file (Executable, Text, Data, etc.)."""
        from .prodos_types import get_file_category

        return get_file_category(self.file_type)

    def is_executable(self) -> bool:
        """Check if this file is executable."""
        from .prodos_types import is_executable_type

        return is_executable_type(self.file_type)

    def is_text_file(self) -> bool:
        """Check if this is a text file."""
        from .prodos_types import is_text_type

        return is_text_type(self.file_type)

    def is_graphics_file(self) -> bool:
        """Check if this is a graphics file."""
        from .prodos_types import is_graphics_type

        return is_graphics_type(self.file_type)

    def get_load_address(self) -> int | None:
        """Get load address for binary files, None for other types."""
        if self.file_type == 0x06:  # Binary file
            return self.aux_type
        return None

    def get_record_length(self) -> int | None:
        """Get record length for text files, None for other types."""
        if self.file_type == 0x04:  # Text file
            return self.aux_type if self.aux_type > 0 else None
        return None

    def read_subdirectory(self):
        """Read subdirectory contents if this is a directory entry."""
        if not self.is_directory:
            raise ValueError(f"{self.filename} is not a directory")

        if hasattr(self, "_image") and self._image:
            from .prodos import ProDOSSubdirectory

            return ProDOSSubdirectory(self._image, self.key_block, self.filename)

        raise InvalidFileError(
            "No image reference available for subdirectory reading", self.filename
        )

    def is_basic_file(self) -> bool:
        """Check if this is a BASIC program file."""
        return self.file_type in (0xFC, 0xFA)  # BAS (Applesoft) or INT (Integer)

    def read_as_text(self) -> str:
        """Read BASIC file as plain text (detokenized if necessary).
        
        Returns:
            Plain text BASIC program
        """
        if not self.is_basic_file():
            raise InvalidFileError(
                f"Cannot read file type ${self.file_type:02X} as BASIC text", self.filename
            )
        
        # Read raw file data
        data = self.read_data()
        
        # Import here to avoid circular imports
        from .basic_tokenizer import detokenize_applesoft, detokenize_integer_basic
        
        # Detect if data is tokenized or already plain text
        if self._is_tokenized_data(data):
            # Detokenize based on file type
            if self.file_type == 0xFC:  # Applesoft BAS
                return detokenize_applesoft(data)
            else:  # Integer BASIC
                return detokenize_integer_basic(data)
        else:
            # Already plain text
            try:
                return data.decode('ascii')
            except UnicodeDecodeError:
                # Fallback for non-ASCII data
                return data.decode('ascii', errors='replace')
    
    def read_as_tokens(self) -> bytes:
        """Read BASIC file as tokenized bytes.
        
        Returns:
            Tokenized BASIC program bytes
        """
        if not self.is_basic_file():
            raise InvalidFileError(
                f"Cannot read file type ${self.file_type:02X} as BASIC tokens", self.filename
            )
        
        # Read raw file data
        data = self.read_data()
        
        # If already tokenized, return as-is
        if self._is_tokenized_data(data):
            return data
        
        # Need to tokenize plain text
        from .basic_tokenizer import tokenize_applesoft, tokenize_integer_basic
        
        try:
            text = data.decode('ascii')
            if self.file_type == 0xFC:  # Applesoft BAS
                return tokenize_applesoft(text)
            else:  # Integer BASIC
                return tokenize_integer_basic(text)
        except UnicodeDecodeError:
            # Cannot tokenize non-ASCII data
            raise InvalidFileError(
                f"Cannot tokenize non-ASCII BASIC program", self.filename
            )
    
    def _is_tokenized_data(self, data: bytes) -> bool:
        """Check if data appears to be tokenized BASIC.
        
        Args:
            data: File data to check
            
        Returns:
            True if data appears tokenized, False if plain text
        """
        if len(data) < 4:
            return False
        
        # Check for BASIC program structure:
        # - First 2 bytes: next line pointer (usually 0 for single line)
        # - Next 2 bytes: line number (little-endian, should be reasonable)
        try:
            line_num = struct.unpack('<H', data[2:4])[0]
            
            # Reasonable line numbers are typically 1-63999
            if not (1 <= line_num <= 63999):
                return False
            
            # Look for tokens in the data
            if self.file_type == 0xFC:  # Applesoft - tokens are 128-255
                token_count = sum(1 for b in data[4:min(len(data), 50)] if b >= 128)
            else:  # Integer BASIC - tokens are in different ranges
                token_count = sum(1 for b in data[4:min(len(data), 50)] if 16 <= b <= 102)
            
            # If we have tokens, likely tokenized; if not, likely plain text
            return token_count > 0
            
        except (struct.error, IndexError):
            return False


def normalize_filename(filename: str, target_system: str = "host") -> str:
    """Normalize filename for different systems.

    Args:
        filename: Original filename
        target_system: "host", "dos", or "prodos"
    """
    if target_system == "dos":
        # DOS 3.3 requirements: max 30 chars, high ASCII, must start with letter
        cleaned = filename.upper()[:30]
        if not cleaned or not cleaned[0].isalpha():
            cleaned = "A" + cleaned[:29]
        return cleaned

    elif target_system == "prodos":
        # ProDOS requirements: max 15 chars, letters/digits/periods only
        cleaned = ""
        for char in filename[:15]:
            if char.isalnum() or char == ".":
                cleaned += char.upper()
        if not cleaned or not cleaned[0].isalpha():
            cleaned = "A" + cleaned[:14]
        return cleaned

    else:  # host system
        # Convert high ASCII to regular ASCII, remove invalid chars
        cleaned = ""
        for char in filename:
            if ord(char) > 127:
                char = chr(ord(char) - 128)  # Convert high ASCII
            if char.isprintable() and char not in '<>:"/\\|?*':
                cleaned += char
        return cleaned or "unnamed"


def convert_file_type(
    file_type: FileType | int | str, target_system: str
) -> FileType | int | str:
    """Convert file type between systems."""
    if target_system == "dos":
        # Convert to DOS single character
        type_map = {
            FileType.TEXT: "T",
            FileType.INTEGER_BASIC: "I",
            FileType.APPLESOFT_BASIC: "A",
            FileType.BINARY: "B",
            FileType.SPECIAL: "S",
            FileType.RELOCATABLE: "R",
        }
        return type_map.get(file_type, "B")  # Default to binary

    elif target_system == "prodos":
        # Convert to ProDOS hex type
        type_map = {
            FileType.TEXT: 0x04,
            FileType.INTEGER_BASIC: 0xFA,  # Integer BASIC
            FileType.APPLESOFT_BASIC: 0xFC,  # Applesoft BASIC
            FileType.BINARY: 0x06,
        }
        return type_map.get(file_type, 0x06)  # Default to binary

    return file_type
