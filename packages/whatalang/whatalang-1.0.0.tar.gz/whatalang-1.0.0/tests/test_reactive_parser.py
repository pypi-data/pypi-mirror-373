import pytest
from whatalang.lexer import Lexer
from whatalang.parser import Parser, ReactStatement, ReactiveCondition


class TestReactiveParser:
    """Test the reactive parsing functionality"""
    
    def test_simple_react_statement(self):
        """Test parsing a simple reactive statement"""
        source = """
        react to counter when > 10 {
          set status = "high"
          print "Counter is high!"
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.statements) == 1
        statement = program.statements[0]
        
        assert isinstance(statement, ReactStatement)
        from whatalang.parser import Path
        assert isinstance(statement.target, Path)
        assert statement.target.parts == ["counter"]
        assert len(statement.conditions) == 1
        assert len(statement.actions) == 0  # Actions are in the condition
        
        condition = statement.conditions[0]
        assert isinstance(condition, ReactiveCondition)
        assert condition.operator == ">"
        assert condition.value.value == 10
        assert len(condition.actions) == 2
    
    def test_react_with_multiple_conditions(self):
        """Test parsing reactive statements with multiple conditions"""
        source = """
        react to status when == "active" {
          set indicator = "green"
        }
        when == "inactive" {
          set indicator = "red"
        }
        default {
          set indicator = "yellow"
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.statements) == 1
        statement = program.statements[0]
        
        assert isinstance(statement, ReactStatement)
        from whatalang.parser import Path
        assert isinstance(statement.target, Path)
        assert statement.target.parts == ["status"]
        assert len(statement.conditions) == 2
        assert len(statement.actions) == 1  # Default actions
        
        # Check first condition
        condition1 = statement.conditions[0]
        assert condition1.operator == "=="
        assert condition1.value.value == "active"
        assert len(condition1.actions) == 1
        
        # Check second condition
        condition2 = statement.conditions[1]
        assert condition2.operator == "=="
        assert condition2.value.value == "inactive"
        assert len(condition2.actions) == 1
        
        # Check default actions
        assert len(statement.actions) == 1
    
    def test_react_with_comparison_operators(self):
        """Test parsing reactive statements with different comparison operators"""
        source = """
        react to counter when >= 100 {
          set level = "expert"
        }
        when < 10 {
          set level = "beginner"
        }
        when != 0 {
          set active = true
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.statements) == 1
        statement = program.statements[0]
        
        assert len(statement.conditions) == 3
        
        # Check operators
        assert statement.conditions[0].operator == ">="
        assert statement.conditions[1].operator == "<"
        assert statement.conditions[2].operator == "!="
    
    def test_react_with_complex_expressions(self):
        """Test parsing reactive statements with complex expressions"""
        source = """
        react to user.age when >= 18 {
          set user.adult = true
          set user.permissions = ["read", "write"]
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.statements) == 1
        statement = program.statements[0]
        
        # Check target path
        from whatalang.parser import Path
        assert isinstance(statement.target, Path)
        assert statement.target.parts == ["user", "age"]
        
        # Check condition
        condition = statement.conditions[0]
        assert condition.operator == ">="
        assert condition.value.value == 18
        assert len(condition.actions) == 2
    
    def test_react_integration_with_other_statements(self):
        """Test that reactive statements work alongside other statements"""
        source = """
        state { counter: 0 }
        
        react to counter when > 5 {
          set status = "high"
        }
        
        set counter = 10
        print status
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.statements) == 4
        
        # Check statement types
        from whatalang.parser import StateDeclaration, ReactStatement, SetStatement, PrintStatement
        assert isinstance(program.statements[0], StateDeclaration)
        assert isinstance(program.statements[1], ReactStatement)
        assert isinstance(program.statements[2], SetStatement)
        assert isinstance(program.statements[3], PrintStatement)
    
    def test_react_error_handling(self):
        """Test that reactive parsing handles errors gracefully"""
        source = """
        react to counter when > 10 {
          set status = "high"
        }
        when invalid_condition {
          set status = "error"
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        
        # Should not crash, but may produce incomplete AST
        program = parser.parse()
        from whatalang.parser import Program
        assert isinstance(program, Program)
        assert len(program.statements) > 0
