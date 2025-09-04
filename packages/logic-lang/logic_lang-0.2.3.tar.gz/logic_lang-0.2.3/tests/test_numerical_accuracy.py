#!/usr/bin/env python3
"""
NUMERICAL ACCURACY TEST SUITE FOR LOGIC-LANG

This test suite validates the mathematical correctness and numerical accuracy
of all logic-lang operations, ensuring results match expected mathematical
computations within acceptable tolerance levels.

Test Categories:
1. Arithmetic Operations Accuracy
2. Logical Operations Truth Tables
3. Built-in Functions Mathematical Correctness
4. Tensor Operations Accuracy
5. Edge Case Numerical Stability
6. Constraint Mathematics Validation
7. Semantic Operations Accuracy
8. Floating Point Precision Tests
"""

import torch
import numpy as np
import pytest
import math
from typing import Dict, List, Tuple, Any
from logic_lang import (
    RuleParser,
    RuleInterpreter,
    RuleMammoLoss,
    Truth,
    Constraint,
    ConstraintSet,
    GodelSemantics,
    LukasiewiczSemantics,
    ProductSemantics,
)


class NumericalAccuracyTest:
    """Comprehensive numerical accuracy validation for logic-lang."""

    def __init__(self):
        self.parser = RuleParser()
        self.interpreter = RuleInterpreter()
        self.tolerance = 1e-6  # Default numerical tolerance
        self.test_results = []

    def log_test(
        self,
        test_name: str,
        passed: bool,
        details: str = "",
        expected=None,
        actual=None,
    ):
        """Log test results with numerical comparison details."""
        status = "✅ PASS" if passed else "❌ FAIL"
        detail_str = f": {details}" if details else ""
        if expected is not None and actual is not None and not passed:
            detail_str += f" (Expected: {expected}, Got: {actual})"
        print(f"{status} {test_name}{detail_str}")
        self.test_results.append((test_name, passed, details, expected, actual))

    def assert_close(self, actual: Any, expected: Any, tolerance: float = None) -> bool:
        """Check if two values are numerically close within tolerance."""
        if tolerance is None:
            tolerance = self.tolerance

        if isinstance(actual, torch.Tensor) and isinstance(expected, torch.Tensor):
            return torch.allclose(actual, expected, atol=tolerance, rtol=tolerance)
        elif isinstance(actual, torch.Tensor) and isinstance(expected, (int, float)):
            return torch.allclose(
                actual,
                torch.tensor(expected, dtype=actual.dtype),
                atol=tolerance,
                rtol=tolerance,
            )
        elif isinstance(expected, torch.Tensor) and isinstance(actual, (int, float)):
            return torch.allclose(
                torch.tensor(actual, dtype=expected.dtype),
                expected,
                atol=tolerance,
                rtol=tolerance,
            )
        elif isinstance(actual, Truth) and isinstance(expected, torch.Tensor):
            return torch.allclose(
                actual.value, expected, atol=tolerance, rtol=tolerance
            )
        elif isinstance(actual, Truth) and isinstance(expected, Truth):
            return torch.allclose(
                actual.value, expected.value, atol=tolerance, rtol=tolerance
            )
        elif isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            return abs(actual - expected) <= tolerance
        else:
            return actual == expected

    # =================================================================
    # 1. ARITHMETIC OPERATIONS ACCURACY
    # =================================================================

    def test_basic_arithmetic_accuracy(self):
        """Test basic arithmetic operations for numerical correctness."""
        test_cases = [
            # Addition tests
            ("const result = 2.5 + 3.7", 6.2, "Addition: 2.5 + 3.7"),
            ("const result = -1.5 + 4.3", 2.8, "Addition with negative: -1.5 + 4.3"),
            ("const result = 0.1 + 0.2", 0.3, "Small decimals: 0.1 + 0.2"),
            # Subtraction tests
            ("const result = 10.0 - 3.5", 6.5, "Subtraction: 10.0 - 3.5"),
            ("const result = 5.2 - 8.7", -3.5, "Subtraction to negative: 5.2 - 8.7"),
            ("const result = 1.0 - 0.9", 0.1, "Small difference: 1.0 - 0.9"),
            # Multiplication tests
            ("const result = 2.5 * 4.0", 10.0, "Multiplication: 2.5 * 4.0"),
            ("const result = -3.0 * 2.5", -7.5, "Negative multiplication: -3.0 * 2.5"),
            ("const result = 0.25 * 0.25", 0.0625, "Small multiplication: 0.25 * 0.25"),
            # Division tests
            ("const result = 15.0 / 3.0", 5.0, "Division: 15.0 / 3.0"),
            (
                "const result = 1.0 / 3.0",
                1.0 / 3.0,
                "Division with repeating decimal: 1.0 / 3.0",
            ),
            ("const result = -8.0 / 2.0", -4.0, "Negative division: -8.0 / 2.0"),
        ]

        for script, expected, description in test_cases:
            try:
                self.interpreter.execute(script)
                actual = self.interpreter.get_variable("result")
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Arithmetic_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Arithmetic_{description}", False, f"Error: {e}")

    def test_complex_arithmetic_expressions(self):
        """Test complex arithmetic expressions for order of operations."""
        test_cases = [
            # Operator precedence
            ("const result = 2 + 3 * 4", 14.0, "Precedence: 2 + 3 * 4 = 14"),
            ("const result = (2 + 3) * 4", 20.0, "Parentheses: (2 + 3) * 4 = 20"),
            ("const result = 2 * 3 + 4", 10.0, "Precedence: 2 * 3 + 4 = 10"),
            ("const result = 20 / 4 + 2", 7.0, "Division precedence: 20 / 4 + 2 = 7"),
            # Nested operations
            (
                "const result = (10 + 5) / (3 - 1)",
                7.5,
                "Nested: (10 + 5) / (3 - 1) = 7.5",
            ),
            ("const result = 2 * (3 + 4) - 1", 13.0, "Complex: 2 * (3 + 4) - 1 = 13"),
            (
                "const result = (6 / 2) * (4 - 1)",
                9.0,
                "Multi-nested: (6 / 2) * (4 - 1) = 9",
            ),
            # Scientific notation
            ("const result = 1e2 + 1e1", 110.0, "Scientific: 1e2 + 1e1 = 110"),
            ("const result = 2e-3 * 1e3", 2.0, "Scientific mixed: 2e-3 * 1e3 = 2"),
        ]

        for script, expected, description in test_cases:
            try:
                self.interpreter.execute(script)
                actual = self.interpreter.get_variable("result")
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Complex_Arithmetic_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Complex_Arithmetic_{description}", False, f"Error: {e}")

    def test_tensor_arithmetic_accuracy(self):
        """Test tensor arithmetic operations for numerical correctness."""
        features = {
            "tensor_a": torch.tensor([[2.0, 4.0], [6.0, 8.0]]),
            "tensor_b": torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
            "scalar": torch.tensor([[2.0], [2.0]]),
        }

        test_cases = [
            # Element-wise operations
            (
                "expect tensor_a, tensor_b; define result = tensor_a + tensor_b",
                torch.tensor([[3.0, 6.0], [9.0, 12.0]]),
                "Tensor addition",
            ),
            (
                "expect tensor_a, tensor_b; define result = tensor_a - tensor_b",
                torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
                "Tensor subtraction",
            ),
            (
                "expect tensor_a, tensor_b; define result = tensor_a * tensor_b",
                torch.tensor([[2.0, 8.0], [18.0, 32.0]]),
                "Tensor multiplication",
            ),
            (
                "expect tensor_a, tensor_b; define result = tensor_a / tensor_b",
                torch.tensor([[2.0, 2.0], [2.0, 2.0]]),
                "Tensor division",
            ),
            # Scalar-tensor operations
            (
                "expect tensor_a; define result = tensor_a + 5",
                torch.tensor([[7.0, 9.0], [11.0, 13.0]]),
                "Tensor + scalar",
            ),
            (
                "expect tensor_a; define result = tensor_a * 0.5",
                torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
                "Tensor * scalar",
            ),
            (
                "expect tensor_a; define result = 10 - tensor_a",
                torch.tensor([[8.0, 6.0], [4.0, 2.0]]),
                "Scalar - tensor",
            ),
        ]

        for script, expected, description in test_cases:
            try:
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual = actual.value
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Tensor_Arithmetic_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Tensor_Arithmetic_{description}", False, f"Error: {e}")

    # =================================================================
    # 2. LOGICAL OPERATIONS TRUTH TABLES
    # =================================================================

    def test_logical_operations_truth_tables(self):
        """Test logical operations against mathematical truth tables."""
        # Test with precise probability values
        prob_values = [0.0, 0.3, 0.7, 1.0]  # False, low, high, true

        for p1 in prob_values:
            for p2 in prob_values:
                features = {
                    "a": torch.tensor([[p1]]),
                    "b": torch.tensor([[p2]]),
                }

                # Test OR operation (maximum in Godel semantics)
                try:
                    result = self.interpreter.execute(
                        "expect a, b; define result = a | b", features
                    )
                    actual = self.interpreter.get_variable("result").value.item()
                    expected = max(p1, p2)  # Godel semantics for OR
                    is_close = self.assert_close(actual, expected)
                    self.log_test(
                        f"Logical_OR_{p1}_{p2}",
                        is_close,
                        f"OR({p1}, {p2})",
                        expected=expected,
                        actual=actual,
                    )
                except Exception as e:
                    self.log_test(f"Logical_OR_{p1}_{p2}", False, f"Error: {e}")

                # Test AND operation (minimum in Godel semantics)
                try:
                    result = self.interpreter.execute(
                        "expect a, b; define result = a & b", features
                    )
                    actual = self.interpreter.get_variable("result").value.item()
                    expected = min(p1, p2)  # Godel semantics for AND
                    is_close = self.assert_close(actual, expected)
                    self.log_test(
                        f"Logical_AND_{p1}_{p2}",
                        is_close,
                        f"AND({p1}, {p2})",
                        expected=expected,
                        actual=actual,
                    )
                except Exception as e:
                    self.log_test(f"Logical_AND_{p1}_{p2}", False, f"Error: {e}")

    def test_comparison_operations_accuracy(self):
        """Test comparison operations for numerical correctness."""
        test_cases = [
            # Greater than
            (5.0, 3.0, ">", 1.0, "5.0 > 3.0 = True"),
            (3.0, 5.0, ">", 0.0, "3.0 > 5.0 = False"),
            (4.0, 4.0, ">", 0.0, "4.0 > 4.0 = False"),
            # Less than
            (3.0, 5.0, "<", 1.0, "3.0 < 5.0 = True"),
            (5.0, 3.0, "<", 0.0, "5.0 < 3.0 = False"),
            (4.0, 4.0, "<", 0.0, "4.0 < 4.0 = False"),
            # Equal
            (4.0, 4.0, "==", 1.0, "4.0 == 4.0 = True"),
            (4.0, 5.0, "==", 0.0, "4.0 == 5.0 = False"),
            (1.0 / 3.0, 0.3333333333333333, "==", 1.0, "1/3 == 0.3333... = True"),
            # Greater than or equal
            (5.0, 3.0, ">=", 1.0, "5.0 >= 3.0 = True"),
            (4.0, 4.0, ">=", 1.0, "4.0 >= 4.0 = True"),
            (3.0, 5.0, ">=", 0.0, "3.0 >= 5.0 = False"),
            # Less than or equal
            (3.0, 5.0, "<=", 1.0, "3.0 <= 5.0 = True"),
            (4.0, 4.0, "<=", 1.0, "4.0 <= 4.0 = True"),
            (5.0, 3.0, "<=", 0.0, "5.0 <= 3.0 = False"),
        ]

        for val1, val2, op, expected, description in test_cases:
            try:
                script = f"const result = {val1} {op} {val2}"
                self.interpreter.execute(script)
                actual = self.interpreter.get_variable("result")
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Comparison_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Comparison_{description}", False, f"Error: {e}")

    # =================================================================
    # 3. BUILT-IN FUNCTIONS MATHEMATICAL CORRECTNESS
    # =================================================================

    def test_sum_function_accuracy(self):
        """Test sum function for mathematical correctness."""
        # Create test tensor with known values
        predictions = torch.tensor([[0.1, 0.2, 0.3, 0.4], [0.15, 0.25, 0.35, 0.25]])
        features = {"predictions": predictions}

        test_cases = [
            # Sum of consecutive indices
            ([0, 1], torch.tensor([[0.3], [0.4]]), "Sum indices [0,1]"),
            ([2, 3], torch.tensor([[0.7], [0.6]]), "Sum indices [2,3]"),
            ([0, 2], torch.tensor([[0.4], [0.5]]), "Sum non-consecutive [0,2]"),
            ([1, 2, 3], torch.tensor([[0.9], [0.85]]), "Sum indices [1,2,3]"),
            ([0, 1, 2, 3], torch.tensor([[1.0], [1.0]]), "Sum all indices"),
        ]

        for indices, expected, description in test_cases:
            try:
                script = (
                    f"expect predictions; define result = sum(predictions, {indices})"
                )
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual = actual.value
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Sum_{description}", is_close, expected=expected, actual=actual
                )
            except Exception as e:
                self.log_test(f"Sum_{description}", False, f"Error: {e}")

    def test_cardinality_functions_accuracy(self):
        """Test cardinality constraint functions for mathematical correctness."""
        # Test with deterministic probability distributions
        probs = torch.tensor([[0.8, 0.1, 0.05, 0.05], [0.2, 0.3, 0.4, 0.1]])
        features = {"probs": probs}

        # For at_least_k, we expect: truth value based on how many exceed threshold
        test_cases = [
            ("at_least_k(probs, 0)", "At least 0 (always true)"),
            ("at_least_k(probs, 1)", "At least 1"),
            ("at_least_k(probs, 2)", "At least 2"),
            ("at_least_k(probs, 4)", "At least 4 (all)"),
            ("at_most_k(probs, 0)", "At most 0"),
            ("at_most_k(probs, 1)", "At most 1"),
            ("at_most_k(probs, 3)", "At most 3"),
            ("at_most_k(probs, 4)", "At most 4 (always true)"),
            ("exactly_k(probs, 0)", "Exactly 0"),
            ("exactly_k(probs, 1)", "Exactly 1"),
            ("exactly_k(probs, 2)", "Exactly 2"),
        ]

        for expr, description in test_cases:
            try:
                script = f"expect probs; define result = {expr}"
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual_val = actual.value
                    # Validate that result is a valid probability (0 <= val <= 1)
                    is_valid = torch.all(actual_val >= 0) and torch.all(actual_val <= 1)
                    self.log_test(
                        f"Cardinality_{description}",
                        is_valid,
                        f"Result range [0,1]: {actual_val.min().item():.6f} to {actual_val.max().item():.6f}",
                    )
                else:
                    self.log_test(
                        f"Cardinality_{description}",
                        False,
                        f"Not a Truth object: {type(actual)}",
                    )
            except Exception as e:
                self.log_test(f"Cardinality_{description}", False, f"Error: {e}")

    def test_threshold_functions_accuracy(self):
        """Test threshold-based functions for mathematical correctness."""
        features = {
            "values": torch.tensor([[0.2, 0.8, 0.5, 0.9], [0.1, 0.6, 0.3, 0.7]]),
        }

        test_cases = [
            # Threshold function - should return 1 if >= threshold, 0 otherwise
            (
                "threshold(values, 0.5)",
                [[0.0, 1.0, 1.0, 1.0], [0.0, 1.0, 0.0, 1.0]],
                "Threshold 0.5",
            ),
            (
                "threshold(values, 0.8)",
                [[0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0]],
                "Threshold 0.8",
            ),
            # Clamp function - should constrain values between min and max
            (
                "clamp(values, 0.3, 0.7)",
                [[0.3, 0.7, 0.5, 0.7], [0.3, 0.6, 0.3, 0.7]],
                "Clamp [0.3, 0.7]",
            ),
            (
                "clamp(values, 0.0, 1.0)",
                [[0.2, 0.8, 0.5, 0.9], [0.1, 0.6, 0.3, 0.7]],
                "Clamp [0.0, 1.0] (no change)",
            ),
        ]

        for expr, expected_list, description in test_cases:
            try:
                script = f"expect values; define result = {expr}"
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual = actual.value

                expected = torch.tensor(expected_list)
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Threshold_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Threshold_{description}", False, f"Error: {e}")

    # =================================================================
    # 4. EDGE CASE NUMERICAL STABILITY
    # =================================================================

    def test_floating_point_precision(self):
        """Test floating point precision and edge cases."""
        test_cases = [
            # Very small numbers
            ("const result = 1e-10 + 1e-10", 2e-10, "Very small addition"),
            ("const result = 1e-15 * 1e15", 1.0, "Very small * very large"),
            # Numbers close to 1
            ("const result = 0.9999999 + 0.0000001", 1.0, "Close to 1"),
            ("const result = 1.0000001 - 0.0000001", 1.0, "Close to 1 subtraction"),
            # Precision edge cases
            ("const result = 0.1 + 0.1 + 0.1", 0.3, "Multiple 0.1 additions"),
            ("const result = 1.0 / 3.0 * 3.0", 1.0, "Division then multiplication"),
        ]

        for script, expected, description in test_cases:
            try:
                self.interpreter.execute(script)
                actual = self.interpreter.get_variable("result")
                # Use slightly higher tolerance for floating point edge cases
                is_close = self.assert_close(actual, expected, tolerance=1e-10)
                self.log_test(
                    f"Precision_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Precision_{description}", False, f"Error: {e}")

    def test_boundary_value_accuracy(self):
        """Test operations at boundary values (0, 1, extremes)."""
        features = {
            "zeros": torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
            "ones": torch.tensor([[1.0, 1.0], [1.0, 1.0]]),
            "mixed": torch.tensor([[0.0, 1.0], [1.0, 0.0]]),
        }

        test_cases = [
            # Operations with zeros
            (
                "expect zeros; define result = zeros + 1",
                torch.tensor([[1.0, 1.0], [1.0, 1.0]]),
                "Zeros + 1",
            ),
            (
                "expect zeros; define result = zeros * 100",
                torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
                "Zeros * 100",
            ),
            # Operations with ones
            (
                "expect ones; define result = ones - 1",
                torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
                "Ones - 1",
            ),
            (
                "expect ones; define result = ones * 0.5",
                torch.tensor([[0.5, 0.5], [0.5, 0.5]]),
                "Ones * 0.5",
            ),
            # Logical operations at boundaries
            (
                "expect zeros, ones; define result = zeros | ones",
                torch.tensor([[1.0, 1.0], [1.0, 1.0]]),
                "Zeros OR Ones",
            ),
            (
                "expect zeros, ones; define result = zeros & ones",
                torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
                "Zeros AND Ones",
            ),
            # NOT operation
            (
                "expect zeros; define result = ~zeros",
                torch.tensor([[1.0, 1.0], [1.0, 1.0]]),
                "NOT Zeros",
            ),
            (
                "expect ones; define result = ~ones",
                torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
                "NOT Ones",
            ),
        ]

        for script, expected, description in test_cases:
            try:
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual = actual.value
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Boundary_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Boundary_{description}", False, f"Error: {e}")

    # =================================================================
    # 5. SEMANTIC OPERATIONS ACCURACY
    # =================================================================

    def test_different_semantics_accuracy(self):
        """Test logical operations under different semantics."""
        semantics_list = [
            (GodelSemantics(), "Godel"),
            (LukasiewiczSemantics(), "Lukasiewicz"),
            (ProductSemantics(), "Product"),
        ]

        # Test values
        p1, p2 = 0.7, 0.3
        features = {"a": torch.tensor([[p1]]), "b": torch.tensor([[p2]])}

        for semantics, name in semantics_list:
            interpreter = RuleInterpreter(default_semantics=semantics)

            # Expected results for each semantics
            if name == "Godel":
                expected_and = min(p1, p2)  # 0.3
                expected_or = max(p1, p2)  # 0.7
            elif name == "Lukasiewicz":
                expected_and = max(0, p1 + p2 - 1)  # max(0, 0.7 + 0.3 - 1) = 0.0
                expected_or = min(1, p1 + p2)  # min(1, 0.7 + 0.3) = 1.0
            elif name == "Product":
                expected_and = p1 * p2  # 0.7 * 0.3 = 0.21
                expected_or = p1 + p2 - p1 * p2  # 0.7 + 0.3 - 0.21 = 0.79

            # Test AND operation
            try:
                result = interpreter.execute(
                    "expect a, b; define result = a & b", features
                )
                actual = interpreter.get_variable("result").value.item()
                is_close = self.assert_close(actual, expected_and)
                self.log_test(
                    f"Semantics_{name}_AND",
                    is_close,
                    f"AND({p1}, {p2}) in {name}",
                    expected=expected_and,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Semantics_{name}_AND", False, f"Error: {e}")

            # Test OR operation
            try:
                result = interpreter.execute(
                    "expect a, b; define result = a | b", features
                )
                actual = interpreter.get_variable("result").value.item()
                is_close = self.assert_close(actual, expected_or)
                self.log_test(
                    f"Semantics_{name}_OR",
                    is_close,
                    f"OR({p1}, {p2}) in {name}",
                    expected=expected_or,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Semantics_{name}_OR", False, f"Error: {e}")

    # =================================================================
    # 6. INTEGRATION NUMERICAL TESTS
    # =================================================================

    def test_complex_mathematical_scenarios(self):
        """Test complex mathematical scenarios for end-to-end accuracy."""
        features = {
            "probs": torch.tensor([[0.6, 0.3, 0.1], [0.2, 0.5, 0.3]]),
            "weights": torch.tensor([[0.8], [0.4]]),
            "baseline": torch.tensor([[0.5], [0.5]]),
        }

        # Complex weighted probability calculation
        script = """
        expect probs, weights, baseline
        
        # Weighted sum of probabilities  
        define high_prob_classes = sum(probs, [0, 1])
        define weighted_score = high_prob_classes * weights
        
        # Normalized difference from baseline
        define diff_from_baseline = weighted_score - baseline
        define normalized_diff = diff_from_baseline / baseline
        
        # Threshold decision
        define significant_deviation = normalized_diff > 0.2
        """

        try:
            result = self.interpreter.execute(script, features)

            # Manually calculate expected results
            high_prob_sum = torch.tensor([[0.9], [0.7]])  # [0.6+0.3, 0.2+0.5]
            weighted = high_prob_sum * features["weights"]  # [[0.72], [0.28]]
            diff = weighted - features["baseline"]  # [[0.22], [-0.22]]
            normalized = diff / features["baseline"]  # [[0.44], [-0.44]]
            significant = (normalized > 0.2).float()  # [[1.0], [0.0]]

            # Check each intermediate result
            tests = [
                ("high_prob_classes", high_prob_sum, "High probability sum"),
                ("weighted_score", weighted, "Weighted score"),
                ("diff_from_baseline", diff, "Difference from baseline"),
                ("normalized_diff", normalized, "Normalized difference"),
                ("significant_deviation", significant, "Significant deviation"),
            ]

            for var_name, expected, description in tests:
                actual = self.interpreter.get_variable(var_name)
                if isinstance(actual, Truth):
                    actual = actual.value
                is_close = self.assert_close(actual, expected)
                self.log_test(
                    f"Complex_{description}", is_close, expected=expected, actual=actual
                )

        except Exception as e:
            self.log_test("Complex_Mathematical_Scenario", False, f"Error: {e}")

    # =================================================================
    # MAIN TEST RUNNER
    # =================================================================

    def run_all_tests(self):
        """Run the complete numerical accuracy test suite."""
        print("🔬 NUMERICAL ACCURACY TEST SUITE FOR LOGIC-LANG")
        print("=" * 70)

        # Reset interpreter for clean state
        self.interpreter = RuleInterpreter()

        print("\n🧮 1. ARITHMETIC OPERATIONS ACCURACY")
        self.test_basic_arithmetic_accuracy()
        self.test_complex_arithmetic_expressions()
        self.test_tensor_arithmetic_accuracy()

        print("\n📊 2. LOGICAL OPERATIONS TRUTH TABLES")
        self.test_logical_operations_truth_tables()
        self.test_comparison_operations_accuracy()

        print("\n⚙️ 3. BUILT-IN FUNCTIONS MATHEMATICAL CORRECTNESS")
        self.test_sum_function_accuracy()
        self.test_cardinality_functions_accuracy()
        self.test_threshold_functions_accuracy()

        print("\n🎯 4. EDGE CASE NUMERICAL STABILITY")
        self.test_floating_point_precision()
        self.test_boundary_value_accuracy()

        print("\n🧠 5. SEMANTIC OPERATIONS ACCURACY")
        self.test_different_semantics_accuracy()

        print("\n🔗 6. INTEGRATION NUMERICAL TESTS")
        self.test_complex_mathematical_scenarios()

        # Summary
        print("\n" + "=" * 70)
        print("📊 NUMERICAL ACCURACY TEST SUMMARY")
        print("=" * 70)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _, _, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Numerical Accuracy: {passed_tests/total_tests*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED NUMERICAL TESTS:")
            for name, passed, details, expected, actual in self.test_results:
                if not passed:
                    error_detail = f"  • {name}: {details}"
                    if expected is not None and actual is not None:
                        if isinstance(expected, torch.Tensor):
                            exp_str = f"tensor({expected.tolist()})"
                        else:
                            exp_str = str(expected)
                        if isinstance(actual, torch.Tensor):
                            act_str = f"tensor({actual.tolist()})"
                        else:
                            act_str = str(actual)
                        error_detail += (
                            f"\n    Expected: {exp_str}\n    Actual:   {act_str}"
                        )
                    print(error_detail)
        else:
            print("\n✅ All numerical accuracy tests passed!")
            print("🎯 Logic-lang mathematical operations are numerically correct!")

        return failed_tests == 0


def main():
    """Run the numerical accuracy test suite."""
    tester = NumericalAccuracyTest()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 ALL NUMERICAL TESTS PASSED! Logic-lang is mathematically accurate.")
    else:
        print(
            "\n⚠️  Some numerical accuracy issues found. Please review the failures above."
        )

    return success


if __name__ == "__main__":
    main()
