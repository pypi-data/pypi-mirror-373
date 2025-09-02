"""Applesoft BASIC tokenizer."""

import re
import struct
from typing import List, Tuple, Optional, Dict, Any

from ..common import BaseTokenizer, is_immediate_mode_command, extract_numeric_literal, extract_string_literal
from ..tokens import get_applesoft_table


class ApplesoftTokenizer(BaseTokenizer):
    """Converts plain text Applesoft BASIC programs to tokenized format."""
    
    def __init__(self):
        """Initialize Applesoft BASIC tokenizer."""
        super().__init__("applesoft")
        self.token_table = get_applesoft_table()
    
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
            # Empty program still needs terminator
            return b'\x00\x00'
        
        lines = self._parse_lines(text)
        if not lines:
            # No valid lines, still need terminator
            return b'\x00\x00'
        
        # First pass: tokenize all lines without next line pointers
        tokenized_lines = []
        line_info = []  # Track original line numbers
        for line_num, line_text in lines:
            tokenized_line = self._tokenize_line(line_num, line_text)
            tokenized_lines.append(tokenized_line)
            line_info.append(line_num)
        
        # Second pass: update next line pointers (skip immediate mode commands)
        result = bytearray()
        current_offset = 0
        
        for i, line_data in enumerate(tokenized_lines):
            # Check if this is an immediate mode command (line_num == -1)
            if line_info[i] == -1:
                # Immediate mode commands don't have line pointers - use as-is
                result.extend(line_data)
            else:
                # Regular lines: update next line pointer
                line_with_pointer = bytearray(line_data)
                
                # Calculate next line pointer
                if i < len(tokenized_lines) - 1:
                    # Point to next line's start position
                    next_line_offset = current_offset + len(line_data)
                    line_with_pointer[0:2] = struct.pack('<H', next_line_offset)
                else:
                    # Last line: next line pointer is 0
                    line_with_pointer[0:2] = struct.pack('<H', 0)
                
                result.extend(line_with_pointer)
            
            current_offset += len(line_data)
        
        # Applesoft BASIC program terminator (two null bytes)
        result.extend(b'\x00\x00')
        
        return bytes(result)
    
    def _tokenize_line(self, line_num: int, line_text: str) -> bytes:
        """Tokenize a single Applesoft BASIC line.
        
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
        
        # Applesoft BASIC format: next line pointer + line number + content + terminator
        # Add next line pointer placeholder (2 bytes) - will be updated if needed
        line_data.extend(b'\x00\x00')
        
        # Add line number (2 bytes, little-endian)
        line_data.extend(struct.pack('<H', line_num))
        
        # Add tokenized content
        tokenized_content = self._tokenize_content(line_text)
        line_data.extend(tokenized_content)
        
        # Add line terminator (null byte)
        line_data.append(0x00)
        
        return bytes(line_data)
    
    def _tokenize_immediate_mode(self, line_text: str) -> bytes:
        """Tokenize immediate mode command for Applesoft BASIC.
        
        Args:
            line_text: Command text
            
        Returns:
            Tokenized command
        """
        if not is_immediate_mode_command(line_text):
            # Regular line content without line number
            return self._tokenize_content(line_text) + b'\x00'
        
        # Applesoft immediate mode
        # Some immediate commands may have special tokenization
        return self._tokenize_content(line_text) + b'\x00'
    
    def _tokenize_content(self, content: str) -> bytes:
        """Tokenize the content portion of an Applesoft BASIC line.
        
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
            
            # Check for keywords and operators
            if content[i].isalpha():
                # Find end of word
                word_start = i
                while i < len(content) and (content[i].isalnum() or content[i] in '$#'):
                    i += 1
                
                # Check for commands ending with '=' (like COLOR=, HCOLOR=)
                if i < len(content) and content[i] == '=':
                    potential_command = content[word_start:i+1].upper()
                    if self.token_table.get_token(potential_command) is not None:
                        i += 1  # Include the '=' in the token
                        word = potential_command
                    else:
                        word = content[word_start:i].upper()
                else:
                    word = content[word_start:i].upper()
                
                # Enhanced handling for REM and DATA statements
                if word in ['REM', 'DATA']:
                    token = self.token_table.get_token(word)
                    if token is not None:
                        result.append(token)
                    
                    rem_data_result, consumed = self._parse_rem_data_statement(content, i, word)
                    result.extend(rem_data_result)
                    i += consumed
                    continue
                
                # Context-aware keyword detection
                token = self._get_contextual_token(word, content, word_start, i)
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
            token = self.token_table.get_token(char)
            if token is not None:
                result.append(token)
            else:
                result.append(ord(char))
            i += 1
        
        return bytes(result)
    
    def _parse_string_literal(self, content: str, start: int) -> Tuple[bytes, int]:
        """Parse string literal in Applesoft BASIC format.
        
        Args:
            content: Full line content
            start: Starting position of quote
            
        Returns:
            Tuple of (tokenized_string, bytes_consumed)
        """
        string_text, consumed = extract_string_literal(content, start)
        
        # Applesoft BASIC: quoted string as ASCII
        return string_text.encode('ascii'), consumed
    
    def _parse_numeric_literal(self, content: str, start: int) -> Tuple[bytes, int]:
        """Parse numeric literal in Applesoft BASIC format.
        
        Args:
            content: Full line content
            start: Starting position of number
            
        Returns:
            Tuple of (tokenized_number, bytes_consumed)
        """
        number_str, consumed = extract_numeric_literal(content, start)
        
        # For Applesoft, store numbers as ASCII (they use floating point format)
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
            # Applesoft REM: preserve as ASCII
            result.extend(remaining_content.encode('ascii'))
            return bytes(result), len(content) - start
            
        elif keyword == 'DATA':
            # DATA statements: preserve data items exactly
            remaining_content = content[i:]
            # In Applesoft, DATA content is stored as ASCII
            result.extend(remaining_content.encode('ascii'))
            return bytes(result), len(content) - start
        
        return b'', 0
    
    def _get_contextual_token(self, word: str, content: str, word_start: int, word_end: int) -> Optional[int]:
        """Get token for word based on context using Applesoft BASIC rules.
        
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
        
        # Apply Applesoft-specific disambiguation rules
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
        """Apply Applesoft BASIC specific disambiguation rules."""
        # Applesoft is generally more permissive with keyword tokenization
        
        # Functions should be tokenized when followed by parentheses
        if context['is_before_paren'] and self._is_function_name(word):
            return token
        
        # Statement keywords at start of statement
        if context['position'] == 'start' and self._is_statement_keyword(word):
            return token
        
        # Always tokenize these keywords regardless of context
        always_tokenize = {
            'PRINT', 'INPUT', 'IF', 'THEN', 'ELSE', 'FOR', 'TO', 'NEXT', 'STEP',
            'GOTO', 'GOSUB', 'RETURN', 'END', 'STOP', 'RUN', 'LIST', 'NEW',
            'SAVE', 'LOAD', 'REM', 'DATA', 'READ', 'DIM', 'DEF', 'FN'
        }
        
        if word in always_tokenize:
            return token
        
        # Default: tokenize in most contexts for Applesoft
        return token
    
    def _is_function_name(self, word: str) -> bool:
        """Check if word is a function name in Applesoft BASIC."""
        applesoft_functions = {
            'ABS', 'ATN', 'COS', 'EXP', 'INT', 'LOG', 'RND', 'SGN', 'SIN', 'SQR', 'TAN',
            'ASC', 'CHR$', 'LEFT$', 'LEN', 'MID$', 'RIGHT$', 'STR$', 'VAL',
            'PEEK', 'USR', 'FRE', 'POS', 'SCRN', 'PDL', 'TAB', 'SPC', 'FN'
        }
        return word in applesoft_functions
    
    def _is_statement_keyword(self, word: str) -> bool:
        """Check if word is a statement keyword in Applesoft BASIC."""
        statement_keywords = {
            'PRINT', 'INPUT', 'LET', 'IF', 'FOR', 'NEXT', 'GOTO', 'GOSUB',
            'RETURN', 'END', 'STOP', 'RUN', 'LIST', 'NEW', 'SAVE', 'LOAD',
            'REM', 'DATA', 'READ', 'DIM', 'DEF', 'POKE', 'CALL', 'HOME',
            'TEXT', 'GR', 'HGR', 'HGR2', 'PLOT', 'HPLOT', 'DRAW', 'XDRAW'
        }
        return word in statement_keywords