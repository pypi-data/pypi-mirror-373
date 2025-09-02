"""Applesoft BASIC detokenizer."""

import struct
from typing import Tuple

from ..common import BaseDetokenizer
from ..tokens import get_applesoft_table


class ApplesoftDetokenizer(BaseDetokenizer):
    """Converts tokenized Applesoft BASIC programs back to plain text."""
    
    def __init__(self):
        """Initialize Applesoft BASIC detokenizer."""
        super().__init__("applesoft")
        self.token_table = get_applesoft_table()
    
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
        
        # Check for immediate mode command (starts with token, not line pointer)
        if len(data) >= 2:
            first_byte = data[0]
            # If first byte is a token (0x80-0xFF), this is likely immediate mode
            if 0x80 <= first_byte <= 0xFF:
                # Find the end of the immediate mode command (first null byte)
                end_pos = data.find(0)
                if end_pos != -1:
                    immediate_content = data[:end_pos]
                    detokenized_content = self._detokenize_content(immediate_content)
                    return detokenized_content
        
        # Applesoft BASIC: each line has next line pointer + line number + content + terminator
        while offset < len(data):
            # Check if we have enough bytes for a line header
            if offset + 4 > len(data):
                break
                
            # Read next line pointer (2 bytes, little-endian)
            next_line_ptr = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Check if this is the program terminator (two consecutive null bytes)
            # If next line pointer is 0 and the next two bytes are also 0, we're done
            if next_line_ptr == 0:
                # Check if the next bytes are a line number or more zeros (program terminator)
                if offset + 2 < len(data):
                    potential_line_num = struct.unpack('<H', data[offset:offset+2])[0]
                    if potential_line_num == 0:
                        # Two consecutive zeros - this is the program terminator, not a line
                        break
                    # Otherwise this is a valid line with a zero next line pointer (last line)
                else:
                    # Not enough data left for a line, consider this the end
                    break
            
            # Read line number (2 bytes, little-endian)
            line_number = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Find the end of this line (null terminator)
            line_start = offset
            while offset < len(data) and data[offset] != 0:
                offset += 1
            
            if offset >= len(data):
                break
            
            # Extract and detokenize line content
            line_content = self._detokenize_content(data[line_start:offset])
            lines.append(f"{line_number} {line_content}")
            
            # Skip the null terminator
            offset += 1
        
        # Return the lines joined with newlines
        result = '\n'.join(lines)
        return result
    
    def _detokenize_content(self, content_data: bytes) -> str:
        """Detokenize the content portion of an Applesoft BASIC line.
        
        Args:
            content_data: Tokenized content bytes
            
        Returns:
            Plain text content
        """
        result = []
        i = 0
        
        while i < len(content_data):
            byte_val = content_data[i]
            
            # Applesoft BASIC: tokens are 128-255, ASCII is 0-127
            if self.token_table.is_token(byte_val):
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
                    
                    result.append(keyword)  # Applesoft doesn't add spaces after tokens
                else:
                    # Unknown token, output as hex
                    result.append(f"[${byte_val:02X}]")
            else:
                # ASCII character
                if 32 <= byte_val <= 126:  # Printable ASCII
                    char = chr(byte_val)
                    # Add space after alphanumeric characters if followed by a token that starts with a letter
                    if (char.isalnum() and i + 1 < len(content_data) and 
                        self.token_table.is_token(content_data[i + 1])):
                        next_keyword = self.token_table.get_keyword(content_data[i + 1])
                        if next_keyword and next_keyword[0].isalpha():
                            result.append(char + ' ')
                        else:
                            result.append(char)
                    else:
                        result.append(char)
                elif byte_val == 13:  # CR
                    result.append('\\r')
                elif byte_val == 10:  # LF
                    result.append('\\n')
                else:
                    # Non-printable, output as hex
                    result.append(f"[${byte_val:02X}]")
            
            i += 1
        
        return ''.join(result)
    
    def _add_applesoft_spacing(self, text: str) -> str:
        """Add appropriate spacing for Applesoft BASIC."""
        if not text:
            return text
        
        # Applesoft generally maintains the original spacing from detokenization
        # Just clean up any excessive whitespace
        lines = text.split('\\n')
        cleaned_lines = []
        
        for line in lines:
            # Normalize internal spacing but preserve structure
            cleaned_line = ' '.join(line.split())
            cleaned_lines.append(cleaned_line)
        
        return '\\n'.join(cleaned_lines)