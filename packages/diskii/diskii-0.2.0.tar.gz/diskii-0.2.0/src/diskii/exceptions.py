"""Exception classes for diskii disk image library."""


class DiskiiError(Exception):
    """Base exception for all diskii-related errors."""

    pass


class ImageFormatError(DiskiiError):
    """Raised when disk image format cannot be determined or is invalid."""

    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message)


class UnrecognizedFormatError(ImageFormatError):
    """Raised when disk image format is completely unrecognized."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Unrecognized disk image format: {file_path}", file_path)


class CorruptedImageError(DiskiiError):
    """Raised when disk image appears to be corrupted or invalid."""

    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message)


class InvalidImageSizeError(CorruptedImageError):
    """Raised when disk image has an invalid size for its format."""

    def __init__(self, file_path: str, actual_size: int, expected_sizes: list[int]):
        self.file_path = file_path
        self.actual_size = actual_size
        self.expected_sizes = expected_sizes
        expected_str = ", ".join(str(s) for s in expected_sizes)
        super().__init__(
            f"Invalid image size {actual_size} bytes for {file_path}. "
            f"Expected one of: {expected_str} bytes",
            file_path,
        )


class InvalidHeaderError(CorruptedImageError):
    """Raised when disk image has invalid or missing header information."""

    def __init__(
        self, message: str, file_path: str = None, block_or_sector: int = None
    ):
        self.file_path = file_path
        self.block_or_sector = block_or_sector
        super().__init__(message, file_path)


class FilesystemError(DiskiiError):
    """Base class for filesystem-related errors."""

    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message)


class DirectoryCorruptedError(FilesystemError):
    """Raised when directory structure is corrupted or unreadable."""

    pass


class FileNotFoundError(FilesystemError):
    """Raised when a file cannot be found in the disk image."""

    def __init__(self, filename: str, file_path: str = None):
        self.filename = filename
        super().__init__(f"File not found: {filename}", file_path)


class InvalidFileError(FilesystemError):
    """Raised when file data is corrupted or invalid."""

    def __init__(self, message: str, filename: str = None, file_path: str = None):
        self.filename = filename
        super().__init__(message, file_path)


class AccessError(DiskiiError):
    """Raised when there are file system access issues."""

    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message)


class PermissionError(AccessError):
    """Raised when there are permission issues accessing the image."""

    pass


class IOError(AccessError):
    """Raised when there are I/O errors reading/writing the image."""

    pass


class UnsupportedOperationError(DiskiiError):
    """Raised when an operation is not supported for a particular image type."""

    def __init__(self, operation: str, image_type: str = None):
        self.operation = operation
        self.image_type = image_type
        message = f"Unsupported operation: {operation}"
        if image_type:
            message += f" for {image_type} images"
        super().__init__(message)
