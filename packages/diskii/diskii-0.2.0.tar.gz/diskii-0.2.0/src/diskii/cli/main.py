#!/usr/bin/env python3
"""Main entry point for diskii command line interface."""

import sys
import argparse
from pathlib import Path
from typing import NoReturn

from ..exceptions import DiskiiError


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="diskii",
        description="Apple II disk image manipulation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  diskii info mydisk.dsk                  # Show disk information
  diskii extract mydisk.po                # Extract all files
  diskii extract mydisk.dsk HELLO.BAS     # Extract specific file
  diskii add mydisk.po myfile.txt         # Add file to disk
  diskii create blank.po --name MYDISK    # Create blank ProDOS disk
  diskii convert mydisk.dsk output.po     # Convert DOS-ordered to ProDOS-ordered
  diskii basic detokenize HELLO.BAS       # Detokenize BASIC program

For more help on a specific command, use: diskii <command> --help"""
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="<command>"
    )
    
    # info command
    info_parser = subparsers.add_parser(
        "info", 
        help="Show disk image information",
        description="Display information about a disk image including format, files, and free space."
    )
    info_parser.add_argument("image", help="Disk image file")
    info_parser.add_argument(
        "--detailed", "-d", 
        action="store_true",
        help="Show detailed file metadata"
    )
    info_parser.add_argument(
        "--tree", "-t",
        action="store_true", 
        help="Show files in tree format"
    )
    
    # extract command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract files from disk image", 
        description="Extract one or more files from a disk image to the local filesystem."
    )
    extract_parser.add_argument("image", help="Disk image file")
    extract_parser.add_argument(
        "files", 
        nargs="*",
        help="Files to extract (default: all files)"
    )
    extract_parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        help="Output directory (default: current directory)"
    )
    extract_parser.add_argument(
        "--convert", "-c",
        action="store_true",
        help="Auto-convert BASIC programs to text"
    )
    extract_parser.add_argument(
        "--preserve-types",
        action="store_true",
        help="Preserve Apple II file type information"
    )
    
    # add command
    add_parser = subparsers.add_parser(
        "add",
        help="Add files to disk image",
        description="Add one or more files to a disk image."
    )
    add_parser.add_argument("image", help="Disk image file")
    add_parser.add_argument("files", nargs="+", help="Files to add")
    add_parser.add_argument(
        "--type", 
        help="Override file type detection (e.g., TXT, BIN, BAS)"
    )
    add_parser.add_argument(
        "--backup", "-b",
        action="store_true", 
        help="Create backup before writing"
    )
    
    # create command
    create_parser = subparsers.add_parser(
        "create", 
        help="Create blank disk image",
        description="Create a new blank disk image."
    )
    create_parser.add_argument("image", help="Output disk image file")
    create_parser.add_argument(
        "--format", 
        choices=["prodos", "dos33", "dos32"],
        help="Disk format (auto-detected from extension if not specified)"
    )
    create_parser.add_argument(
        "--size",
        help="Disk size (e.g., 140K, 800K, 32M)"
    )
    create_parser.add_argument(
        "--name",
        help="Volume name"
    )
    
    # convert command  
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert between sector orderings",
        description="Convert a disk image between different sector orderings without changing the filesystem. "
                   "Common conversions: .dsk (DOS-ordered) ↔ .po (ProDOS-ordered), .do ↔ .po, .dsk ↔ .hdv. "
                   "The filesystem and all files remain unchanged - only the physical sector arrangement is converted."
    )
    convert_parser.add_argument("source", help="Source disk image (.dsk, .do, .po, .hdv, .d13)")
    convert_parser.add_argument("dest", help="Destination disk image (sector ordering determined by extension)")
    convert_parser.add_argument(
        "--backup", "-b",
        action="store_true",
        help="Create backup of source before conversion"
    )
    
    # basic command
    basic_parser = subparsers.add_parser(
        "basic",
        help="BASIC program utilities",
        description="Utilities for working with Apple II BASIC programs."
    )
    basic_subparsers = basic_parser.add_subparsers(
        dest="basic_command",
        help="BASIC operations"
    )
    
    # basic tokenize
    tokenize_parser = basic_subparsers.add_parser(
        "tokenize",
        help="Convert BASIC text to tokens"
    )
    tokenize_parser.add_argument("input", help="Text file or '-' for stdin")
    tokenize_parser.add_argument(
        "--variant", 
        choices=["applesoft", "integer"],
        default="applesoft",
        help="BASIC variant"
    )
    tokenize_parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout as hex)"
    )
    
    # basic detokenize
    detokenize_parser = basic_subparsers.add_parser(
        "detokenize", 
        help="Convert BASIC tokens to text"
    )
    detokenize_parser.add_argument("input", help="Tokenized file")
    detokenize_parser.add_argument(
        "--variant",
        choices=["applesoft", "integer"], 
        default="applesoft",
        help="BASIC variant"
    )
    detokenize_parser.add_argument(
        "--output", "-o",
        help="Output text file (default: stdout)"
    )
    
    # basic validate
    validate_parser = basic_subparsers.add_parser(
        "validate",
        help="Validate BASIC syntax"
    )
    validate_parser.add_argument("input", help="BASIC text file")
    validate_parser.add_argument(
        "--variant",
        choices=["applesoft", "integer"],
        default="applesoft", 
        help="BASIC variant"
    )
    
    # basic extract
    extract_basic_parser = basic_subparsers.add_parser(
        "extract",
        help="Extract and detokenize BASIC files from disk"
    )
    extract_basic_parser.add_argument("image", help="Disk image file")
    extract_basic_parser.add_argument(
        "files",
        nargs="*", 
        help="BASIC files to extract (default: all BASIC files)"
    )
    extract_basic_parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        help="Output directory"
    )
    
    return parser


def main() -> NoReturn:
    """Main entry point for the diskii CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Import commands dynamically to avoid circular imports
        if args.command == "info":
            from .commands.info import run_info
            run_info(args)
        elif args.command == "extract":
            from .commands.extract import run_extract
            run_extract(args)
        elif args.command == "add":
            from .commands.add import run_add
            run_add(args)
        elif args.command == "create":
            from .commands.create import run_create
            run_create(args)
        elif args.command == "convert":
            from .commands.convert import run_convert
            run_convert(args)
        elif args.command == "basic":
            from .commands.basic import run_basic
            run_basic(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)
            
    except DiskiiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()