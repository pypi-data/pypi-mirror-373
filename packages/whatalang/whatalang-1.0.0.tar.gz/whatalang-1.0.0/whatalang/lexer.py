"""
Whatalang Lexer - Converts source code into tokens
"""

import re
from enum import Enum, auto
from typing import List, Tuple, Optional


class TokenType(Enum):
    """Token types for Whatalang"""
    # Keywords
    STATE = auto()
    SET = auto()
    PRINT = auto()
    REACT = auto()
    TO = auto()
    WHEN = auto()
    DEFAULT = auto()
    
    # Literals
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Operators
    EQUALS = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER = auto()
    LESS = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    
    # Delimiters
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COLON = auto()
    COMMA = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    DOT = auto()
    
    # Special
    EOF = auto()
    WHITESPACE = auto()


class Token:
    """Represents a single token"""
    
    def __init__(self, token_type: TokenType, value: str, line: int, column: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"


class Lexer:
    """Lexer for Whatalang"""
    
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Token patterns
        self.patterns = [
            # Keywords
            (r'\bstate\b', TokenType.STATE),
            (r'\bset\b', TokenType.SET),
            (r'\bprint\b', TokenType.PRINT),
            (r'\breact\b', TokenType.REACT),
            (r'\bto\b', TokenType.TO),
            (r'\bwhen\b', TokenType.WHEN),
            (r'\bdefault\b', TokenType.DEFAULT),
            (r'\btrue\b', TokenType.BOOLEAN),
            (r'\bfalse\b', TokenType.BOOLEAN),
            (r'\bnull\b', TokenType.NULL),
            
            # Numbers
            (r'\b\d+\.\d+\b', TokenType.NUMBER),  # Float
            (r'\b\d+\b', TokenType.NUMBER),        # Integer
            
            # Strings
            (r'"[^"]*"', TokenType.STRING),
            (r"'[^']*'", TokenType.STRING),
            
            # Operators
            (r'==', TokenType.EQUAL_EQUAL),
            (r'!=', TokenType.NOT_EQUAL),
            (r'>=', TokenType.GREATER_EQUAL),
            (r'<=', TokenType.LESS_EQUAL),
            (r'=', TokenType.EQUALS),
            (r'\+', TokenType.PLUS),
            (r'-', TokenType.MINUS),
            (r'\*', TokenType.MULTIPLY),
            (r'/', TokenType.DIVIDE),
            (r'>', TokenType.GREATER),
            (r'<', TokenType.LESS),
            
            # Delimiters
            (r'\{', TokenType.LEFT_BRACE),
            (r'\}', TokenType.RIGHT_BRACE),
            (r'\[', TokenType.LEFT_BRACKET),
            (r'\]', TokenType.RIGHT_BRACKET),
            (r':', TokenType.COLON),
            (r',', TokenType.COMMA),
            (r'\(', TokenType.LEFT_PAREN),
            (r'\)', TokenType.RIGHT_PAREN),
            (r'\.', TokenType.DOT),
            
            # Identifiers
            (r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', TokenType.IDENTIFIER),
            
            # Whitespace
            (r'\s+', TokenType.WHITESPACE),
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [(re.compile(pattern), token_type) 
                                 for pattern, token_type in self.patterns]
    
    def tokenize(self) -> List[Token]:
        """Convert source code into tokens"""
        self.tokens = []
        self.position = 0
        self.line = 1
        self.column = 1
        
        while self.position < len(self.source):
            token = self._next_token()
            if token and token.type != TokenType.WHITESPACE:
                self.tokens.append(token)
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def _next_token(self) -> Optional[Token]:
        """Get the next token from the source"""
        if self.position >= len(self.source):
            return None
        
        # Try to match patterns
        for pattern, token_type in self.compiled_patterns:
            match = pattern.match(self.source, self.position)
            if match:
                value = match.group(0)
                start_pos = self.position
                self.position = match.end()
                
                # Create token with current position
                token = Token(token_type, value, self.line, self.column)
                
                # Update line and column for next token
                self._update_position(value, start_pos)
                
                return token
        
        # If no pattern matches, it's an error
        raise ValueError(f"Unexpected character '{self.source[self.position]}' at line {self.line}, column {self.column}")
    
    def _update_position(self, value: str, start_pos: int):
        """Update line and column position"""
        # Count newlines and characters to update line/column
        newlines = value.count('\n')
        if newlines > 0:
            self.line += newlines
            # Column becomes position after last newline + 1
            last_newline_pos = value.rfind('\n')
            self.column = len(value) - last_newline_pos
        else:
            self.column += len(value)
