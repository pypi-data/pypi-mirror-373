"""Common base classes and utilities for BASIC syntax validation."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set, Tuple

from .tokens import BasicTokenTable


class BASICError(Exception):
    """Base exception for BASIC syntax validation errors."""
    pass


class SyntaxError(BASICError):
    """SYNTAX ERROR - malformed statement structure."""
    pass


class IllegalQuantityError(BASICError):
    """ILLEGAL QUANTITY - invalid numbers or ranges."""
    pass


class BadSubscriptError(BASICError):
    """BAD SUBSCRIPT - array bounds violations."""
    pass


class UndefinedStatementError(BASICError):
    """UNDEF'D STATEMENT - invalid line references."""
    pass


@dataclass
class SyntaxErrorInfo:
    """Information about a syntax validation error."""
    error_type: str
    message: str
    line_number: Optional[int] = None
    character_position: Optional[int] = None
    context: Optional[str] = None


class TokenType(Enum):
    """Token types for syntax validation."""
    KEYWORD = "keyword"
    OPERATOR = "operator"
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    LINE_NUMBER = "line_number"
    SEPARATOR = "separator"
    STRING = "string"
    COMMENT = "comment"


@dataclass
class Token:
    """Represents a parsed token with position information."""
    type: TokenType
    value: str
    position: int
    line: int
    token_id: Optional[int] = None


class BaseSyntaxValidator:
    """Base class for BASIC syntax validators."""
    
    def __init__(self, variant: str):
        """Initialize base validator.
        
        Args:
            variant: BASIC variant ("applesoft" or "integer")
        """
        self.variant = variant.lower()
        self.token_table = BasicTokenTable(variant)
        
        # Common validation patterns
        self._line_number_pattern = re.compile(r"^(\d+)")
        self._identifier_pattern = re.compile(r"^[A-Z][A-Z0-9]*\$?")
        self._string_pattern = re.compile(r'^"([^"]*)"')
        self._number_pattern = re.compile(r"^(\d+(?:\.\d*)?)")
    
    def validate_program(self, text: str) -> List[SyntaxErrorInfo]:
        """Validate entire BASIC program syntax.

        Args:
            text: Plain text BASIC program

        Returns:
            List of syntax errors found (empty if valid)
        """
        errors = []
        
        if not text.strip():
            return errors
            
        lines = self._parse_lines(text)

        # Track program structure for validation
        line_numbers = set()
        goto_references = set()
        gosub_references = set()
        for_stack = []

        for line_num, line_content in lines:
            try:
                # Validate individual line
                line_errors = self.validate_line(line_num, line_content)
                errors.extend(line_errors)

                # Track program structure
                line_numbers.add(line_num)

                # Extract GOTO/GOSUB references for validation
                goto_refs = self._extract_line_references(
                    line_content, ["GOTO", "GOSUB"]
                )
                goto_references.update(goto_refs)
                gosub_references.update(goto_refs)

                # Track FOR/NEXT nesting
                for_info = self._extract_for_next_info(line_content)
                if for_info:
                    for_stack.append((line_num, for_info))

            except Exception as e:
                errors.append(
                    SyntaxErrorInfo(
                        error_type="SYNTAX_ERROR", message=str(e), line_number=line_num
                    )
                )

        # Validate program structure
        structure_errors = self._validate_program_structure(
            line_numbers, goto_references, gosub_references, for_stack
        )
        errors.extend(structure_errors)

        # ROM-specific program-level validations
        rom_memory_errors = self._validate_rom_memory_limits(text)
        errors.extend(rom_memory_errors)

        rom_line_errors = self._validate_rom_line_limits(lines)
        errors.extend(rom_line_errors)

        # Apply ROM error precedence rules
        errors = self._apply_rom_error_precedence(errors)

        return errors
    
    def validate_line(self, line_num: int, content: str) -> List[SyntaxErrorInfo]:
        """Validate a single line of BASIC code.
        
        Args:
            line_num: Line number
            content: Line content (without line number)
            
        Returns:
            List of syntax errors found
        """
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement validate_line")
    
    def _parse_lines(self, text: str) -> List[Tuple[int, str]]:
        """Parse program text into lines with line numbers.

        Args:
            text: Complete program text

        Returns:
            List of (line_number, content) tuples
        """
        lines = []

        for line_text in text.strip().split("\n"):
            line_text = line_text.strip()
            if not line_text:
                continue

            # Extract line number
            match = self._line_number_pattern.match(line_text)
            if match:
                line_num = int(match.group(1))
                content = line_text[match.end() :].strip()

                # Validate line number range
                if not (1 <= line_num <= 63999):
                    raise IllegalQuantityError(
                        f"Line number {line_num} out of range (1-63999)"
                    )

                lines.append((line_num, content))
            else:
                # Line without line number - this is a syntax error in stored programs
                raise SyntaxError("Missing line number")

        return lines
    
    def _tokenize_line_for_validation(self, content: str) -> List[Token]:
        """Tokenize a line for syntax validation purposes.

        Args:
            content: Line content to tokenize

        Returns:
            List of tokens with position information
        """
        tokens = []
        position = 0

        # Skip leading whitespace
        while position < len(content) and content[position].isspace():
            position += 1

        while position < len(content):
            # Try to match different token types
            token = None

            # String literals
            if content[position] == '"':
                match = self._string_pattern.match(content[position:])
                if match:
                    token = Token(
                        type=TokenType.STRING,
                        value=match.group(0),
                        position=position,
                        line=0,  # Line number filled in by caller
                    )
                    position += len(match.group(0))
                else:
                    # Unclosed string
                    raise SyntaxError("Unterminated string literal")

            # Numbers
            elif content[position].isdigit():
                match = self._number_pattern.match(content[position:])
                if match:
                    token = Token(
                        type=TokenType.LITERAL,
                        value=match.group(0),
                        position=position,
                        line=0,
                    )
                    position += len(match.group(0))

            # Identifiers and keywords
            elif content[position].isalpha():
                # Extract the word
                start = position
                while position < len(content) and (
                    content[position].isalnum() or content[position] in "$="
                ):
                    position += 1

                word = content[start:position].upper()

                # This method will be overridden by subclasses to check reserved words
                if self._is_reserved_word(word):
                    token_id = self.token_table.get_token(word)
                    token = Token(
                        type=TokenType.KEYWORD,
                        value=word,
                        position=start,
                        line=0,
                        token_id=token_id,
                    )
                else:
                    token = Token(
                        type=TokenType.IDENTIFIER, value=word, position=start, line=0
                    )

            # Operators and separators
            elif content[position] in "+-*/^=<>(),:;":
                # Handle multi-character operators
                if position + 1 < len(content):
                    two_char = content[position : position + 2]
                    if two_char in [">=", "<=", "<>"]:
                        token = Token(
                            type=TokenType.OPERATOR,
                            value=two_char,
                            position=position,
                            line=0,
                        )
                        position += 2
                    else:
                        token = Token(
                            type=TokenType.OPERATOR
                            if content[position] in "+-*/^=<>()"
                            else TokenType.SEPARATOR,
                            value=content[position],
                            position=position,
                            line=0,
                        )
                        position += 1
                else:
                    token = Token(
                        type=TokenType.OPERATOR
                        if content[position] in "+-*/^=<>()"
                        else TokenType.SEPARATOR,
                        value=content[position],
                        position=position,
                        line=0,
                    )
                    position += 1

            # Skip whitespace
            elif content[position].isspace():
                position += 1
                continue

            # Unknown character
            else:
                raise SyntaxError(f"Unexpected character: {content[position]}")

            if token:
                tokens.append(token)

        return tokens
    
    def _is_reserved_word(self, word: str) -> bool:
        """Check if a word is a reserved word. Should be overridden by subclasses."""
        return False
    
    def _validate_program_structure(
        self,
        line_numbers: Set[int],
        goto_refs: Set[int],
        gosub_refs: Set[int],
        for_stack: List[Tuple[int, str]],
    ) -> List[SyntaxErrorInfo]:
        """Validate overall program structure."""
        errors = []

        # Check for undefined line references
        for ref in goto_refs.union(gosub_refs):
            if ref not in line_numbers:
                errors.append(
                    SyntaxErrorInfo(
                        error_type="UNDEF_STATEMENT",
                        message=f"Undefined line number: {ref}",
                    )
                )

        # Validate FOR/NEXT nesting (proper stack-based validation)
        for_count = sum(1 for _, info in for_stack if info == "FOR")
        next_count = sum(1 for _, info in for_stack if info == "NEXT")

        if for_count != next_count:
            errors.append(
                SyntaxErrorInfo(
                    error_type="SYNTAX_ERROR", message="Unmatched FOR/NEXT statements"
                )
            )
        
        # Additional validation: Check proper nesting order
        # FOR/NEXT should follow LIFO (last-in, first-out) order
        for_variables = []
        
        for line_num, info in for_stack:
            if info == "FOR":
                # Extract variable name from FOR statement 
                # This is simplified - in real implementation we'd parse the actual variable
                for_variables.append((line_num, f"VAR_{line_num}"))
            elif info == "NEXT":
                if not for_variables:
                    errors.append(
                        SyntaxErrorInfo(
                            error_type="SYNTAX_ERROR",
                            message=f"NEXT without FOR at line {line_num}"
                        )
                    )
                else:
                    # Pop the most recent FOR - this is proper nesting
                    for_variables.pop()
        
        # Check for any remaining unmatched FOR statements
        if for_variables:
            for line_num, var in for_variables:
                errors.append(
                    SyntaxErrorInfo(
                        error_type="SYNTAX_ERROR",
                        message=f"FOR without NEXT at line {line_num}"
                    )
                )

        return errors
    
    def _extract_line_references(self, content: str, commands: List[str]) -> Set[int]:
        """Extract line number references from content.
        
        Args:
            content: Line content to analyze
            commands: Commands that reference line numbers
            
        Returns:
            Set of referenced line numbers
        """
        refs = set()
        content_upper = content.upper()
        
        for command in commands:
            # Look for pattern: COMMAND followed by number
            pattern = rf'\b{command}\s+(\d+)'
            matches = re.finditer(pattern, content_upper)
            for match in matches:
                try:
                    line_ref = int(match.group(1))
                    refs.add(line_ref)
                except ValueError:
                    continue
                    
        return refs
    
    def _extract_for_next_info(self, content: str) -> Optional[str]:
        """Extract FOR/NEXT loop information for nesting validation."""
        content_upper = content.upper()

        # Don't count FOR/NEXT keywords inside REM statements
        if content_upper.strip().startswith("REM"):
            return None

        if content_upper.startswith("FOR ") or " FOR " in content_upper:
            return "FOR"
        elif content_upper.startswith("NEXT") or " NEXT" in content_upper:
            return "NEXT"

        return None
    
    def _validate_rom_memory_limits(self, program: str) -> List[SyntaxErrorInfo]:
        """Validate program against ROM memory limits."""
        errors = []

        # ROM memory limits
        if self.variant == "integer":
            # Integer BASIC: roughly 28K available for programs
            max_program_size = 28 * 1024
        else:
            # Applesoft BASIC: roughly 38K available for programs
            max_program_size = 38 * 1024

        if len(program.encode("utf-8")) > max_program_size:
            errors.append(
                SyntaxErrorInfo(
                    error_type="MEM_FULL",
                    message=self._get_rom_error_message("MEM_FULL"),
                )
            )

        return errors

    def _validate_rom_line_limits(self, lines: List[Tuple[int, str]]) -> List[SyntaxErrorInfo]:
        """Validate program against ROM line limits."""
        errors = []

        # ROM line length limits
        max_line_length = 255 if self.variant == "applesoft" else 127

        for line_num, line_content in lines:
            if len(line_content) > max_line_length:
                errors.append(
                    SyntaxErrorInfo(
                        error_type="STRING_TOO_LONG",
                        message=self._get_rom_error_message(
                            "STRING_TOO_LONG", f"AT LINE {line_num}"
                        ),
                        line_number=line_num,
                    )
                )

        return errors
    
    def _apply_rom_error_precedence(self, errors: List[SyntaxErrorInfo]) -> List[SyntaxErrorInfo]:
        """Apply ROM-accurate error precedence rules."""
        if not errors:
            return errors

        # Default error precedence (subclasses should override)
        error_precedence = [
            "BAD_SUBSCRIPT",  # Array bounds checked first
            "UNDEF_STATEMENT",  # Line number validation
            "ILLEGAL_QUANTITY",  # Number/range validation
            "SYNTAX_ERROR",  # General syntax issues last
        ]

        # Group errors by type for precedence sorting
        error_groups = {}
        for error in errors:
            error_type = error.error_type
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)

        # Apply precedence order (highest priority first)
        sorted_errors = []
        for error_type in error_precedence:
            if error_type in error_groups:
                sorted_errors.extend(error_groups[error_type])

        # Add any unrecognized error types at the end
        for error_type, error_list in error_groups.items():
            if error_type not in error_precedence:
                sorted_errors.extend(error_list)

        return sorted_errors
    
    def _get_rom_error_message(self, error_type: str, context: str = "") -> str:
        """Get ROM-accurate error message for error type."""

        # ROM-accurate error messages per Apple II BASIC specification
        rom_messages = {
            # Integer BASIC ROM error messages
            "BAD_SUBSCRIPT": "BAD SUBSCRIPT",
            "UNDEF_STATEMENT": "UNDEF'D STATEMENT",
            "ILLEGAL_QUANTITY": "ILLEGAL QUANTITY",
            "SYNTAX_ERROR": "SYNTAX ERROR",
            "MEM_FULL": "MEM FULL",
            "NEXT_WITHOUT_FOR": "NEXT WITHOUT FOR",
            "TYPE_MISMATCH": "TYPE MISMATCH",
            "STRING_TOO_LONG": "STRING TOO LONG",
            "DIV_BY_ZERO": "DIV BY ZERO",
            "RANGE_ERROR": "RANGE ERR",
            # Applesoft BASIC ROM error messages (slightly different)
            "OUT_OF_MEMORY": "OUT OF MEMORY",
            "OVERFLOW": "OVERFLOW",
            "OUT_OF_DATA": "OUT OF DATA",
            "FORMULA_TOO_COMPLEX": "FORMULA TOO COMPLEX",
            "CAN_T_CONTINUE": "CAN'T CONTINUE",
            "RETURN_WITHOUT_GOSUB": "RETURN WITHOUT GOSUB",
        }

        base_message = rom_messages.get(error_type, error_type)

        # Add context if provided
        if context:
            return f"{base_message} {context}"
        else:
            return base_message