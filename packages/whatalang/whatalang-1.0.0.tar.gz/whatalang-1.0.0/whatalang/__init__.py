"""
Whatalang - A reactive programming language
"""

__version__ = "1.0.0"
__author__ = "Whatalang Team"

from .lexer import Lexer
from .parser import Parser
from .state import StateManager, Interpreter
from .reactive import ReactiveEngine, ReactiveInterpreter

__all__ = [
    'Lexer',
    'Parser', 
    'StateManager',
    'Interpreter',
    'ReactiveEngine',
    'ReactiveInterpreter'
]
