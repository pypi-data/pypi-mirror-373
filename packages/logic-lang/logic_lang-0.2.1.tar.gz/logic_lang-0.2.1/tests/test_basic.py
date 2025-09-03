"""Basic tests for the logic_lang package."""

import pytest
import torch
from logic_lang import RuleParser, RuleInterpreter


def test_import():
    """Test that the package can be imported."""
    from logic_lang import RuleParser, RuleInterpreter

    assert RuleParser is not None
    assert RuleInterpreter is not None


def test_basic_parsing():
    """Test basic rule parsing."""
    parser = RuleParser()

    # Test simple rule
    script = """
    expect var1
    define test = var1
    """

    ast = parser.parse(script)
    assert ast is not None
    assert len(ast.statements) == 2


def test_interpreter_creation():
    """Test that interpreter can be created."""
    interpreter = RuleInterpreter()
    assert interpreter is not None


def test_negative_numbers():
    """Test negative number parsing and evaluation."""
    parser = RuleParser()
    interpreter = RuleInterpreter()

    # Test negative constants
    script = """
    const neg_threshold = -0.5
    const pos_threshold = 0.7
    expect values
    define low_values = values < neg_threshold
    define high_values = values > pos_threshold
    constraint low_values weight=-1.0
    constraint high_values weight=2.0
    """

    # Should parse without errors
    ast = parser.parse(script)
    assert ast is not None
    assert (
        len(ast.statements) == 7
    )  # Updated count: 2 const + 1 expect + 2 define + 2 constraint

    # Should execute without errors
    features = {"values": torch.tensor([[0.0, -0.8, 0.9]])}
    constraint_set = interpreter.execute(script, features)
    assert len(constraint_set.constraints) == 2


if __name__ == "__main__":
    test_import()
    test_basic_parsing()
    test_interpreter_creation()
    test_negative_numbers()
    print("All tests passed!")
