"""Test negative number support in logic-lang."""

import torch
from logic_lang import RuleParser, RuleInterpreter


def test_negative_numbers():
    """Test that negative numbers are parsed and evaluated correctly."""

    # Test parsing negative numbers
    parser = RuleParser()

    # Test simple negative number
    script1 = "const negative_threshold = -0.5"
    ast1 = parser.parse(script1)
    assert len(ast1.statements) == 1
    print("✓ Parsed negative constant")

    # Test negative number in expression
    script2 = """
    expect values
    define low_values = values < -0.3
    """
    ast2 = parser.parse(script2)
    assert len(ast2.statements) == 2
    print("✓ Parsed negative number in comparison")

    # Test execution with negative numbers
    interpreter = RuleInterpreter()

    # Test with negative constant
    script3 = """
    const neg_threshold = -0.7
    const pos_threshold = 0.8
    expect risk_score
    define high_risk = risk_score > pos_threshold
    define very_low_risk = risk_score < neg_threshold
    constraint high_risk weight=1.0
    constraint very_low_risk weight=0.5
    """

    features = {"risk_score": torch.tensor([[0.9, -0.8, 0.2, -0.5]])}

    constraint_set = interpreter.execute(script3, features)
    print(
        f"✓ Executed script with negative constants, got {len(constraint_set.constraints)} constraints"
    )

    # Test unary minus on variables
    script4 = """
    expect values
    define negated_values = -values
    constraint negated_values < 0.0 weight=1.0
    """

    features4 = {"values": torch.tensor([[0.5, 0.3, 0.8]])}

    constraint_set4 = interpreter.execute(script4, features4)
    print(
        f"✓ Executed script with unary minus on variables, got {len(constraint_set4.constraints)} constraints"
    )

    # Test mixed positive and negative numbers
    script5 = """
    const low = -1.0
    const high = +1.0
    expect data
    define in_range = (data >= low) & (data <= high)
    constraint in_range weight=0.8
    """

    features5 = {"data": torch.tensor([[-0.5, 0.0, 0.5, 1.5, -1.5]])}

    constraint_set5 = interpreter.execute(script5, features5)
    print(
        f"✓ Executed script with positive and negative bounds, got {len(constraint_set5.constraints)} constraints"
    )

    print("All negative number tests passed! ✅")


if __name__ == "__main__":
    test_negative_numbers()
