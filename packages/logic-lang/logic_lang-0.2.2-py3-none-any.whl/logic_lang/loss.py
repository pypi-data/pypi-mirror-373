"""
Flexible Rule-based Constraints Loss

A completely flexible version of rule-based constraint loss that works with any
feature configuration. Features and their indices are defined via a dictionary,
and constraints are specified through rule scripts (.logic files), making the
loss function fully agnostic and versatile for any domain.

Key Features:
- No hard-coded feature requirements
- Configurable activation functions per feature
- Support for .logic files for constraint specification
- Flexible tensor indexing for any model output structure
- Domain-agnostic constraint enforcement

Usage:
    1. Define feature_indices dictionary with (domain, indices, activation) tuples
    2. Create .logic file with constraint rules, or provide rules as string
    3. Initialize loss with feature_indices and rules
    4. Use with any model output tensor structure
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Callable, Literal, Optional, Dict, Union
from .soft_logic import (
    GodelSemantics,
    LukasiewiczSemantics,
    ProductSemantics,
    Semantics,
    _clamp01,
    Truth,
)
from .interpreter import RuleInterpreter


class RuleMammoLoss(nn.Module):
    """
    Flexible rule-based constraints loss using interpretable rule scripts.

    This class provides a completely flexible constraint loss that can work with any
    feature configuration and tensor shapes. Features and their indices are defined
    via a dictionary with flexible indexing schemes, and constraints are specified
    through rule scripts (.logic files), making the loss function fully agnostic
    and versatile.

    Args:
        feature_indices (dict): Maps feature names to extraction specifications.
                               Supports multiple indexing formats:
                               - Direct indexing: 'feature': 5 or 'feature': slice(0, 5)
                               - With activation: 'feature': (indices, 'softmax')
                               - Multi-dimensional: 'feature': (dim1_idx, dim2_idx, ...)
                               - Legacy 2D: 'feature': (domain_idx, output_indices)
                               - Complex: 'feature': ([1, 2], slice(0, 5), 'sigmoid')
        rules (str): Rule script defining constraints and logic (can be loaded from .logic file)
        semantics (Semantics | str, optional): Logic semantics for Truth operations
        eps (float): Numerical stability epsilon
        tau (float): Temperature parameter for semantics
        reduction (str): Loss reduction method ('mean', 'sum', or 'none')
        default_activation (str): Default activation function ('sigmoid', 'softmax', 'relu', 'tanh', 'none')

    Indexing Examples:
        >>> feature_indices = {
        ...     # Direct indexing (uses default activation)
        ...     'single_output': 5,                          # tensor[:, 5:6]
        ...     'range_outputs': slice(0, 5),                # tensor[:, 0:5]
        ...
        ...     # With custom activation
        ...     'categorical': (slice(0, 7), 'softmax'),     # tensor[:, 0:7] + softmax
        ...     'binary': (3, 'sigmoid'),                    # tensor[:, 3:4] + sigmoid
        ...
        ...     # Multi-dimensional indexing
        ...     'matrix_elem': (2, 3),                       # tensor[:, 2, 3]
        ...     'matrix_row': (1, slice(None)),              # tensor[:, 1, :]
        ...     'tensor_slice': (0, slice(2, 5), 1),         # tensor[:, 0, 2:5, 1]
        ...
        ...     # With activation for multi-dim
        ...     'complex': ((1, slice(0, 3)), 'softmax'),    # tensor[:, 1, 0:3] + softmax
        ...
        ...     # Legacy 2D format (backward compatible)
        ...     'legacy_feature': (1, slice(0, 7), 'softmax'), # domain 1, outputs 0:7
        ... }
        >>>
        >>> # Works with any tensor shape
        >>> # 2D: (batch, features)
        >>> # 3D: (batch, domains, features_per_domain)
        >>> # 4D: (batch, channels, height, width)
        >>> # etc.
        >>>
        >>> loss_fn = RuleMammoLoss(feature_indices, rules)
        >>> constraint_loss = loss_fn(logits)
    """

    def __init__(
        self,
        feature_indices: dict,
        rules: str,
        semantics: Optional[Union[str, Semantics]] = None,
        normalize_weights: Union[bool, float] = True,
        aggregation_mode: Literal["sum", "cvar"] = "sum",
        reduction: str = "mean",
        default_activation: str = "sigmoid",
        cvar_beta: float = 0.25,
        tau: float = 12.0,
        eps: float = 1e-7,
    ):
        super().__init__()

        # Validate and store feature indices
        self._validate_feature_indices(feature_indices)
        self.feature_indices = feature_indices
        self.default_activation = default_activation
        self.normalize_weights = float(normalize_weights)

        # Set up semantics
        if isinstance(semantics, str):
            semantics = {
                "godel": GodelSemantics(eps=eps, tau=tau),
                "lukasiewicz": LukasiewiczSemantics(eps=eps, softness=tau),
                "product": ProductSemantics(eps=eps),
            }.get(semantics.lower(), None)

        self.semantics = semantics or GodelSemantics(eps=eps, tau=tau)
        self.eps = eps

        # Store rules and create interpreter
        if os.path.isfile(rules) and rules.lower().endswith(".logic"):
            self.rules = load_rules_from_file(rules)
        else:
            self.rules = rules
        self.interpreter = RuleInterpreter(
            default_semantics=self.semantics, default_eps=eps
        )

        # Reduction settings
        assert reduction in [
            "mean",
            "sum",
            "none",
        ], "reduction must be 'mean', 'sum', or 'none'"
        self.reduction = reduction

        assert aggregation_mode in [
            "sum",
            "cvar",
        ], "aggregation_mode must be 'sum' or 'cvar'"
        self.aggregation_mode = aggregation_mode
        self.cvar_beta = cvar_beta

    def _validate_feature_indices(self, feature_indices: dict) -> None:
        """Validate that feature indices are provided in correct format."""
        if not feature_indices:
            raise ValueError("feature_indices cannot be empty")

        # Validate format: supports various indexing schemes
        # - (indices, activation): For arbitrary tensor indexing with activation
        # - (indices,): For arbitrary tensor indexing with default activation
        # - indices: For direct indexing (backward compatibility)
        # Where indices can be:
        #   - int: single index
        #   - tuple/list of ints: multi-dimensional indexing
        #   - slice: slice indexing
        #   - tuple/list containing mix of ints, slices, etc.

        for feature_name, config in feature_indices.items():
            if isinstance(config, (int, slice)):
                # Direct indexing: feature_name: 5 or feature_name: slice(0, 5)
                continue
            elif isinstance(config, (tuple, list)):
                if len(config) == 0:
                    raise ValueError(f"Feature '{feature_name}' config cannot be empty")
                elif len(config) == 1:
                    # Single element tuple/list: (indices,)
                    indices = config[0]
                    self._validate_indices(feature_name, indices)
                elif len(config) == 2:
                    # Could be (indices, activation) or legacy (domain_idx, output_indices)
                    indices, second_element = config
                    if isinstance(second_element, str):
                        # Format: (indices, activation)
                        self._validate_indices(feature_name, indices)
                        self._validate_activation(feature_name, second_element)
                    else:
                        # Legacy format: (domain_idx, output_indices) - validate both as indices
                        self._validate_indices(feature_name, indices)
                        self._validate_indices(feature_name, second_element)
                elif len(config) == 3:
                    # Format: (domain_idx, output_indices, activation) or (indices..., activation)
                    first, second, third = config
                    if isinstance(third, str):
                        # Has string activation as last element
                        # Legacy: (domain_idx, output_indices, activation)
                        self._validate_indices(feature_name, first)
                        self._validate_indices(feature_name, second)
                        self._validate_activation(feature_name, third)
                    else:
                        # Multi-dimensional indices: (dim1, dim2, dim3)
                        self._validate_indices(feature_name, config)
                else:
                    # Length > 3: could be (multi_dim_indices..., activation) or just multi_dim_indices
                    if isinstance(config[-1], str):
                        # Last element is activation: (indices..., activation)
                        indices_part = config[:-1]
                        activation = config[-1]
                        self._validate_indices(feature_name, indices_part)
                        self._validate_activation(feature_name, activation)
                    else:
                        # Arbitrary length tuple - treat as multi-dimensional indices
                        self._validate_indices(feature_name, config)
            else:
                raise ValueError(
                    f"Feature '{feature_name}' config must be indices, (indices,), "
                    f"(indices, activation), or tuple of indices, got {type(config)}"
                )

    def _validate_indices(self, feature_name: str, indices) -> None:
        """Validate individual index components."""
        if isinstance(indices, (int, slice)):
            return
        elif isinstance(indices, (tuple, list)):
            for idx in indices:
                if not isinstance(idx, (int, slice, type(None), type(...))):
                    raise ValueError(
                        f"Index component for '{feature_name}' must be int, slice, None, or ..., "
                        f"got {type(idx)}"
                    )
        else:
            raise ValueError(
                f"Indices for '{feature_name}' must be int, slice, tuple, or list, "
                f"got {type(indices)}"
            )

    def _validate_activation(self, feature_name: str, activation: str) -> None:
        """Validate activation function."""
        valid_activations = {"softmax", "sigmoid", "none", "relu", "tanh"}
        if activation not in valid_activations:
            raise ValueError(
                f"Activation for '{feature_name}' must be one of {valid_activations}, "
                f"got {activation}"
            )

    def _extract_features(self, logits: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Extract feature tensors from model output using flexible feature indices."""
        features = {}

        for feature_name, config in self.feature_indices.items():
            # Parse configuration to extract indices and activation
            indices, activation = self._parse_feature_config(config)

            # Extract feature tensor using arbitrary indexing
            feature_logits = self._extract_tensor_with_indices(
                logits, indices, feature_name
            )

            # Apply specified activation function
            probabilities = self._apply_activation(
                feature_logits, activation, feature_name
            )

            # Clamp for numerical stability and convert to Truth objects
            probabilities = _clamp01(probabilities, eps=self.eps)
            features[feature_name] = Truth(probabilities, self.semantics)

        return features

    def _parse_feature_config(self, config):
        """Parse feature configuration to extract indices and activation."""
        if isinstance(config, (int, slice)):
            # Direct indexing: indices
            return config, self.default_activation
        elif isinstance(config, (tuple, list)):
            if len(config) == 1:
                # Format: (indices,)
                return config[0], self.default_activation
            elif len(config) == 2:
                indices, second_element = config
                if isinstance(second_element, str):
                    # Format: (indices, activation)
                    return indices, second_element
                else:
                    # Legacy format: (domain_idx, output_indices)
                    return config, self.default_activation
            elif len(config) == 3:
                first, second, third = config
                if isinstance(third, str):
                    # Legacy: (domain_idx, output_indices, activation)
                    return (first, second), third
                else:
                    # Multi-dimensional indices: (dim1, dim2, dim3)
                    return config, self.default_activation
            else:
                # Length > 3: could be (multi_dim_indices..., activation) or just multi_dim_indices
                if isinstance(config[-1], str):
                    # Last element is activation: (indices..., activation)
                    indices_part = config[:-1]
                    activation = config[-1]
                    return indices_part, activation
                else:
                    # Arbitrary length tuple - treat as multi-dimensional indices
                    return config, self.default_activation
        else:
            return config, self.default_activation

    def _extract_tensor_with_indices(
        self, tensor: torch.Tensor, indices, feature_name: str
    ):
        """Extract tensor slice using arbitrary indexing scheme."""
        try:
            if isinstance(indices, int):
                # Single integer index - assume it's for the last dimension after batch
                if tensor.dim() == 3:  # (B, D, F) - legacy 3D format
                    return tensor[:, :, indices : indices + 1]
                elif tensor.dim() == 2:  # (B, F) - 2D format
                    return tensor[:, indices : indices + 1]
                else:
                    # For other dimensions, use advanced indexing
                    idx_list = [slice(None)] + [indices]  # Keep batch dim, index others
                    return tensor[tuple(idx_list)]

            elif isinstance(indices, slice):
                # Single slice - assume it's for the last dimension after batch
                if tensor.dim() == 3:  # (B, D, F)
                    return tensor[:, :, indices]
                elif tensor.dim() == 2:  # (B, F)
                    return tensor[:, indices]
                else:
                    idx_list = [slice(None)] + [indices]
                    return tensor[tuple(idx_list)]

            elif isinstance(indices, (tuple, list)):
                if len(indices) == 2 and all(isinstance(x, int) for x in indices[:1]):
                    # Legacy format: (domain_idx, output_indices)
                    domain_idx, output_indices = indices
                    if tensor.dim() != 3:
                        raise ValueError(
                            f"Legacy indexing requires 3D tensor, got {tensor.dim()}D"
                        )

                    # Extract from specific domain
                    domain_logits = tensor[:, domain_idx, :]  # (B, outputs_per_domain)

                    # Extract specific outputs within domain
                    if isinstance(output_indices, slice):
                        return domain_logits[:, output_indices]
                    elif isinstance(output_indices, (list, tuple)):
                        return domain_logits[:, output_indices]
                    elif isinstance(output_indices, int):
                        return domain_logits[:, output_indices : output_indices + 1]
                    else:
                        raise ValueError(
                            f"Unsupported output_indices type: {type(output_indices)}"
                        )
                else:
                    # General multi-dimensional indexing
                    # Always preserve batch dimension (first dimension)
                    if len(indices) >= tensor.dim():
                        raise ValueError(
                            f"Too many indices {len(indices)} for tensor with {tensor.dim()} dimensions"
                        )

                    # Construct full indexing tuple: [batch_slice, ...user_indices]
                    full_indices = [slice(None)] + list(indices)
                    return tensor[tuple(full_indices)]

            else:
                raise ValueError(f"Unsupported indices type: {type(indices)}")

        except Exception as e:
            raise ValueError(
                f"Failed to extract feature '{feature_name}' with indices {indices} "
                f"from tensor shape {tensor.shape}: {str(e)}"
            )

    def _apply_activation(
        self, feature_logits: torch.Tensor, activation: str, feature_name: str
    ):
        """Apply activation function to feature logits."""
        if activation == "softmax":
            return F.softmax(feature_logits, dim=-1)
        elif activation == "sigmoid":
            return torch.sigmoid(feature_logits)
        elif activation == "relu":
            return F.relu(feature_logits)
        elif activation == "tanh":
            return torch.tanh(feature_logits)
        elif activation == "none":
            return feature_logits
        else:
            raise ValueError(
                f"Unsupported activation '{activation}' for feature '{feature_name}'"
            )

    def update_rules(self, new_rules: str) -> None:
        """Update the rule script without recreating the entire loss function."""
        self.rules = new_rules

    def get_rules(self) -> str:
        """Get the current rule script."""
        return self.rules

    def add_custom_function(self, name: str, func: Callable) -> None:
        """Add a custom function to the rule interpreter."""
        self.interpreter.add_builtin_function(name, func)

    def forward(self, logits: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """
        Compute mammography constraints loss using rule-based constraints.

        Args:
            logits (torch.Tensor): Model outputs of shape (B, D, total_features)

        Returns:
            torch.Tensor: Computed constraint violation loss
        """
        # Extract features from model output
        features = self._extract_features(logits)

        # Execute rules to generate constraints
        constraint_set = self.interpreter.execute(self.rules, features)

        if self.normalize_weights > 0:
            constraint_set.normalize_weights(self.normalize_weights)

        # Compute aggregated loss
        loss = constraint_set.loss(mode=self.aggregation_mode, beta=self.cvar_beta)

        # Apply reduction
        if self.reduction == "mean":
            return loss.mean() if loss.dim() > 0 else loss
        elif self.reduction == "sum":
            return loss.sum() if loss.dim() > 0 else loss
        else:  # reduction == "none"
            return loss


def load_rules_from_file(file_path: str) -> str:
    """
    Load rule script from a .logic file.

    Args:
        file_path (str): Path to the .logic file containing rules

    Returns:
        str: Rule script content

    Example:
        >>> rules = load_rules_from_file('constraints.logic')
        >>> loss_fn = RuleBasedMammoConstraintsLoss(feature_indices, rules)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def create_flexible_loss(
    feature_indices: dict, logic_file: str, **kwargs
) -> RuleMammoLoss:
    """
    Create a RuleBasedMammoConstraintsLoss from feature indices and a .logic file.

    Args:
        feature_indices (dict): Feature mapping configuration
        logic_file (str): Path to .logic file containing constraints
        **kwargs: Additional arguments for RuleBasedMammoConstraintsLoss

    Returns:
        RuleBasedMammoConstraintsLoss: Configured loss function

    Example:
        >>> feature_indices = {
        ...     'category_A': (0, slice(0, 5), 'softmax'),
        ...     'binary_B': (1, 0, 'sigmoid'),
        ... }
        >>> loss_fn = create_flexible_loss(feature_indices, 'my_constraints.logic')
    """
    return RuleMammoLoss(feature_indices, logic_file, **kwargs)


def create_default_mammo_rules() -> str:
    """
    Create a default rule script that mimics the original MammoConstraintsLoss behavior.

    Returns:
        str: Default mammography rule script
    """
    return """
# Default Mammography Constraint Rules
# ====================================

# Feature definitions - combine findings per breast
define findings_L = mass_L | mc_L
define findings_R = mass_R | mc_R

# BI-RADS probability groups
define high_birads_L = sum(birads_L, [4, 5, 6])
define high_birads_R = sum(birads_R, [4, 5, 6])
define very_high_birads_L = sum(birads_L, [5, 6])
define very_high_birads_R = sum(birads_R, [5, 6])
define low_birads_L = sum(birads_L, [1, 2])
define low_birads_R = sum(birads_R, [1, 2])

# No findings (negation of findings)
define no_findings_L = ~findings_L
define no_findings_R = ~findings_R

# Categorical exclusivity constraints
constraint exactly_one(birads_L) weight=1.0 transform="logbarrier"
constraint exactly_one(birads_R) weight=1.0 transform="logbarrier"
constraint exactly_one(comp) weight=0.7 transform="logbarrier"

# Logical implication constraints
# Findings -> High BI-RADS (4-6)
constraint findings_L >> high_birads_L weight=0.7 transform="logbarrier"
constraint findings_R >> high_birads_R weight=0.7 transform="logbarrier"

# Very High BI-RADS (5-6) -> Findings
constraint very_high_birads_L >> findings_L weight=0.7 transform="logbarrier"
constraint very_high_birads_R >> findings_R weight=0.7 transform="logbarrier"

# Low BI-RADS (1-2) -> No findings (gentle constraint)
constraint low_birads_L >> no_findings_L weight=0.3 transform="logbarrier"
constraint low_birads_R >> no_findings_R weight=0.3 transform="logbarrier"
"""


def create_simplified_mammo_rules() -> str:
    """
    Create a simplified rule script with fewer constraints for testing.

    Returns:
        str: Simplified mammography rule script
    """
    return """
# Simplified Mammography Rules
# =============================

# Basic feature definitions
define findings_L = mass_L | mc_L
define findings_R = mass_R | mc_R
define high_birads_L = sum(birads_L, [4, 5, 6])
define high_birads_R = sum(birads_R, [4, 5, 6])

# Essential constraints only
constraint exactly_one(birads_L) weight=1.0 transform="logbarrier"
constraint exactly_one(birads_R) weight=1.0 transform="logbarrier"
constraint exactly_one(comp) weight=1.0 transform="logbarrier"
constraint findings_L >> high_birads_L weight=1.0 transform="logbarrier"
constraint findings_R >> high_birads_R weight=1.0 transform="logbarrier"
"""


RuleBasedConstraintsLoss = RuleMammoLoss
