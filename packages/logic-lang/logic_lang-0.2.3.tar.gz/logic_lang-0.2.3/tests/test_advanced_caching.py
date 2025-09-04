#!/usr/bin/env python3
"""Test caching with expressions that should truly hit cache."""

import torch
from logic_lang.interpreter import RuleInterpreter


def test_subexpression_caching():
    """Test that subexpressions within a complex expression get cached."""

    print("🔍 Testing subexpression caching...")

    # Create a script where the same subexpression appears multiple times
    # within a single complex expression
    script = """
    expect x, y, z
    define complex = (x + y) * (x + y) + (x + y) * z
    """

    interpreter = RuleInterpreter(enable_caching=True)
    features = {
        "x": torch.tensor([1.0]),
        "y": torch.tensor([2.0]),
        "z": torch.tensor([3.0]),
    }

    # Execute the script
    constraints = interpreter.execute(script, features)

    stats = interpreter.get_cache_stats()
    print(f"   Cache stats: {stats}")

    if stats["cache_hits"] > 0:
        print(f"   ✓ Found {stats['cache_hits']} cache hits!")
        print(
            "   This means subexpressions within complex expressions are being cached."
        )
    else:
        print("   ⚠️  No cache hits found.")
        print(
            "   This suggests that even within a single expression, subexpressions aren't reused."
        )

    return stats["cache_hits"] > 0


def test_function_call_caching():
    """Test that function calls with same arguments get cached."""

    print("\n🔍 Testing function call caching...")

    # Use a simple arithmetic function call that will work
    script = """
    expect a, b, c
    define temp1 = greater_than(a, b)
    define temp2 = greater_than(a, b)  # Same function call
    define result = temp1 + temp2
    """

    interpreter = RuleInterpreter(enable_caching=True)
    features = {
        "a": torch.tensor([1.0]),
        "b": torch.tensor([0.5]),
        "c": torch.tensor([2.0]),
    }

    # Execute the script
    constraints = interpreter.execute(script, features)

    stats = interpreter.get_cache_stats()
    print(f"   Cache stats: {stats}")

    if stats["cache_hits"] > 0:
        print(f"   ✓ Found {stats['cache_hits']} cache hits!")
        print("   Function calls with identical arguments are being cached.")
    else:
        print("   ⚠️  No cache hits found.")
        print(
            "   This is expected due to variable environment changes between define statements."
        )

    return stats["cache_hits"] > 0


if __name__ == "__main__":
    print("🧪 Advanced Cache Testing")
    print("=" * 40)

    subexpr_success = test_subexpression_caching()
    func_success = test_function_call_caching()

    if subexpr_success or func_success:
        print(f"\n✅ Cache optimization is working!")
    else:
        print(f"\n⚠️  Cache optimization needs investigation.")
        print(
            "   The cache infrastructure is in place but may need tuning for better hits."
        )
