"""
Whatalang Parser - Converts tokens into Abstract Syntax Tree (AST)
"""

from typing import List, Optional, Union
from .lexer import Token, TokenType


class ASTNode:
    """Base class for all AST nodes"""
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Program(ASTNode):
    """Represents a complete Whatalang program"""
    
    def __init__(self, statements: List['Statement']):
        self.statements = statements
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


class Statement(ASTNode):
    """Base class for all statements"""
    pass


class ReactStatement(Statement):
    """Represents a reactive statement"""
    
    def __init__(self, target: 'Expression', conditions: List['ReactiveCondition'], actions: List['Statement']):
        self.target = target
        self.conditions = conditions
        self.actions = actions
    
    def __repr__(self):
        return f"ReactStatement({self.target}, {len(self.conditions)} conditions, {len(self.actions)} actions)"


class ReactiveCondition(ASTNode):
    """Represents a reactive condition"""
    
    def __init__(self, operator: str, value: 'Expression', actions: List['Statement']):
        self.operator = operator
        self.value = value
        self.actions = actions
    
    def __repr__(self):
        return f"ReactiveCondition({self.operator} {self.value}, {len(self.actions)} actions)"


class ReactiveAction(ASTNode):
    """Represents a reactive action"""
    
    def __init__(self, action_type: str, target: 'Expression', value: 'Expression'):
        self.action_type = action_type
        self.target = target
        self.value = value
    
    def __repr__(self):
        return f"ReactiveAction({self.action_type} {self.target} = {self.value})"


class StateDeclaration(Statement):
    """Represents a state declaration"""
    
    def __init__(self, key_value_pairs: List['KeyValuePair']):
        self.key_value_pairs = key_value_pairs
    
    def __repr__(self):
        return f"StateDeclaration({len(self.key_value_pairs)} pairs)"


class KeyValuePair(ASTNode):
    """Represents a key-value pair in state"""
    
    def __init__(self, key: str, value: 'Value'):
        self.key = key
        self.value = value
    
    def __repr__(self):
        return f"KeyValuePair({self.key}: {self.value})"


class SetStatement(Statement):
    """Represents a set statement"""
    
    def __init__(self, path: 'Path', value: 'Expression'):
        self.path = path
        self.value = value
    
    def __repr__(self):
        return f"SetStatement({self.path} = {self.value})"


class PrintStatement(Statement):
    """Represents a print statement"""
    
    def __init__(self, expression: 'Expression'):
        self.expression = expression
    
    def __repr__(self):
        return f"PrintStatement({self.expression})"


class Value(ASTNode):
    """Base class for all values"""
    pass


class Literal(Value):
    """Represents a literal value"""
    
    def __init__(self, value: Union[str, int, float, bool, None], literal_type: str):
        self.value = value
        self.literal_type = literal_type
    
    def __repr__(self):
        return f"Literal({self.value}, {self.literal_type})"


class Object(Value):
    """Represents an object value"""
    
    def __init__(self, key_value_pairs: List[KeyValuePair]):
        self.key_value_pairs = key_value_pairs
    
    def __repr__(self):
        return f"Object({len(self.key_value_pairs)} pairs)"


class Array(Value):
    """Represents an array value"""
    
    def __init__(self, elements: List[Value]):
        self.elements = elements
    
    def __repr__(self):
        return f"Array({len(self.elements)} elements)"


class Path(ASTNode):
    """Represents a path to a value in state"""
    
    def __init__(self, parts: List[Union[str, 'Expression']]):
        self.parts = parts
    
    def __repr__(self):
        return f"Path({self.parts})"


class Expression(ASTNode):
    """Base class for expressions"""
    pass


class Identifier(Expression):
    """Represents an identifier"""
    
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"


class Parser:
    """Parser for Whatalang"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Program:
        """Parse tokens into an AST"""
        statements = []
        
        while not self._is_at_end():
            statement = self._parse_statement()
            if statement:
                statements.append(statement)
        
        return Program(statements)
    
    def _parse_statement(self) -> Optional[Statement]:
        """Parse a single statement"""
        if self._match(TokenType.STATE):
            return self._parse_state_declaration()
        elif self._match(TokenType.SET):
            return self._parse_set_statement()
        elif self._match(TokenType.PRINT):
            return self._parse_print_statement()
        elif self._match(TokenType.REACT):
            return self._parse_react_statement()
        else:
            # Skip unknown tokens for now
            self._advance()
            return None
    
    def _parse_state_declaration(self) -> StateDeclaration:
        """Parse a state declaration"""
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'state'")
        
        key_value_pairs = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            if self._check(TokenType.IDENTIFIER):
                key_value_pairs.append(self._parse_key_value_pair())
            else:
                self._advance()  # Skip unexpected tokens
        
        # Try to consume the closing brace, but don't crash if it's missing
        try:
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after state declaration")
        except ValueError:
            # If we can't find the closing brace, just continue
            pass
        
        return StateDeclaration(key_value_pairs)
    
    def _parse_key_value_pair(self) -> KeyValuePair:
        """Parse a key-value pair"""
        key = self._consume(TokenType.IDENTIFIER, "Expected identifier as key").value
        self._consume(TokenType.COLON, "Expected ':' after key")
        value = self._parse_value()
        
        # If value parsing failed, create a placeholder
        if value is None:
            value = Literal("", "unknown")
        
        # Handle trailing comma
        if self._match(TokenType.COMMA):
            pass
        
        return KeyValuePair(key, value)
    
    def _parse_value(self) -> Value:
        """Parse a value"""
        if self._check(TokenType.LEFT_BRACE):
            return self._parse_object()
        elif self._check(TokenType.LEFT_BRACKET):
            return self._parse_array()
        elif self._check(TokenType.STRING):
            token = self._advance()
            return Literal(token.value.strip('"\''), "string")
        elif self._check(TokenType.NUMBER):
            token = self._advance()
            try:
                if '.' in token.value:
                    return Literal(float(token.value), "float")
                else:
                    return Literal(int(token.value), "integer")
            except ValueError:
                return Literal(token.value, "number")
        elif self._check(TokenType.BOOLEAN):
            token = self._advance()
            return Literal(token.value == "true", "boolean")
        elif self._check(TokenType.NULL):
            self._advance()
            return Literal(None, "null")
        elif self._check(TokenType.IDENTIFIER):
            token = self._advance()
            return Identifier(token.value)
        else:
            # Skip unexpected tokens instead of treating them as literals
            self._advance()
            return None
    
    def _parse_object(self) -> Object:
        """Parse an object"""
        self._consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        key_value_pairs = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            if self._check(TokenType.IDENTIFIER):
                key_value_pairs.append(self._parse_key_value_pair())
            else:
                self._advance()
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after object")
        return Object(key_value_pairs)
    
    def _parse_array(self) -> Array:
        """Parse an array"""
        self._consume(TokenType.LEFT_BRACKET, "Expected '['")
        
        elements = []
        while not self._check(TokenType.RIGHT_BRACKET) and not self._is_at_end():
            elements.append(self._parse_value())
            
            if self._match(TokenType.COMMA):
                continue
            else:
                break
        
        self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after array")
        return Array(elements)
    
    def _parse_set_statement(self) -> SetStatement:
        """Parse a set statement"""
        path = self._parse_path()
        self._consume(TokenType.EQUALS, "Expected '=' in set statement")
        value = self._parse_expression()
        return SetStatement(path, value)
    
    def _parse_print_statement(self) -> PrintStatement:
        """Parse a print statement"""
        expression = self._parse_expression()
        return PrintStatement(expression)
    
    def _parse_react_statement(self) -> ReactStatement:
        """Parse a reactive statement"""
        self._consume(TokenType.TO, "Expected 'to' after 'react'")
        target = self._parse_path()  # Use path parsing instead of expression
        
        conditions = []
        actions = []
        
        # Parse conditions and actions
        while not self._is_at_end():
            if self._match(TokenType.WHEN):
                condition = self._parse_reactive_condition()
                conditions.append(condition)
            elif self._match(TokenType.DEFAULT):
                # Parse default actions
                actions = self._parse_reactive_actions()
                break
            elif self._check(TokenType.LEFT_BRACE):
                # If we see a brace, we're done parsing conditions
                break
            else:
                break
        
        return ReactStatement(target, conditions, actions)
    
    def _parse_reactive_condition(self) -> ReactiveCondition:
        """Parse a reactive condition"""
        # Parse the condition (e.g., "> 10", "== 'active'")
        operator = ""
        value = None
        
        if self._check(TokenType.GREATER):
            operator = ">"
            self._advance()
        elif self._check(TokenType.LESS):
            operator = "<"
            self._advance()
        elif self._check(TokenType.EQUAL_EQUAL):
            operator = "=="
            self._advance()
        elif self._check(TokenType.NOT_EQUAL):
            operator = "!="
            self._advance()
        elif self._check(TokenType.GREATER_EQUAL):
            operator = ">="
            self._advance()
        elif self._check(TokenType.LESS_EQUAL):
            operator = "<="
            self._advance()
        else:
            # Default to equals
            operator = "=="
        
        value = self._parse_expression()
        
        # Parse actions for this condition
        actions = self._parse_reactive_actions()
        
        return ReactiveCondition(operator, value, actions)
    
    def _parse_reactive_actions(self) -> List[Statement]:
        """Parse reactive actions"""
        actions = []
        
        # Expect opening brace
        self._consume(TokenType.LEFT_BRACE, "Expected '{' for reactive actions")
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            if self._match(TokenType.SET):
                actions.append(self._parse_set_statement())
            elif self._match(TokenType.PRINT):
                actions.append(self._parse_print_statement())
            else:
                self._advance()  # Skip unknown actions
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after reactive actions")
        return actions
    
    def _parse_path(self) -> Path:
        """Parse a path"""
        parts = []
        
        if self._check(TokenType.IDENTIFIER):
            parts.append(self._advance().value)
            
            while not self._is_at_end():
                if self._match(TokenType.DOT):
                    if self._check(TokenType.IDENTIFIER):
                        parts.append(self._advance().value)
                    elif self._check(TokenType.NUMBER):
                        # Allow numeric parts for array indices like "preferences.0"
                        parts.append(self._advance().value)
                    else:
                        break
                elif self._match(TokenType.LEFT_BRACKET):
                    parts.append(self._parse_expression())
                    self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after array index")
                else:
                    break
        
        return Path(parts)
    
    def _parse_expression(self) -> Expression:
        """Parse an expression (simplified for now)"""
        if self._check(TokenType.IDENTIFIER):
            return Identifier(self._advance().value)
        elif self._check(TokenType.STATE):
            # Allow 'state' keyword to be used as an identifier in expressions
            return Identifier(self._advance().value)
        else:
            value = self._parse_value()
            if value is None:
                # If value parsing failed, return a placeholder
                return Identifier("unknown")
            return value
    
    # Helper methods
    def _match(self, token_type: TokenType) -> bool:
        """Match and consume a token if it matches the expected type"""
        if self._check(token_type):
            self._advance()
            return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token matches the expected type"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Advance to next token"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _peek(self) -> Token:
        """Peek at current token without consuming it"""
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Get the previous token"""
        return self.tokens[self.current - 1]
    
    def _is_at_end(self) -> bool:
        """Check if we've reached the end of tokens"""
        return self._peek().type == TokenType.EOF
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume a token of the expected type or raise an error"""
        if self._check(token_type):
            return self._advance()
        
        raise ValueError(f"{message} at line {self._peek().line}, column {self._peek().column}")
