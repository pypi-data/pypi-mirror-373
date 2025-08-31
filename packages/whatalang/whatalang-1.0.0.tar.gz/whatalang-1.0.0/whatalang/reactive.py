"""
Whatalang Reactive Engine - Automatically executes actions when conditions are met
"""

from typing import Any, List, Dict, Optional
from .parser import (
    ReactStatement, ReactiveCondition, Statement, StateDeclaration, 
    SetStatement, PrintStatement, Identifier, Path, Literal, Object, Array
)
from .state import StateManager


class ReactiveEngine:
    """Engine for evaluating and executing reactive statements"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.execution_history = []
    
    def evaluate_condition(self, condition: ReactiveCondition, target_value: Any) -> bool:
        """Evaluate if a reactive condition is met"""
        try:
            condition_value = self._evaluate_expression(condition.value)
            operator = condition.operator
            
            if operator == "==":
                return target_value == condition_value
            elif operator == "!=":
                return target_value != condition_value
            elif operator == ">":
                return target_value > condition_value
            elif operator == "<":
                return target_value < condition_value
            elif operator == ">=":
                return target_value >= condition_value
            elif operator == "<=":
                return target_value <= condition_value
            else:
                # Default to equals
                return target_value == condition_value
        except Exception as e:
            # If evaluation fails, condition is not met
            return False
    
    def _evaluate_expression(self, expression) -> Any:
        """Evaluate an expression to its value"""
        if hasattr(expression, 'value'):
            return expression.value
        elif hasattr(expression, 'name'):
            # For identifiers, try to get from state
            try:
                return self.state_manager.get([expression.name])
            except KeyError:
                return None
        else:
            return expression
    
    def check_reactive_statements(self, changed_path: List[str]) -> List[Dict[str, Any]]:
        """Check all reactive statements for triggered conditions"""
        triggered_actions = []
        
        for react_statement in self.state_manager.get_reactive_statements():
            # Check if this reactive statement monitors the changed path
            if self._paths_match(react_statement.target.parts, changed_path):
                triggered = self._evaluate_reactive_statement(react_statement)
                if triggered:
                    triggered_actions.extend(triggered)
        
        return triggered_actions
    
    def _paths_match(self, reactive_path: List[str], changed_path: List[str]) -> bool:
        """Check if a reactive path matches a changed path"""
        # Exact match
        if reactive_path == changed_path:
            return True
        
        # Check if changed path is a prefix of reactive path
        # e.g., reactive_path = ["user", "age"], changed_path = ["user"]
        if len(changed_path) < len(reactive_path):
            return changed_path == reactive_path[:len(changed_path)]
        
        return False
    
    def _evaluate_reactive_statement(self, react_statement: ReactStatement) -> List[Dict[str, Any]]:
        """Evaluate a reactive statement and return triggered actions"""
        triggered_actions = []
        
        # Get the current value of the target
        try:
            target_value = self.state_manager.get(react_statement.target.parts)
        except KeyError:
            # Target doesn't exist, can't evaluate
            return triggered_actions
        
        # Check each condition
        for condition in react_statement.conditions:
            if self.evaluate_condition(condition, target_value):
                # Condition met! Add actions to triggered list
                for action in condition.actions:
                    triggered_actions.append({
                        'type': 'reactive',
                        'condition': condition,
                        'action': action,
                        'target_value': target_value,
                        'condition_value': self._evaluate_expression(condition.value)
                    })
        
        return triggered_actions
    
    def execute_reactive_actions(self, triggered_actions: List[Dict[str, Any]]) -> List[str]:
        """Execute triggered reactive actions and return output"""
        output = []
        
        for triggered in triggered_actions:
            action = triggered['action']
            condition = triggered['condition']
            
            output.append(f"🔄 Reactive trigger: {'.'.join(triggered.get('target_path', ['unknown']))} {condition.operator} {triggered['condition_value']}")
            
            # Execute the action (this will be handled by the interpreter)
            output.append(f"  → Executing: {type(action).__name__}")
        
        return output
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the history of reactive executions"""
        return self.execution_history.copy()
    
    def clear_history(self) -> None:
        """Clear the execution history"""
        self.execution_history = []


class ReactiveInterpreter:
    """Enhanced interpreter with reactive capabilities"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.reactive_engine = ReactiveEngine(self.state_manager)
        self.output = []
    
    def execute(self, program) -> List[str]:
        """Execute a Whatalang program with reactive capabilities"""
        self.output = []
        
        try:
            # First pass: register all reactive statements
            for statement in program.statements:
                if isinstance(statement, ReactStatement):
                    self.state_manager.register_reactive(statement)
                    self.output.append(f"📝 Registered reactive statement for {'.'.join(statement.target.parts)}")
            
            # Second pass: execute all non-reactive statements
            for statement in program.statements:
                if isinstance(statement, ReactStatement):
                    # Skip reactive statements in execution (they're already registered)
                    continue
                else:
                    self._execute_statement(statement)
                    
                    # Check for reactive triggers after each state change
                    if isinstance(statement, SetStatement):
                        path = self._evaluate_path(statement.path)
                        triggered = self.reactive_engine.check_reactive_statements(path)
                        if triggered:
                            reactive_output = self.reactive_engine.execute_reactive_actions(triggered)
                            self.output.extend(reactive_output)
                            
                            # Execute the triggered actions and check for chained reactions
                            for trigger in triggered:
                                self._execute_statement(trigger['action'])
                                
                                # Check if this reactive action triggered other reactions
                                if isinstance(trigger['action'], SetStatement):
                                    action_path = self._evaluate_path(trigger['action'].path)
                                    chained_triggered = self.reactive_engine.check_reactive_statements(action_path)
                                    if chained_triggered:
                                        chained_output = self.reactive_engine.execute_reactive_actions(chained_triggered)
                                        self.output.extend(chained_output)
                                        
                                        # Execute chained actions (recursive, but limited depth)
                                        for chained_trigger in chained_triggered:
                                            self._execute_statement(chained_trigger['action'])
        
        except Exception as e:
            self.output.append(f"Error: {e}")
        
        return self.output
    
    def _execute_statement(self, statement):
        """Execute a single statement"""
        if isinstance(statement, StateDeclaration):
            self._execute_state_declaration(statement)
        elif isinstance(statement, SetStatement):
            self._execute_set_statement(statement)
        elif isinstance(statement, PrintStatement):
            self._execute_print_statement(statement)
        else:
            self.output.append(f"Warning: Unknown statement type: {type(statement).__name__}")
    
    def _execute_state_declaration(self, declaration):
        """Execute a state declaration"""
        for kvp in declaration.key_value_pairs:
            key = kvp.key
            value = self._evaluate_value(kvp.value)
            self.state_manager.set([key], value)
        
        self.output.append(f"State initialized with {len(declaration.key_value_pairs)} key-value pairs")
    
    def _execute_set_statement(self, set_stmt):
        """Execute a set statement"""
        path = self._evaluate_path(set_stmt.path)
        value = self._evaluate_value(set_stmt.value)
        
        self.state_manager.set(path, value)
        self.output.append(f"Set {'.'.join(str(p) for p in path)} = {value}")
    
    def _execute_print_statement(self, print_stmt):
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
    
    def _evaluate_path(self, path) -> List[str]:
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
    
    def _evaluate_value(self, value) -> Any:
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
    
    def _print_state_recursive(self, state, indent=0):
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
    
    def get_state(self):
        """Get the current state"""
        return self.state_manager.get_state()
    
    def reset(self):
        """Reset the interpreter state"""
        self.state_manager.clear()
        self.state_manager.clear_reactive_statements()
        self.reactive_engine.clear_history()
        self.output = []
