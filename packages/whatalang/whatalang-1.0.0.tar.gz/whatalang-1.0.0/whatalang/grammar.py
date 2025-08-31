"""
Whatalang Grammar Definition
Complete syntax specification for the reactive programming language

File Extensions Supported:
- .wa    - Standard Whatalang extension (recommended)
- .what  - Descriptive Whatalang extension
- (none) - No extension (also supported)
"""

# ============================================================================
# TOKEN DEFINITIONS
# ============================================================================

TOKENS = {
    'KEYWORD': [
        'state',      # Declare initial state
        'set',        # Set a value
        'print',      # Print output
        'react',      # Reactive statement
        'to',         # Part of react statement
        'when',       # Condition in react statement
        'default',    # Default actions in react statement
    ],
    
    'OPERATOR': [
        '=',          # Assignment
        '==',         # Equality
        '!=',         # Inequality
        '>',          # Greater than
        '<',          # Less than
        '>=',         # Greater than or equal
        '<=',         # Less than or equal
        '+',          # Addition
        '-',          # Subtraction
        '*',          # Multiplication
        '/',          # Division
    ],
    
    'DELIMITER': [
        '{',          # Object/block start
        '}',          # Object/block end
        '[',          # Array start
        ']',          # Array end
        ':',          # Key-value separator
        ',',          # List separator
        '(',          # Grouping start
        ')',          # Grouping end
        '.',          # Path separator
    ],
    
    'LITERAL': [
        'STRING',     # String literals
        'NUMBER',     # Numeric literals
        'BOOLEAN',    # Boolean literals
        'NULL',       # Null value
    ],
    
    'IDENTIFIER': 'IDENTIFIER'  # Variable names, keys
}

# ============================================================================
# GRAMMAR RULES (BNF-like notation)
# ============================================================================

GRAMMAR_RULES = {
    # Program structure
    'program': 'statement*',
    
    # Statement types
    'statement': 'state_decl | set_statement | print_statement | react_statement',
    
    # State declaration
    'state_decl': 'state { key_value_pair* }',
    'key_value_pair': 'identifier : value',
    
    # Values
    'value': 'literal | object | array | identifier',
    'object': '{ key_value_pair* }',
    'array': '[ value* ]',
    
    # Set statement
    'set_statement': 'set path = expression',
    
    # Print statement
    'print_statement': 'print expression',
    
    # Reactive statements
    'react_statement': 'react to target (when_condition | default_actions)*',
    'when_condition': 'when comparison_operator expression { action* }',
    'default_actions': 'default { action* }',
    'comparison_operator': '== | != | > | < | >= | <=',
    
    # Actions (can be any statement)
    'action': 'set_statement | print_statement',
    
    # Paths for accessing nested state
    'path': 'identifier ( . identifier | [ expression ] )*',
    
    # Expressions
    'expression': 'literal | identifier | path',
    
    # Identifiers and literals
    'identifier': 'IDENTIFIER',
    'literal': 'STRING | NUMBER | BOOLEAN | NULL'
}

# ============================================================================
# SYNTAX EXAMPLES
# ============================================================================

SYNTAX_EXAMPLES = {
    'state_declaration': '''
state {
  counter: 0,
  status: "normal",
  user: {
    name: "Alice",
    age: 25
  }
}
''',
    
    'set_statement': '''
set counter = 10
set user.age = 26
set user.preferences = ["dark", "large"]
''',
    
    'print_statement': '''
print counter
print user.name
print state
''',
    
    'reactive_statement': '''
react to counter when > 10 {
  set status = "high"
  print "Counter is high!"
}

react to user.age when >= 18 {
  set user.adult = true
}
''',
    
    'complex_reactive': '''
react to counter when > 100 {
  set level = "expert"
}
when > 50 {
  set level = "advanced"
}
when > 10 {
  set level = "intermediate"
}
default {
  set level = "beginner"
}
'''
}

# ============================================================================
# LANGUAGE FEATURES
# ============================================================================

LANGUAGE_FEATURES = {
    'core': [
        'Single global state',
        'Nested objects and arrays',
        'Path-based state access',
        'Type inference',
        'Dynamic typing'
    ],
    
    'reactive': [
        'Automatic condition monitoring',
        'Immediate action execution',
        'Chained reactive triggers',
        'Multiple conditions per target',
        'Default action handling'
    ],
    
    'syntax': [
        'Clean, readable syntax',
        'JSON-like object notation',
        'Natural language keywords',
        'Consistent operator precedence',
        'Flexible whitespace handling'
    ]
}

# ============================================================================
# VALIDATION RULES
# ============================================================================

VALIDATION_RULES = {
    'state_declaration': [
        'Must have opening and closing braces',
        'Key-value pairs separated by commas',
        'Keys must be valid identifiers',
        'Values must be valid expressions'
    ],
    
    'reactive_statement': [
        'Must start with "react to"',
        'Target must be a valid path',
        'Conditions must have valid operators',
        'Actions must be enclosed in braces',
        'At least one condition or default required'
    ],
    
    'path_access': [
        'Must start with valid identifier',
        'Dot notation for object properties',
        'Bracket notation for array indices',
        'Nested paths must exist in state'
    ]
}

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES = {
    'syntax_error': 'Syntax error in Whatalang code',
    'invalid_path': 'Invalid path for state access',
    'missing_brace': 'Missing opening or closing brace',
    'invalid_operator': 'Invalid comparison operator',
    'missing_condition': 'Reactive statement missing condition',
    'invalid_action': 'Invalid action in reactive statement'
}

def get_grammar_summary():
    """Get a summary of the Whatalang grammar"""
    return {
        'tokens': len(TOKENS['KEYWORD']) + len(TOKENS['OPERATOR']) + len(TOKENS['DELIMITER']) + len(TOKENS['LITERAL']) + 1,
        'rules': len(GRAMMAR_RULES),
        'features': sum(len(features) for features in LANGUAGE_FEATURES.values()),
        'examples': len(SYNTAX_EXAMPLES)
    }

if __name__ == "__main__":
    summary = get_grammar_summary()
    print("🎯 Whatalang Grammar Summary:")
    print(f"  Tokens: {summary['tokens']}")
    print(f"  Grammar Rules: {summary['rules']}")
    print(f"  Language Features: {summary['features']}")
    print(f"  Syntax Examples: {summary['examples']}")
    print("\n✨ Whatalang is a complete, well-defined language!")
