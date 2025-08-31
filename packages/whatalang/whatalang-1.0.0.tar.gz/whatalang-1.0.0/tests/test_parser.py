import pytest
from whatalang.lexer import Lexer, TokenType
from whatalang.parser import Parser, Program, StateDeclaration, KeyValuePair, SetStatement, PrintStatement, Literal, Object, Array, Identifier, Path


class TestParser:
    """Test the Whatalang parser"""
    
    def test_empty_program(self):
        """Test parsing an empty program"""
        source = ""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert isinstance(ast, Program)
        assert len(ast.statements) == 0
    
    def test_simple_state_declaration(self):
        """Test parsing a simple state declaration"""
        source = "state { counter: 0 }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert isinstance(ast, Program)
        assert len(ast.statements) == 1
        
        statement = ast.statements[0]
        assert isinstance(statement, StateDeclaration)
        assert len(statement.key_value_pairs) == 1
        
        kvp = statement.key_value_pairs[0]
        assert isinstance(kvp, KeyValuePair)
        assert kvp.key == "counter"
        assert isinstance(kvp.value, Literal)
        assert kvp.value.value == 0
        assert kvp.value.literal_type == "integer"
    
    def test_state_with_multiple_values(self):
        """Test parsing state with multiple key-value pairs"""
        source = """
        state {
          counter: 0,
          name: "test",
          active: true
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert isinstance(ast, Program)
        assert len(ast.statements) == 1
        
        statement = ast.statements[0]
        assert isinstance(statement, StateDeclaration)
        assert len(statement.key_value_pairs) == 3
        
        # Check counter
        assert statement.key_value_pairs[0].key == "counter"
        assert statement.key_value_pairs[0].value.value == 0
        
        # Check name
        assert statement.key_value_pairs[1].key == "name"
        assert statement.key_value_pairs[1].value.value == "test"
        
        # Check active
        assert statement.key_value_pairs[2].key == "active"
        assert statement.key_value_pairs[2].value.value is True
    
    def test_nested_objects(self):
        """Test parsing nested objects in state"""
        source = """
        state {
          user: {
            name: "John",
            age: 30
          }
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        statement = ast.statements[0]
        kvp = statement.key_value_pairs[0]
        
        assert kvp.key == "user"
        assert isinstance(kvp.value, Object)
        assert len(kvp.value.key_value_pairs) == 2
        
        # Check nested name
        assert kvp.value.key_value_pairs[0].key == "name"
        assert kvp.value.key_value_pairs[0].value.value == "John"
        
        # Check nested age
        assert kvp.value.key_value_pairs[1].key == "age"
        assert kvp.value.key_value_pairs[1].value.value == 30
    
    def test_arrays(self):
        """Test parsing arrays in state"""
        source = """
        state {
          numbers: [1, 2, 3],
          names: ["Alice", "Bob"]
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        statement = ast.statements[0]
        
        # Check numbers array
        numbers_kvp = statement.key_value_pairs[0]
        assert numbers_kvp.key == "numbers"
        assert isinstance(numbers_kvp.value, Array)
        assert len(numbers_kvp.value.elements) == 3
        assert numbers_kvp.value.elements[0].value == 1
        assert numbers_kvp.value.elements[1].value == 2
        assert numbers_kvp.value.elements[2].value == 3
        
        # Check names array
        names_kvp = statement.key_value_pairs[1]
        assert names_kvp.key == "names"
        assert isinstance(names_kvp.value, Array)
        assert len(names_kvp.value.elements) == 2
        assert names_kvp.value.elements[0].value == "Alice"
        assert names_kvp.value.elements[1].value == "Bob"
    
    def test_set_statement(self):
        """Test parsing set statements"""
        source = "set counter = 42"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.statements) == 1
        statement = ast.statements[0]
        
        assert isinstance(statement, SetStatement)
        assert isinstance(statement.path, Path)
        assert statement.path.parts == ["counter"]
        assert isinstance(statement.value, Literal)
        assert statement.value.value == 42
    
    def test_set_statement_with_path(self):
        """Test parsing set statements with complex paths"""
        source = "set user.name = \"Jane\""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        statement = ast.statements[0]
        assert isinstance(statement, SetStatement)
        
        path = statement.path
        assert len(path.parts) == 2
        assert path.parts[0] == "user"
        assert path.parts[1] == "name"
        
        assert statement.value.value == "Jane"
    
    def test_print_statement(self):
        """Test parsing print statements"""
        source = "print state"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.statements) == 1
        statement = ast.statements[0]
        
        assert isinstance(statement, PrintStatement)
        assert isinstance(statement.expression, Identifier)
        assert statement.expression.name == "state"
    
    def test_complex_program(self):
        """Test parsing a complex program with multiple statements"""
        source = """
        state {
          counter: 0,
          user: {
            name: "John",
            preferences: ["coffee", "books"]
          }
        }
        
        set counter = 1
        set user.name = "Jane"
        print state
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert isinstance(ast, Program)
        assert len(ast.statements) == 4
        
        # Check state declaration
        assert isinstance(ast.statements[0], StateDeclaration)
        
        # Check set statements
        assert isinstance(ast.statements[1], SetStatement)
        assert isinstance(ast.statements[2], SetStatement)
        
        # Check print statement
        assert isinstance(ast.statements[3], PrintStatement)
    
    def test_literal_types(self):
        """Test parsing different literal types"""
        source = """
        state {
          string_val: "hello",
          int_val: 42,
          float_val: 3.14,
          bool_val: true,
          null_val: null
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        statement = ast.statements[0]
        pairs = statement.key_value_pairs
        
        # Check string
        assert pairs[0].value.literal_type == "string"
        assert pairs[0].value.value == "hello"
        
        # Check integer
        assert pairs[1].value.literal_type == "integer"
        assert pairs[1].value.value == 42
        
        # Check float
        assert pairs[2].value.literal_type == "float"
        assert pairs[2].value.value == 3.14
        
        # Check boolean
        assert pairs[3].value.literal_type == "boolean"
        assert pairs[3].value.value is True
        
        # Check null
        assert pairs[4].value.literal_type == "null"
        assert pairs[4].value.value is None
    
    def test_error_handling(self):
        """Test that parser handles errors gracefully"""
        source = "state { counter: }"  # Missing value
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        
        # Should not crash, but may produce incomplete AST
        ast = parser.parse()
        assert isinstance(ast, Program)
