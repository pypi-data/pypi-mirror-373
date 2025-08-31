"""
Whatalang State Management System - Executes ASTs and manages global state
"""

from typing import Any, Dict, List, Union, Optional
from .parser import (
    Program, Statement, StateDeclaration, KeyValuePair, 
    SetStatement, PrintStatement, ReactStatement, ReactiveCondition,
    Value, Literal, Object, Array, Identifier, Path
)


class StateManager:
    """Manages the global state for Whatalang"""
    
    def __init__(self):
        self.state = {}
        self._reactive_statements = []  # Store reactive statements
        self._reactive_cache = {}  # Cache for reactive evaluations
    
    def get(self, path: List[str]) -> Any:
        """Get a value from state using a path"""
        current = self.state
        
        for part in path:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise IndexError(f"Array index {index} out of bounds")
            else:
                raise KeyError(f"Path {path} not found in state")
        
        return current
    
    def set(self, path: List[str], value: Any) -> None:
        """Set a value in state using a path"""
        if not path:
            raise ValueError("Path cannot be empty")
        
        current = self.state
        
        # Navigate to the parent of the target
        for part in path[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    # Allow creating root-level keys, but not intermediate paths
                    if current is self.state:
                        current[part] = {}
                    else:
                        raise KeyError(f"Cannot create intermediate path {path} - '{part}' not found")
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise IndexError(f"Array index {index} out of bounds")
            else:
                raise TypeError(f"Cannot set path {path} - intermediate value is not dict or array")
        
        # Set the final value
        final_part = path[-1]
        if isinstance(current, dict):
            current[final_part] = value
        elif isinstance(current, list) and final_part.isdigit():
            index = int(final_part)
            if 0 <= index < len(current):
                current[index] = value
            else:
                raise IndexError(f"Array index {index} out of bounds")
        else:
            raise TypeError(f"Cannot set path {path} - target is not dict or array")
    
    def delete(self, path: List[str]) -> None:
        """Delete a value from state using a path"""
        if not path:
            raise ValueError("Path cannot be empty")
        
        current = self.state
        
        # Navigate to the parent of the target
        for part in path[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise IndexError(f"Array index {index} out of bounds")
            else:
                raise KeyError(f"Path {path} not found in state")
        
        # Delete the final value
        final_part = path[-1]
        if isinstance(current, dict) and final_part in current:
            del current[final_part]
        elif isinstance(current, list) and final_part.isdigit():
            index = int(final_part)
            if 0 <= index < len(current):
                del current[index]
            else:
                raise IndexError(f"Array index {index} out of bounds")
        else:
            raise KeyError(f"Path {path} not found in state")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the entire state"""
        return self.state.copy()
    
    def set_state(self, new_state: Dict[str, Any]) -> None:
        """Set the entire state"""
        self.state = new_state.copy()
    
    def clear(self) -> None:
        """Clear the entire state"""
        self.state = {}
        self._reactive_cache = {}
    
    def register_reactive(self, react_statement: ReactStatement) -> None:
        """Register a reactive statement for monitoring"""
        self._reactive_statements.append(react_statement)
    
    def get_reactive_statements(self) -> List[ReactStatement]:
        """Get all registered reactive statements"""
        return self._reactive_statements.copy()
    
    def clear_reactive_statements(self) -> None:
        """Clear all reactive statements"""
        self._reactive_statements = []
        self._reactive_cache = {}
    
    def __repr__(self) -> str:
        return f"StateManager(state={self.state}, reactive={len(self._reactive_statements)})"


class Interpreter:
    """Interprets and executes Whatalang ASTs"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.output = []
    
    def execute(self, program: Program) -> List[str]:
        """Execute a Whatalang program"""
        self.output = []
        
        try:
            for statement in program.statements:
                self._execute_statement(statement)
        except Exception as e:
            self.output.append(f"Error: {e}")
        
        return self.output
    
    def _execute_statement(self, statement: Statement) -> None:
        """Execute a single statement"""
        if isinstance(statement, StateDeclaration):
            self._execute_state_declaration(statement)
        elif isinstance(statement, SetStatement):
            self._execute_set_statement(statement)
        elif isinstance(statement, PrintStatement):
            self._execute_print_statement(statement)
        else:
            self.output.append(f"Warning: Unknown statement type: {type(statement).__name__}")
    
    def _execute_state_declaration(self, declaration: StateDeclaration) -> None:
        """Execute a state declaration"""
        for kvp in declaration.key_value_pairs:
            key = kvp.key
            value = self._evaluate_value(kvp.value)
            self.state_manager.set([key], value)
        
        self.output.append(f"State initialized with {len(declaration.key_value_pairs)} key-value pairs")
    
    def _execute_set_statement(self, set_stmt: SetStatement) -> None:
        """Execute a set statement"""
        path = self._evaluate_path(set_stmt.path)
        value = self._evaluate_value(set_stmt.value)
        
        try:
            self.state_manager.set(path, value)
            self.output.append(f"Set {'.'.join(str(p) for p in path)} = {value}")
        except (KeyError, IndexError, TypeError) as e:
            self.output.append(f"Warning: Could not set {'.'.join(str(p) for p in path)}: {e}")
    
    def _execute_print_statement(self, print_stmt: PrintStatement) -> None:
        """Execute a print statement"""
        if isinstance(print_stmt.expression, Identifier):
            if print_stmt.expression.name == "state":
                # Special case: print the entire state
                state = self.state_manager.get_state()
                self.output.append("Current state:")
                self._print_state_recursive(state, indent=2)
            else:
                # Print a specific value
                try:
                    value = self.state_manager.get([print_stmt.expression.name])
                    self.output.append(f"{print_stmt.expression.name}: {value}")
                except KeyError:
                    self.output.append(f"Error: '{print_stmt.expression.name}' not found in state")
        else:
            # Print the evaluated expression
            value = self._evaluate_value(print_stmt.expression)
            self.output.append(str(value))
    
    def _evaluate_path(self, path: Path) -> List[str]:
        """Evaluate a path to a list of strings"""
        result = []
        
        for part in path.parts:
            if isinstance(part, str):
                result.append(part)
            elif isinstance(part, Identifier):
                result.append(part.name)
            else:
                # For array indices, evaluate the expression
                value = self._evaluate_value(part)
                result.append(str(value))
        
        return result
    
    def _evaluate_value(self, value: Value) -> Any:
        """Evaluate a value to its actual value"""
        if isinstance(value, Literal):
            return value.value
        elif isinstance(value, Object):
            result = {}
            for kvp in value.key_value_pairs:
                result[kvp.key] = self._evaluate_value(kvp.value)
            return result
        elif isinstance(value, Array):
            return [self._evaluate_value(element) for element in value.elements]
        elif isinstance(value, Identifier):
            try:
                return self.state_manager.get([value.name])
            except KeyError:
                self.output.append(f"Warning: Identifier '{value.name}' not found, using as string")
                return value.name
        else:
            return str(value)
    
    def _print_state_recursive(self, state: Any, indent: int = 0) -> None:
        """Recursively print the state with proper indentation"""
        if isinstance(state, dict):
            for key, value in state.items():
                self.output.append(" " * indent + f"{key}: {value}")
                if isinstance(value, (dict, list)):
                    self._print_state_recursive(value, indent + 2)
        elif isinstance(state, list):
            for i, value in enumerate(state):
                self.output.append(" " * indent + f"[{i}]: {value}")
                if isinstance(value, (dict, list)):
                    self._print_state_recursive(value, indent + 2)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state"""
        return self.state_manager.get_state()
    
    def reset(self) -> None:
        """Reset the interpreter state"""
        self.state_manager.clear()
        self.output = []
