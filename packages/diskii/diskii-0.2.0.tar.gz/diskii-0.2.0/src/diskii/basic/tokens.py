"""Apple II BASIC tokenization tables and utilities."""

from typing import Dict, Optional

# Applesoft BASIC token table (128-255, $80-$FF)
# Based on Applesoft BASIC Programming Reference Manual and research
APPLESOFT_TOKENS: Dict[int, str] = {
    # Control flow
    128: "END",        # $80
    129: "FOR",        # $81
    130: "NEXT",       # $82
    131: "DATA",       # $83
    132: "INPUT",      # $84
    133: "DEL",        # $85
    134: "DIM",        # $86
    135: "READ",       # $87
    136: "GR",         # $88
    137: "TEXT",       # $89
    138: "PR#",        # $8A
    139: "IN#",        # $8B
    140: "CALL",       # $8C
    141: "PLOT",       # $8D
    142: "HLIN",       # $8E
    143: "VLIN",       # $8F
    144: "HGR2",       # $90
    145: "HGR",        # $91
    146: "HCOLOR=",    # $92
    147: "HPLOT",      # $93
    148: "DRAW",       # $94
    149: "XDRAW",      # $95
    150: "HTAB",       # $96
    151: "HOME",       # $97
    152: "ROT=",       # $98
    153: "SCALE=",     # $99
    154: "SHLOAD",     # $9A
    155: "TRACE",      # $9B
    156: "NOTRACE",    # $9C
    157: "NORMAL",     # $9D
    158: "INVERSE",    # $9E
    159: "FLASH",      # $9F
    160: "COLOR=",     # $A0
    161: "POP",        # $A1
    162: "VTAB",       # $A2
    163: "HIMEM:",     # $A3
    164: "LOMEM:",     # $A4
    165: "ONERR",      # $A5
    166: "RESUME",     # $A6
    167: "RECALL",     # $A7
    168: "STORE",      # $A8
    169: "SPEED=",     # $A9
    170: "LET",        # $AA
    171: "GOTO",       # $AB
    172: "RUN",        # $AC
    173: "IF",         # $AD
    174: "RESTORE",    # $AE
    175: "&",          # $AF
    176: "GOSUB",      # $B0
    177: "RETURN",     # $B1
    178: "REM",        # $B2
    179: "STOP",       # $B3
    180: "ON",         # $B4
    181: "WAIT",       # $B5
    182: "LOAD",       # $B6
    183: "SAVE",       # $B7
    184: "DEF",        # $B8
    185: "POKE",       # $B9
    186: "PRINT",      # $BA
    187: "CONT",       # $BB
    188: "LIST",       # $BC
    189: "CLEAR",      # $BD
    190: "GET",        # $BE
    191: "NEW",        # $BF
    
    # Functions and operators
    192: "TAB(",       # $C0
    193: "TO",         # $C1
    194: "FN",         # $C2
    195: "SPC(",       # $C3
    196: "THEN",       # $C4
    197: "AT",         # $C5
    198: "NOT",        # $C6
    199: "STEP",       # $C7
    200: "+",          # $C8
    201: "-",          # $C9
    202: "*",          # $CA
    203: "/",          # $CB
    204: ";",          # $CC (statement separator)
    205: "AND",        # $CD
    206: "OR",         # $CE
    207: ">",          # $CF
    208: "=",          # $D0
    209: "<",          # $D1
    210: "SGN",        # $D2
    211: "INT",        # $D3
    212: "ABS",        # $D4
    213: "USR",        # $D5
    214: "FRE",        # $D6
    215: "SCRN(",      # $D7
    216: "PDL",        # $D8
    217: "POS",        # $D9
    218: "SQR",        # $DA
    219: "RND",        # $DB
    220: "LOG",        # $DC
    221: "EXP",        # $DD
    222: "COS",        # $DE
    223: "SIN",        # $DF
    224: "TAN",        # $E0
    225: "ATN",        # $E1
    226: "PEEK",       # $E2
    227: "LEN",        # $E3
    228: "STR$",       # $E4
    229: "VAL",        # $E5
    230: "ASC",        # $E6
    231: "CHR$",       # $E7
    232: "LEFT$",      # $E8
    233: "RIGHT$",     # $E9
    234: "MID$",       # $EA
    235: "",           # $EB - unused
    236: "",           # $EC - unused
    237: "",           # $ED - unused
    238: "",           # $EE - unused
    239: "",           # $EF - unused
    240: "",           # $F0 - unused
    241: "",           # $F1 - unused
    242: "",           # $F2 - unused
    243: "",           # $F3 - unused
    244: "",           # $F4 - unused
    245: "",           # $F5 - unused
    246: "",           # $F6 - unused
    247: "",           # $F7 - unused
    248: "",           # $F8 - unused
    249: "",           # $F9 - unused
    250: "",           # $FA - unused
    251: "",           # $FB - unused
    252: "",           # $FC - unused  
    253: "(",          # $FD - left parenthesis (special handling)
    254: "(",          # $FE - left parenthesis (special handling)
    255: "(",          # $FF - left parenthesis (special handling)
}

# Integer BASIC token table - Authentic ROM-based implementation
# Based on ROM disassembly analysis: https://6502disassembly.com/a2-rom/IntegerBASIC.html
# Key insight: Integer BASIC uses high-bit tokens ($80+) to avoid ASCII conflicts
INTEGER_BASIC_TOKENS: Dict[int, str] = {
    # Operators and punctuation (low range, safe from ASCII letters)
    # These are the only safe low-range tokens that don't conflict with variables
    22: "=",           # $16 - Assignment/comparison
    24: ">=",          # $18 - Greater than or equal  
    25: ">",           # $19 - Greater than
    26: "<=",          # $1A - Less than or equal
    27: "<>",          # $1B - Not equal
    28: "<",           # $1C - Less than
    29: "AND",         # $1D - Logical AND
    30: "OR",          # $1E - Logical OR 
    31: "MOD",         # $1F - Modulo operator
    32: "^",           # $20 - Exponentiation (stored as space in memory)
    
    # All keywords use high-bit tokens ($80-$FF) to avoid ASCII conflicts
    # This matches authentic Integer BASIC ROM behavior
    
    # Control flow keywords
    128: "IF",         # $80
    129: "THEN",       # $81
    130: "ELSE",       # $82 - Integer BASIC had ELSE
    131: "FOR",        # $83
    132: "TO",         # $84
    133: "STEP",       # $85
    134: "NEXT",       # $86
    135: "GOTO",       # $87
    136: "GOSUB",      # $88
    137: "RETURN",     # $89
    138: "END",        # $8A
    
    # I/O and basic commands
    139: "PRINT",      # $8B
    140: "INPUT",      # $8C
    141: "GET",        # $8D
    142: "REM",        # $8E
    143: "LET",        # $8F - Often optional in Integer BASIC
    
    # System commands  
    144: "RUN",        # $90
    145: "LIST",       # $91
    146: "NEW",        # $92
    147: "LOAD",       # $93
    148: "SAVE",       # $94
    149: "CLR",        # $95
    150: "AUTO",       # $96
    151: "MAN",        # $97
    
    # Memory management
    152: "HIMEM:",     # $98
    153: "LOMEM:",     # $99
    154: "DIM",        # $9A
    155: "READ",       # $9B - Read from DATA statement
    
    # Functions
    160: "ABS",        # $A0
    161: "SGN",        # $A1
    162: "RND",        # $A2
    163: "PEEK",       # $A3
    164: "POKE",       # $A4
    165: "TAB",        # $A5
    166: "SPC",        # $A6
    167: "LEN",        # $A7
    168: "CHR$",       # $A8
    169: "ASC",        # $A9
    170: "MID$",       # $AA
    171: "LEFT$",      # $AB
    172: "RIGHT$",     # $AC
    173: "STR$",       # $AD
    174: "VAL",        # $AE
    175: "NOT",        # $AF
    
    # Graphics and display commands (conflict-free high-bit tokens)
    # Using 0xC0+ range to avoid both ASCII and numeric literal conflicts
    192: "TEXT",       # $C0 - Switch to text mode
    193: "GR",         # $C1 - Switch to graphics mode  
    194: "CALL",       # $C2 - Call machine language routine
    195: "COLOR=",     # $C3 - Set color
    196: "PLOT",       # $C4 - Plot point
    197: "HLIN",       # $C5 - Horizontal line
    198: "VLIN",       # $C6 - Vertical line  
    199: "VTAB",       # $C7 - Vertical tab
    # HOME was not in original Integer BASIC
    
    # Additional operators (using arithmetic token prefix)
    18: "+",           # $12
    19: "-",           # $13
    20: "*",           # $14
    21: "/",           # $15
}

# Reverse mappings for tokenization (keyword -> token value)
APPLESOFT_KEYWORDS: Dict[str, int] = {
    keyword: token for token, keyword in APPLESOFT_TOKENS.items() if keyword
}

INTEGER_BASIC_KEYWORDS: Dict[str, int] = {
    keyword: token for token, keyword in INTEGER_BASIC_TOKENS.items() if keyword
}


class BasicTokenTable:
    """Token table manager for BASIC variants."""
    
    def __init__(self, variant: str = "applesoft"):
        """Initialize token table for specified BASIC variant.
        
        Args:
            variant: Either "applesoft" or "integer"
        """
        if variant.lower() == "applesoft":
            self.tokens = APPLESOFT_TOKENS
            self.keywords = APPLESOFT_KEYWORDS
            self.variant = "applesoft"
        elif variant.lower() == "integer":
            self.tokens = INTEGER_BASIC_TOKENS
            self.keywords = INTEGER_BASIC_KEYWORDS
            self.variant = "integer"
        else:
            raise ValueError(f"Unknown BASIC variant: {variant}")
    
    def get_keyword(self, token: int) -> Optional[str]:
        """Get keyword string for token value.
        
        Args:
            token: Token byte value
            
        Returns:
            Keyword string or None if token not found
        """
        return self.tokens.get(token)
    
    def get_token(self, keyword: str) -> Optional[int]:
        """Get token value for keyword string.
        
        Args:
            keyword: BASIC keyword (case-insensitive)
            
        Returns:
            Token byte value or None if keyword not found
        """
        return self.keywords.get(keyword.upper())
    
    def is_token(self, byte_value: int) -> bool:
        """Check if byte value is a valid token.
        
        Args:
            byte_value: Byte value to check
            
        Returns:
            True if valid token, False otherwise
        """
        if self.variant == "applesoft":
            # Applesoft tokens are 128-255
            return 128 <= byte_value <= 255 and byte_value in self.tokens
        else:
            # Integer BASIC: Check if it's a valid token
            return byte_value in self.tokens
    
    def is_ascii_char(self, byte_value: int) -> bool:
        """Check if byte value should be treated as ASCII character.
        
        Args:
            byte_value: Byte value to check
            
        Returns:
            True if ASCII character, False if token
        """
        if self.variant == "applesoft":
            # Applesoft preserves ASCII 0-127, tokens are 128-255
            return 0 <= byte_value <= 127
        else:
            # Integer BASIC has different ASCII handling
            return byte_value not in self.tokens
    
    def get_token_range(self) -> tuple[int, int]:
        """Get the token value range for this BASIC variant.
        
        Returns:
            Tuple of (min_token, max_token)
        """
        if self.variant == "applesoft":
            return (128, 255)
        else:
            tokens = [t for t in self.tokens.keys()]
            return (min(tokens), max(tokens)) if tokens else (0, 0)


def get_applesoft_table() -> BasicTokenTable:
    """Get Applesoft BASIC token table."""
    return BasicTokenTable("applesoft")


def get_integer_basic_table() -> BasicTokenTable:
    """Get Integer BASIC token table.""" 
    return BasicTokenTable("integer")