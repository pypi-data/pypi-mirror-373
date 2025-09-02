"""Common utilities and base classes for Apple II BASIC variants."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
import re
import struct


class BaseTokenizer(ABC):
    """Abstract base class for BASIC tokenizers."""
    
    def __init__(self, variant: str):
        """Initialize tokenizer for specified BASIC variant.
        
        Args:
            variant: Either "applesoft" or "integer"
        """
        self.variant = variant.lower()
        from .tokens import BasicTokenTable
        self.token_table = BasicTokenTable(variant)
    
    @abstractmethod
    def tokenize_program(self, text: str) -> bytes:
        """Convert plain text BASIC program to tokenized format."""
        pass
    
    def _parse_lines(self, text: str) -> List[Tuple[int, str]]:
        """Parse program text into individual lines with line numbers.
        
        Args:
            text: Program text
            
        Returns:
            List of (line_number, line_content) tuples
        """
        lines = []
        
        # Handle line continuation first
        processed_lines = self._handle_line_continuation(text)
        
        for line in processed_lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract line number if present
            match = re.match(r'^(\d+)\s*(.*)', line)
            if match:
                line_num = int(match.group(1))
                line_text = match.group(2)
                lines.append((line_num, line_text))
            else:
                # Immediate mode command (no line number)
                if is_immediate_mode_command(line):
                    lines.append((-1, line))
                # Otherwise skip invalid lines
        
        # Sort by line number, with immediate mode commands (-1) at the end
        return sorted(lines, key=lambda x: (x[0] if x[0] != -1 else float('inf')))
    
    def _handle_line_continuation(self, text: str) -> List[str]:
        """Handle line continuation indicators in BASIC programs.
        
        Args:
            text: Raw program text
            
        Returns:
            List of complete logical lines
        """
        physical_lines = text.splitlines()
        logical_lines = []
        current_line = ""
        
        for physical_line in physical_lines:
            stripped = physical_line.strip()
            if not stripped:
                continue
                
            # Check for continuation
            if self._has_line_continuation(stripped):
                # Remove continuation indicator and append to current line
                continuation_removed = self._remove_continuation_indicator(stripped)
                if current_line:
                    current_line += " " + continuation_removed
                else:
                    current_line = continuation_removed
            else:
                # Complete line
                if current_line:
                    current_line += " " + stripped
                    logical_lines.append(current_line)
                    current_line = ""
                else:
                    logical_lines.append(stripped)
        
        # Handle any remaining continued line
        if current_line:
            logical_lines.append(current_line)
        
        return logical_lines
    
    def _has_line_continuation(self, line: str) -> bool:
        """Check if line has continuation indicator."""
        line = line.strip()
        
        # Always treat backslash and underscore as continuation
        if line.endswith('\\') or line.endswith('_'):
            return True
        
        # Trailing comma suggests continuation
        if line.endswith(','):
            # Don't treat trailing comma as continuation in specific contexts
            line_upper = line.upper()
            
            # PRINT statements: trailing comma has semantic meaning (suppresses newline)
            if 'PRINT ' in line_upper:
                return False  # Keep the comma, it's not continuation
                
            # Other cases: could be continuation
            return True
        
        # Trailing colon - check if it's a complete construct or continuation
        if line.endswith(':'):
            # Check for complete constructs that end with colon
            line_upper = line.upper()
            
            # Complete IF-THEN statements
            if 'IF ' in line_upper and line_upper.endswith(' THEN:'):
                return False  # Complete IF-THEN construct
            
            # Complete FOR-TO statements
            if line_upper.startswith('FOR ') and ' TO ' in line_upper and line_upper.endswith(':'):
                return False  # Complete FOR-TO construct
            
            # Otherwise, colon at end suggests continuation
            return True
        
        return False
    
    def _remove_continuation_indicator(self, line: str) -> str:
        """Remove continuation indicators from line.
        
        Args:
            line: Line with possible continuation indicator
            
        Returns:
            Line with indicator removed
        """
        line = line.rstrip()
        
        # Always remove backslash and underscore continuation indicators
        if line.endswith('\\') or line.endswith('_'):
            return line[:-1].rstrip()
        
        # For commas and colons, only remove if it's likely a continuation indicator
        if line.endswith(',') or line.endswith(':'):
            # Don't remove commas from DATA statements - they're part of the data
            if line.upper().startswith('DATA ') and line.endswith(','):
                return line  # Keep the comma
            # Don't remove colons from specific contexts where they're meaningful
            elif line.endswith(':'):
                # Remove trailing colon as continuation indicator
                return line[:-1].rstrip()
            elif line.endswith(','):
                # Remove trailing comma as continuation indicator
                return line[:-1].rstrip()
        
        return line
    
    def _is_complete_statement(self, line: str) -> bool:
        """Check if line represents a complete BASIC statement."""
        # Remove line number if present
        content = re.sub(r'^\d+\s*', '', line).strip()
        if not content:
            return True
            
        # Check for balanced constructs
        return self._has_balanced_constructs(content)
    
    def _has_balanced_constructs(self, line: str) -> bool:
        """Check if line has balanced quotes, parentheses, etc."""
        quote_count = line.count('"')
        paren_balance = line.count('(') - line.count(')')
        
        return (quote_count % 2 == 0) and (paren_balance == 0)
    
    def _is_complex_expression(self, expression: str) -> bool:
        """Check if an expression is complex (multiple operations, functions, parentheses).
        
        Args:
            expression: Expression string to analyze
            
        Returns:
            True if expression is considered complex
        """
        if not expression or not expression.strip():
            return False
            
        expression = expression.strip()
        
        # Simple variable/number is not complex
        if re.match(r'^[A-Za-z][A-Za-z0-9]*\$?$', expression) or re.match(r'^\d+(\.\d*)?$', expression):
            return False
        
        # Check for function calls (word followed by parenthesis)
        if re.search(r'[A-Za-z]+\s*\(', expression):
            return True
            
        # Check for parentheses (grouping)
        if '(' in expression or ')' in expression:
            return True
            
        # Count operators - more than one operator makes it complex
        operators = ['+', '-', '*', '/', '^', '=', '<', '>', '<=', '>=', '<>']
        operator_count = 0
        
        for op in operators:
            operator_count += expression.count(op)
            
        # Simple binary operation (A + B) is not complex, but A + B * C is
        return operator_count > 1
    
    def _is_immediate_mode_command(self, line: str) -> bool:
        """Check if line is an immediate mode command (no line number).
        
        This is a wrapper around the global is_immediate_mode_command function.
        """
        return is_immediate_mode_command(line)


class BaseDetokenizer(ABC):
    """Abstract base class for BASIC detokenizers."""
    
    def __init__(self, variant: str):
        """Initialize detokenizer for specified BASIC variant.
        
        Args:
            variant: Either "applesoft" or "integer"
        """
        self.variant = variant.lower()
        from .tokens import BasicTokenTable
        self.token_table = BasicTokenTable(variant)
    
    @abstractmethod
    def detokenize_program(self, data: bytes) -> str:
        """Convert tokenized BASIC program to plain text."""
        pass


def is_immediate_mode_command(line: str) -> bool:
    """Check if line is an immediate mode command (no line number)."""
    stripped = line.strip()
    if not stripped:
        return False
        
    # Check if starts with a digit (line number)
    if stripped[0].isdigit():
        return False
        
    # Check for immediate mode commands
    immediate_commands = {
        'RUN', 'LIST', 'NEW', 'SAVE', 'LOAD', 'CATALOG', 'PRINT', 'INPUT',
        'LET', 'HOME', 'TEXT', 'GR', 'HGR', 'CALL', 'POKE', 'PEEK'
    }
    
    first_word = stripped.split()[0].upper()
    if first_word in immediate_commands:
        return True
    
    # Check for shorthand commands
    if stripped[0] == '?':
        # ? is shorthand for PRINT
        return True
    
    # Check for variable assignment (e.g., "X = 10", "A$ = "HELLO"")
    # This is a common immediate mode pattern
    if '=' in stripped:
        # Make sure it looks like an assignment: VARIABLE = VALUE
        parts = stripped.split('=', 1)
        if len(parts) == 2:
            var_part = parts[0].strip()
            # Check if left side looks like a variable name
            if re.match(r'^[A-Za-z][A-Za-z0-9]*\$?$', var_part):
                return True
    
    return False


def normalize_basic_text(text: str) -> str:
    """Normalize BASIC text for comparison."""
    # Remove extra whitespace and normalize case for keywords
    return ' '.join(text.split())


def extract_numeric_literal(text: str, start: int) -> Tuple[str, int]:
    """Extract numeric literal from text starting at position.
    
    Args:
        text: Source text
        start: Starting position
        
    Returns:
        Tuple of (numeric_string, characters_consumed)
    """
    i = start
    has_decimal = False
    has_exponent = False
    
    # Handle negative sign
    if i < len(text) and text[i] == '-':
        i += 1
    
    # Extract digits and decimal point
    while i < len(text):
        char = text[i]
        
        if char.isdigit():
            i += 1
        elif char == '.' and not has_decimal and not has_exponent:
            has_decimal = True
            i += 1
        elif char.upper() == 'E' and not has_exponent and i > start:
            has_exponent = True
            i += 1
            # Handle exponent sign
            if i < len(text) and text[i] in '+-':
                i += 1
        else:
            break
    
    return text[start:i], i - start


def extract_string_literal(text: str, start: int) -> Tuple[str, int]:
    """Extract string literal from text starting at position.
    
    Args:
        text: Source text
        start: Starting position (should point to opening quote)
        
    Returns:
        Tuple of (string_including_quotes, characters_consumed)
    """
    if start >= len(text) or text[start] != '"':
        return "", 0
    
    i = start + 1
    while i < len(text):
        if text[i] == '"':
            # Check for escaped quote
            if i + 1 < len(text) and text[i + 1] == '"':
                i += 2  # Skip escaped quote
            else:
                i += 1  # Include closing quote
                break
        else:
            i += 1
    
    return text[start:i], i - start