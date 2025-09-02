"""Integer BASIC detokenizer."""

import struct
from typing import Tuple

from ..common import BaseDetokenizer
from ..tokens import get_integer_basic_table


class IntegerDetokenizer(BaseDetokenizer):
    """Converts tokenized Integer BASIC programs back to plain text."""
    
    def __init__(self):
        """Initialize Integer BASIC detokenizer."""
        super().__init__("integer")
        self.token_table = get_integer_basic_table()
    
    def detokenize_program(self, data: bytes) -> str:
        """Convert tokenized BASIC program to plain text.
        
        Args:
            data: Tokenized program data
            
        Returns:
            Plain text BASIC program
        """
        if not data:
            return ""
        
        lines = []
        offset = 0
        
        # Check for immediate mode command  
        # Integer BASIC immediate mode: command + 0x01 + 0x00 (no length byte prefix)
        # Regular lines: length_byte + line_number(2) + content + 0x01
        if len(data) >= 3:
            # Check if this might be immediate mode by looking for the pattern:
            # content + 0x01 + 0x00 without a length byte at the start
            end_of_line_pos = data.find(1)  # Find 0x01 end-of-line marker
            if end_of_line_pos != -1 and end_of_line_pos + 1 < len(data):
                # Check if after 0x01 we have 0x00 (program terminator)
                if data[end_of_line_pos + 1] == 0:
                    # This could be immediate mode: content + 0x01 + 0x00
                    # But we need to distinguish from regular lines
                    first_byte = data[0]
                    
                    # Better heuristic: check if this could be a valid length byte
                    # If first byte + 1 == end_of_line_pos + 1, it's a valid length byte for a regular line
                    expected_line_end = first_byte + 1  # +1 for the length byte itself
                    if expected_line_end == end_of_line_pos + 1:
                        # This is a regular line, not immediate mode
                        pass
                    else:
                        # This might be immediate mode - first byte is likely content, not length
                        if (32 <= first_byte <= 126) or first_byte >= 0x80:  # ASCII or token
                            immediate_content = data[:end_of_line_pos]
                            detokenized_content = self._detokenize_content(immediate_content)
                            return detokenized_content
        
        # Integer BASIC: each line starts with a length byte
        while offset < len(data):
            if data[offset] == 0:
                # Zero length byte = program terminator
                break
                
            try:
                line, line_length = self._detokenize_integer_line(data, offset)
                if line:
                    lines.append(line)
                if line_length <= 0:  # Safety check
                    break
                offset += line_length
            except (struct.error, IndexError):
                break
        
        result = '\n'.join(lines)
        return self._add_rom_based_spacing_simple(result)
    
    def _detokenize_integer_line(self, data: bytes, offset: int) -> Tuple[str, int]:
        """Detokenize a single Integer BASIC line.
        
        Args:
            data: Full program data
            offset: Starting offset of this line
            
        Returns:
            Tuple of (line_text, bytes_consumed)
        """
        start_offset = offset
        
        # Read line length byte
        if offset >= len(data):
            return "", 0
            
        line_length = data[offset]
        if line_length == 0:
            # Program terminator
            return "", 1
            
        offset += 1
        
        # Check if we have enough data for the full line
        if offset + line_length > len(data):
            return "", line_length + 1  # Skip this malformed line
            
        # Read line number (2 bytes, little-endian)  
        if offset + 2 > len(data):
            return "", line_length + 1
            
        line_num = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        
        # Calculate content boundaries based on line length
        # Line format: length_byte + line_number(2) + content + end_token(1)
        # So content goes from current offset to (start + line_length - 1) 
        content_start = offset
        content_end = start_offset + line_length  # This points to the end-of-line token
        
        # Extract content (excluding the end-of-line token)
        content = self._detokenize_content(data[content_start:content_end])
        
        line_text = f"{line_num} {content}".strip()
        
        # Return total bytes consumed (line length byte + line data)
        return line_text, line_length + 1
    
    def _detokenize_content(self, content_data: bytes) -> str:
        """Detokenize the content portion of an Integer BASIC line.
        
        Args:
            content_data: Tokenized content bytes
            
        Returns:
            Plain text content
        """
        result = []
        i = 0
        in_rem_statement = False  # Track if we're inside a REM statement
        
        while i < len(content_data):
            byte_val = content_data[i]
            
            # Check if we're entering a REM statement
            if byte_val == 0x8E:  # REM token in Integer BASIC
                in_rem_statement = True
                keyword = self.token_table.get_keyword(byte_val)
                if keyword:
                    result.append(keyword + ' ')
                i += 1
                continue
            
            # In REM statements, treat everything after REM as literal ASCII
            if in_rem_statement:
                # Everything after REM token is literal ASCII (including spaces, parentheses, etc)
                if 32 <= byte_val <= 126:  # Printable ASCII
                    result.append(chr(byte_val))
                else:
                    result.append(f"[${byte_val:02X}]")
                # Skip all other processing for REM content
                i += 1
                continue
            
            # Integer BASIC special handling for non-REM contexts
            if byte_val == 0x20:  # This could be ^ (exponentiation) OR space in REM
                # In other contexts, 0x20 is the exponentiation operator
                result.append('^')
            elif byte_val == 0x28:  # Could be string start token OR parenthesis
                # Check if this is actually a string literal by looking ahead
                if self._is_integer_basic_string(content_data, i):
                    # Handle string literal: $28 + high-bit ASCII + $29
                    result.append('"')
                    i += 1
                    # Read high-bit ASCII characters until $29
                    while i < len(content_data) and content_data[i] != 0x29:
                        char_byte = content_data[i]
                        if char_byte & 0x80:  # High bit set
                            result.append(chr(char_byte & 0x7F))  # Clear high bit
                        else:
                            # This shouldn't happen in proper string, but handle gracefully
                            result.append(chr(char_byte) if 32 <= char_byte <= 126 else f"[${char_byte:02X}]")
                        i += 1
                    result.append('"')
                    i += 1  # Skip the $29 end token
                    continue
                else:
                    # This is just a regular parenthesis
                    result.append('(')
            elif 0xB0 <= byte_val <= 0xB9:  # Numeric literal prefix
                # Handle Integer BASIC numeric literal: prefix + 2 bytes (little-endian)
                if i + 2 < len(content_data):
                    low_byte = content_data[i + 1]
                    high_byte = content_data[i + 2]
                    number_val = low_byte | (high_byte << 8)
                    
                    # Convert from unsigned to signed if needed
                    if number_val > 32767:
                        number_val = number_val - 65536
                        
                    # Add number with trailing space, except before closing parenthesis
                    if i + 3 < len(content_data) and content_data[i + 3] == 0x29:
                        result.append(str(number_val))  # No space before closing parenthesis
                    else:
                        result.append(str(number_val) + ' ')  # Add space normally
                    i += 2  # Skip the two data bytes
                else:
                    # Malformed numeric literal
                    result.append(f"[${byte_val:02X}]")
            elif self.token_table.is_token(byte_val) and not (65 <= byte_val <= 90):
                # This is a valid Integer BASIC token (but not an ASCII letter A-Z)
                # ASCII letters in variable context should be treated as ASCII, not tokens
                keyword = self.token_table.get_keyword(byte_val)
                if keyword:
                    # Check if this is part of a compound operator for binary equivalence
                    is_compound_operator_start = False
                    is_compound_operator_end = False
                    
                    # Check if this is the START of a compound operator
                    if keyword in ['<', '>'] and i + 1 < len(content_data):
                        next_byte = content_data[i + 1]
                        next_keyword = self.token_table.get_keyword(next_byte)
                        if ((keyword == '<' and next_keyword in ['=', '>']) or  # <= or <>
                            (keyword == '>' and next_keyword == '=')):          # >=
                            is_compound_operator_start = True
                    
                    # Check if this is the END of a compound operator
                    if keyword in ['=', '>'] and i > 0:
                        prev_byte = content_data[i - 1]
                        prev_keyword = self.token_table.get_keyword(prev_byte)
                        if ((keyword == '=' and prev_keyword in ['<', '>']) or  # <= or >=
                            (keyword == '>' and prev_keyword == '<')):          # <>
                            is_compound_operator_end = True
                    
                    # Add the keyword with a trailing space for proper separation
                    # Exception: Don't add space if followed by opening parenthesis (function calls)
                    if (i + 1 < len(content_data) and content_data[i + 1] == 0x28 and 
                        not self._is_integer_basic_string(content_data, i + 1)):
                        result.append(keyword)  # No space before parenthesis in function calls
                    elif keyword == 'REM':
                        result.append(keyword)  # Don't add space - next byte will be the space
                    elif is_compound_operator_start or is_compound_operator_end:
                        result.append(keyword)  # No space for compound operators
                    else:
                        result.append(keyword + ' ')  # Add space normally (including before strings)
                else:
                    result.append(f"[${byte_val:02X}]")
            elif byte_val == 0x29:  # Could be string end token OR closing parenthesis
                # If this is not consumed by string handling above, it's a closing parenthesis
                result.append(')')
            else:
                # Regular ASCII character in Integer BASIC (including A-Z for variables)
                if 32 <= byte_val <= 126:  # Printable ASCII
                    char = chr(byte_val)
                    # Add space after alphanumeric characters in certain contexts
                    # BUT NOT in REM statements where everything is literal
                    if not in_rem_statement and char.isalnum() and i + 1 < len(content_data):
                        next_byte = content_data[i + 1]
                        
                        # Add space if followed by a token that starts with a letter
                        if self.token_table.is_token(next_byte):
                            next_keyword = self.token_table.get_keyword(next_byte)
                            if next_keyword and next_keyword[0].isalpha():
                                result.append(char + ' ')
                            else:
                                result.append(char)
                        # Add space if followed by another letter (for word separation)
                        elif 65 <= next_byte <= 90 or 97 <= next_byte <= 122:  # A-Z or a-z
                            # For ASCII text, preserve the original spacing
                            # Don't add artificial spaces based on keyword detection
                            result.append(char)
                        else:
                            result.append(char)
                    else:
                        result.append(char)
                else:
                    result.append(f"[${byte_val:02X}]")
            
            i += 1
        
        return ''.join(result)
    
    def _is_integer_basic_string(self, content_data: bytes, start_pos: int) -> bool:
        """Determine if 0x28 at start_pos begins a string literal or is just a parenthesis.
        
        In Integer BASIC strings are: 0x28 + high-bit ASCII chars + 0x29
        Regular parentheses are just: 0x28 and 0x29 as ASCII
        """
        if start_pos >= len(content_data) or content_data[start_pos] != 0x28:
            return False
        
        # Look for the pattern: 0x28 followed by high-bit chars, then 0x29
        pos = start_pos + 1
        found_high_bit = False
        
        while pos < len(content_data):
            byte_val = content_data[pos]
            
            if byte_val == 0x29:  # End marker
                # This is a string if we found at least one high-bit character OR it's an empty string
                # Empty string: 0x28 immediately followed by 0x29
                return found_high_bit or (pos == start_pos + 1)
            elif byte_val & 0x80:  # High bit set
                found_high_bit = True
                pos += 1
            else:
                # Regular ASCII character - this is probably not a string
                return False
        
        # Reached end without finding 0x29 - not a string
        return False
    
    def _add_rom_based_spacing_simple(self, text: str) -> str:
        """Simplified ROM-based spacing that cleans up spaces from token detokenization."""
        if not text:
            return text
            
        # Detect REM statements to avoid modifying spacing inside them
        rem_positions = []
        rem_start = text.find(' REM ')
        while rem_start != -1:
            # Find the end of this line (or end of text)
            line_end = text.find('\\n', rem_start)
            if line_end == -1:
                line_end = len(text)
            rem_positions.append((rem_start + 5, line_end))  # +5 to skip " REM "
            rem_start = text.find(' REM ', line_end)
            
        def is_in_rem(pos):
            """Check if position is inside a REM statement."""
            for start, end in rem_positions:
                if start <= pos < end:
                    return True
            return False
            
        # Clean up multiple spaces and handle compound operators properly
        result = []
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Skip multiple consecutive spaces
            if char == ' ' and i > 0 and result and result[-1] == ' ':
                i += 1
                continue
            
            # Skip spacing modifications in REM statements
            if is_in_rem(i):
                result.append(char)
                i += 1
                continue
            
            # Handle compound operators first (before adding to result)
            if i + 1 < len(text):
                two_char = text[i:i+2]
                if two_char in ['>=', '<=', '<>']:
                    # Add compound operator as single unit with proper spacing
                    result.append(' ' + two_char + ' ')
                    i += 2
                    continue
            
            result.append(char)
            
            if i + 1 < len(text):
                next_char = text[i + 1]
                
                # Handle punctuation that only needs space AFTER (not before)
                if char in ',;' and next_char != ' ':
                    result.append(' ')
                    
                # Handle operators that need space AROUND them (both before and after)
                elif char in '=<>^+*/-' and next_char != ' ' and next_char not in '()':
                    # Don't add space if this will be part of compound operator
                    if not (char in '<>' and next_char == '='):
                        # Don't add space if this '=' is part of a command (like COLOR=)
                        if not (char == '=' and i > 0 and text[i-1].isalpha()):
                            result.append(' ')
                            
                # Add space BEFORE operators when needed
                elif next_char in '=<>^+*/-' and char != ' ' and char not in '()':
                    # Don't add space if this is before compound operator
                    if not (next_char in '<>' and i + 2 < len(text) and text[i + 2] == '='):
                        # Don't add space before '=' in commands (like COLOR=, HCOLOR=)
                        # Check if this looks like a command by looking for the pattern: WORD=
                        is_command_equals = False
                        if next_char == '=' and char.isalpha():
                            # Look backward to see if this is part of a known command
                            word_start = i
                            while word_start > 0 and text[word_start-1].isalpha():
                                word_start -= 1
                            potential_command = text[word_start:i+2]  # Include the =
                            # Check if this is a known command with =
                            if potential_command.upper() in ['COLOR=', 'HCOLOR=', 'SCALE=', 'ROT=', 'SPEED=', 'HIMEM:', 'LOMEM:']:
                                is_command_equals = True
                        
                        if not is_command_equals:
                            result.append(' ')
            
            i += 1
        
        return ''.join(result)