import pytest
from whatalang.lexer import Lexer
from whatalang.parser import Parser
from whatalang.state import StateManager, Interpreter


class TestStateManager:
    """Test the StateManager class"""
    
    def test_empty_state(self):
        """Test that new state manager starts empty"""
        sm = StateManager()
        assert sm.get_state() == {}
    
    def test_simple_set_get(self):
        """Test basic set and get operations"""
        sm = StateManager()
        sm.set(["counter"], 42)
        assert sm.get(["counter"]) == 42
    
    def test_nested_set_get(self):
        """Test nested path operations"""
        sm = StateManager()
        sm.set(["user", "name"], "John")
        sm.set(["user", "age"], 30)
        
        assert sm.get(["user", "name"]) == "John"
        assert sm.get(["user", "age"]) == 30
        assert sm.get(["user"]) == {"name": "John", "age": 30}
    
    def test_array_operations(self):
        """Test array operations"""
        sm = StateManager()
        sm.set(["numbers"], [1, 2, 3])
        sm.set(["numbers", "1"], 99)
        
        assert sm.get(["numbers"]) == [1, 99, 3]
        assert sm.get(["numbers", "0"]) == 1
        assert sm.get(["numbers", "2"]) == 3
    
    def test_delete_operations(self):
        """Test delete operations"""
        sm = StateManager()
        sm.set(["user", "name"], "John")
        sm.set(["user", "age"], 30)
        
        sm.delete(["user", "age"])
        assert sm.get(["user"]) == {"name": "John"}
        
        # Test deleting non-existent key
        with pytest.raises(KeyError):
            sm.delete(["user", "age"])
    
    def test_error_handling(self):
        """Test error handling for invalid operations"""
        sm = StateManager()
        
        # Test empty path
        with pytest.raises(ValueError):
            sm.set([], "value")
        
        # Test invalid path
        with pytest.raises(KeyError):
            sm.get(["nonexistent"])
        
        # Test array index out of bounds
        sm.set(["numbers"], [1, 2, 3])
        with pytest.raises(IndexError):
            sm.get(["numbers", "5"])
    
    def test_state_copying(self):
        """Test that state is properly copied"""
        sm = StateManager()
        sm.set(["counter"], 42)
        
        state_copy = sm.get_state()
        state_copy["counter"] = 99
        
        # Original state should be unchanged
        assert sm.get(["counter"]) == 42


class TestInterpreter:
    """Test the Interpreter class"""
    
    def test_empty_program(self):
        """Test executing an empty program"""
        interpreter = Interpreter()
        
        # Create empty program
        from whatalang.parser import Program
        program = Program([])
        
        output = interpreter.execute(program)
        assert output == []
        assert interpreter.get_state() == {}
    
    def test_simple_state_declaration(self):
        """Test executing a simple state declaration"""
        source = "state { counter: 0, name: \"test\" }"
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        assert "State initialized with 2 key-value pairs" in output
        assert interpreter.get_state() == {"counter": 0, "name": "test"}
    
    def test_nested_state_declaration(self):
        """Test executing nested state declarations"""
        source = """
        state {
          user: {
            name: "John",
            age: 30
          },
          settings: {
            theme: "dark"
          }
        }
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        expected_state = {
            "user": {"name": "John", "age": 30},
            "settings": {"theme": "dark"}
        }
        
        assert interpreter.get_state() == expected_state
    
    def test_set_statements(self):
        """Test executing set statements"""
        source = """
        state { counter: 0 }
        set counter = 42
        set counter = 99
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        assert "Set counter = 42" in output
        assert "Set counter = 99" in output
        assert interpreter.get_state()["counter"] == 99
    
    def test_nested_set_statements(self):
        """Test executing nested set statements"""
        source = """
        state { user: { name: "John" } }
        set user.name = "Jane"
        set user.age = 25
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        expected_state = {
            "user": {"name": "Jane", "age": 25}
        }
        
        assert interpreter.get_state() == expected_state
        assert "Set user.name = Jane" in output
        assert "Set user.age = 25" in output
    
    def test_print_statements(self):
        """Test executing print statements"""
        source = """
        state { counter: 42, name: "test" }
        print counter
        print name
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        assert "counter: 42" in output
        assert "name: test" in output
    
    def test_print_state(self):
        """Test printing the entire state"""
        source = """
        state { 
          counter: 42, 
          user: { name: "John" } 
        }
        print state
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        assert "Current state:" in output
        assert "  counter: 42" in output
        assert "  user: {'name': 'John'}" in output
    
    def test_complex_program(self):
        """Test executing a complex program"""
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
        set user.preferences.0 = "tea"
        
        print state
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        # Check final state
        final_state = interpreter.get_state()
        assert final_state["counter"] == 1
        assert final_state["user"]["name"] == "Jane"
        assert final_state["user"]["preferences"][0] == "tea"
        
        # Check output
        assert "Set counter = 1" in output
        assert "Set user.name = Jane" in output
        assert "Current state:" in output
    
    def test_error_handling(self):
        """Test that interpreter handles errors gracefully"""
        source = """
        state { counter: 0 }
        set counter = "invalid_type"
        print counter
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = Interpreter()
        output = interpreter.execute(program)
        
        # Should not crash, should handle errors gracefully
        assert len(output) > 0
        assert interpreter.get_state() == {"counter": "invalid_type"}
        # Should have output from the print statement
        assert any("counter:" in line for line in output)
    
    def test_interpreter_reset(self):
        """Test that interpreter can be reset"""
        interpreter = Interpreter()
        
        # Set some state
        source = "state { counter: 42 }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter.execute(program)
        assert interpreter.get_state() == {"counter": 42}
        
        # Reset
        interpreter.reset()
        assert interpreter.get_state() == {}
        assert interpreter.output == []
