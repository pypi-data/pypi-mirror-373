import pytest
from whatalang.lexer import Lexer, TokenType, Token


class TestLexer:
    """Test the Whatalang lexer"""
    
    def test_basic_keywords(self):
        """Test that keywords are correctly tokenized"""
        source = "state set print react to when default"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.STATE,
            TokenType.SET,
            TokenType.PRINT,
            TokenType.REACT,
            TokenType.TO,
            TokenType.WHEN,
            TokenType.DEFAULT,
            TokenType.EOF
        ]
        
        assert len(tokens) == len(expected_types)
        for token, expected_type in zip(tokens, expected_types):
            assert token.type == expected_type
    
    def test_literals(self):
        """Test that literals are correctly tokenized"""
        source = '42 3.14 "hello" true false null'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Remove EOF token for comparison
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        assert len(tokens) == 6
        assert tokens[0].type == TokenType.NUMBER and tokens[0].value == "42"
        assert tokens[1].type == TokenType.NUMBER and tokens[1].value == "3.14"
        assert tokens[2].type == TokenType.STRING and tokens[2].value == '"hello"'
        assert tokens[3].type == TokenType.BOOLEAN and tokens[3].value == "true"
        assert tokens[4].type == TokenType.BOOLEAN and tokens[4].value == "false"
        assert tokens[5].type == TokenType.NULL and tokens[5].value == "null"
    
    def test_operators(self):
        """Test that operators are correctly tokenized"""
        source = "= == != > < >= <= + - * /"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Remove EOF token for comparison
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        expected_types = [
            TokenType.EQUALS,
            TokenType.EQUAL_EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.GREATER,
            TokenType.LESS,
            TokenType.GREATER_EQUAL,
            TokenType.LESS_EQUAL,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MULTIPLY,
            TokenType.DIVIDE
        ]
        
        assert len(tokens) == len(expected_types)
        for token, expected_type in zip(tokens, expected_types):
            assert token.type == expected_type
    
    def test_delimiters(self):
        """Test that delimiters are correctly tokenized"""
        source = "{ } [ ] : , ( ) ."
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Remove EOF token for comparison
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        expected_types = [
            TokenType.LEFT_BRACE,
            TokenType.RIGHT_BRACE,
            TokenType.LEFT_BRACKET,
            TokenType.RIGHT_BRACKET,
            TokenType.COLON,
            TokenType.COMMA,
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.DOT
        ]
        
        assert len(tokens) == len(expected_types)
        for token, expected_type in zip(tokens, expected_types):
            assert token.type == expected_type
    
    def test_identifiers(self):
        """Test that identifiers are correctly tokenized"""
        source = "user_name counter123 _private"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Remove EOF token for comparison
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.IDENTIFIER and tokens[0].value == "user_name"
        assert tokens[1].type == TokenType.IDENTIFIER and tokens[1].value == "counter123"
        assert tokens[2].type == TokenType.IDENTIFIER and tokens[2].value == "_private"
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly"""
        source = "state\n  user\n    name"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Remove EOF token for comparison
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.STATE
        assert tokens[1].type == TokenType.IDENTIFIER and tokens[1].value == "user"
        assert tokens[2].type == TokenType.IDENTIFIER and tokens[2].value == "name"
    
    def test_simple_whatalang_code(self):
        """Test tokenizing a simple Whatalang program"""
        source = """
        state {
          counter: 0,
          user: { name: "John", age: 30 }
        }
        
        set counter = 1
        print state
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Remove EOF token for comparison
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        # Should have tokens for: state { counter : 0 , user : { name : "John" , age : 30 } } set counter = 1 print state
        assert len(tokens) > 0
        
        # Check first few tokens
        assert tokens[0].type == TokenType.STATE
        assert tokens[1].type == TokenType.LEFT_BRACE
        assert tokens[2].type == TokenType.IDENTIFIER and tokens[2].value == "counter"
    
    def test_error_handling(self):
        """Test that invalid characters raise appropriate errors"""
        source = "state @ invalid"
        lexer = Lexer(source)
        
        with pytest.raises(ValueError) as exc_info:
            lexer.tokenize()
        
        assert "Unexpected character '@'" in str(exc_info.value)
    
    def test_position_tracking(self):
        """Test that line and column positions are tracked correctly"""
        source = "state\n  user"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Remove EOF token for comparison
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        assert tokens[0].line == 1 and tokens[0].column == 1  # "state"
        assert tokens[1].line == 2 and tokens[1].column == 3  # "user"
