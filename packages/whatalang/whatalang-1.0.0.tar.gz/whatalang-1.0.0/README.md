# Whatalang

A programming language built around a single global state with reactive updates.

## Features
- Single global state management
- Reactive programming
- Functional operations
- Simple, readable syntax

## Development Status
🚧 In Development - Basic parser and state management

## Getting Started
```bash
pip install -e .
whatalang example.wa      # With .wa extension
whatalang example.what    # With .what extension  
whatalang example         # Without extension
```

## Syntax Examples
```wa
state {
  counter: 0,
  user: { name: "John", age: 30 }
}

set counter = 1
print state
```

## Project Structure
```
whatalang/      # Main package
├── lexer.py    # Tokenizer
├── parser.py   # Parser and AST
├── state.py    # State management
├── reactive.py # Reactive engine
├── grammar.py  # Language grammar
└── cli.py      # Command-line interface

tests/          # Test suite
```
