"""Integer BASIC tokenizer."""

import re
import struct
from typing import List, Tuple, Optional, Dict, Any

from ..common import BaseTokenizer, is_immediate_mode_command, extract_numeric_literal, extract_string_literal
from ..tokens import get_integer_basic_table


class IntegerTokenizer(BaseTokenizer):
    """Converts plain text Integer BASIC programs to tokenized format."""
    
    def __init__(self):
        """Initialize Integer BASIC tokenizer."""
        super().__init__("integer")
        self.token_table = get_integer_basic_table()
    
    def tokenize(self, text: str) -> bytes:
        """Convert plain text BASIC program to tokenized format.
        
        This is an alias for tokenize_program for CLI compatibility.
        
        Args:
            text: Plain text BASIC program
            
        Returns:
            Tokenized program as bytes
        """
        return self.tokenize_program(text)
    
    def tokenize_program(self, text: str) -> bytes:
        """Convert plain text BASIC program to tokenized format.
        
        Args:
            text: Plain text BASIC program
            
        Returns:
            Tokenized program as bytes
        """
        if not text.strip():
            return b''
        
        lines = self._parse_lines(text)
        if not lines:
            return b''
        
        result = bytearray()
        
        for line_num, line_text in lines:
            tokenized_line = self._tokenize_line(line_num, line_text)
            result.extend(tokenized_line)
        
        # Integer BASIC program terminator (single null byte)
        result.append(0x00)
        
        return bytes(result)
    
    def _tokenize_line(self, line_num: int, line_text: str) -> bytes:
        """Tokenize a single Integer BASIC line.
        
        Args:
            line_num: Line number (-1 for immediate mode)
            line_text: Line content
            
        Returns:
            Tokenized line as bytes
        """
        # Handle immediate mode commands
        if line_num == -1:
            return self._tokenize_immediate_mode(line_text)
        
        line_data = bytearray()
        
        # Integer BASIC format: length byte + line number + content + end-of-line token
        # First, build the content to calculate total length
        tokenized_content = self._tokenize_content(line_text)
        
        # Calculate total line length (line number + content + end token)
        line_length = 2 + len(tokenized_content) + 1  # 2 bytes line num + content + 1 byte end token
        
        # Add line length byte
        line_data.append(line_length)
        
        # Add line number (2 bytes, little-endian)
        line_data.extend(struct.pack('<H', line_num))
        
        # Add tokenized content
        line_data.extend(tokenized_content)
        
        # Add end-of-line token ($01)
        line_data.append(0x01)
        
        return bytes(line_data)
    
    def _tokenize_immediate_mode(self, line_text: str) -> bytes:
        """Tokenize immediate mode command for Integer BASIC.
        
        Args:
            line_text: Command text
            
        Returns:
            Tokenized command
        """
        if not is_immediate_mode_command(line_text):
            # Regular line content without line number
            return self._tokenize_content(line_text) + b'\x01'
        
        # Integer BASIC immediate mode
        return self._tokenize_content(line_text) + b'\x01'
    
    def _tokenize_content(self, content: str) -> bytes:
        """Tokenize the content portion of an Integer BASIC line.
        
        Args:
            content: Line content without line number
            
        Returns:
            Tokenized content as bytes
        """
        result = bytearray()
        i = 0
        
        while i < len(content):
            # Check for string literals (don't tokenize inside quotes)
            if content[i] == '"':
                string_result, consumed = self._parse_string_literal(content, i)
                result.extend(string_result)
                i += consumed
                continue
            
            # Check for numeric literals
            if content[i].isdigit() or (content[i] == '.' and i + 1 < len(content) and content[i + 1].isdigit()):
                number_result, consumed = self._parse_numeric_literal(content, i)
                result.extend(number_result)
                i += consumed
                continue
            
            # Handle unary minus specially
            elif content[i] == '-':
                # Special handling for minus sign - distinguish unary vs binary
                if self._is_unary_minus_context(content, i):
                    # Check if this minus is immediately followed by a digit
                    # If so, let the numeric literal parser handle it
                    if i + 1 < len(content) and content[i + 1].isdigit():
                        # Skip this minus - the numeric parser will handle it
                        pass
                    else:
                        # Unary minus not followed by digit - keep as ASCII
                        result.append(ord('-'))
                else:
                    # Binary minus - tokenize normally
                    token = self.token_table.get_token('-')
                    if token is not None:
                        result.append(token)
                    else:
                        result.append(ord('-'))
                i += 1
                continue
            
            # Check for keywords and operators
            if content[i].isalpha():
                # Find end of word
                word_start = i
                while i < len(content) and (content[i].isalnum() or content[i] in '$#'):
                    i += 1
                
                word = content[word_start:i].upper()
                
                # Enhanced handling for REM statement (Integer BASIC doesn't have DATA)
                if word == 'REM':
                    token = self.token_table.get_token(word)
                    if token is not None:
                        result.append(token)
                    
                    rem_data_result, consumed = self._parse_rem_data_statement(content, i, word)
                    result.extend(rem_data_result)
                    i += consumed
                    continue
                
                # Check if word is a keyword token
                token = self.token_table.get_token(word)
                if token is not None:
                    result.append(token)
                else:
                    # Not a token, store as ASCII
                    result.extend(word.encode('ascii'))
                continue
            
            # Handle multi-character operators
            if i + 1 < len(content):
                two_char = content[i:i+2]
                if two_char in ['>=', '<=', '<>', '**']:
                    # For binary equivalence, preserve original compound operators as individual tokens
                    first_token = self.token_table.get_token(two_char[0])
                    second_token = self.token_table.get_token(two_char[1])
                    
                    if first_token is not None:
                        result.append(first_token)
                    else:
                        result.append(ord(two_char[0]))
                        
                    if second_token is not None:
                        result.append(second_token)
                    else:
                        result.append(ord(two_char[1]))
                    
                    i += 2
                    continue
            
            # Single character operators and punctuation
            char = content[i]
            
            # Special case for Integer BASIC: skip spaces entirely (they get stripped)
            if char == ' ':
                pass  # Skip spaces in Integer BASIC - they don't get tokenized
            else:
                token = self.token_table.get_token(char)
                if token is not None:
                    result.append(token)
                else:
                    result.append(ord(char))
            i += 1
        
        return bytes(result)
    
    def _is_unary_minus_context(self, content: str, minus_pos: int) -> bool:
        """Determine if minus sign is unary (not binary operator)."""
        if minus_pos == 0:
            return True
        
        # Look at the character before the minus
        prev_pos = minus_pos - 1
        while prev_pos >= 0 and content[prev_pos].isspace():
            prev_pos -= 1
        
        if prev_pos < 0:
            return True
        
        prev_char = content[prev_pos]
        
        # Unary minus contexts: after operators, opening parenthesis, comma, etc.
        unary_contexts = {'(', ',', '=', '<', '>', '+', '-', '*', '/', '^', ';', ':'}
        return prev_char in unary_contexts
    
    def _parse_string_literal(self, content: str, start: int) -> Tuple[bytes, int]:
        """Parse string literal in Integer BASIC format.
        
        Args:
            content: Full line content
            start: Starting position of quote
            
        Returns:
            Tuple of (tokenized_string, bytes_consumed)
        """
        string_text, consumed = extract_string_literal(content, start)
        
        # Integer BASIC: string stored with special encoding
        # Format: $28 + high-bit ASCII chars + $29
        result = bytearray()
        result.append(0x28)  # String start token
        
        # Convert string content to high-bit ASCII
        if len(string_text) >= 2:  # Has quotes
            content_text = string_text[1:-1]  # Remove quotes
            for char in content_text:
                result.append(ord(char) | 0x80)  # Set high bit
        
        result.append(0x29)  # String end token
        
        return bytes(result), consumed
    
    def _parse_numeric_literal(self, content: str, start: int) -> Tuple[bytes, int]:
        """Parse numeric literal in Integer BASIC format.
        
        Args:
            content: Full line content
            start: Starting position of number
            
        Returns:
            Tuple of (tokenized_number, bytes_consumed)
        """
        number_str, consumed = extract_numeric_literal(content, start)
        
        # Try to parse as integer for special encoding
        try:
            # Handle negative numbers
            if number_str.startswith('-'):
                value = int(number_str)
            else:
                value = int(number_str)
            
            # Integer BASIC: integers stored in special format
            if -32768 <= value <= 32767:
                # Store as: prefix_byte + value (2 bytes little-endian)
                result = bytearray()
                result.append(0xB0)  # Integer literal prefix
                result.extend(struct.pack('<h', value))  # Signed 16-bit little-endian
                return bytes(result), consumed
            else:
                # Too large for 16-bit, store as ASCII
                return number_str.encode('ascii'), consumed
                
        except ValueError:
            # Not a simple integer, store as ASCII
            return number_str.encode('ascii'), consumed
    
    def _parse_rem_data_statement(self, content: str, start: int, keyword: str) -> Tuple[bytes, int]:
        """Parse REM or DATA statement content with proper preservation.
        
        Args:
            content: Full line content
            start: Starting position after the keyword
            keyword: Either 'REM' or 'DATA'
            
        Returns:
            Tuple of (tokenized_content, bytes_consumed)
        """
        result = bytearray()
        i = start
        
        if keyword == 'REM':
            # REM statements: preserve everything exactly as written
            remaining_content = content[i:]
            # Integer BASIC REM: content stored as regular ASCII
            # Leading spaces are significant for REM statements
            result.extend(remaining_content.encode('ascii'))
            return bytes(result), len(content) - start
            
        elif keyword == 'DATA':
            # Integer BASIC doesn't have DATA statements - treat as regular content
            remaining_content = content[i:]
            result.extend(remaining_content.encode('ascii'))
            return bytes(result), len(content) - start
        
        return b'', 0
    
    def _get_contextual_token(self, word: str, content: str, word_start: int, word_end: int) -> Optional[int]:
        """Get token for word based on context using Integer BASIC rules.
        
        Args:
            word: The word to tokenize
            content: Full line content
            word_start: Start position of word
            word_end: End position of word
            
        Returns:
            Token value or None if not a token
        """
        token = self.token_table.get_token(word)
        if token is None:
            return None
        
        # Analyze context for disambiguation
        context = self._analyze_syntactic_context(content, word_start, word_end, word)
        
        # Apply Integer BASIC-specific disambiguation rules
        return self._apply_disambiguation_rules(word, token, context)
    
    def _analyze_syntactic_context(self, content: str, word_start: int, word_end: int, word: str) -> Dict[str, Any]:
        """Analyze the syntactic context around a word."""
        context = {
            'word': word,
            'position': 'middle',
            'prev_char': '',
            'next_char': '',
            'prev_word': '',
            'next_word': '',
            'is_after_equals': False,
            'is_before_paren': False,
            'line_type': 'statement'
        }
        
        # Position in line
        if word_start == 0 or content[:word_start].strip() == '':
            context['position'] = 'start'
        elif word_end >= len(content) or content[word_end:].strip() == '':
            context['position'] = 'end'
        
        # Adjacent characters
        if word_start > 0:
            context['prev_char'] = content[word_start - 1]
        if word_end < len(content):
            context['next_char'] = content[word_end]
        
        # Check for function call pattern
        next_non_space = word_end
        while next_non_space < len(content) and content[next_non_space].isspace():
            next_non_space += 1
        if next_non_space < len(content) and content[next_non_space] == '(':
            context['is_before_paren'] = True
        
        # Check if after equals sign
        prev_content = content[:word_start].strip()
        if prev_content.endswith('='):
            context['is_after_equals'] = True
        
        return context
    
    def _apply_disambiguation_rules(self, word: str, token: int, context: Dict[str, Any]) -> Optional[int]:
        """Apply Integer BASIC specific disambiguation rules."""
        # Integer BASIC is more strict about variable vs keyword disambiguation
        
        # Functions should be tokenized when followed by parentheses
        if context['is_before_paren'] and self._is_function_name(word):
            return token
        
        # Statement keywords at start of statement
        if context['position'] == 'start' and self._is_statement_keyword(word):
            return token
        
        # Be more conservative with tokenization in Integer BASIC
        conservative_tokenize = {
            'IF', 'THEN', 'ELSE', 'FOR', 'TO', 'NEXT', 'STEP', 'GOTO', 'GOSUB',
            'RETURN', 'END', 'PRINT', 'INPUT', 'REM', 'LET', 'DIM'
        }
        
        if word in conservative_tokenize:
            return token
        
        # Don't tokenize potential variable names
        if context['is_after_equals'] and len(word) <= 2:
            return None
        
        return token
    
    def _is_function_name(self, word: str) -> bool:
        """Check if word is a function name in Integer BASIC."""
        integer_functions = {
            'ABS', 'SGN', 'RND', 'PEEK', 'ASC', 'LEN', 'CHR$', 'LEFT$', 'RIGHT$',
            'MID$', 'STR$', 'VAL', 'NOT', 'TAB', 'SPC'
        }
        return word in integer_functions
    
    def _is_statement_keyword(self, word: str) -> bool:
        """Check if word is a statement keyword in Integer BASIC."""
        statement_keywords = {
            'PRINT', 'INPUT', 'LET', 'IF', 'FOR', 'NEXT', 'GOTO', 'GOSUB',
            'RETURN', 'END', 'RUN', 'LIST', 'NEW', 'SAVE', 'LOAD', 'REM',
            'DIM', 'POKE', 'CALL', 'TEXT', 'GR', 'COLOR=', 'PLOT', 'HLIN', 'VLIN'
        }
        return word in statement_keywords