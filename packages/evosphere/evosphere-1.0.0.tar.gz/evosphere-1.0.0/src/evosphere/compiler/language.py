"""
Language Processor for EvoLanguage

Implements the patent-pending EvoLanguage parser and AST generation
for biological evolutionary programming.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import re
import ast
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """EvoLanguage token types."""
    
    # Literals
    NUMBER = auto()
    STRING = auto()
    GENOME = auto()
    BOOLEAN = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    FUNCTION = auto()
    VARIABLE = auto()
    
    # Keywords
    EVOLVE = auto()
    MUTATE = auto()
    SELECT = auto()
    RECOMBINE = auto()
    PRESSURE = auto()
    ENVIRONMENT = auto()
    QUANTUM = auto()
    POPULATION = auto()
    GENERATION = auto()
    FITNESS = auto()
    
    # Operators
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    POWER = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    
    # Control flow
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """EvoLanguage token."""
    
    type: TokenType
    value: str
    line: int
    column: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.type.name}({self.value})"


class EvoLanguageLexer:
    """
    Lexical analyzer for EvoLanguage.
    
    Patent Feature: Domain-specific lexer for evolutionary biology
    programming with biological keyword recognition and genome literals.
    """
    
    def __init__(self):
        """Initialize lexer."""
        
        # Keyword mappings
        self.keywords = {
            'evolve': TokenType.EVOLVE,
            'mutate': TokenType.MUTATE,
            'select': TokenType.SELECT,
            'recombine': TokenType.RECOMBINE,
            'pressure': TokenType.PRESSURE,
            'environment': TokenType.ENVIRONMENT,
            'quantum': TokenType.QUANTUM,
            'population': TokenType.POPULATION,
            'generation': TokenType.GENERATION,
            'fitness': TokenType.FITNESS,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'return': TokenType.RETURN,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
        }
        
        # Operator mappings
        self.operators = {
            '=': TokenType.ASSIGN,
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<': TokenType.LESS,
            '>': TokenType.GREATER,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '**': TokenType.POWER,
        }
        
        # Delimiter mappings
        self.delimiters = {
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            '.': TokenType.DOT,
        }
        
        logger.info("EvoLanguage lexer initialized")
    
    def tokenize(self, source_code: str) -> List[Token]:
        """
        Tokenize EvoLanguage source code.
        
        Args:
            source_code: Source code to tokenize
            
        Returns:
            List of tokens
        """
        
        tokens = []
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            tokens.extend(self._tokenize_line(line, line_num))
            
            # Add newline token if line is not empty
            if line.strip():
                tokens.append(Token(TokenType.NEWLINE, '\n', line_num, len(line)))
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', len(lines), 0))
        
        return tokens
    
    def _tokenize_line(self, line: str, line_num: int) -> List[Token]:
        """Tokenize single line."""
        
        tokens = []
        i = 0
        
        while i < len(line):
            # Skip whitespace
            if line[i].isspace():
                i += 1
                continue
            
            # Skip comments
            if line[i:i+2] == '//':
                break  # Rest of line is comment
            
            if line[i] == '#':
                break  # Rest of line is comment
            
            # Numbers
            if line[i].isdigit() or (line[i] == '.' and i+1 < len(line) and line[i+1].isdigit()):
                start = i
                while i < len(line) and (line[i].isdigit() or line[i] in '.e-+'):
                    i += 1
                
                number_str = line[start:i]
                tokens.append(Token(TokenType.NUMBER, number_str, line_num, start))
                continue
            
            # String literals
            if line[i] in '"\'':
                quote = line[i]
                start = i
                i += 1
                
                while i < len(line) and line[i] != quote:
                    if line[i] == '\\':  # Escape sequence
                        i += 2
                    else:
                        i += 1
                
                if i < len(line):
                    i += 1  # Include closing quote
                
                string_literal = line[start:i]
                tokens.append(Token(TokenType.STRING, string_literal, line_num, start))
                continue
            
            # Genome literals (DNA sequences)
            if line[i:i+2] == 'g"' or line[i:i+2] == "g'":
                quote = line[i+1]
                start = i
                i += 2
                
                while i < len(line) and line[i] != quote:
                    i += 1
                
                if i < len(line):
                    i += 1  # Include closing quote
                
                genome_literal = line[start:i]
                tokens.append(Token(TokenType.GENOME, genome_literal, line_num, start))
                continue
            
            # Two-character operators
            if i + 1 < len(line) and line[i:i+2] in self.operators:
                op = line[i:i+2]
                tokens.append(Token(self.operators[op], op, line_num, i))
                i += 2
                continue
            
            # Single-character operators and delimiters
            if line[i] in self.operators:
                op = line[i]
                tokens.append(Token(self.operators[op], op, line_num, i))
                i += 1
                continue
            
            if line[i] in self.delimiters:
                delim = line[i]
                tokens.append(Token(self.delimiters[delim], delim, line_num, i))
                i += 1
                continue
            
            # Identifiers and keywords
            if line[i].isalpha() or line[i] == '_':
                start = i
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                
                identifier = line[start:i]
                
                # Check if it's a keyword
                if identifier.lower() in self.keywords:
                    token_type = self.keywords[identifier.lower()]
                else:
                    token_type = TokenType.IDENTIFIER
                
                tokens.append(Token(token_type, identifier, line_num, start))
                continue
            
            # Unknown character
            tokens.append(Token(TokenType.UNKNOWN, line[i], line_num, i))
            i += 1
        
        return tokens


@dataclass
class ASTNode(ABC):
    """Base class for AST nodes."""
    
    line: int
    column: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgramNode(ASTNode):
    """Root program node."""
    
    statements: List[ASTNode] = field(default_factory=list)


@dataclass
class EvolutionBlockNode(ASTNode):
    """Evolution block containing evolutionary operations."""
    
    population_name: str
    operations: List[ASTNode] = field(default_factory=list)
    conditions: List[ASTNode] = field(default_factory=list)


@dataclass
class MutationNode(ASTNode):
    """Mutation operation node."""
    
    mutation_type: str
    rate: float
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SelectionNode(ASTNode):
    """Selection operation node."""
    
    selection_type: str
    strength: float
    criteria: List[str] = field(default_factory=list)


@dataclass
class EnvironmentNode(ASTNode):
    """Environmental pressure node."""
    
    pressure_type: str
    intensity: float
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuantumNode(ASTNode):
    """Quantum evolution operation node."""
    
    operation_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExpressionNode(ASTNode):
    """Expression node."""
    
    operator: str
    operands: List[ASTNode] = field(default_factory=list)


@dataclass
class LiteralNode(ASTNode):
    """Literal value node."""
    
    value: Any
    literal_type: str


class EvoLanguageParser:
    """
    Parser for EvoLanguage evolutionary programming language.
    
    Patent Feature: Recursive descent parser with biological syntax
    recognition and evolutionary constraint validation.
    """
    
    def __init__(self):
        """Initialize parser."""
        self.tokens: List[Token] = []
        self.current = 0
        self.errors: List[str] = []
        
        logger.info("EvoLanguage parser initialized")
    
    def parse(self, tokens: List[Token]) -> ProgramNode:
        """
        Parse tokens into AST.
        
        Args:
            tokens: List of tokens from lexer
            
        Returns:
            Abstract syntax tree
        """
        
        self.tokens = tokens
        self.current = 0
        self.errors = []
        
        try:
            program = self._parse_program()
            
            if self.errors:
                logger.warning(f"Parser completed with {len(self.errors)} errors")
            
            return program
            
        except Exception as e:
            logger.error(f"Parser error: {e}")
            self.errors.append(str(e))
            
            # Return partial AST
            return ProgramNode(0, 0, statements=[])
    
    def _parse_program(self) -> ProgramNode:
        """Parse program (top-level)."""
        
        program = ProgramNode(0, 0)
        
        while not self._is_at_end():
            # Skip newlines
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            try:
                statement = self._parse_statement()
                if statement:
                    program.statements.append(statement)
            except Exception as e:
                self.errors.append(f"Error parsing statement: {e}")
                self._synchronize()
        
        return program
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse single statement."""
        
        token = self._peek()
        
        if token.type == TokenType.EVOLVE:
            return self._parse_evolution_block()
        
        elif token.type == TokenType.MUTATE:
            return self._parse_mutation()
        
        elif token.type == TokenType.SELECT:
            return self._parse_selection()
        
        elif token.type == TokenType.ENVIRONMENT:
            return self._parse_environment()
        
        elif token.type == TokenType.QUANTUM:
            return self._parse_quantum()
        
        elif token.type == TokenType.IF:
            return self._parse_if_statement()
        
        elif token.type == TokenType.WHILE:
            return self._parse_while_statement()
        
        elif token.type == TokenType.FOR:
            return self._parse_for_statement()
        
        else:
            # Expression statement
            expr = self._parse_expression()
            self._consume_semicolon()
            return expr
    
    def _parse_evolution_block(self) -> EvolutionBlockNode:
        """Parse evolution block."""
        
        evolve_token = self._consume(TokenType.EVOLVE)
        
        # Population name
        population_name = "default"
        if self._peek().type == TokenType.IDENTIFIER:
            population_name = self._advance().value
        
        # Block body
        self._consume(TokenType.LBRACE)
        
        operations = []
        conditions = []
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
            
            statement = self._parse_statement()
            if statement:
                operations.append(statement)
        
        self._consume(TokenType.RBRACE)
        
        return EvolutionBlockNode(
            line=evolve_token.line,
            column=evolve_token.column,
            population_name=population_name,
            operations=operations,
            conditions=conditions
        )
    
    def _parse_mutation(self) -> MutationNode:
        """Parse mutation operation."""
        
        mutate_token = self._consume(TokenType.MUTATE)
        
        # Mutation type
        mutation_type = "point"
        if self._peek().type == TokenType.IDENTIFIER:
            mutation_type = self._advance().value
        
        # Parameters
        parameters = {}
        rate = 1e-6  # Default rate
        
        if self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            
            # Parse parameter list
            while not self._check(TokenType.RPAREN) and not self._is_at_end():
                param_name = self._consume(TokenType.IDENTIFIER).value
                self._consume(TokenType.ASSIGN)
                param_value = self._parse_expression()
                
                parameters[param_name] = param_value
                
                if param_name == 'rate' and isinstance(param_value, LiteralNode):
                    rate = float(param_value.value)
                
                if self._check(TokenType.COMMA):
                    self._advance()
            
            self._consume(TokenType.RPAREN)
        
        self._consume_semicolon()
        
        return MutationNode(
            line=mutate_token.line,
            column=mutate_token.column,
            mutation_type=mutation_type,
            rate=rate,
            parameters=parameters
        )
    
    def _parse_selection(self) -> SelectionNode:
        """Parse selection operation."""
        
        select_token = self._consume(TokenType.SELECT)
        
        # Selection type
        selection_type = "fitness"
        if self._peek().type == TokenType.IDENTIFIER:
            selection_type = self._advance().value
        
        # Parameters
        strength = 1.0
        criteria = []
        
        if self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            
            while not self._check(TokenType.RPAREN) and not self._is_at_end():
                param_name = self._consume(TokenType.IDENTIFIER).value
                self._consume(TokenType.ASSIGN)
                param_value = self._parse_expression()
                
                if param_name == 'strength' and isinstance(param_value, LiteralNode):
                    strength = float(param_value.value)
                elif param_name == 'criteria':
                    # Parse criteria list
                    pass
                
                if self._check(TokenType.COMMA):
                    self._advance()
            
            self._consume(TokenType.RPAREN)
        
        self._consume_semicolon()
        
        return SelectionNode(
            line=select_token.line,
            column=select_token.column,
            selection_type=selection_type,
            strength=strength,
            criteria=criteria
        )
    
    def _parse_environment(self) -> EnvironmentNode:
        """Parse environmental pressure."""
        
        env_token = self._consume(TokenType.ENVIRONMENT)
        
        # Pressure type
        pressure_type = "default"
        if self._peek().type == TokenType.IDENTIFIER:
            pressure_type = self._advance().value
        
        # Parameters
        intensity = 1.0
        parameters = {}
        
        if self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            
            while not self._check(TokenType.RPAREN) and not self._is_at_end():
                param_name = self._consume(TokenType.IDENTIFIER).value
                self._consume(TokenType.ASSIGN)
                param_value = self._parse_expression()
                
                parameters[param_name] = param_value
                
                if param_name == 'intensity' and isinstance(param_value, LiteralNode):
                    intensity = float(param_value.value)
                
                if self._check(TokenType.COMMA):
                    self._advance()
            
            self._consume(TokenType.RPAREN)
        
        self._consume_semicolon()
        
        return EnvironmentNode(
            line=env_token.line,
            column=env_token.column,
            pressure_type=pressure_type,
            intensity=intensity,
            parameters=parameters
        )
    
    def _parse_quantum(self) -> QuantumNode:
        """Parse quantum operation."""
        
        quantum_token = self._consume(TokenType.QUANTUM)
        
        # Operation type
        operation_type = "superposition"
        if self._peek().type == TokenType.IDENTIFIER:
            operation_type = self._advance().value
        
        # Parameters
        parameters = {}
        
        if self._check(TokenType.LPAREN):
            self._advance()  # consume '('
            
            while not self._check(TokenType.RPAREN) and not self._is_at_end():
                param_name = self._consume(TokenType.IDENTIFIER).value
                self._consume(TokenType.ASSIGN)
                param_value = self._parse_expression()
                
                parameters[param_name] = param_value
                
                if self._check(TokenType.COMMA):
                    self._advance()
            
            self._consume(TokenType.RPAREN)
        
        self._consume_semicolon()
        
        return QuantumNode(
            line=quantum_token.line,
            column=quantum_token.column,
            operation_type=operation_type,
            parameters=parameters
        )
    
    def _parse_if_statement(self) -> Optional[ASTNode]:
        """Parse if statement."""
        
        if_token = self._consume(TokenType.IF)
        
        self._consume(TokenType.LPAREN)
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN)
        
        then_stmt = self._parse_statement()
        
        else_stmt = None
        if self._check(TokenType.ELSE):
            self._advance()
            else_stmt = self._parse_statement()
        
        # Return conditional AST node (simplified)
        return ExpressionNode(
            line=if_token.line,
            column=if_token.column,
            operator='if',
            operands=[condition, then_stmt] + ([else_stmt] if else_stmt else [])
        )
    
    def _parse_while_statement(self) -> Optional[ASTNode]:
        """Parse while loop."""
        
        while_token = self._consume(TokenType.WHILE)
        
        self._consume(TokenType.LPAREN)
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN)
        
        body = self._parse_statement()
        
        return ExpressionNode(
            line=while_token.line,
            column=while_token.column,
            operator='while',
            operands=[condition, body]
        )
    
    def _parse_for_statement(self) -> Optional[ASTNode]:
        """Parse for loop."""
        
        for_token = self._consume(TokenType.FOR)
        
        self._consume(TokenType.LPAREN)
        
        # For loop components
        init = self._parse_expression() if not self._check(TokenType.SEMICOLON) else None
        self._consume(TokenType.SEMICOLON)
        
        condition = self._parse_expression() if not self._check(TokenType.SEMICOLON) else None
        self._consume(TokenType.SEMICOLON)
        
        update = self._parse_expression() if not self._check(TokenType.RPAREN) else None
        self._consume(TokenType.RPAREN)
        
        body = self._parse_statement()
        
        operands = list(filter(None, [init, condition, update, body]))
        
        return ExpressionNode(
            line=for_token.line,
            column=for_token.column,
            operator='for',
            operands=operands
        )
    
    def _parse_expression(self) -> ASTNode:
        """Parse expression."""
        
        return self._parse_equality()
    
    def _parse_equality(self) -> ASTNode:
        """Parse equality expression."""
        
        expr = self._parse_comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous()
            right = self._parse_comparison()
            
            expr = ExpressionNode(
                line=operator.line,
                column=operator.column,
                operator=operator.value,
                operands=[expr, right]
            )
        
        return expr
    
    def _parse_comparison(self) -> ASTNode:
        """Parse comparison expression."""
        
        expr = self._parse_term()
        
        while self._match(TokenType.GREATER, TokenType.LESS):
            operator = self._previous()
            right = self._parse_term()
            
            expr = ExpressionNode(
                line=operator.line,
                column=operator.column,
                operator=operator.value,
                operands=[expr, right]
            )
        
        return expr
    
    def _parse_term(self) -> ASTNode:
        """Parse term expression."""
        
        expr = self._parse_factor()
        
        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._parse_factor()
            
            expr = ExpressionNode(
                line=operator.line,
                column=operator.column,
                operator=operator.value,
                operands=[expr, right]
            )
        
        return expr
    
    def _parse_factor(self) -> ASTNode:
        """Parse factor expression."""
        
        expr = self._parse_unary()
        
        while self._match(TokenType.DIVIDE, TokenType.MULTIPLY):
            operator = self._previous()
            right = self._parse_unary()
            
            expr = ExpressionNode(
                line=operator.line,
                column=operator.column,
                operator=operator.value,
                operands=[expr, right]
            )
        
        return expr
    
    def _parse_unary(self) -> ASTNode:
        """Parse unary expression."""
        
        if self._match(TokenType.MINUS):
            operator = self._previous()
            right = self._parse_unary()
            
            return ExpressionNode(
                line=operator.line,
                column=operator.column,
                operator='-',
                operands=[right]
            )
        
        return self._parse_primary()
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expression."""
        
        token = self._peek()
        
        if token.type == TokenType.BOOLEAN:
            self._advance()
            return LiteralNode(
                line=token.line,
                column=token.column,
                value=token.value == 'true',
                literal_type='boolean'
            )
        
        if token.type == TokenType.NUMBER:
            self._advance()
            value = float(token.value) if '.' in token.value else int(token.value)
            return LiteralNode(
                line=token.line,
                column=token.column,
                value=value,
                literal_type='number'
            )
        
        if token.type == TokenType.STRING:
            self._advance()
            # Remove quotes
            value = token.value[1:-1]
            return LiteralNode(
                line=token.line,
                column=token.column,
                value=value,
                literal_type='string'
            )
        
        if token.type == TokenType.GENOME:
            self._advance()
            # Remove g" quotes and validate DNA
            genome_seq = token.value[2:-1]
            if self._validate_genome_sequence(genome_seq):
                return LiteralNode(
                    line=token.line,
                    column=token.column,
                    value=genome_seq,
                    literal_type='genome'
                )
            else:
                self.errors.append(f"Invalid genome sequence at line {token.line}")
        
        if token.type == TokenType.IDENTIFIER:
            self._advance()
            return LiteralNode(
                line=token.line,
                column=token.column,
                value=token.value,
                literal_type='identifier'
            )
        
        if token.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN)
            return expr
        
        raise Exception(f"Unexpected token {token.type} at line {token.line}")
    
    def _validate_genome_sequence(self, sequence: str) -> bool:
        """Validate genome sequence contains only valid bases."""
        
        valid_bases = set('ATCGN')  # Including N for unknown
        return all(base.upper() in valid_bases for base in sequence)
    
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the types."""
        
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Consume current token and return it."""
        
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if at end of tokens."""
        
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Return current token without advancing."""
        
        return self.tokens[self.current] if self.current < len(self.tokens) else self.tokens[-1]
    
    def _previous(self) -> Token:
        """Return previous token."""
        
        return self.tokens[self.current - 1] if self.current > 0 else self.tokens[0]
    
    def _consume(self, token_type: TokenType) -> Token:
        """Consume token of expected type."""
        
        if self._check(token_type):
            return self._advance()
        
        current = self._peek()
        raise Exception(f"Expected {token_type}, got {current.type} at line {current.line}")
    
    def _consume_semicolon(self):
        """Consume optional semicolon."""
        
        if self._check(TokenType.SEMICOLON):
            self._advance()
    
    def _synchronize(self):
        """Synchronize after parse error."""
        
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type in [
                TokenType.EVOLVE, TokenType.MUTATE, TokenType.SELECT,
                TokenType.IF, TokenType.WHILE, TokenType.FOR
            ]:
                return
            
            self._advance()


class EvoLanguageAnalyzer:
    """
    Semantic analyzer for EvoLanguage AST.
    
    Patent Feature: Biological constraint checking and evolutionary
    consistency validation for compiled evolutionary programs.
    """
    
    def __init__(self):
        """Initialize semantic analyzer."""
        self.symbol_table: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Biological constraint validators
        self.constraint_validators = {
            'mutation_rate': self._validate_mutation_rate,
            'selection_strength': self._validate_selection_strength,
            'genome_length': self._validate_genome_length,
            'gc_content': self._validate_gc_content,
        }
        
        logger.info("EvoLanguage semantic analyzer initialized")
    
    def analyze(self, ast: ProgramNode) -> Dict[str, Any]:
        """
        Perform semantic analysis on AST.
        
        Args:
            ast: Abstract syntax tree to analyze
            
        Returns:
            Analysis results with errors and constraints
        """
        
        self.errors = []
        self.warnings = []
        
        # Analyze AST nodes
        for statement in ast.statements:
            self._analyze_node(statement)
        
        # Validate biological constraints
        self._validate_biological_constraints()
        
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'symbol_table': self.symbol_table.copy(),
            'constraint_violations': self._check_constraint_violations()
        }
    
    def _analyze_node(self, node: ASTNode):
        """Analyze single AST node."""
        
        if isinstance(node, EvolutionBlockNode):
            self._analyze_evolution_block(node)
        
        elif isinstance(node, MutationNode):
            self._analyze_mutation(node)
        
        elif isinstance(node, SelectionNode):
            self._analyze_selection(node)
        
        elif isinstance(node, EnvironmentNode):
            self._analyze_environment(node)
        
        elif isinstance(node, QuantumNode):
            self._analyze_quantum(node)
        
        elif isinstance(node, ExpressionNode):
            for operand in node.operands:
                self._analyze_node(operand)
    
    def _analyze_evolution_block(self, node: EvolutionBlockNode):
        """Analyze evolution block."""
        
        # Register population
        self.symbol_table[node.population_name] = {
            'type': 'population',
            'operations': len(node.operations)
        }
        
        # Analyze operations
        for operation in node.operations:
            self._analyze_node(operation)
    
    def _analyze_mutation(self, node: MutationNode):
        """Analyze mutation operation."""
        
        # Validate mutation rate
        if not self._validate_mutation_rate(node.rate):
            self.errors.append(
                f"Invalid mutation rate {node.rate} at line {node.line}"
            )
        
        # Check for realistic mutation types
        valid_types = ['point', 'indel', 'structural', 'conditional']
        if node.mutation_type not in valid_types:
            self.warnings.append(
                f"Unknown mutation type '{node.mutation_type}' at line {node.line}"
            )
    
    def _analyze_selection(self, node: SelectionNode):
        """Analyze selection operation."""
        
        # Validate selection strength
        if not self._validate_selection_strength(node.strength):
            self.errors.append(
                f"Invalid selection strength {node.strength} at line {node.line}"
            )
        
        # Check selection type
        valid_types = ['fitness', 'frequency', 'environmental', 'sexual']
        if node.selection_type not in valid_types:
            self.warnings.append(
                f"Unknown selection type '{node.selection_type}' at line {node.line}"
            )
    
    def _analyze_environment(self, node: EnvironmentNode):
        """Analyze environmental pressure."""
        
        # Validate intensity
        if node.intensity < 0:
            self.errors.append(
                f"Negative pressure intensity at line {node.line}"
            )
        
        # Check pressure type
        valid_types = ['drug', 'temperature', 'ph', 'radiation', 'competition']
        if node.pressure_type not in valid_types:
            self.warnings.append(
                f"Unknown pressure type '{node.pressure_type}' at line {node.line}"
            )
    
    def _analyze_quantum(self, node: QuantumNode):
        """Analyze quantum operation."""
        
        # Validate quantum operation
        valid_operations = ['superposition', 'entanglement', 'measurement', 'annealing']
        if node.operation_type not in valid_operations:
            self.warnings.append(
                f"Unknown quantum operation '{node.operation_type}' at line {node.line}"
            )
    
    def _validate_mutation_rate(self, rate: float) -> bool:
        """Validate mutation rate is biologically reasonable."""
        
        # Typical mutation rates: 1e-10 to 1e-3 per base per generation
        return 1e-10 <= rate <= 1e-3
    
    def _validate_selection_strength(self, strength: float) -> bool:
        """Validate selection strength is reasonable."""
        
        # Selection strength typically 0.01 to 10.0
        return 0.001 <= strength <= 100.0
    
    def _validate_genome_length(self, length: int) -> bool:
        """Validate genome length is reasonable."""
        
        # Genome length: 100 bp to 1Gb
        return 100 <= length <= 1_000_000_000
    
    def _validate_gc_content(self, gc_content: float) -> bool:
        """Validate GC content is reasonable."""
        
        # GC content: 20% to 80%
        return 0.2 <= gc_content <= 0.8
    
    def _validate_biological_constraints(self):
        """Validate overall biological constraints."""
        
        # Check for contradictory operations
        # Check for unrealistic parameter combinations
        # Validate evolutionary pathway feasibility
        
        # Example: High mutation + strong selection might be unrealistic
        # This would be expanded with actual biological knowledge
        pass
    
    def _check_constraint_violations(self) -> List[str]:
        """Check for constraint violations."""
        
        violations = []
        
        # Check symbol table for violations
        for name, info in self.symbol_table.items():
            if info.get('type') == 'population':
                if info.get('operations', 0) == 0:
                    violations.append(f"Population '{name}' has no operations")
        
        return violations
