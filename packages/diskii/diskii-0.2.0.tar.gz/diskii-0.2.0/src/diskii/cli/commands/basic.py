"""BASIC command implementation."""

import argparse
import sys
from pathlib import Path
from typing import List

from ...detection import open_disk_image
from ...exceptions import DiskiiError
from ...basic import (
    BasicTokenizer as BasicTokenizerFactory, 
    BasicDetokenizer as BasicDetokenizerFactory, 
    BasicSyntaxValidator as BasicSyntaxValidatorFactory
)
from ..utils import print_success, print_error, print_warning


def run_basic(args: argparse.Namespace) -> None:
    """Run the basic command."""
    if not args.basic_command:
        print_error("No BASIC subcommand specified")
        sys.exit(1)
    
    if args.basic_command == "tokenize":
        _run_tokenize(args)
    elif args.basic_command == "detokenize":
        _run_detokenize(args)
    elif args.basic_command == "validate":
        _run_validate(args)
    elif args.basic_command == "extract":
        _run_extract_basic(args)
    else:
        print_error(f"Unknown BASIC command: {args.basic_command}")
        sys.exit(1)


def _run_tokenize(args: argparse.Namespace) -> None:
    """Run the tokenize subcommand."""
    # Read input
    if args.input == '-':
        text = sys.stdin.read()
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            raise DiskiiError(f"Input file not found: {input_path}")
        text = input_path.read_text(encoding='utf-8')
    
    # Tokenize
    try:
        tokenizer = BasicTokenizerFactory(args.variant)
        tokens = tokenizer.tokenize(text)
        
        # Output
        if args.output:
            output_path = Path(args.output)
            output_path.write_bytes(tokens)
            print_success(f"Tokenized {len(text)} chars -> {len(tokens)} bytes: {output_path}")
        else:
            # Output as hex dump to stdout
            print(_format_hex_dump(tokens))
    
    except Exception as e:
        raise DiskiiError(f"Tokenization failed: {e}") from e


def _run_detokenize(args: argparse.Namespace) -> None:
    """Run the detokenize subcommand."""
    input_path = Path(args.input)
    if not input_path.exists():
        raise DiskiiError(f"Input file not found: {input_path}")
    
    # Read tokenized data
    tokens = input_path.read_bytes()
    
    # Detokenize
    try:
        detokenizer = BasicDetokenizerFactory(args.variant)
        text = detokenizer.detokenize_program(tokens)
        
        # Output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(text, encoding='utf-8')
            print_success(f"Detokenized {len(tokens)} bytes -> {len(text)} chars: {output_path}")
        else:
            print(text)
    
    except Exception as e:
        raise DiskiiError(f"Detokenization failed: {e}") from e


def _run_validate(args: argparse.Namespace) -> None:
    """Run the validate subcommand."""
    input_path = Path(args.input)
    if not input_path.exists():
        raise DiskiiError(f"Input file not found: {input_path}")
    
    text = input_path.read_text(encoding='utf-8')
    
    # Validate
    try:
        validator = BasicSyntaxValidatorFactory(args.variant)
        errors = validator.validate(text)
        
        if not errors:
            print_success(f"BASIC syntax is valid ({args.variant})")
        else:
            print_error(f"Found {len(errors)} syntax error(s):")
            for error in errors:
                print(f"  Line {error.line}: {error.message}")
                if error.suggestion:
                    print(f"    Suggestion: {error.suggestion}")
            sys.exit(1)
    
    except Exception as e:
        raise DiskiiError(f"Validation failed: {e}") from e


def _run_extract_basic(args: argparse.Namespace) -> None:
    """Run the extract subcommand."""
    image_path = Path(args.image)
    if not image_path.exists():
        raise DiskiiError(f"Image file not found: {image_path}")
    
    output_dir = args.output_dir or Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open_disk_image(image_path) as image:
        files = image.get_file_list()
        
        # Filter to BASIC files
        basic_files = _find_basic_files(files)
        
        if not basic_files:
            print("No BASIC files found in image")
            return
        
        # Filter by requested files if specified
        if args.files:
            requested_files = [name.upper() for name in args.files]
            basic_files = [f for f in basic_files if f.filename.upper() in requested_files]
            
            if not basic_files:
                print_error("No matching BASIC files found")
                return
        
        print(f"Extracting {len(basic_files)} BASIC file(s) to {output_dir}")
        
        extracted_count = 0
        for file_entry in basic_files:
            try:
                _extract_basic_file(file_entry, output_dir)
                extracted_count += 1
                print_success(f"Extracted {file_entry.filename}")
            except Exception as e:
                print_error(f"Failed to extract {file_entry.filename}: {e}")
        
        print(f"\nExtracted {extracted_count} of {len(basic_files)} BASIC files")


def _find_basic_files(files) -> List:
    """Find BASIC files in the file list."""
    basic_files = []
    
    for file_entry in files:
        is_basic = False
        
        # Check ProDOS file types
        if hasattr(file_entry, 'file_type') and isinstance(file_entry.file_type, int):
            if file_entry.file_type in [0xFC, 0xFA]:  # Applesoft, Integer BASIC
                is_basic = True
        
        # Check DOS file types
        elif hasattr(file_entry, 'file_type') and isinstance(file_entry.file_type, str):
            if file_entry.file_type in ['A', 'I']:  # Applesoft, Integer BASIC
                is_basic = True
        
        if is_basic:
            basic_files.append(file_entry)
    
    return basic_files


def _extract_basic_file(file_entry, output_dir: Path) -> None:
    """Extract and detokenize a single BASIC file."""
    # Determine BASIC variant
    variant = "applesoft"
    if hasattr(file_entry, 'file_type'):
        if (isinstance(file_entry.file_type, int) and file_entry.file_type == 0xFA) or \
           (isinstance(file_entry.file_type, str) and file_entry.file_type == 'I'):
            variant = "integer"
    
    # Read and detokenize
    tokens = file_entry.read_data()
    detokenizer = BasicDetokenizerFactory(variant)
    text = detokenizer.detokenize_program(tokens)
    
    # Write to file
    output_name = file_entry.filename.replace('/', '_')  # Handle ProDOS subdirs
    output_path = output_dir / f"{output_name}.bas"
    output_path.write_text(text, encoding='utf-8')


def _format_hex_dump(data: bytes) -> str:
    """Format binary data as a hex dump."""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        lines.append(f"{i:08X}  {hex_part:<48} |{ascii_part}|")
    return '\n'.join(lines)