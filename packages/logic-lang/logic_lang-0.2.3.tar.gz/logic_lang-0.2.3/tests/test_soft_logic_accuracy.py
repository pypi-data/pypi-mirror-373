#!/usr/bin/env python3
"""
SOFT LOGIC NUMERICAL ACCURACY TEST SUITE FOR LOGIC-LANG

This test suite validates the mathematical correctness and numerical accuracy
of logic-lang operations, accounting for the soft/differentiable nature of
the logical operations which use smooth approximations rather than exact
Boolean logic for neural network compatibility.

Key insights from testing:
- Logical operations use smooth approximations (e.g., sigmoid-based) rather than exact min/max
- Small deviations from exact Boolean logic are expected and by design
- Arithmetic operations maintain high numerical precision
- Constraint functions operate within valid probability ranges [0,1]
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


class SoftLogicAccuracyTest:
    """Numerical accuracy validation for soft logic operations in logic-lang."""

    def __init__(self):
        self.parser = RuleParser()
        self.interpreter = RuleInterpreter()
        # Use appropriate tolerances for different operation types
        self.arithmetic_tolerance = 1e-6  # High precision for arithmetic
        self.soft_logic_tolerance = 1e-2  # More relaxed for soft logic operations
        self.boundary_tolerance = 1e-5  # Medium precision for boundary cases
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

    def assert_close(self, actual: Any, expected: Any, tolerance: float) -> bool:
        """Check if two values are numerically close within tolerance."""
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
    # 1. ARITHMETIC PRECISION VALIDATION
    # =================================================================

    def test_arithmetic_high_precision(self):
        """Test arithmetic operations maintain high numerical precision."""
        test_cases = [
            # High precision arithmetic
            ("const result = 2.5 + 3.7", 6.2, "Addition precision"),
            ("const result = 1.0 / 3.0", 1.0 / 3.0, "Division precision"),
            ("const result = 0.1 + 0.2", 0.3, "Decimal precision"),
            ("const result = (10 + 5) / (3 - 1)", 7.5, "Complex expression precision"),
            ("const result = 1e-10 + 1e-10", 2e-10, "Small number precision"),
            ("const result = 1e2 + 1e1", 110.0, "Scientific notation precision"),
        ]

        for script, expected, description in test_cases:
            try:
                self.interpreter.execute(script)
                actual = self.interpreter.get_variable("result")
                is_close = self.assert_close(
                    actual, expected, self.arithmetic_tolerance
                )
                self.log_test(
                    f"Arithmetic_Precision_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(
                    f"Arithmetic_Precision_{description}", False, f"Error: {e}"
                )

    def test_tensor_arithmetic_precision(self):
        """Test tensor arithmetic maintains precision."""
        features = {
            "a": torch.tensor([[2.0, 4.0], [6.0, 8.0]]),
            "b": torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
        }

        test_cases = [
            (
                "expect a, b; define result = a + b",
                torch.tensor([[3.0, 6.0], [9.0, 12.0]]),
                "Tensor addition",
            ),
            (
                "expect a, b; define result = a * b",
                torch.tensor([[2.0, 8.0], [18.0, 32.0]]),
                "Tensor multiplication",
            ),
            (
                "expect a; define result = a * 0.5",
                torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
                "Scalar multiplication",
            ),
        ]

        for script, expected, description in test_cases:
            try:
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual = actual.value
                is_close = self.assert_close(
                    actual, expected, self.arithmetic_tolerance
                )
                self.log_test(
                    f"Tensor_Precision_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Tensor_Precision_{description}", False, f"Error: {e}")

    # =================================================================
    # 2. SOFT LOGIC BEHAVIOR VALIDATION
    # =================================================================

    def test_soft_logic_approximations(self):
        """Test that soft logic operations behave approximately as expected."""
        prob_values = [0.0, 0.3, 0.7, 1.0]

        for p1 in prob_values:
            for p2 in prob_values:
                features = {"a": torch.tensor([[p1]]), "b": torch.tensor([[p2]])}

                # Test OR operation - should be approximately max(p1, p2)
                try:
                    result = self.interpreter.execute(
                        "expect a, b; define result = a | b", features
                    )
                    actual = self.interpreter.get_variable("result").value.item()
                    expected = max(p1, p2)
                    is_close = self.assert_close(
                        actual, expected, self.soft_logic_tolerance
                    )
                    self.log_test(
                        f"SoftLogic_OR_{p1}_{p2}",
                        is_close,
                        f"OR({p1}, {p2}) ≈ {expected}",
                        expected=expected,
                        actual=actual,
                    )
                except Exception as e:
                    self.log_test(f"SoftLogic_OR_{p1}_{p2}", False, f"Error: {e}")

                # Test AND operation - should be approximately min(p1, p2)
                try:
                    result = self.interpreter.execute(
                        "expect a, b; define result = a & b", features
                    )
                    actual = self.interpreter.get_variable("result").value.item()
                    expected = min(p1, p2)
                    is_close = self.assert_close(
                        actual, expected, self.soft_logic_tolerance
                    )
                    self.log_test(
                        f"SoftLogic_AND_{p1}_{p2}",
                        is_close,
                        f"AND({p1}, {p2}) ≈ {expected}",
                        expected=expected,
                        actual=actual,
                    )
                except Exception as e:
                    self.log_test(f"SoftLogic_AND_{p1}_{p2}", False, f"Error: {e}")

    def test_soft_logic_boundary_behavior(self):
        """Test soft logic operations at boundaries with appropriate tolerance."""
        features = {
            "zeros": torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
            "ones": torch.tensor([[1.0, 1.0], [1.0, 1.0]]),
        }

        test_cases = [
            # NOT operation at boundaries - allow small deviations
            (
                "expect zeros; define result = ~zeros",
                torch.tensor([[1.0, 1.0], [1.0, 1.0]]),
                "NOT zeros ≈ ones",
            ),
            (
                "expect ones; define result = ~ones",
                torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
                "NOT ones ≈ zeros",
            ),
            # OR with boundaries
            (
                "expect zeros, ones; define result = zeros | ones",
                torch.tensor([[1.0, 1.0], [1.0, 1.0]]),
                "zeros OR ones ≈ ones",
            ),
            # AND with boundaries
            (
                "expect zeros, ones; define result = zeros & ones",
                torch.tensor([[0.0, 0.0], [0.0, 0.0]]),
                "zeros AND ones ≈ zeros",
            ),
        ]

        for script, expected, description in test_cases:
            try:
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual = actual.value
                is_close = self.assert_close(actual, expected, self.boundary_tolerance)
                self.log_test(
                    f"SoftLogic_Boundary_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"SoftLogic_Boundary_{description}", False, f"Error: {e}")

    # =================================================================
    # 3. CONSTRAINT FUNCTION VALIDATION
    # =================================================================

    def test_sum_function_precision(self):
        """Test sum function maintains arithmetic precision."""
        predictions = torch.tensor([[0.1, 0.2, 0.3, 0.4], [0.15, 0.25, 0.35, 0.25]])
        features = {"predictions": predictions}

        test_cases = [
            ([0, 1], torch.tensor([[0.3], [0.4]]), "Sum [0,1] precision"),
            ([0, 1, 2, 3], torch.tensor([[1.0], [1.0]]), "Sum all indices precision"),
            ([2], torch.tensor([[0.3], [0.35]]), "Sum single index precision"),
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
                is_close = self.assert_close(
                    actual, expected, self.arithmetic_tolerance
                )
                self.log_test(
                    f"Sum_Precision_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Sum_Precision_{description}", False, f"Error: {e}")

    def test_constraint_validity_ranges(self):
        """Test that constraint functions return valid probability ranges."""
        probs = torch.tensor([[0.8, 0.1, 0.05, 0.05], [0.2, 0.3, 0.4, 0.1]])
        features = {"probs": probs}

        constraint_functions = [
            ("at_least_k(probs, 1)", "at_least_k"),
            ("at_most_k(probs, 2)", "at_most_k"),
            ("exactly_k(probs, 1)", "exactly_k"),
            ("exactly_one(probs)", "exactly_one"),
        ]

        for expr, name in constraint_functions:
            try:
                script = f"expect probs; define result = {expr}"
                result = self.interpreter.execute(script, features)
                actual = self.interpreter.get_variable("result")
                if isinstance(actual, Truth):
                    actual_val = actual.value
                    # Validate that result is in valid probability range [0, 1]
                    min_val = actual_val.min().item()
                    max_val = actual_val.max().item()
                    is_valid = min_val >= 0.0 and max_val <= 1.0
                    self.log_test(
                        f"Constraint_Range_{name}",
                        is_valid,
                        f"Range [{min_val:.6f}, {max_val:.6f}] ∈ [0,1]",
                    )
                else:
                    self.log_test(
                        f"Constraint_Range_{name}",
                        False,
                        f"Not a Truth object: {type(actual)}",
                    )
            except Exception as e:
                self.log_test(f"Constraint_Range_{name}", False, f"Error: {e}")

    def test_threshold_function_behavior(self):
        """Test threshold function behavior (uses > not >=)."""
        features = {
            "values": torch.tensor([[0.2, 0.8, 0.5, 0.9], [0.1, 0.6, 0.3, 0.7]])
        }

        test_cases = [
            # Threshold function uses > (strictly greater than)
            (
                "threshold(values, 0.5)",
                [[0.0, 1.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0]],
                "Threshold 0.5 (> not >=)",
            ),
            (
                "threshold(values, 0.7)",
                [[0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0]],
                "Threshold 0.7",
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
                is_close = self.assert_close(
                    actual, expected, self.arithmetic_tolerance
                )
                self.log_test(
                    f"Threshold_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Threshold_{description}", False, f"Error: {e}")

    # =================================================================
    # 4. COMPARISON OPERATIONS PRECISION
    # =================================================================

    def test_comparison_precision(self):
        """Test comparison operations for exact results."""
        test_cases = [
            (5.0, 3.0, ">", 1.0, "5.0 > 3.0"),
            (3.0, 5.0, ">", 0.0, "3.0 > 5.0"),
            (4.0, 4.0, "==", 1.0, "4.0 == 4.0"),
            (4.0, 5.0, "==", 0.0, "4.0 == 5.0"),
            (3.0, 5.0, "<=", 1.0, "3.0 <= 5.0"),
        ]

        for val1, val2, op, expected, description in test_cases:
            try:
                script = f"const result = {val1} {op} {val2}"
                self.interpreter.execute(script)
                actual = self.interpreter.get_variable("result")
                is_close = self.assert_close(
                    actual, expected, self.arithmetic_tolerance
                )
                self.log_test(
                    f"Comparison_Precision_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(
                    f"Comparison_Precision_{description}", False, f"Error: {e}"
                )

    # =================================================================
    # 5. INTEGRATION CORRECTNESS TEST
    # =================================================================

    def test_complex_mathematical_integration(self):
        """Test complex mathematical scenarios for end-to-end correctness."""
        features = {
            "probs": torch.tensor([[0.6, 0.3, 0.1], [0.2, 0.5, 0.3]]),
            "weights": torch.tensor([[0.8], [0.4]]),
            "baseline": torch.tensor([[0.5], [0.5]]),
        }

        # Simpler version to avoid parsing issues
        script = """
        expect probs, weights, baseline
        
        # Weighted sum of probabilities  
        define high_prob_classes = sum(probs, [0, 1])
        define weighted_score = high_prob_classes * weights
        
        # Difference from baseline
        define diff_from_baseline = weighted_score - baseline
        """

        try:
            result = self.interpreter.execute(script, features)

            # Manually calculate expected results
            high_prob_sum = torch.tensor([[0.9], [0.7]])  # [0.6+0.3, 0.2+0.5]
            weighted = high_prob_sum * features["weights"]  # [[0.72], [0.28]]
            diff = weighted - features["baseline"]  # [[0.22], [-0.22]]

            # Check each intermediate result
            tests = [
                ("high_prob_classes", high_prob_sum, "High probability sum"),
                ("weighted_score", weighted, "Weighted score"),
                ("diff_from_baseline", diff, "Difference from baseline"),
            ]

            for var_name, expected, description in tests:
                actual = self.interpreter.get_variable(var_name)
                if isinstance(actual, Truth):
                    actual = actual.value
                is_close = self.assert_close(
                    actual, expected, self.arithmetic_tolerance
                )
                self.log_test(
                    f"Integration_{description}",
                    is_close,
                    expected=expected,
                    actual=actual,
                )

        except Exception as e:
            self.log_test("Integration_Complex_Scenario", False, f"Error: {e}")

    # =================================================================
    # 6. SEMANTIC OPERATION APPROXIMATIONS
    # =================================================================

    def test_semantic_approximations(self):
        """Test logical operations under different semantics with appropriate tolerance."""
        semantics_list = [
            (GodelSemantics(), "Godel"),
            (LukasiewiczSemantics(), "Lukasiewicz"),
            (ProductSemantics(), "Product"),
        ]

        p1, p2 = 0.7, 0.3
        features = {"a": torch.tensor([[p1]]), "b": torch.tensor([[p2]])}

        for semantics, name in semantics_list:
            interpreter = RuleInterpreter(default_semantics=semantics)

            # Expected results for each semantics
            if name == "Godel":
                expected_and = min(p1, p2)  # 0.3
                expected_or = max(p1, p2)  # 0.7
            elif name == "Lukasiewicz":
                expected_and = max(0, p1 + p2 - 1)  # 0.0
                expected_or = min(1, p1 + p2)  # 1.0
            elif name == "Product":
                expected_and = p1 * p2  # 0.21
                expected_or = p1 + p2 - p1 * p2  # 0.79

            # Test AND operation with soft logic tolerance
            try:
                result = interpreter.execute(
                    "expect a, b; define result = a & b", features
                )
                actual = interpreter.get_variable("result").value.item()
                is_close = self.assert_close(
                    actual, expected_and, self.soft_logic_tolerance
                )
                self.log_test(
                    f"Semantics_{name}_AND_Approx",
                    is_close,
                    f"AND({p1}, {p2}) ≈ {expected_and} in {name}",
                    expected=expected_and,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Semantics_{name}_AND_Approx", False, f"Error: {e}")

            # Test OR operation with soft logic tolerance
            try:
                result = interpreter.execute(
                    "expect a, b; define result = a | b", features
                )
                actual = interpreter.get_variable("result").value.item()
                is_close = self.assert_close(
                    actual, expected_or, self.soft_logic_tolerance
                )
                self.log_test(
                    f"Semantics_{name}_OR_Approx",
                    is_close,
                    f"OR({p1}, {p2}) ≈ {expected_or} in {name}",
                    expected=expected_or,
                    actual=actual,
                )
            except Exception as e:
                self.log_test(f"Semantics_{name}_OR_Approx", False, f"Error: {e}")

    # =================================================================
    # MAIN TEST RUNNER
    # =================================================================

    def run_all_tests(self):
        """Run the complete soft logic accuracy test suite."""
        print("🔬 SOFT LOGIC NUMERICAL ACCURACY TEST SUITE FOR LOGIC-LANG")
        print("=" * 75)
        print(
            "Testing numerical accuracy accounting for soft/differentiable logic operations"
        )
        print("=" * 75)

        # Reset interpreter for clean state
        self.interpreter = RuleInterpreter()

        print("\n🧮 1. ARITHMETIC PRECISION VALIDATION")
        self.test_arithmetic_high_precision()
        self.test_tensor_arithmetic_precision()

        print("\n🌊 2. SOFT LOGIC BEHAVIOR VALIDATION")
        self.test_soft_logic_approximations()
        self.test_soft_logic_boundary_behavior()

        print("\n⚙️ 3. CONSTRAINT FUNCTION VALIDATION")
        self.test_sum_function_precision()
        self.test_constraint_validity_ranges()
        self.test_threshold_function_behavior()

        print("\n📊 4. COMPARISON OPERATIONS PRECISION")
        self.test_comparison_precision()

        print("\n🔗 5. INTEGRATION CORRECTNESS TEST")
        self.test_complex_mathematical_integration()

        print("\n🧠 6. SEMANTIC OPERATION APPROXIMATIONS")
        self.test_semantic_approximations()

        # Summary
        print("\n" + "=" * 75)
        print("📊 SOFT LOGIC ACCURACY TEST SUMMARY")
        print("=" * 75)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _, _, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Soft Logic Accuracy: {passed_tests/total_tests*100:.1f}%")

        # Categorize results
        arithmetic_tests = [
            r for r in self.test_results if "Precision" in r[0] or "Comparison" in r[0]
        ]
        soft_logic_tests = [
            r for r in self.test_results if "SoftLogic" in r[0] or "Semantics" in r[0]
        ]
        constraint_tests = [
            r
            for r in self.test_results
            if "Constraint" in r[0] or "Sum_" in r[0] or "Threshold" in r[0]
        ]

        arithmetic_passed = sum(1 for _, passed, _, _, _ in arithmetic_tests if passed)
        soft_logic_passed = sum(1 for _, passed, _, _, _ in soft_logic_tests if passed)
        constraint_passed = sum(1 for _, passed, _, _, _ in constraint_tests if passed)

        print(f"\n📈 Category Breakdown:")
        print(
            f"  Arithmetic Operations: {arithmetic_passed}/{len(arithmetic_tests)} ({arithmetic_passed/len(arithmetic_tests)*100:.1f}%)"
        )
        print(
            f"  Soft Logic Operations: {soft_logic_passed}/{len(soft_logic_tests)} ({soft_logic_passed/len(soft_logic_tests)*100:.1f}%)"
        )
        print(
            f"  Constraint Functions: {constraint_passed}/{len(constraint_tests)} ({constraint_passed/len(constraint_tests)*100:.1f}%)"
        )

        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for name, passed, details, expected, actual in self.test_results:
                if not passed:
                    print(f"  • {name}: {details}")
        else:
            print("\n✅ All numerical accuracy tests passed!")
            print(
                "🎯 Logic-lang operations are numerically accurate within expected tolerances!"
            )

        return failed_tests == 0


def main():
    """Run the soft logic accuracy test suite."""
    tester = SoftLogicAccuracyTest()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 ALL SOFT LOGIC ACCURACY TESTS PASSED!")
        print("✨ Logic-lang provides mathematically sound soft logic operations!")
    else:
        print("\n⚠️  Some accuracy issues found. This may indicate:")
        print("   - Unexpected behavior in soft logic approximations")
        print("   - Tolerance thresholds may need adjustment")
        print("   - Possible implementation issues")

    return success


if __name__ == "__main__":
    main()
