# diskii - Apple II Disk Image Tool & Library

**diskii** is both a command-line utility and Python library for reading, writing, and manipulating Apple II disk images. It supports both DOS 3.3 and ProDOS filesystems across various image formats.

## Features

### ✅ **Disk Image Reading**
- **Complete DOS 3.3 support**: Read catalogs, extract files, handle all file types (T/I/A/B/S/R)
- **Full ProDOS support**: Volume directories, subdirectories, all storage types (seedling/sapling/tree)  
- **DOS 3.2 support**: Read 13-sector disk images (.d13 format)
- **Multiple image formats**: .dsk, .do, .po, .hdv, .d13
- **Automatic format detection**: Smart detection based on file extension and content analysis

### ✅ **File Operations**
- **File extraction**: Read any file from disk images to host filesystem
- **File writing**: Create new files on disk images with proper metadata
- **File type preservation**: Maintain Apple II file types and auxiliary information
- **Cross-format operations**: Copy files between DOS 3.3 and ProDOS images

### ✅ **Disk Image Creation**
- **Blank disk creation**: Create empty DOS 3.3, DOS 3.2, and ProDOS images
- **Multiple sizes supported**: Standard 140K disks up to 32MB ProDOS volumes
- **Proper filesystem initialization**: Correct VTOC, catalogs, and volume bitmaps

### ✅ **Advanced Features** 
- **Hierarchical directory support**: Full ProDOS subdirectory navigation
- **Sparse file handling**: Efficient handling of ProDOS sparse files
- **Free space tracking**: Volume bitmap and VTOC management
- **BASIC (de)tokenization**: Convert between tokenized and text BASIC programs
- **BASIC syntax validation**: ROM-compliant syntax checking for Apple II BASIC programs
- **Robust error handling**: Graceful handling of corrupted or invalid images
- **Type-safe**: Full type annotations throughout
- **Comprehensive testing**: Extensive test suite with real disk images

## Installation

```bash
pip install diskii
```

Or with Poetry:

```bash
poetry add diskii
```

## Command Line Usage

diskii provides a comprehensive command-line interface for disk image manipulation:

```bash
# Show disk information
diskii info mydisk.dsk

# Extract all files from a disk
diskii extract mydisk.po

# Extract specific files
diskii extract mydisk.dsk HELLO.BAS

# Add files to a disk
diskii add mydisk.po myfile.txt

# Create blank disk images
diskii create blank.po --name MYDISK

# Convert between sector orderings
diskii convert mydisk.dsk output.po

# BASIC program utilities
diskii basic detokenize HELLO.BAS
diskii basic tokenize myprogram.txt --variant applesoft
diskii basic validate myprogram.txt
```

For detailed help on any command:
```bash
diskii --help
diskii <command> --help
```

## Python Library Usage

```python
import diskii

# Open any disk image - format detected automatically
with diskii.open_disk_image("mydisk.dsk") as image:
    # Get volume information
    print(f"Volume: {image.get_volume_name()}")
    print(f"Format: {image.format}")
    
    # List all files
    files = image.get_file_list()
    for file_entry in files:
        print(f"{file_entry.filename} ({file_entry.size} bytes)")
        
        # Extract file
        data = file_entry.read_data()
        with open(file_entry.filename, 'wb') as f:
            f.write(data)

# Create a new blank disk
diskii.disk_creator.create_blank_prodos_image("new_disk.po", "MY.DISK")

# Add files to existing disk (requires read_only=False)
with diskii.open_disk_image("mydisk.po", read_only=False) as image:
    image.create_file("HELLO.TXT", 0x04, b"Hello from diskii!")

# BASIC program tokenization
import diskii

# Tokenize Applesoft BASIC program
program_text = '''10 HOME
20 PRINT "HELLO WORLD!"
30 END'''

tokenized = diskii.tokenize_applesoft(program_text)
detokenized = diskii.detokenize_applesoft(tokenized)

# Work with BASIC files on disk images
with diskii.open_disk_image("mydisk.po", read_only=False) as image:
    # Save as tokenized BASIC program
    image.create_file("HELLO.BAS", 0xFC, tokenized)
    
    # Read BASIC file and detokenize automatically
    files = image.get_file_list()
    for file_entry in files:
        if file_entry.is_basic_file():
            plain_text = file_entry.read_as_text()  # Auto-detokenizes
            raw_tokens = file_entry.read_as_tokens()  # Raw tokenized data

# BASIC syntax validation with ROM compliance
program_text = '''10 HOME
20 FOR I = 1 TO 10
30 PRINT "COUNT: "; I
40 NEXT I
50 END'''

# Validate Applesoft BASIC syntax
errors = diskii.validate_basic_syntax(program_text, "applesoft")
if not errors:
    print("✅ Program syntax is valid!")
else:
    for error in errors:
        print(f"Line {error.line}: {error.message}")

# Advanced syntax validation with custom validator
validator = diskii.BASICSyntaxValidator("applesoft")
errors = validator.validate_program(program_text)

# Validate Integer BASIC programs
integer_program = '''10 HOME
20 FOR I = 1 TO 10
30 PRINT "COUNT: "; I
40 NEXT I
50 END'''

# Also test Integer BASIC tokenization functions
tokenized_integer = diskii.tokenize_integer_basic(integer_program)
detokenized_integer = diskii.detokenize_integer_basic(tokenized_integer)

errors = diskii.validate_basic_syntax(integer_program, "integer")
```

## Supported Formats

| Extension | Description | Sector Ordering | Supported Filesystems |
|-----------|-------------|----------------|----------------------|
| `.dsk` | DOS order disk images (140KB) | DOS order | DOS 3.3, ProDOS |
| `.do` | DOS order disk images | DOS order | DOS 3.3, ProDOS |
| `.po` | ProDOS order disk images | ProDOS order | DOS 3.3, ProDOS |
| `.hdv` | ProDOS hard disk volumes (up to 32MB) | ProDOS order | ProDOS |
| `.d13` | DOS 3.2 13-sector images | DOS 3.2 order | DOS 3.2, ProDOS* |

*ProDOS on 13-sector images is theoretically possible but extremely rare in practice.

## Error Handling

diskii provides comprehensive error handling:

```python
try:
    with diskii.open_disk_image("questionable.dsk") as image:
        files = image.get_file_list()
except diskii.UnrecognizedFormatError:
    print("Not a valid disk image")
except diskii.CorruptedImageError:
    print("Image appears to be corrupted")
except diskii.AccessError:
    print("Cannot access the image file")
```

## Examples

The `examples/` directory contains practical usage examples:

- **`directory_tree.py`**: Display disk contents in tree format
- **`file_info.py`**: Show detailed file metadata and type information  
- **`create_files.py`**: Demonstrate creating files on disk images
- **`cross_format_copy.py`**: Copy files between ProDOS and DOS formats
- **`basic_tokenization.py`**: BASIC program tokenization and detokenization examples

## Requirements

- Python 3.13+
- No external dependencies for core functionality

## Development

```bash
# Install with development dependencies
poetry install --with dev,docs

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/diskii

# Format code
poetry run ruff format src/ tests/

# Type checking  
poetry run mypy src/

# Build documentation
cd docs && make html
```

## Planned Features

- **Advanced copy operations**: Batch file operations with progress reporting
- **CLI interface**: Command-line tools for disk manipulation

## Not Planned (Pull Requests Welcome)

- WOZ image format support
- 2MG image format support  
- NIB image format support
- Pascal or CP/M filesystem support

## References

- [ProDOS Technical Reference](https://prodos8.com/docs/techref/file-organization/)
- [ProDOS Format Notes](https://ciderpress2.com/formatdoc/ProDOS-notes.html)
- [DOS 3.3 Format Notes](https://ciderpress2.com/formatdoc/DOS-notes.html)
- [Disk Image Format Reference](https://ciderpress2.com/formatdoc/Unadorned-notes.html)
- [Applesoft BASIC Tokenized File Format](http://justsolve.archiveteam.org/wiki/Applesoft_BASIC_tokenized_file)
- [Applesoft BASIC Programming Reference Manual](https://mirrors.apple2.org.za/ftp.apple.asimov.net/documentation/programming/basic/Applesoft%20BASIC%20Programming%20Reference%20Manual%20-%20Apple%20Computer.pdf)
- [BASIC Keywords and Tokens Reference](http://mirrors.apple2.org.za/apple.cabi.net/Languages.Programming/BASIC.keywords.tokens.txt)
- [Integer BASIC ROM Disassembly](https://6502disassembly.com/a2-rom/IntegerBASIC.html)
- [Applesoft BASIC ROM Disassembly](https://6502disassembly.com/a2-rom/Applesoft.html)

## License

ISC License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.