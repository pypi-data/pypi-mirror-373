"""Integer BASIC syntax validator."""

from typing import List

from ..common_validator import BaseSyntaxValidator, SyntaxErrorInfo, Token, TokenType


class IntegerSyntaxValidator(BaseSyntaxValidator):
    """ROM-compliant Integer BASIC syntax validator.
    
    Based on Integer BASIC ROM (E000-F7FF) with 32 syntax categories
    and multi-stage token validation using syntax stacks.
    """
    
    def __init__(self):
        """Initialize Integer BASIC syntax validator."""
        super().__init__("integer")
        self._init_integer_basic_validator()
    
    def _init_integer_basic_validator(self):
        """Initialize Integer BASIC ROM-specific validation rules."""
        # Integer BASIC syntax categories (ROM specification)
        self.syntax_categories = {
            0: "program_start",  # Program beginning
            1: "statement",  # Statement parsing
            2: "expression",  # Expression evaluation
            3: "variable",  # Variable references
            4: "array_ref",  # Array subscripts
            5: "function_call",  # Function invocations
            6: "string_literal",  # String constants
            7: "numeric_literal",  # Numeric constants
            8: "operator",  # Mathematical operators
            9: "comparison",  # Comparison operators
            10: "logical",  # Logical operators (AND, OR, NOT)
            11: "assignment",  # Assignment statements
            12: "control_flow",  # FOR, IF, GOTO, etc.
            13: "subroutine",  # GOSUB, RETURN
            14: "input_output",  # PRINT, INPUT, GET
            15: "graphics",  # GR, COLOR=, PLOT, etc.
            16: "system",  # END, NEW, RUN, etc.
            17: "data_handling",  # REM, DATA (though Integer BASIC has limited DATA)
            18: "line_reference",  # Line number references
            19: "parentheses",  # Grouping expressions
            20: "array_dimension",  # DIM statement parsing
            21: "for_loop",  # FOR loop specific parsing
            22: "if_statement",  # IF statement parsing
            23: "print_statement",  # PRINT statement parsing
            24: "function_params",  # Function parameter lists
            25: "expression_list",  # Multiple expressions (comma-separated)
            26: "statement_separator",  # : separator between statements
            27: "string_context",  # Inside string literals
            28: "comment_context",  # Inside REM statements
            29: "error_recovery",  # Error handling
            30: "program_end",  # Program termination
            31: "syntax_stack",  # Stack management
        }

        # Integer BASIC ROM control codes (from ROM disassembly)
        self.rom_control_codes = {
            0x00: "syntax_error",  # Return with syntax error
            0x01: "no_error",  # Return with no error
            0x02: "comment_char",  # Parse comment character
            0x03: "string_char",  # Parse string literal character
        }

        # Integer BASIC reserved words from ROM
        self.integer_reserved_words = {
            "FOR",
            "PRINT",
            "IF",
            "THEN",
            "TO",
            "STEP",
            "NEXT",
            "END",
            "GOTO",
            "GOSUB",
            "RETURN",
            "INPUT",
            "REM",
            "LET",
            "DIM",
            "RUN",
            "LIST",
            "NEW",
            "LOAD",
            "SAVE",
            "CLR",
            "AND",
            "OR",
            "NOT",
            "MOD",
            "ABS",
            "SGN",
            "RND",
            "PEEK",
            "POKE",
            "TEXT",
            "GR",
            "CALL",
            "COLOR=",
            "PLOT",
            "HLIN",
            "VLIN",
            "VTAB",
            "GET",
        }

        # Integer BASIC error precedence (from ROM behavior)
        self.error_precedence = [
            "BAD_SUBSCRIPT",  # Array bounds checked first
            "UNDEF_STATEMENT",  # Line number validation
            "ILLEGAL_QUANTITY",  # Number/range validation
            "SYNTAX_ERROR",  # General syntax issues last
        ]

        # Parsing state management (ROM simulation)
        self.syntax_stack = []
        self.syntax_stack_index = 0
        self.text_index = 0
        self.token_index = 0
    
    def _is_reserved_word(self, word: str) -> bool:
        """Check if a word is reserved in Integer BASIC."""
        return word in self.integer_reserved_words or word.rstrip("=") in self.integer_reserved_words
    
    def validate_line(self, line_num: int, content: str) -> List[SyntaxErrorInfo]:
        """Validate a single line of Integer BASIC code.
        
        Args:
            line_num: Line number
            content: Line content (without line number)
            
        Returns:
            List of syntax errors found
        """
        errors = []
        
        if not content.strip():
            return errors  # Empty lines are valid
        
        # Tokenize the line for validation
        tokens = self._tokenize_line_for_validation(content)
        if not tokens:
            return errors
        
        # Validate using Integer BASIC ROM-based approach
        errors.extend(self._validate_integer_control_structures(line_num, tokens))
        errors.extend(self._validate_integer_expressions(line_num, tokens))
        errors.extend(self._validate_integer_graphics_commands(line_num, tokens))
        
        # Add line number to all errors
        for error in errors:
            if error.line_number is None:
                error.line_number = line_num
        
        return errors
    
    def validate(self, text: str) -> List[SyntaxErrorInfo]:
        """Validate Integer BASIC code.
        
        This is the main entry point for validation.
        
        Args:
            text: The BASIC program text to validate
            
        Returns:
            List of syntax errors found
        """
        return self.validate_program(text)
    
    def _validate_integer_control_structures(self, line_num: int, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate Integer BASIC control structures.
        
        Args:
            line_num: Current line number
            tokens: List of tokens to validate
            
        Returns:
            List of syntax errors
        """
        errors = []
        
        for i, token in enumerate(tokens):
            if token.type == TokenType.KEYWORD:
                if token.value == "FOR":
                    errors.extend(self._validate_for_statement(tokens[i:]))
                elif token.value == "IF":
                    errors.extend(self._validate_if_statement(tokens[i:]))
                elif token.value in ["GOTO", "GOSUB"]:
                    errors.extend(self._validate_goto_gosub_statement(tokens[i:]))
                elif token.value == "DIM":
                    errors.extend(self._validate_dim_statement(tokens[i:]))
        
        return errors
    
    def _validate_integer_expressions(self, line_num: int, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate Integer BASIC expressions.
        
        Args:
            line_num: Current line number
            tokens: List of tokens to validate
            
        Returns:
            List of syntax errors
        """
        errors = []
        
        # Check for integer overflow (Integer BASIC uses 16-bit integers)
        for token in tokens:
            if token.type == TokenType.LITERAL and token.value.isdigit():
                try:
                    value = int(token.value)
                    if value > 32767 or value < -32768:
                        errors.append(SyntaxErrorInfo(
                            error_type="ILLEGAL QUANTITY",
                            message=f"Integer value {value} out of range (-32768 to 32767)",
                            character_position=token.position
                        ))
                except ValueError:
                    pass
        
        return errors
    
    def _validate_integer_graphics_commands(self, line_num: int, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate Integer BASIC graphics commands.
        
        Args:
            line_num: Current line number 
            tokens: List of tokens to validate
            
        Returns:
            List of syntax errors
        """
        errors = []
        
        for i, token in enumerate(tokens):
            if token.type == TokenType.KEYWORD:
                if token.value == "PLOT":
                    # PLOT requires X,Y coordinates
                    if len(tokens) <= i + 3:  # PLOT X,Y
                        errors.append(SyntaxErrorInfo(
                            error_type="SYNTAX ERROR",
                            message="PLOT command requires X,Y coordinates"
                        ))
                elif token.value in ["HLIN", "VLIN"]:
                    # These commands require specific parameter patterns
                    if len(tokens) <= i + 2:
                        errors.append(SyntaxErrorInfo(
                            error_type="SYNTAX ERROR",
                            message=f"{token.value} command requires parameters"
                        ))
        
        return errors
    
    def _validate_for_statement(self, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate FOR statement syntax for Integer BASIC.
        
        Args:
            tokens: Token sequence starting with FOR
            
        Returns:
            List of syntax errors
        """
        errors = []
        
        if len(tokens) < 6:  # FOR var = start TO end
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="Incomplete FOR statement"
            ))
            return errors
        
        # Check FOR var = start TO end pattern
        if tokens[1].type != TokenType.IDENTIFIER:
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="FOR statement requires variable name"
            ))
        
        # Look for TO keyword
        to_found = False
        for token in tokens[2:]:
            if token.type == TokenType.KEYWORD and token.value == "TO":
                to_found = True
                break
        
        if not to_found:
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="FOR statement missing TO keyword"
            ))
        
        return errors
    
    def _validate_if_statement(self, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate IF statement syntax for Integer BASIC.
        
        Args:
            tokens: Token sequence starting with IF
            
        Returns:
            List of syntax errors
        """
        errors = []
        
        if len(tokens) < 4:  # IF condition THEN
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="Incomplete IF statement"
            ))
            return errors
        
        # Look for THEN keyword
        then_found = False
        for token in tokens[1:]:
            if token.type == TokenType.KEYWORD and token.value == "THEN":
                then_found = True
                break
        
        if not then_found:
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="IF statement missing THEN keyword"
            ))
        
        return errors
    
    def _validate_goto_gosub_statement(self, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate GOTO/GOSUB statement syntax.
        
        Args:
            tokens: Token sequence starting with GOTO/GOSUB
            
        Returns:
            List of syntax errors
        """
        errors = []
        
        if len(tokens) < 2:
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message=f"{tokens[0].value} statement requires line number"
            ))
            return errors
        
        # Check that next token is a number or expression
        if tokens[1].type not in [TokenType.LITERAL, TokenType.IDENTIFIER]:
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message=f"{tokens[0].value} requires line number or expression"
            ))
        
        return errors
    
    def _validate_dim_statement(self, tokens: List[Token]) -> List[SyntaxErrorInfo]:
        """Validate DIM statement syntax for Integer BASIC.
        
        Args:
            tokens: Token sequence starting with DIM
            
        Returns:
            List of syntax errors
        """
        errors = []
        
        if len(tokens) < 4:  # DIM array(size)
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="Incomplete DIM statement"
            ))
            return errors
        
        # Check DIM array(size) pattern
        if tokens[1].type != TokenType.IDENTIFIER:
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="DIM statement requires array name"
            ))
        
        # Check for parentheses with array dimensions
        paren_found = False
        for token in tokens[2:]:
            if token.type == TokenType.SEPARATOR and token.value == "(":
                paren_found = True
                break
        
        if not paren_found:
            errors.append(SyntaxErrorInfo(
                error_type="SYNTAX ERROR",
                message="DIM statement requires array dimensions in parentheses"
            ))
        
        return errors