import pytest
from whatalang.lexer import Lexer
from whatalang.parser import Parser, ReactStatement, ReactiveCondition, Path, Literal, SetStatement, PrintStatement, Identifier
from whatalang.reactive import ReactiveEngine, ReactiveInterpreter
from whatalang.state import StateManager


class TestReactiveEngine:
    """Test the reactive engine functionality"""
    
    def test_condition_evaluation(self):
        """Test that conditions are evaluated correctly"""
        state_manager = StateManager()
        reactive_engine = ReactiveEngine(state_manager)
        
        # Test various operators
        assert reactive_engine.evaluate_condition(
            ReactiveCondition(">", 10, []), 15
        ) is True
        
        assert reactive_engine.evaluate_condition(
            ReactiveCondition("<", 10, []), 5
        ) is True
        
        assert reactive_engine.evaluate_condition(
            ReactiveCondition("==", "active", []), "active"
        ) is True
        
        assert reactive_engine.evaluate_condition(
            ReactiveCondition("!=", "inactive", []), "active"
        ) is True
        
        assert reactive_engine.evaluate_condition(
            ReactiveCondition(">=", 10, []), 10
        ) is True
        
        assert reactive_engine.evaluate_condition(
            ReactiveCondition("<=", 10, []), 5
        ) is True
    
    def test_path_matching(self):
        """Test that reactive paths match changed paths correctly"""
        state_manager = StateManager()
        reactive_engine = ReactiveEngine(state_manager)
        
        # Exact matches
        assert reactive_engine._paths_match(["counter"], ["counter"]) is True
        assert reactive_engine._paths_match(["user", "age"], ["user", "age"]) is True
        
        # Prefix matches (parent changes trigger child reactions)
        assert reactive_engine._paths_match(["user", "age"], ["user"]) is True
        assert reactive_engine._paths_match(["user", "profile", "name"], ["user"]) is True
        
        # No matches
        assert reactive_engine._paths_match(["counter"], ["status"]) is False
        assert reactive_engine._paths_match(["user", "age"], ["counter"]) is False
    
    def test_reactive_statement_evaluation(self):
        """Test that reactive statements are evaluated correctly"""
        state_manager = StateManager()
        reactive_engine = ReactiveEngine(state_manager)
        
        # Set up some state
        state_manager.set(["counter"], 5)
        
        # Mock a reactive statement: react to counter when > 10 { set status = "high" }
        # Create a mock action
        mock_action = SetStatement(Path(["status"]), Literal("high", "string"))
        condition = ReactiveCondition(">", Literal(10, "integer"), [mock_action])
        target = Path(["counter"])
        react_statement = ReactStatement(target, [condition], [])
        
        # Register the reactive statement
        state_manager.register_reactive(react_statement)
        
        # Check if it triggers when counter changes
        triggered = reactive_engine.check_reactive_statements(["counter"])
        
        # Should not trigger because counter (5) is not > 10
        assert len(triggered) == 0
        
        # Change counter to trigger the condition
        state_manager.set(["counter"], 15)
        triggered = reactive_engine.check_reactive_statements(["counter"])
        
        # Should now trigger because counter (15) is > 10
        assert len(triggered) > 0


class TestReactiveInterpreter:
    """Test the reactive interpreter functionality"""
    
    def test_simple_reactive_program(self):
        """Test executing a simple reactive program"""
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
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Check that reactive statement was registered
        assert "📝 Registered reactive statement for counter" in output
        
        # Check that reactive trigger was activated
        assert any("🔄 Reactive trigger:" in line for line in output)
        
        # Check final state
        final_state = interpreter.get_state()
        assert final_state["counter"] == 10
        assert final_state["status"] == "high"
    
    def test_multiple_reactive_conditions(self):
        """Test programs with multiple reactive conditions"""
        source = """
        state { counter: 0, status: "normal" }
        
        react to counter when > 10 {
          set status = "high"
        }
        when < 0 {
          set status = "negative"
        }
        
        set counter = 15
        print status
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Check final state
        final_state = interpreter.get_state()
        assert final_state["counter"] == 15
        assert final_state["status"] == "high"
        
        # Reset and test negative condition
        interpreter.reset()
        output = interpreter.execute(program)
        
        # Change to negative value
        interpreter.state_manager.set(["counter"], -5)
        triggered = interpreter.reactive_engine.check_reactive_statements(["counter"])
        
        # Should trigger negative condition
        assert len(triggered) > 0
    
    def test_nested_path_reactivity(self):
        """Test reactive statements with nested paths"""
        source = """
        state { 
          user: { 
            age: 25,
            status: "active"
          }
        }
        
        react to user.age when >= 18 {
          set user.status = "adult"
        }
        
        set user.age = 30
        print user.status
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Check final state
        final_state = interpreter.get_state()
        assert final_state["user"]["age"] == 30
        assert final_state["user"]["status"] == "adult"
    
    def test_reactive_chain(self):
        """Test that reactive actions can trigger other reactive statements"""
        source = """
        state { 
          counter: 0,
          status: "normal",
          level: "beginner"
        }
        
        react to counter when > 10 {
          set status = "high"
        }
        
        react to status when == "high" {
          set level = "expert"
        }
        
        set counter = 15
        print level
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Check final state - should have triggered both reactive statements
        final_state = interpreter.get_state()
        assert final_state["counter"] == 15
        assert final_state["status"] == "high"
        assert final_state["level"] == "expert"
        
        # Should have multiple reactive triggers
        reactive_triggers = [line for line in output if "🔄 Reactive trigger:" in line]
        assert len(reactive_triggers) >= 2
    
    def test_reactive_error_handling(self):
        """Test that reactive engine handles errors gracefully"""
        source = """
        state { counter: 0 }
        
        react to counter when > 10 {
          set nonexistent = "value"
        }
        
        set counter = 15
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Should not crash, should handle errors gracefully
        assert len(output) > 0
        assert interpreter.get_state()["counter"] == 15
    
    def test_reactive_reset(self):
        """Test that reactive interpreter can be reset"""
        source = """
        state { counter: 0 }
        
        react to counter when > 5 {
          set status = "high"
        }
        
        set counter = 10
        """
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        interpreter = ReactiveInterpreter()
        output = interpreter.execute(program)
        
        # Check that reactive statements were registered
        assert len(interpreter.state_manager.get_reactive_statements()) > 0
        
        # Reset
        interpreter.reset()
        
        # Check that everything was cleared
        assert len(interpreter.state_manager.get_reactive_statements()) == 0
        assert interpreter.get_state() == {}
        assert interpreter.output == []
