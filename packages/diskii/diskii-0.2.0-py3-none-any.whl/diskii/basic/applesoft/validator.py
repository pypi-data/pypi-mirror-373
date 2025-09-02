"""Applesoft BASIC syntax validator."""

from typing import List

from ..common_validator import BaseSyntaxValidator, SyntaxErrorInfo, Token, TokenType


class ApplesoftSyntaxValidator(BaseSyntaxValidator):
    """ROM-compliant Applesoft BASIC syntax validator.
    
    Based on Applesoft BASIC ROM with greedy reserved word recognition
    and two-step execution model.
    """
    
    def __init__(self):
        """Initialize Applesoft BASIC syntax validator."""
        super().__init__("applesoft")
        self._init_applesoft_validator()
    
    def _init_applesoft_validator(self):
        """Initialize Applesoft BASIC ROM-specific validation rules."""
        # Applesoft BASIC reserved words (from ROM token table)
        self.applesoft_reserved_words = {
            "END", "FOR", "NEXT", "DATA", "INPUT", "DEL", "DIM", "READ",
            "GR", "TEXT", "PR#", "IN#", "CALL", "PLOT", "HLIN", "VLIN",
            "HGR2", "HGR", "HCOLOR=", "HPLOT", "DRAW", "XDRAW", "HTAB",
            "HOME", "ROT=", "SCALE=", "SHLOAD", "TRACE", "NOTRACE",
            "NORMAL", "INVERSE", "FLASH", "COLOR=", "POP", "VTAB",
            "HIMEM:", "LOMEM:", "ONERR", "RESUME", "RECALL", "STORE",
            "SPEED=", "LET", "GOTO", "RUN", "IF", "RESTORE", "GOSUB",
            "RETURN", "REM", "STOP", "ON", "WAIT", "LOAD", "SAVE",
            "DEF", "POKE", "PRINT", "CONT", "LIST", "CLEAR", "GET",
            "NEW", "TAB(", "TO", "FN", "SPC(", "THEN", "AT", "NOT",
            "STEP", "AND", "OR", "SGN", "INT", "ABS", "USR", "FRE",
            "SCRN(", "PDL", "POS", "SQR", "RND", "LOG", "EXP", "COS",
            "SIN", "TAN", "ATN", "PEEK", "LEN", "STR$", "VAL", "ASC",
            "CHR$", "LEFT$", "RIGHT$", "MID$"
        }
        
        # Applesoft error precedence (from ROM behavior analysis)
        self.error_precedence = [
            "BAD_SUBSCRIPT",  # Array bounds checked first
            "UNDEF_STATEMENT",  # Line number validation
            "ILLEGAL_QUANTITY",  # Number/range validation
            "SYNTAX_ERROR",  # General syntax issues last
        ]
        
        # Two-step execution simulation
        self.parsing_step = 1  # Step 1: Parse tokens, Step 2: Validate syntax
    
    def _is_reserved_word(self, word: str) -> bool:
        """Check if a word is reserved in Applesoft BASIC."""
        return word in self.applesoft_reserved_words or word.rstrip("=") in self.applesoft_reserved_words
    
    def validate_line(self, line_num: int, content: str) -> List[SyntaxErrorInfo]:
        """Validate a single line of Applesoft BASIC code.
        
        Args:
            line_num: Line number
            content: Line content (without line number)
            
        Returns:
            List of syntax errors found
        """
        errors = []
        
        if not content.strip():
            return errors  # Empty lines are valid
        
        try:
            # Tokenize the line for validation
            tokens = self._tokenize_line_for_validation(content)
            
            # Applesoft BASIC specific validations
            line_content = " ".join([token.value for token in tokens])
            errors.extend(self._validate_applesoft_greedy_parsing(line_content))
            errors.extend(self._validate_applesoft_two_step_execution(tokens))
            errors.extend(self._validate_applesoft_string_handling(tokens))

        except Exception as e:
            errors.append(
                SyntaxErrorInfo(
                    error_type="SYNTAX_ERROR", message=str(e), line_number=line_num
                )
            )

        return errors
    
    def validate(self, text: str) -> List[SyntaxErrorInfo]:
        """Validate Applesoft BASIC code.
        
        This is the main entry point for validation.
        
        Args:
            text: The BASIC program text to validate
            
        Returns:
            List of syntax errors found
        """
        return self.validate_program(text)
    
    def _validate_applesoft_greedy_parsing(self, line_content: str) -> List[SyntaxErrorInfo]:
        """Validate using Applesoft's greedy reserved word parsing."""
        errors = []
        # Implementation will be added in subsequent phases
        return errors

    def _validate_applesoft_two_step_execution(self, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate using Applesoft's two-step execution model."""
        errors = []
        # Implementation will be added in subsequent phases
        return errors
    
    def _validate_applesoft_string_handling(self, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate Applesoft string handling per ROM specification."""
        errors = []

        for token in tokens:
            if token.type == TokenType.STRING:
                # Verify string is properly quoted
                if not (token.value.startswith('"') and token.value.endswith('"')):
                    errors.append(
                        SyntaxErrorInfo(
                            error_type="SYNTAX_ERROR",
                            message="String literals must be enclosed in double quotes",
                        )
                    )

                # Check for proper escape handling (Applesoft doesn't support escaping)
                content = token.value[1:-1]  # Remove quotes
                if "\\" in content:
                    # Applesoft BASIC doesn't support escape sequences
                    errors.append(
                        SyntaxErrorInfo(
                            error_type="SYNTAX_ERROR",
                            message="Applesoft BASIC does not support escape sequences in strings",
                        )
                    )

        return errors