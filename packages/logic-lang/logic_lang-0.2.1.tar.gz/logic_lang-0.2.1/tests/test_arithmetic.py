#!/usr/bin/env python3
"""Test arithmetic operations in logic-lang."""

import torch
from logic_lang import RuleInterpreter


def test_arithmetic_operations():
    """Test comprehensive arithmetic operations."""
    interpreter = RuleInterpreter()

    # Test data
    features = {
        "a": torch.tensor([[2.0]]),
        "b": torch.tensor([[3.0]]),
        "c": torch.tensor([[4.0]]),
        "score": torch.tensor([[0.7]]),
        "predictions": torch.tensor([[0.8, 0.1, 0.1]]),
    }

    # Test script with comprehensive arithmetic
    script = """
    expect a, b, c, score, predictions
    
    # Basic arithmetic constants
    const addition_result = 5 + 3
    const subtraction_result = 10 - 3  
    const multiplication_result = 4 * 2
    const division_result = 8 / 2
    
    # Complex arithmetic constants
    const complex_calc = (5 + 3) * 2 - 1
    const negative_arithmetic = -5 + 3
    const double_negative = -(-5)
    
    # Arithmetic with variables
    define sum_vars = a + b
    define diff_vars = c - a
    define product_vars = a * c
    define quotient_vars = c / a
    
    # Mixed arithmetic and logical operations
    define complex_expr = (a + b) > c
    define arithmetic_logic = a * 2 > score
    
    # Arithmetic in constraints
    constraint sum_vars > (a + 1) weight=0.5
    constraint exactly_one(predictions) alpha=(2 * 3) beta=(-1.5)
    """

    try:
        constraint_set = interpreter.execute(script, features)

        # Verify constant calculations
        assert interpreter.get_variable("addition_result") == 8
        assert interpreter.get_variable("subtraction_result") == 7
        assert interpreter.get_variable("multiplication_result") == 8
        assert interpreter.get_variable("division_result") == 4
        assert interpreter.get_variable("complex_calc") == 15  # (5+3)*2-1 = 8*2-1 = 15
        assert interpreter.get_variable("negative_arithmetic") == -2  # -5+3 = -2
        assert interpreter.get_variable("double_negative") == 5  # -(-5) = 5

        # Verify variable operations
        sum_result = interpreter.get_variable("sum_vars")
        assert torch.allclose(sum_result, torch.tensor([[5.0]]))  # 2 + 3 = 5

        diff_result = interpreter.get_variable("diff_vars")
        assert torch.allclose(diff_result, torch.tensor([[2.0]]))  # 4 - 2 = 2

        product_result = interpreter.get_variable("product_vars")
        assert torch.allclose(product_result, torch.tensor([[8.0]]))  # 2 * 4 = 8

        quotient_result = interpreter.get_variable("quotient_vars")
        assert torch.allclose(quotient_result, torch.tensor([[2.0]]))  # 4 / 2 = 2

        # Verify constraints were created
        assert len(constraint_set.constraints) == 2

        print("✅ All arithmetic operations working correctly!")
        return True

    except Exception as e:
        print(f"❌ Arithmetic test failed: {e}")
        return False


def test_operator_precedence():
    """Test operator precedence is correct."""
    interpreter = RuleInterpreter()

    script = """
    # Test arithmetic precedence: 2 + 3 * 4 should be 2 + 12 = 14, not 5 * 4 = 20
    const precedence_test = 2 + 3 * 4
    
    # Test with parentheses: (2 + 3) * 4 should be 5 * 4 = 20
    const parentheses_test = (2 + 3) * 4
    
    # Mixed arithmetic and comparison: 2 * 3 > 5 should be 6 > 5 = true
    const mixed_test = 2 * 3 > 5
    """

    try:
        interpreter.execute(script)

        assert interpreter.get_variable("precedence_test") == 14  # 2 + (3 * 4)
        assert interpreter.get_variable("parentheses_test") == 20  # (2 + 3) * 4
        assert interpreter.get_variable("mixed_test") == 1.0  # (2 * 3) > 5 = true

        print("✅ Operator precedence working correctly!")
        return True

    except Exception as e:
        print(f"❌ Precedence test failed: {e}")
        return False


def test_division_by_zero():
    """Test division by zero handling."""
    interpreter = RuleInterpreter()

    script = "const invalid = 5 / 0"

    try:
        interpreter.execute(script)
        print("❌ Division by zero should have failed!")
        return False
    except Exception as e:
        if "Division by zero" in str(e):
            print("✅ Division by zero correctly handled!")
            return True
        else:
            print(f"❌ Wrong error for division by zero: {e}")
            return False


if __name__ == "__main__":
    test_arithmetic_operations()
    test_operator_precedence()
    test_division_by_zero()
