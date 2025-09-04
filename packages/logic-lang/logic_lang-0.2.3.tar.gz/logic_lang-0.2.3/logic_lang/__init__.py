"""
Logic Language for Soft Logic Constraints
========================================

A domain-specific language (DSL) for defining soft logic constraints in medical imaging.
This package provides an interpreter for rule scripts that can be used to replace
hard-coded constraint logic with flexible, configurable rule sets.

Components:
- `parser`: Parses rule scripts into abstract syntax tree (AST)
- `interpreter`: Executes parsed rules to generate constraint objects
- `ast_nodes`: AST node definitions for logic language constructs
- `exceptions`: Custom exceptions for logic language errors

Example usage:
```python
from losses.rule_language import RuleInterpreter

# Define rules as text
rules = '''
# Feature definitions
define findings_L = mass_L | mc_L
define findings_R = mass_R | mc_R
define high_birads_L = sum(birads_L, [4, 5, 6])
define high_birads_R = sum(birads_R, [4, 5, 6])

# Constraints
constraint exactly_one(birads_L) weight=1.0 transform="logbarrier"
constraint exactly_one(birads_R) weight=1.0 transform="logbarrier"
constraint exactly_one(comp) weight=0.7 transform="logbarrier"
constraint findings_L >> high_birads_L weight=0.7 transform="logbarrier"
constraint findings_R >> high_birads_R weight=0.7 transform="logbarrier"
'''

# Parse and execute
interpreter = RuleInterpreter()
constraints = interpreter.execute(rules, features)
```
"""

from .parser import RuleParser
from .interpreter import RuleInterpreter
from .ast_nodes import *
from .exceptions import *
from .soft_logic import *
from .loss import RuleMammoLoss, RuleBasedConstraintsLoss

__all__ = [
    "RuleParser",
    "RuleInterpreter",
    "RuleMammoLoss",
    "RuleBasedConstraintsLoss",
    "RuleLanguageError",
    "ParseError",
    "InterpreterError",
    "VariableNotFoundError",
    "Truth",
    "Constraint",
    "ConstraintSet",
    "exactly_one_constraint",
    "implication_constraint",
    "mutual_exclusion_constraint",
    "sum_class_probabilities",
    "exactly_one",
    "mutual_exclusion",
    "GodelSemantics",
    "LukasiewiczSemantics",
    "ProductSemantics",
]
