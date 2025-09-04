"""Tests for the expect statement with 'as' keyword aliasing functionality."""

import pytest
import torch
from logic_lang import RuleParser, RuleInterpreter


def test_expect_with_single_alias():
    """Test expect statement with a single aliased variable."""
    script = """
    expect original_var as alias_var
    define test_expr = alias_var
    """

    features = {"original_var": torch.tensor([[0.5]])}

    interpreter = RuleInterpreter()
    constraint_set = interpreter.execute(script, features)

    # Both original and alias should be available
    assert "original_var" in interpreter.variables
    assert "alias_var" in interpreter.variables
    assert torch.equal(
        interpreter.variables["original_var"], interpreter.variables["alias_var"]
    )


def test_expect_with_multiple_aliases():
    """Test expect statement with multiple aliased variables."""
    script = """
    expect left_birads as birads_L, right_birads as birads_R, mass_original as mass_L
    
    define findings_L = mass_L
    define test_sum = sum(birads_L, [3, 4])
    
    constraint exactly_one(birads_L)
    constraint exactly_one(birads_R)
    """

    features = {
        "left_birads": torch.tensor([[0.1, 0.2, 0.3, 0.3, 0.1]]),
        "right_birads": torch.tensor([[0.2, 0.3, 0.2, 0.2, 0.1]]),
        "mass_original": torch.tensor([[0.7]]),
    }

    interpreter = RuleInterpreter()
    constraint_set = interpreter.execute(script, features)

    # Check all aliases are correctly mapped
    assert torch.equal(
        interpreter.variables["left_birads"], interpreter.variables["birads_L"]
    )
    assert torch.equal(
        interpreter.variables["right_birads"], interpreter.variables["birads_R"]
    )
    assert torch.equal(
        interpreter.variables["mass_original"], interpreter.variables["mass_L"]
    )

    # Check constraints were created
    assert len(constraint_set.constraints) == 2


def test_expect_mixed_aliases_and_regular():
    """Test expect statement with both aliased and non-aliased variables."""
    script = """
    expect var1 as alias1, var2, var3 as alias3, var4
    
    define combined = alias1 | var2 | alias3 | var4
    """

    features = {
        "var1": torch.tensor([[0.1]]),
        "var2": torch.tensor([[0.2]]),
        "var3": torch.tensor([[0.3]]),
        "var4": torch.tensor([[0.4]]),
    }

    interpreter = RuleInterpreter()
    constraint_set = interpreter.execute(script, features)

    # Check all variables are available
    expected_vars = ["var1", "alias1", "var2", "var3", "alias3", "var4"]
    for var in expected_vars:
        assert var in interpreter.variables

    # Check aliases point to correct original variables
    assert torch.equal(interpreter.variables["var1"], interpreter.variables["alias1"])
    assert torch.equal(interpreter.variables["var3"], interpreter.variables["alias3"])


def test_expect_without_aliases_still_works():
    """Test that regular expect statements without aliases still work."""
    script = """
    expect var1, var2, var3
    define test_expr = var1 | var2 | var3
    """

    features = {
        "var1": torch.tensor([[0.1]]),
        "var2": torch.tensor([[0.2]]),
        "var3": torch.tensor([[0.3]]),
    }

    interpreter = RuleInterpreter()
    constraint_set = interpreter.execute(script, features)

    # Check that variables are available (no aliases should be created)
    for var in ["var1", "var2", "var3"]:
        assert var in interpreter.variables


def test_expect_parsing_errors():
    """Test that parsing errors are properly handled for malformed expect statements."""
    parser = RuleParser()

    # Missing alias after 'as'
    with pytest.raises(Exception):
        parser.parse("expect var1 as")

    # Missing variable before 'as'
    with pytest.raises(Exception):
        parser.parse("expect as alias1")


def test_expect_alias_usage_in_constraints():
    """Test that aliased variables can be used properly in constraints."""
    script = """
    expect predictions as preds, labels as targets
    
    # Use aliases in constraint
    constraint exactly_one(preds) weight=1.0
    constraint exactly_one(targets) weight=0.5
    
    # Use aliases in definitions
    define accuracy_check = preds == targets
    """

    features = {
        "predictions": torch.tensor([[0.1, 0.7, 0.2]]),
        "labels": torch.tensor([[0.0, 1.0, 0.0]]),
    }

    interpreter = RuleInterpreter()
    constraint_set = interpreter.execute(script, features)

    # Check that constraints were created and aliases work
    assert len(constraint_set.constraints) == 2

    # Verify that the defined variable uses aliases correctly
    assert "accuracy_check" in interpreter.variables
