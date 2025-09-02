"""DiskII - Apple II Disk Image Library - manipulate Apple II disk images."""

from .addressing import AddressTranslator, BlockAddress, SectorAddress
from .detection import detect_format, open_disk_image, validate_image_file
from .dos33 import DOSVTOC, DOSCatalog, DOSTrackSectorList, parse_dos33_catalog
from .exceptions import (
    AccessError,
    CorruptedImageError,
    DirectoryCorruptedError,
    DiskiiError,
    FileNotFoundError,
    FilesystemError,
    ImageFormatError,
    InvalidFileError,
    InvalidHeaderError,
    InvalidImageSizeError,
    IOError,
    PermissionError,
    UnrecognizedFormatError,
    UnsupportedOperationError,
)
from .fileentry import DOSFileEntry, FileEntry, FileType, ProDOSFileEntry
from .image import (
    DiskImage,
    DOS32Image,
    DOSImage,
    DOSOrderedProDOSImage,
    FilesystemType,
    ImageFormat,
    ProDOSImage,
    ProDOSOrderedDOSImage,
    SectorOrdering,
)
from .prodos import (
    ProDOSSubdirectory,
    ProDOSVolumeBitmap,
    ProDOSVolumeDirectory,
    parse_prodos_directory,
)
from .prodos_types import ProDOSFileType, get_file_category, get_file_type_description
from .basic_tokenizer import (
    tokenize_applesoft,
    detokenize_applesoft,
    tokenize_integer_basic,
    detokenize_integer_basic,
    auto_detect_variant,
)
from .basic_tokens import get_applesoft_table, get_integer_basic_table, BasicTokenTable
from .basic import BasicSyntaxValidator
from .basic.common_validator import SyntaxErrorInfo
from .dos_writer import create_dos_file, delete_dos_file
from .file_operations import copy_file, copy_all_files


def validate_basic_syntax(program_text: str, variant: str = "applesoft") -> list[SyntaxErrorInfo]:
    """Validate BASIC program syntax using ROM-compliant rules.
    
    Args:
        program_text: The BASIC program text to validate
        variant: Either "applesoft" or "integer" 
        
    Returns:
        List of syntax errors found (empty if valid)
    """
    validator = BasicSyntaxValidator(variant)
    return validator.validate_program(program_text)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "DiskImage",
    "ProDOSImage",
    "DOSImage",
    "DOSOrderedProDOSImage",
    "DOS32Image",
    "ImageFormat",
    "SectorOrdering",
    "FilesystemType",
    # Detection and opening
    "detect_format",
    "open_disk_image",
    "validate_image_file",
    # File entries
    "FileEntry",
    "DOSFileEntry",
    "ProDOSFileEntry",
    "FileType",
    # Addressing
    "SectorAddress",
    "BlockAddress",
    "AddressTranslator",
    # ProDOS filesystem
    "parse_prodos_directory",
    "ProDOSVolumeDirectory",
    "ProDOSSubdirectory",
    "ProDOSVolumeBitmap",
    "ProDOSFileType",
    "get_file_type_description",
    "get_file_category",
    # DOS 3.3 filesystem
    "parse_dos33_catalog",
    "DOSCatalog",
    "DOSVTOC",
    "DOSTrackSectorList",
    # BASIC tokenization
    "tokenize_applesoft",
    "detokenize_applesoft", 
    "tokenize_integer_basic",
    "detokenize_integer_basic",
    "auto_detect_variant",
    "get_applesoft_table",
    "get_integer_basic_table",
    "BasicTokenTable",
    # BASIC syntax validation
    "BasicSyntaxValidator", 
    "SyntaxErrorInfo",
    "validate_basic_syntax",
    # DOS 3.3/3.2 file writing
    "create_dos_file",
    "delete_dos_file",
    # High-level file operations
    "copy_file",
    "copy_all_files",
    # Exceptions
    "DiskiiError",
    "ImageFormatError",
    "UnrecognizedFormatError",
    "CorruptedImageError",
    "InvalidImageSizeError",
    "InvalidHeaderError",
    "FilesystemError",
    "DirectoryCorruptedError",
    "FileNotFoundError",
    "InvalidFileError",
    "AccessError",
    "PermissionError",
    "IOError",
    "UnsupportedOperationError",
]
