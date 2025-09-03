#!/usr/bin/env python3
"""Test script to identify missing arithmetic operations and edge cases."""

import torch
from logic_lang import RuleInterpreter, RuleParser


def test_missing_arithmetic():
    """Test missing arithmetic operations."""
    print("🔍 Testing Missing Arithmetic Operations...")

    parser = RuleParser()
    interpreter = RuleInterpreter()

    test_cases = [
        # Basic arithmetic - these should fail
        ("const sum_result = 5 + 3", "Addition"),
        ("const diff_result = 10 - 3", "Subtraction"),
        ("const prod_result = 4 * 2", "Multiplication"),
        ("const div_result = 8 / 2", "Division"),
        # Arithmetic with variables
        ("define result = score + offset", "Variable addition"),
        ("define adjusted = base_score - penalty", "Variable subtraction"),
        # Complex expressions
        ("define complex = (a + b) * c", "Complex arithmetic"),
        ("const calculation = -5 + 3", "Negative plus positive"),
        ("const calculation2 = 10 - (-5)", "Subtract negative"),
    ]

    features = {
        "score": torch.tensor([[0.7]]),
        "offset": torch.tensor([[0.2]]),
        "base_score": torch.tensor([[0.8]]),
        "penalty": torch.tensor([[0.1]]),
        "a": torch.tensor([[2.0]]),
        "b": torch.tensor([[3.0]]),
        "c": torch.tensor([[4.0]]),
    }

    for script, description in test_cases:
        try:
            ast = parser.parse(script)
            result = interpreter.execute(script, features)
            print(f"✅ {description}: PASSED")
        except Exception as e:
            print(f"❌ {description}: FAILED - {e}")

    return True


def test_edge_cases():
    """Test edge cases with negative numbers."""
    print("\n🔍 Testing Edge Cases...")

    interpreter = RuleInterpreter()

    test_cases = [
        # Edge cases that should work
        ("const neg = -5", "Simple negative constant"),
        ("const pos = +5", "Simple positive constant"),
        ("constraint exactly_one(pred) weight=-0.5", "Negative weight"),
        # Complex negative number scenarios
        ("const complex = -(5)", "Negative with parentheses"),
        ("const double_neg = -(-5)", "Double negative"),
        ("define neg_var = -score", "Negative variable"),
    ]

    features = {
        "pred": torch.tensor([[0.8, 0.1, 0.1]]),
        "score": torch.tensor([[0.7]]),
    }

    for script, description in test_cases:
        try:
            result = interpreter.execute(script, features)
            print(f"✅ {description}: PASSED")
        except Exception as e:
            print(f"❌ {description}: FAILED - {e}")


def test_operator_precedence():
    """Test operator precedence issues."""
    print("\n🔍 Testing Operator Precedence...")

    # This should reveal precedence issues
    test_cases = [
        # Logical vs arithmetic precedence
        ("define result = a > b & c", "Comparison vs logical AND"),
        ("define result2 = ~a > b", "NOT vs comparison"),
    ]

    features = {
        "a": torch.tensor([[0.8]]),
        "b": torch.tensor([[0.5]]),
        "c": torch.tensor([[0.3]]),
    }

    interpreter = RuleInterpreter()

    for script, description in test_cases:
        try:
            result = interpreter.execute(script, features)
            print(f"✅ {description}: PASSED")
        except Exception as e:
            print(f"❌ {description}: FAILED - {e}")


if __name__ == "__main__":
    test_missing_arithmetic()
    test_edge_cases()
    test_operator_precedence()
