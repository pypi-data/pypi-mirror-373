"""ProDOS file type definitions and handling."""

from enum import IntEnum


class ProDOSFileType(IntEnum):
    """ProDOS file type definitions according to Apple II File Type Notes."""

    # Basic types
    UNK = 0x00  # Unknown
    BAD = 0x01  # Bad blocks
    PCD = 0x02  # Pascal code
    PTX = 0x03  # Pascal text
    TXT = 0x04  # ASCII text
    PDA = 0x05  # Pascal data
    BIN = 0x06  # Binary
    FNT = 0x07  # Font
    FOT = 0x08  # Foto
    BA3 = 0x09  # Business BASIC 3.0 program
    DA3 = 0x0A  # Business BASIC data
    WPF = 0x0B  # Word processor
    SOS = 0x0F  # SOS system

    # Directory
    DIR = 0x0F  # Directory (same as SOS)

    # Apple II specific
    RPD = 0x10  # RPS data
    RPI = 0x11  # RPS index
    AFD = 0x12  # AppleFile discard
    AFM = 0x13  # AppleFile model
    AFR = 0x14  # AppleFile report
    SCL = 0x15  # Screen library
    PFS = 0x16  # PFS document

    # AppleWorks
    ADB = 0x19  # AppleWorks database
    AWP = 0x1A  # AppleWorks word processing
    ASP = 0x1B  # AppleWorks spreadsheet

    # System and development
    TDM = 0x20  # Desktop Manager
    IPS = 0x21  # Instant Pascal source
    UPV = 0x29  # UCSD Pascal volume

    # Graphics
    BMP = 0x30  # Bitmap
    PIC = 0x31  # Picture
    ANI = 0x32  # Animation
    PAL = 0x33  # Palette

    # Sound
    SND = 0x50  # Sound
    MUS = 0x51  # Music
    INS = 0x52  # Instrument

    # Apple IIgs specific
    SRC = 0xB0  # Source code
    OBJ = 0xB1  # Object code
    LIB = 0xB2  # Library
    S16 = 0xB3  # Application program (S16)
    RTL = 0xB4  # Runtime library
    EXE = 0xB5  # Shell application
    PIF = 0xB6  # Permanent init file
    TIF = 0xB7  # Temporary init file
    NDA = 0xB8  # New desk accessory
    CDA = 0xB9  # Control panel
    TOL = 0xBA  # Tool
    DRV = 0xBB  # Device driver
    LDF = 0xBC  # Load file
    FST = 0xBD  # File system translator

    # Development
    DOC = 0xBF  # Document

    # Special Apple II types
    ICN = 0xCA  # Icon
    MUS_GS = 0xD5  # Music (GS)
    SND_GS = 0xD6  # Sound (GS)
    CLR = 0xD7  # Color
    IMG = 0xD8  # Image

    # System
    OS = 0xEE  # ProDOS 8 Operating System
    INT = 0xFA  # Integer BASIC program
    IVR = 0xFB  # Integer BASIC variables
    BAS = 0xFC  # Applesoft BASIC program
    VAR = 0xFD  # Applesoft BASIC variables
    REL = 0xFE  # Relocatable
    SYS = 0xFF  # ProDOS 8 system file


# File type descriptions
FILE_TYPE_DESCRIPTIONS: dict[int, str] = {
    0x00: "Unknown",
    0x01: "Bad blocks",
    0x02: "Pascal code",
    0x03: "Pascal text",
    0x04: "ASCII text",
    0x05: "Pascal data",
    0x06: "Binary",
    0x07: "Font",
    0x08: "Foto",
    0x09: "Business BASIC program",
    0x0A: "Business BASIC data",
    0x0B: "Word processor",
    0x0F: "Directory/SOS system",
    0x10: "RPS data",
    0x11: "RPS index",
    0x12: "AppleFile discard",
    0x13: "AppleFile model",
    0x14: "AppleFile report",
    0x15: "Screen library",
    0x16: "PFS document",
    0x19: "AppleWorks database",
    0x1A: "AppleWorks word processing",
    0x1B: "AppleWorks spreadsheet",
    0x20: "Desktop Manager",
    0x21: "Instant Pascal source",
    0x29: "UCSD Pascal volume",
    0x50: "Sound",
    0x51: "Music",
    0x52: "Instrument",
    0xB0: "Source code",
    0xB1: "Object code",
    0xB2: "Library",
    0xB3: "GS/OS application",
    0xB4: "Runtime library",
    0xB5: "Shell application",
    0xB6: "Permanent init file",
    0xB7: "Temporary init file",
    0xB8: "New desk accessory",
    0xB9: "Control panel",
    0xBA: "Tool",
    0xBB: "Device driver",
    0xBC: "Load file",
    0xBD: "File system translator",
    0xBF: "Document",
    0xCA: "Icon",
    0xD5: "Music (GS)",
    0xD6: "Sound (GS)",
    0xD7: "Color",
    0xD8: "Image",
    0xEE: "ProDOS 8 system",
    0xFA: "Integer BASIC program",
    0xFB: "Integer BASIC variables",
    0xFC: "Applesoft BASIC program",
    0xFD: "Applesoft BASIC variables",
    0xFE: "Relocatable",
    0xFF: "ProDOS 8 system file",
}

# Auxiliary type meanings for specific file types
AUX_TYPE_MEANINGS: dict[int, dict[int, str]] = {
    # Text files ($04) - aux type is record length
    0x04: {},  # Aux type is record length (0 = sequential)
    # Binary files ($06) - aux type is load address
    0x06: {},  # Aux type is load address
    # Applesoft BASIC ($FC) - aux type is not used
    0xFC: {},
    # Graphics files
    0x30: {  # Bitmap
        0x0000: "Monochrome bitmap",
        0x0001: "Color bitmap",
    },
    # Sound files
    0x50: {},  # Aux type is sample rate
    # GS/OS applications ($B3)
    0xB3: {
        0x0000: "Standard S16 application",
        0x0001: "Shell application",
        0x0002: "Permanent init file",
        0x0003: "Temporary init file",
    },
}


def get_file_type_description(file_type: int) -> str:
    """Get human-readable description of ProDOS file type."""
    return FILE_TYPE_DESCRIPTIONS.get(file_type, f"Unknown type ${file_type:02X}")


def get_aux_type_description(file_type: int, aux_type: int) -> str | None:
    """Get human-readable description of auxiliary type for given file type."""
    if file_type in AUX_TYPE_MEANINGS:
        meanings = AUX_TYPE_MEANINGS[file_type]
        if aux_type in meanings:
            return meanings[aux_type]

    # Special handling for common aux type patterns
    if file_type == 0x04:  # Text file
        if aux_type == 0:
            return "Sequential text file"
        else:
            return f"Record length: {aux_type}"

    elif file_type == 0x06:  # Binary file
        return f"Load address: ${aux_type:04X}"

    elif file_type == 0x50:  # Sound file
        if aux_type > 0:
            return f"Sample rate: {aux_type} Hz"

    return None


def is_executable_type(file_type: int) -> bool:
    """Check if file type represents an executable program."""
    executable_types = {
        0x09,  # Business BASIC
        0xB3,  # GS/OS application
        0xB5,  # Shell application
        0xFA,  # Integer BASIC
        0xFC,  # Applesoft BASIC
        0xFF,  # System file
    }
    return file_type in executable_types


def is_text_type(file_type: int) -> bool:
    """Check if file type represents a text file."""
    text_types = {
        0x03,  # Pascal text
        0x04,  # ASCII text
        0x0B,  # Word processor
        0x1A,  # AppleWorks word processing
        0xB0,  # Source code
        0xBF,  # Document
    }
    return file_type in text_types


def is_data_type(file_type: int) -> bool:
    """Check if file type represents data/database file."""
    data_types = {
        0x05,  # Pascal data
        0x0A,  # Business BASIC data
        0x10,  # RPS data
        0x19,  # AppleWorks database
        0x1B,  # AppleWorks spreadsheet
        0xFB,  # Integer BASIC variables
        0xFD,  # Applesoft BASIC variables
    }
    return file_type in data_types


def is_graphics_type(file_type: int) -> bool:
    """Check if file type represents graphics/image file."""
    graphics_types = {
        0x08,  # Foto
        0x30,  # Bitmap
        0x31,  # Picture
        0x32,  # Animation
        0x33,  # Palette
        0xCA,  # Icon
        0xD7,  # Color
        0xD8,  # Image
    }
    return file_type in graphics_types


def get_file_category(file_type: int) -> str:
    """Get general category for file type."""
    if is_executable_type(file_type):
        return "Executable"
    elif is_text_type(file_type):
        return "Text"
    elif is_data_type(file_type):
        return "Data"
    elif is_graphics_type(file_type):
        return "Graphics"
    elif file_type in {0x50, 0x51, 0x52, 0xD5, 0xD6}:
        return "Audio"
    elif file_type == 0x0F:
        return "Directory"
    elif file_type in {0xB4, 0xB6, 0xB7, 0xB8, 0xB9, 0xBA, 0xBB, 0xBC, 0xBD}:
        return "System"
    else:
        return "Other"
