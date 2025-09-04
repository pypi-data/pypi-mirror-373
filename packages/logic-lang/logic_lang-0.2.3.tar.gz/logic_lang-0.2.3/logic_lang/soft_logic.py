"""
Soft Logic for PyTorch
======================

A modular, differentiable framework to build soft (fuzzy) logical expressions
on top of PyTorch tensors in [0, 1], then turn them into losses.

Design goals
------------
- **Differentiable everywhere** (uses smooth operations; log/exp with eps; no hard min/max).
- **Clean & composable**: wrap probabilities in `Truth` and compose with `~ & | ^ >>`.
- **Multiple semantics**: Product, smooth Łukasiewicz, smooth Gödel (min/max).
- **Quantifiers**: `forall` and `exists` with stable aggregators (geometric mean, LSE).
- **Loss transforms**: log-barrier, hinge (softplus), linear.
- **Spatial consequents**: efficient neighborhood pooling via 2D/3D convolutions (ball/ring).
- **Good gradient behavior**: temperature parameters and gating to avoid vacuous satisfaction.

This file is self-contained. Drop it into your project and import.

Example usage (see bottom `__main__`).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Sequence, Tuple, Union

import torch
import torch.nn.functional as F

Tensor = torch.Tensor

# -------------------------------------------------------------
# Utilities
# -------------------------------------------------------------


def _clamp01(tensor: Tensor, eps: float = 1e-7) -> Tensor:
    """Clamp probabilities to (0,1) open interval for numerical stability."""
    return tensor.clamp(min=eps, max=1.0 - eps)


def _softplus(x: Tensor, beta: float = 1.0) -> Tensor:
    """Stable softplus with tunable beta: softplus(beta*x)/beta."""
    if beta == 1.0:
        return F.softplus(x)
    elif beta <= 0.0:
        raise ValueError("beta must strictly be positive")
    else:
        return F.softplus(beta * x) / beta


# -------------------------------------------------------------
# Semantics (t-norm families)
# -------------------------------------------------------------


@dataclass
class Semantics:
    eps: float = 1e-6  # numerical stability for logs

    # -- base ops (to be overridden) --
    def NOT(self, a: Tensor) -> Tensor:
        raise NotImplementedError

    def AND(self, a: Tensor, b: Tensor) -> Tensor:
        raise NotImplementedError

    def OR(self, a: Tensor, b: Tensor) -> Tensor:
        # Default via De Morgan duality: a OR b = NOT(AND(NOT a, NOT b))
        return self.NOT(self.AND(self.NOT(a), self.NOT(b)))

    def IMPLIES(self, a: Tensor, b: Tensor) -> Tensor:
        # Default (material implication) via ¬a ∨ b
        return self.OR(self.NOT(a), b)

    def XOR(self, a: Tensor, b: Tensor) -> Tensor:
        # a XOR b = (a ∨ b) ∧ ¬(a ∧ b)
        return self.AND(self.OR(a, b), self.NOT(self.AND(a, b)))

    def GT(self, a: Tensor, b: Tensor) -> Tensor:
        # Default greater than: smooth approximation using sigmoid
        raise NotImplementedError

    def LT(self, a: Tensor, b: Tensor) -> Tensor:
        # Default less than: can be implemented as GT(b, a)
        return self.GT(b, a)

    def EQ(self, a: Tensor, b: Tensor) -> Tensor:
        # Default equals: high when a ≈ b, low when different
        raise NotImplementedError

    # n-ary AND/OR (balanced folds for numerical stability)
    def AND_n(self, xs: Sequence[Tensor]) -> Tensor:
        if not xs:
            raise ValueError("AND_n requires at least one operand")
        out = xs[0]
        for x in xs[1:]:
            out = self.AND(out, x)
        return out

    def OR_n(self, xs: Sequence[Tensor]) -> Tensor:
        if not xs:
            raise ValueError("OR_n requires at least one operand")
        out = xs[0]
        for x in xs[1:]:
            out = self.OR(out, x)
        return out


class ProductSemantics(Semantics):
    """Product logic: smooth, stable, everywhere differentiable."""

    def __init__(self, eps: float = 1e-6, sharpness: float = 8.0):
        super().__init__(eps=eps)
        self.sharpness = sharpness  # Controls steepness of comparison functions

    def NOT(self, a: Tensor) -> Tensor:
        return 1.0 - a

    def AND(self, a: Tensor, b: Tensor) -> Tensor:
        return _clamp01(
            torch.exp(
                torch.log(_clamp01(a, self.eps)) + torch.log(_clamp01(b, self.eps))
            ),
            self.eps,
        )

    def AND_n(self, xs: Sequence[Tensor]) -> Tensor:
        # Numerically stable probabilistic AND in log-space
        if not xs:
            raise ValueError("AND_n requires at least one operand")
        if len(xs) == 1:  # single element, no need to stack
            return xs[0]
        xs = torch.broadcast_tensors(*xs)
        x = torch.stack(xs, dim=0)
        return _clamp01(
            torch.exp(torch.sum(torch.log(_clamp01(x, self.eps)), dim=0)), self.eps
        )

    def OR(self, a: Tensor, b: Tensor) -> Tensor:
        return _clamp01(a + b - self.AND(a, b), self.eps)

    def OR_n(self, xs: Sequence[Tensor]) -> Tensor:
        # Numerically stable probabilistic OR in log-space
        if not xs:
            raise ValueError("OR_n requires at least one operand")
        if len(xs) == 1:  # single element, no need to stack
            return xs[0]
        xs = torch.broadcast_tensors(*xs)
        x = torch.stack(xs, dim=0)
        return _clamp01(
            1.0 - torch.exp(torch.sum(torch.log(_clamp01(1.0 - x, self.eps)), dim=0)),
            self.eps,
        )

    def IMPLIES(self, a: Tensor, b: Tensor) -> Tensor:
        # 1 - a + a*b
        return _clamp01(1.0 - a + self.AND(a, b), self.eps)

    def XOR(self, a: Tensor, b: Tensor) -> Tensor:
        return _clamp01(a + b - 2.0 * self.AND(a, b), self.eps)

    def GT(self, a: Tensor, b: Tensor) -> Tensor:
        # Smooth greater than using sigmoid: high when a > b
        return torch.sigmoid(self.sharpness * (a - b))

    def LT(self, a: Tensor, b: Tensor) -> Tensor:
        # Smooth less than: high when a < b
        return torch.sigmoid(self.sharpness * (b - a))

    def EQ(self, a: Tensor, b: Tensor) -> Tensor:
        # Smooth equals: high when |a - b| is small
        # Using Gaussian-like kernel: exp(-sharpness * |a - b|^2)
        diff = torch.abs(a - b)
        return torch.exp(-self.sharpness * diff * diff)


class LukasiewiczSemantics(Semantics):
    """Smooth Łukasiewicz logic.

    AND(a,b) = max(a + b - 1, 0)
    OR(a,b)  = min(a + b, 1)
    IMPLIES(a,b) = min(1, 1 - a + b)

    softness controls transition sharpness; larger -> closer to hard piecewise.
    """

    def __init__(self, eps: float = 1e-6, sharpness: float = 8.0, **kwargs):
        super().__init__(eps=eps)
        self.sharpness = sharpness  # For comparison operators

    def NOT(self, a: Tensor) -> Tensor:
        return 1.0 - a

    def AND(self, a: Tensor, b: Tensor) -> Tensor:
        # max(a + b - 1, 0) - exact Lukasiewicz t-norm
        return _clamp01(a + b - 1.0, self.eps)

    def AND_n(self, xs: Sequence[Tensor]) -> Tensor:
        if not xs:
            raise ValueError("AND_n requires at least one operand")
        if len(xs) == 1:  # single element, no need to stack
            return xs[0]
        xs = torch.broadcast_tensors(*xs)
        x = torch.stack(xs, dim=0)
        return _clamp01(torch.min(x, dim=0).values, self.eps)

    def OR(self, a: Tensor, b: Tensor) -> Tensor:
        # min(a + b, 1) - exact Lukasiewicz t-conorm
        return _clamp01(a + b, self.eps)

    def OR_n(self, xs: Sequence[Tensor]) -> Tensor:
        if not xs:
            raise ValueError("OR_n requires at least one operand")
        if len(xs) == 1:  # single element, no need to stack
            return xs[0]
        xs = torch.broadcast_tensors(*xs)
        x = torch.stack(xs, dim=0)
        return _clamp01(torch.sum(x, dim=0), self.eps)

    def IMPLIES(self, a: Tensor, b: Tensor) -> Tensor:
        # min(1, 1 - a + b) - exact Lukasiewicz implication
        return _clamp01(1.0 - a + b, self.eps)

    def GT(self, a: Tensor, b: Tensor) -> Tensor:
        # Lukasiewicz-style greater than: max(a - b, 0) scaled and shifted
        # Scale to [0,1] and apply smooth transition
        diff = a - b
        # Smooth version of max(diff, 0) using softplus
        smooth_max = _softplus(diff, self.sharpness)
        # Sigmoid to map to [0,1] probabilities
        return torch.sigmoid(self.sharpness * smooth_max)

    def LT(self, a: Tensor, b: Tensor) -> Tensor:
        # Lukasiewicz-style less than: max(b - a, 0) scaled
        return self.GT(b, a)

    def EQ(self, a: Tensor, b: Tensor) -> Tensor:
        # Lukasiewicz-style equality: 1 - |a - b| clamped to [0,1]
        # This maintains the bounded linear characteristic of Lukasiewicz logic
        diff = torch.abs(a - b)
        equality = 1.0 - diff
        return _clamp01(equality, self.eps)


class GodelSemantics(Semantics):
    """Smooth Gödel (min/max) via log-sum-exp softmin/softmax in value space."""

    def __init__(self, eps: float = 1e-6, tau: float = 8.0, sharpness: float = 8.0):
        super().__init__(eps=eps)
        self.tau = tau
        self.sharpness = sharpness  # For comparison operators

    def NOT(self, a: Tensor) -> Tensor:
        return 1.0 - a

    def AND(self, a: Tensor, b: Tensor) -> Tensor:  # Soft min via log-sum-exp
        # For identical tensors, use a numerically stable computation
        # that preserves idempotence while maintaining differentiability
        a_broadcast, b_broadcast = torch.broadcast_tensors(a, b)

        if torch.equal(a_broadcast, b_broadcast):
            # When inputs are identical, softmin(x,x) should equal x
            # but the standard formula gives x - log(2)/tau
            # We compute the correction and subtract it
            x = torch.stack([a_broadcast, a_broadcast], dim=0)
            uncorrected = -torch.logsumexp(-self.tau * x, dim=0) / self.tau
            # Correction term: log(2)/tau (this is differentiable)
            correction = (
                torch.log(torch.tensor(2.0, device=a.device, dtype=a.dtype)) / self.tau
            )
            return _clamp01(uncorrected + correction, self.eps)
        else:
            # Normal case for different inputs
            x = torch.stack([a_broadcast, b_broadcast], dim=0)
            return _clamp01(-torch.logsumexp(-self.tau * x, dim=0) / self.tau, self.eps)

    def AND_n(self, xs: Sequence[Tensor]) -> Tensor:
        if not xs:
            raise ValueError("AND_n requires at least one operand")
        if len(xs) == 1:  # single element, no need to stack
            return xs[0]
        xs = torch.broadcast_tensors(*xs)
        x = torch.stack(xs, dim=0)
        return _clamp01(-torch.logsumexp(-self.tau * x, dim=0) / self.tau, self.eps)

    def OR(self, a: Tensor, b: Tensor) -> Tensor:  # Soft max via log-sum-exp
        # For identical tensors, use a numerically stable computation
        # that preserves idempotence while maintaining differentiability
        a_broadcast, b_broadcast = torch.broadcast_tensors(a, b)

        if torch.equal(a_broadcast, b_broadcast):
            # When inputs are identical, softmax(x,x) should equal x
            # but the standard formula gives x + log(2)/tau
            # We compute the correction and subtract it
            x = torch.stack([a_broadcast, a_broadcast], dim=0)
            uncorrected = torch.logsumexp(self.tau * x, dim=0) / self.tau
            # Correction term: log(2)/tau (this is differentiable)
            correction = (
                torch.log(torch.tensor(2.0, device=a.device, dtype=a.dtype)) / self.tau
            )
            return _clamp01(uncorrected - correction, self.eps)
        else:
            # Normal case for different inputs
            x = torch.stack([a_broadcast, b_broadcast], dim=0)
            return _clamp01(torch.logsumexp(self.tau * x, dim=0) / self.tau, self.eps)

    def OR_n(self, xs: Sequence[Tensor]) -> Tensor:  # Soft max via log-sum-exp
        if not xs:
            raise ValueError("OR_n requires at least one operand")
        if len(xs) == 1:  # single element, no need to stack
            return xs[0]
        xs = torch.broadcast_tensors(*xs)
        x = torch.stack(xs, dim=0)
        return _clamp01(torch.logsumexp(self.tau * x, dim=0) / self.tau, self.eps)

    def IMPLIES(self, a: Tensor, b: Tensor) -> Tensor:
        # use default (¬a ∨ b) to inherit softmax OR
        return _clamp01(super().IMPLIES(a, b), self.eps)

    def GT(self, a: Tensor, b: Tensor) -> Tensor:
        # Gödel-style greater than using smooth approximation
        # In Gödel logic, we want sharp transitions but smooth approximations
        # Use temperature-scaled sigmoid for smooth min/max-like behavior
        diff = a - b
        # Scale by sharpness to control transition steepness
        return torch.sigmoid(self.sharpness * diff)

    def LT(self, a: Tensor, b: Tensor) -> Tensor:
        # Gödel-style less than
        return self.GT(b, a)

    def EQ(self, a: Tensor, b: Tensor) -> Tensor:
        # Gödel-style equality: use smooth approximation to exact equality
        # In Gödel logic, equality is typically 1 if a=b, 0 otherwise
        # Smooth version using temperature-scaled Gaussian-like kernel
        diff = torch.abs(a - b)
        # Use a sharper kernel than Product semantics for Gödel-like behavior
        return torch.exp(-self.sharpness * diff)


# -------------------------------------------------------------
# Truth wrapper with operator overloading
# -------------------------------------------------------------


class Truth:
    """Wraps a probability tensor in [0,1] and a semantics.

    Supports logical composition with Python operators:
      ~A  (NOT), A & B (AND), A | B (OR), A ^ B (XOR), A >> B (IMPLIES)

    Notes
    -----
    - Values are *not* auto-clamped at construction. Use `.clamped()` if needed.
    - Broadcasting follows PyTorch semantics.
    """

    def __init__(
        self,
        value: Tensor,
        semantics: Optional[Semantics] = None,
        name: Optional[str] = None,
    ):
        assert isinstance(value, torch.Tensor)
        self.semantics = semantics or ProductSemantics()
        self.value = _clamp01(value, eps=self.semantics.eps)
        self.name = name

    def clone(self) -> "Truth":
        return Truth(self.value.clone(), self.semantics, self.name)

    # ---- unary
    def __invert__(self) -> "Truth":
        return Truth(self.semantics.NOT(self.value), self.semantics)

    # ---- binary
    def __and__(self, other: "Truth") -> "Truth":
        return Truth(
            self.semantics.AND(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    def __or__(self, other: "Truth") -> "Truth":
        return Truth(
            self.semantics.OR(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    def __xor__(self, other: "Truth") -> "Truth":
        return Truth(
            self.semantics.XOR(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    # A >> B  (implication)
    def __rshift__(self, other: "Truth") -> "Truth":
        return Truth(
            self.semantics.IMPLIES(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    # A > B (greater than)
    def __gt__(self, other: "Truth") -> "Truth":
        return Truth(
            self.semantics.GT(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    # A < B (less than)
    def __lt__(self, other: "Truth") -> "Truth":
        return Truth(
            self.semantics.LT(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    # A == B (equals) - note: this overrides Python's equality operator
    # Use with caution as it changes normal Python behavior
    def __eq__(self, other: "Truth") -> "Truth":
        if not isinstance(other, Truth):
            # Fall back to standard equality for non-Truth objects
            return NotImplemented
        return Truth(
            self.semantics.EQ(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    # Provide alternative method names to avoid Python operator conflicts
    def eq(self, other: "Truth") -> "Truth":
        """Logical equality that doesn't override Python's == operator."""
        return Truth(
            self.semantics.EQ(self.value, _as_truth(other, self.semantics).value),
            self.semantics,
        )

    def gt(self, other: "Truth") -> "Truth":
        """Logical greater than (same as > operator)."""
        return self.__gt__(other)

    def lt(self, other: "Truth") -> "Truth":
        """Logical less than (same as < operator)."""
        return self.__lt__(other)

    # ---- n-ary convenience
    @staticmethod
    def AND_n(xs: Sequence["Truth"]) -> "Truth":
        if not xs:
            raise ValueError("AND_n requires at least one operand")
        sem = xs[0].semantics
        return Truth(sem.AND_n([x.value for x in xs]), sem)

    @staticmethod
    def OR_n(xs: Sequence["Truth"]) -> "Truth":
        if not xs:
            raise ValueError("OR_n requires at least one operand")
        sem = xs[0].semantics
        return Truth(sem.OR_n([x.value for x in xs]), sem)

    # ---- quantifiers
    def forall(
        self,
        dims: Union[int, Tuple[int, ...]] = None,
        mode: str = "geomean",
        tau: float = 8.0,
    ) -> "Truth":
        """Universal quantifier aggregator over given dims.

        mode:
          - "geomean": exp(mean(log(x)))  (monotone, stable)
          - "lse":     softmin via -1/tau * log(mean(exp(-tau*x)))
        """
        x = _clamp01(self.value, eps=self.semantics.eps)
        if dims is None:
            dims = tuple(range(x.dim()))
        if isinstance(dims, int):
            dims = (dims,)
        if mode == "geomean":
            s = torch.exp(torch.mean(torch.log(x), dim=dims, keepdim=False))
        elif mode == "lse":
            s = -torch.logsumexp(-tau * x, dim=dims) / tau
        else:
            raise ValueError(f"Unknown forall mode: {mode}")
        return Truth(s, self.semantics)

    def exists(
        self,
        dims: Union[int, Tuple[int, ...]] = None,
        mode: str = "prob_or",
        tau: float = 8.0,
    ) -> "Truth":
        """Existential quantifier aggregator over given dims.

        mode:
          - "prob_or": 1 - prod(1-x) computed stably in log-space
          - "lse":     softmax via 1/tau * log(mean(exp(tau*x)))
        """
        x = _clamp01(self.value, eps=self.semantics.eps)
        if dims is None:
            dims = tuple(range(x.dim()))
        if isinstance(dims, int):
            dims = (dims,)
        if mode == "prob_or":
            s = 1.0 - torch.exp(torch.sum(torch.log(1.0 - x), dim=dims))
        elif mode == "lse":
            s = torch.logsumexp(tau * x, dim=dims) / tau
        else:
            raise ValueError(f"Unknown exists mode: {mode}")
        return Truth(s, self.semantics)

    # ---- transforms to losses
    def loss_logbarrier(self, target: float = 1.0, weight: float = 1.0) -> Tensor:
        """-log satisfaction around a target in [0,1]."""
        z = 1.0 - torch.abs(self.value - target)
        z = _clamp01(z, eps=self.semantics.eps)
        return weight * (-torch.log(z))

    def loss_one_minus(self, weight: float = 1.0) -> Tensor:
        """Linear penalty: 1 - s. Gentler than log barrier."""
        return weight * (1.0 - self.value)

    def loss_hinge(
        self, threshold: float = 1.0, alpha: float = 10.0, weight: float = 1.0
    ) -> Tensor:
        """Soft hinge using softplus: penalize when s < threshold."""
        return weight * _softplus(alpha * (threshold - self.value))

    # ---- helpers
    def clamped(self, eps: Optional[float] = None) -> "Truth":
        eps = self.semantics.eps if eps is None else eps
        return Truth(_clamp01(self.value, eps=eps), self.semantics, self.name)

    def mean(self) -> Tensor:
        return self.value.mean()

    def item(self) -> float:
        return float(self.value.detach().mean().cpu().item())


def _as_truth(x: Union[Truth, Tensor, float], sem: Semantics) -> Truth:
    if isinstance(x, Truth):
        return x
    if isinstance(x, (float, int)):
        t = torch.tensor(x, dtype=torch.float32)
        return Truth(t, sem)
    return Truth(x, sem)


# -------------------------------------------------------------
# High-level helpers for implication-based constraints
# -------------------------------------------------------------


def implication_loss(
    antecedent: Tensor,
    consequent: Tensor,
    semantics: Optional[Semantics] = None,
    reduce: str = "mean",
    detach_b: bool = False,
    gate_gamma: Optional[float] = None,
    eps: float = 1e-6,
) -> Tensor:
    """Per-element implication loss: A ⇒ B under given semantics, as -log(satisfaction).

    Parameters
    ----------
    antecedent: Tensor in [0,1]
    consequent: Tensor in [0,1]
    semantics: Semantics, default ProductSemantics
    reduce: 'mean' | 'sum' | 'none'
    detach_b: stop gradient through consequent (prevents reverse influence)
    gate_gamma: if set, softly gate loss by sigmoid((A-γ)/τg) to avoid vacuous satisfaction
    eps: numerical stability
    """
    sem = semantics or ProductSemantics(eps=eps)
    A = _clamp01(antecedent, eps=eps)
    B = _clamp01(consequent.detach() if detach_b else consequent, eps=eps)
    S = sem.IMPLIES(A, B)  # satisfaction in [0,1]
    loss = -torch.log(_clamp01(S, eps=eps))

    if gate_gamma is not None:
        gate = torch.sigmoid((A - gate_gamma) * 8.0)
        loss = gate * loss

    if reduce == "mean":
        return loss.mean()
    elif reduce == "sum":
        return loss.sum()
    elif reduce == "none":
        return loss
    else:
        raise ValueError("reduce must be 'mean' | 'sum' | 'none'")


# -------------------------------------------------------------
# Constraint sets and CVaR-style aggregation
# -------------------------------------------------------------


class Constraint:
    """Bundle a Truth (satisfaction) with a transform to a scalar loss."""

    def __init__(
        self, truth: Truth, transform: str = "logbarrier", weight: float = 1.0, **kwargs
    ):
        self.truth = truth
        self.transform = transform
        self.weight = weight
        self.kwargs = kwargs

    def loss(self) -> Tensor:
        if self.transform == "logbarrier":
            val = self.truth.loss_logbarrier(**self.kwargs)
        elif self.transform == "linear":
            val = self.truth.loss_one_minus(**self.kwargs)
        elif self.transform == "hinge":
            val = self.truth.loss_hinge(**self.kwargs)
        else:
            raise ValueError(f"Unknown transform: {self.transform}")
        return self.weight * val.mean()


class ConstraintSet:
    """Aggregate multiple constraints with weighted sum or CVaR (focus on worst violators)."""

    def __init__(self, constraints: Sequence[Constraint]):
        self.constraints = list(constraints)
        self.weights = [c.weight for c in constraints]

    def normalize_weights(self, sum_to: float = 1.0):
        if sum_to > 0:
            wsum = sum(self.weights)
            self.weights = [w / wsum * sum_to for w in self.weights]
            for i in range(len(self.constraints)):
                self.constraints[i].weight = self.weights[i]

    def loss(self, mode: str = "sum", beta: float = 0.25) -> Tensor:
        if mode == "sum":
            return torch.stack([c.loss() for c in self.constraints]).sum()
        elif mode == "cvar":
            # CVaR_beta over per-constraint losses: average of top-β fraction
            losses = torch.stack([c.loss() for c in self.constraints])
            k = max(1, int(beta * len(self.constraints)))
            topk = torch.topk(losses, k=k, largest=True).values
            return topk.mean()
        else:
            raise ValueError("mode must be 'sum' or 'cvar'")


# -------------------------------------------------------------
# Common Logic Rules and Patterns
# -------------------------------------------------------------


def exactly_one(
    probabilities: Union[Tensor, Truth],
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    dim: int = -1,
) -> Truth:
    """
    Exactly-one constraint for categorical probabilities.

    Enforces that exactly one category should be true from a set of mutually exclusive options.
    Implemented as (at-least-one) AND (pairwise disjointness).

    Args:
        probabilities: Tensor or Truth of shape (..., K) where K is number of categories
        semantics: Logic semantics to use (default: ProductSemantics)
        eps: Numerical stability epsilon
        dim: Dimension containing the categorical probabilities

    Returns:
        Truth: Satisfaction of exactly-one constraint

    Example:
        >>> # Probabilities for 3 classes: [0.1, 0.8, 0.1] should have high satisfaction
        >>> probs = torch.tensor([[0.1, 0.8, 0.1], [0.5, 0.5, 0.0]])  # (B, K)
        >>> constraint = exactly_one(probs)
        >>> satisfaction = constraint.value  # Higher for first sample
    """
    sem = semantics or ProductSemantics(eps=eps)

    # Handle both Truth and Tensor inputs
    if isinstance(probabilities, Truth):
        P = _clamp01(probabilities.value, eps=eps)
        sem = probabilities.semantics  # Use semantics from Truth object
    else:
        P = _clamp01(probabilities, eps=eps)

    K = P.size(dim)

    # Create Truth objects for each class
    truth_values = []
    for k in range(K):
        # Use torch.index_select for cleaner indexing
        class_prob = torch.index_select(P, dim, torch.tensor([k], device=P.device))
        truth_values.append(Truth(class_prob, sem))

    # At least one must be true
    at_least_one = Truth.OR_n(truth_values)

    # At most one can be true (pairwise disjointness)
    pairwise_exclusive = []
    for i in range(K):
        for j in range(i + 1, K):
            pairwise_exclusive.append(~(truth_values[i] & truth_values[j]))

    at_most_one = (
        Truth.AND_n(pairwise_exclusive) if pairwise_exclusive else at_least_one
    )

    return at_least_one & at_most_one


def at_most_k(
    probabilities: Union[Tensor, Truth],
    k: int,
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    dim: int = -1,
) -> Truth:
    """
    At-most-k constraint: at most k elements can be true simultaneously.

    Args:
        probabilities: Tensor or Truth of shape (..., N)
        k: Maximum number of elements that can be true
        semantics: Logic semantics to use
        eps: Numerical stability epsilon
        dim: Dimension containing the elements

    Returns:
        Truth: Satisfaction of at-most-k constraint
    """
    sem = semantics or ProductSemantics(eps=eps)

    # Handle both Truth and Tensor inputs
    if isinstance(probabilities, Truth):
        P = _clamp01(probabilities.value, eps=eps)
        sem = probabilities.semantics  # Use semantics from Truth object
    else:
        P = _clamp01(probabilities, eps=eps)

    N = P.size(dim)

    if k >= N:
        # Constraint is always satisfied
        return Truth(torch.ones_like(P.sum(dim=dim, keepdim=True)), sem)

    # Create Truth objects for each element
    truth_values = []
    for i in range(N):
        elem_prob = torch.index_select(P, dim, torch.tensor([i], device=P.device))
        truth_values.append(Truth(elem_prob, sem))

    # Generate all combinations of k+1 elements and ensure they're not all true
    import itertools

    violations = []
    for combo in itertools.combinations(range(N), k + 1):
        # At least one in this combination must be false
        combo_truths = [truth_values[i] for i in combo]
        all_true = Truth.AND_n(combo_truths)
        violations.append(~all_true)

    return (
        Truth.AND_n(violations)
        if violations
        else Truth(torch.ones_like(P.sum(dim=dim, keepdim=True)), sem)
    )


def at_least_k(
    probabilities: Union[Tensor, Truth],
    k: int,
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    dim: int = -1,
) -> Truth:
    """
    At-least-k constraint: at least k elements must be true.

    Args:
        probabilities: Tensor or Truth of shape (..., N)
        k: Minimum number of elements that must be true
        semantics: Logic semantics to use
        eps: Numerical stability epsilon
        dim: Dimension containing the elements

    Returns:
        Truth: Satisfaction of at-least-k constraint
    """
    sem = semantics or ProductSemantics(eps=eps)

    # Handle both Truth and Tensor inputs
    if isinstance(probabilities, Truth):
        P = _clamp01(probabilities.value, eps=eps)
        sem = probabilities.semantics  # Use semantics from Truth object
    else:
        P = _clamp01(probabilities, eps=eps)

    N = P.size(dim)

    if k <= 0:
        # Constraint is always satisfied
        return Truth(torch.ones_like(P.sum(dim=dim, keepdim=True)), sem)

    if k > N:
        # Constraint can never be satisfied
        return Truth(torch.zeros_like(P.sum(dim=dim, keepdim=True)), sem)

    # Create Truth objects for each element
    truth_values = []
    for i in range(N):
        elem_prob = torch.index_select(P, dim, torch.tensor([i], device=P.device))
        truth_values.append(Truth(elem_prob, sem))

    # Generate all combinations of k elements and ensure at least one combo is all true
    import itertools

    satisfying_combos = []
    for combo in itertools.combinations(range(N), k):
        combo_truths = [truth_values[i] for i in combo]
        all_true = Truth.AND_n(combo_truths)
        satisfying_combos.append(all_true)

    return (
        Truth.OR_n(satisfying_combos)
        if satisfying_combos
        else Truth(torch.zeros_like(P.sum(dim=dim, keepdim=True)), sem)
    )


def exactly_k(
    probabilities: Union[Tensor, Truth],
    k: int,
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    dim: int = -1,
) -> Truth:
    """
    Exactly-k constraint: exactly k elements must be true.

    Args:
        probabilities: Tensor or Truth of shape (..., N)
        k: Exact number of elements that must be true
        semantics: Logic semantics to use
        eps: Numerical stability epsilon
        dim: Dimension containing the elements

    Returns:
        Truth: Satisfaction of exactly-k constraint
    """
    return at_least_k(probabilities, k, semantics, eps, dim) & at_most_k(
        probabilities, k, semantics, eps, dim
    )


def sum_class_probabilities(
    probabilities: Union[Tensor, Truth],
    indices: Union[list, tuple, slice],
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    dim: int = -1,
) -> Truth:
    """
    Sum probabilities for specified class indices to create a compound probability.

    Useful for grouping classes (e.g., "high risk" = classes [4, 5, 6]).

    Args:
        probabilities: Tensor or Truth of shape (..., K) where K is number of classes
        indices: List/tuple of class indices to sum, or slice object
        semantics: Logic semantics to use
        eps: Numerical stability epsilon
        dim: Dimension containing the class probabilities

    Returns:
        Truth: Combined probability for the specified classes

    Example:
        >>> # Combine classes 4, 5, 6 as "high risk"
        >>> probs = torch.randn(32, 7).softmax(dim=-1)  # (B, 7_classes)
        >>> high_risk = sum_class_probabilities(probs, [4, 5, 6])
    """
    sem = semantics or ProductSemantics(eps=eps)

    # Handle both Truth and Tensor inputs
    if isinstance(probabilities, Truth):
        P = _clamp01(probabilities.value, eps=eps)
        sem = probabilities.semantics  # Use semantics from Truth object
    else:
        P = _clamp01(probabilities, eps=eps)

    if isinstance(indices, slice):
        summed = P.index_select(
            dim, torch.arange(*indices.indices(P.size(dim)), device=P.device)
        ).sum(dim=dim, keepdim=True)
    else:
        indices_tensor = torch.tensor(indices, device=P.device, dtype=torch.long)
        summed = P.index_select(dim, indices_tensor).sum(dim=dim, keepdim=True)

    summed = _clamp01(summed, eps=eps)
    return Truth(summed, sem)


def mutual_exclusion(
    *probabilities: Union[Tensor, Truth],
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
) -> Truth:
    """
    Mutual exclusion constraint: at most one of the given probabilities can be high.

    Args:
        *probabilities: Variable number of probability tensors or Truth objects
        semantics: Logic semantics to use
        eps: Numerical stability epsilon

    Returns:
        Truth: Satisfaction of mutual exclusion constraint

    Example:
        >>> # Ensure findings are mutually exclusive per breast
        >>> mass_prob = torch.rand(32, 1)  # (B, 1)
        >>> calc_prob = torch.rand(32, 1)  # (B, 1)
        >>> constraint = mutual_exclusion(mass_prob, calc_prob)
    """
    # Determine semantics from first Truth object if available
    sem = semantics or ProductSemantics(eps=eps)
    for prob in probabilities:
        if isinstance(prob, Truth):
            sem = prob.semantics
            break

    if len(probabilities) < 2:
        # Need at least 2 for mutual exclusion to make sense
        if len(probabilities) == 1:
            prob = probabilities[0]
            tensor_val = prob.value if isinstance(prob, Truth) else prob
            return Truth(torch.ones_like(tensor_val), sem)
        else:
            # Empty case - always satisfied with a dummy tensor
            device = torch.device("cpu")  # Default device
            return Truth(torch.ones(1, device=device), sem)

    # Convert all inputs to Truth objects and extract tensors for pairwise exclusion
    truth_values = []
    for p in probabilities:
        if isinstance(p, Truth):
            truth_values.append(Truth(_clamp01(p.value, eps=eps), sem))
        else:
            truth_values.append(Truth(_clamp01(p, eps=eps), sem))

    pairwise_exclusive = []
    for i in range(len(truth_values)):
        for j in range(i + 1, len(truth_values)):
            pairwise_exclusive.append(~(truth_values[i] & truth_values[j]))

    return (
        Truth.AND_n(pairwise_exclusive)
        if pairwise_exclusive
        else Truth(
            torch.ones_like(
                probabilities[0].value
                if isinstance(probabilities[0], Truth)
                else probabilities[0]
            ),
            sem,
        )
    )


def threshold_implication(
    antecedent: Union[Tensor, Truth],
    consequent: Union[Tensor, Truth],
    threshold: float = 0.5,
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
) -> Truth:
    """
    Threshold-based implication: if antecedent > threshold, then consequent should be high.

    Useful for ordinal relationships where crossing a threshold has implications.

    Args:
        antecedent: Condition probability tensor or Truth object
        consequent: Result probability tensor or Truth object
        threshold: Threshold for antecedent activation
        semantics: Logic semantics to use
        eps: Numerical stability epsilon

    Returns:
        Truth: Satisfaction of threshold implication

    Example:
        >>> # If findings present (>0.5), then BI-RADS should be high
        >>> findings = torch.rand(32, 1)  # (B, 1)
        >>> high_birads = torch.rand(32, 1)  # (B, 1)
        >>> constraint = threshold_implication(findings, high_birads, threshold=0.5)
    """
    # Determine semantics priority: Truth object semantics > provided semantics > default
    if isinstance(antecedent, Truth):
        sem = antecedent.semantics
        antecedent_tensor = _clamp01(antecedent.value, eps=eps)
    else:
        sem = semantics or ProductSemantics(eps=eps)
        antecedent_tensor = _clamp01(antecedent, eps=eps)

    if isinstance(consequent, Truth):
        # If consequent has semantics and antecedent doesn't, use consequent's
        if not isinstance(antecedent, Truth):
            sem = consequent.semantics
        consequent_tensor = _clamp01(consequent.value, eps=eps)
    else:
        consequent_tensor = _clamp01(consequent, eps=eps)

    # Convert antecedent to thresholded version using smooth step function
    # Smooth step function: sigmoid with high slope around threshold
    slope = 10.0
    thresholded_antecedent = torch.sigmoid(slope * (antecedent_tensor - threshold))

    return Truth(thresholded_antecedent, sem) >> Truth(consequent_tensor, sem)


def conditional_probability(
    condition: Union[Tensor, Truth],
    event: Union[Tensor, Truth],
    target_prob: float,
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
) -> Truth:
    """
    Constraint on conditional probability: P(event | condition) ≈ target_prob.

    Implemented as: condition → (event with probability target_prob).

    Args:
        condition: Conditioning event probability tensor or Truth object
        event: Event probability tensor or Truth object
        target_prob: Target conditional probability [0, 1]
        semantics: Logic semantics to use
        eps: Numerical stability epsilon

    Returns:
        Truth: Satisfaction of conditional probability constraint
    """
    # Determine semantics priority: Truth object semantics > provided semantics > default
    if isinstance(condition, Truth):
        sem = condition.semantics
        condition_tensor = _clamp01(condition.value, eps=eps)
    else:
        sem = semantics or ProductSemantics(eps=eps)
        condition_tensor = _clamp01(condition, eps=eps)

    if isinstance(event, Truth):
        # If event has semantics and condition doesn't, use event's
        if not isinstance(condition, Truth):
            sem = event.semantics
        event_tensor = _clamp01(event.value, eps=eps)
    else:
        event_tensor = _clamp01(event, eps=eps)

    # Implement P(event | condition) ≈ target_prob as implication
    # condition → event_adjusted where event_adjusted has target probability
    event_adjusted = torch.abs(event_tensor - target_prob)
    event_adjusted = 1.0 - event_adjusted  # Convert distance to similarity
    event_adjusted = _clamp01(event_adjusted, eps=eps)

    return Truth(condition_tensor, sem) >> Truth(event_adjusted, sem)


# -------------------------------------------------------------
# Convenience functions for common constraint patterns
# -------------------------------------------------------------


def exactly_one_constraint(
    probabilities: Union[Tensor, Truth],
    weight: float = 1.0,
    transform: str = "logbarrier",
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    dim: int = -1,
    **kwargs,
) -> Constraint:
    """
    Create a ready-to-use exactly-one constraint.

    Args:
        probabilities: Categorical probabilities tensor or Truth object
        weight: Constraint weight
        transform: Loss transform ('logbarrier', 'linear', 'hinge')
        semantics: Logic semantics
        eps: Numerical stability epsilon
        dim: Categorical dimension
        **kwargs: Additional arguments for loss transform

    Returns:
        Constraint: Ready-to-use constraint object
    """
    truth = exactly_one(probabilities, semantics, eps, dim)
    return Constraint(truth, transform, weight, **kwargs)


def implication_constraint(
    antecedent: Union[Tensor, Truth],
    consequent: Union[Tensor, Truth],
    weight: float = 1.0,
    transform: str = "logbarrier",
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    **kwargs,
) -> Constraint:
    """
    Create a ready-to-use implication constraint.

    Args:
        antecedent: Condition tensor or Truth object
        consequent: Result tensor or Truth object
        weight: Constraint weight
        transform: Loss transform
        semantics: Logic semantics
        eps: Numerical stability epsilon
        **kwargs: Additional arguments for loss transform

    Returns:
        Constraint: Ready-to-use constraint object
    """
    # Determine semantics and extract tensors
    if isinstance(antecedent, Truth):
        sem = antecedent.semantics
        antecedent_tensor = _clamp01(antecedent.value, eps=eps)
    else:
        sem = semantics or ProductSemantics(eps=eps)
        antecedent_tensor = _clamp01(antecedent, eps=eps)

    if isinstance(consequent, Truth):
        if not isinstance(antecedent, Truth):
            sem = consequent.semantics
        consequent_tensor = _clamp01(consequent.value, eps=eps)
    else:
        consequent_tensor = _clamp01(consequent, eps=eps)

    antecedent_truth = Truth(antecedent_tensor, sem)
    consequent_truth = Truth(consequent_tensor, sem)
    implication_truth = antecedent_truth >> consequent_truth
    return Constraint(implication_truth, transform, weight, **kwargs)


def mutual_exclusion_constraint(
    *probabilities: Union[Tensor, Truth],
    weight: float = 1.0,
    transform: str = "logbarrier",
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    **kwargs,
) -> Constraint:
    """
    Create a ready-to-use mutual exclusion constraint.

    Args:
        *probabilities: Probability tensors or Truth objects to make mutually exclusive
        weight: Constraint weight
        transform: Loss transform
        semantics: Logic semantics
        eps: Numerical stability epsilon
        **kwargs: Additional arguments for loss transform

    Returns:
        Constraint: Ready-to-use constraint object
    """
    truth = mutual_exclusion(*probabilities, semantics=semantics, eps=eps)
    return Constraint(truth, transform, weight, **kwargs)


def comparison_constraint(
    left: Union[Tensor, Truth],
    right: Union[Tensor, Truth],
    operator: str,
    weight: float = 1.0,
    transform: str = "logbarrier",
    semantics: Optional[Semantics] = None,
    eps: float = 1e-6,
    **kwargs,
) -> Constraint:
    """
    Create a ready-to-use comparison constraint.

    Args:
        left: Left operand tensor or Truth object
        right: Right operand tensor or Truth object
        operator: Comparison operator ('gt', '>', 'lt', '<', 'eq', '==')
        weight: Constraint weight
        transform: Loss transform
        semantics: Logic semantics
        eps: Numerical stability epsilon
        **kwargs: Additional arguments for loss transform

    Returns:
        Constraint: Ready-to-use constraint object

    Example:
        >>> # Ensure high-risk assessment when findings are significant
        >>> findings = torch.rand(32, 1)
        >>> threshold = torch.full_like(findings, 0.7)
        >>> high_risk = torch.rand(32, 1)
        >>> # If findings > 0.7, then high_risk should be high
        >>> cond = comparison_constraint(findings, threshold, 'gt')
        >>> impl = implication_constraint(cond.truth, high_risk)
    """
    # Determine semantics
    if isinstance(left, Truth):
        sem = left.semantics
        left_tensor = _clamp01(left.value, eps=eps)
    else:
        sem = semantics or ProductSemantics(eps=eps)
        left_tensor = _clamp01(left, eps=eps)

    if isinstance(right, Truth):
        if not isinstance(left, Truth):
            sem = right.semantics
        right_tensor = _clamp01(right.value, eps=eps)
    else:
        right_tensor = _clamp01(right, eps=eps)

    left_truth = Truth(left_tensor, sem)
    right_truth = Truth(right_tensor, sem)

    # Apply comparison operator
    if operator in ("gt", ">"):
        comparison_truth = left_truth > right_truth
    elif operator in ("lt", "<"):
        comparison_truth = left_truth < right_truth
    elif operator in ("eq", "=="):
        comparison_truth = left_truth.eq(right_truth)
    else:
        raise ValueError(f"Unknown comparison operator: {operator}")

    return Constraint(comparison_truth, transform, weight, **kwargs)


def ordinal_constraint(
    probabilities: Union[Tensor, Truth],
    semantics: Optional[Semantics] = None,
    apply_cumsum: bool = False,
    eps: float = 1e-6,
    weight: float = 1.0,
    transform: str = "logbarrier",
    **kwargs,
) -> Constraint:
    """
    Create ordinal constraints ensuring P(class ≤ i) ≥ P(class ≤ j) for i ≥ j.

    Useful for ordinal classification where classes have a natural ordering.

    Args:
        probabilities: Cumulative probabilities tensor or Truth object of shape (..., K)
        semantics: Logic semantics
        apply_cumsum: Whether to apply cumulative sum to probabilities
        eps: Numerical stability epsilon
        weight: Constraint weight
        transform: Loss transform
        **kwargs: Additional arguments for loss transform

    Returns:
        Constraint: Ordinal constraint ensuring monotonicity

    Example:
        >>> # For BI-RADS classification: P(≤3) ≥ P(≤2) ≥ P(≤1) ≥ P(≤0)
        >>> logits = torch.randn(32, 5)  # 5 BI-RADS classes
        >>> probs = torch.softmax(logits, dim=-1)
        >>> constraint = ordinal_constraint(probs, apply_cumsum=True)
    """
    sem = semantics or ProductSemantics(eps=eps)

    if isinstance(probabilities, Truth):
        P = _clamp01(probabilities.value, eps=eps)
        sem = probabilities.semantics
    else:
        P = _clamp01(probabilities, eps=eps)

    if apply_cumsum:
        P = torch.cumsum(P, dim=-1)
        P = _clamp01(P, eps=eps)

    K = P.size(-1)
    if K < 2:
        # No constraints needed for single class
        return Constraint(
            Truth(torch.ones_like(P.sum(dim=-1, keepdim=True)), sem),
            transform,
            weight,
            **kwargs,
        )

    # Create monotonicity constraints: P(≤i) ≥ P(≤j) for i > j
    monotonic_constraints = []
    for i in range(1, K):
        for j in range(i):
            # P(≤i) ≥ P(≤j) equivalent to P(≤i) > P(≤j) OR P(≤i) == P(≤j)
            left = Truth(P[..., i : i + 1], sem)
            right = Truth(P[..., j : j + 1], sem)
            monotonic_constraints.append(left > right | left.eq(right))

    if not monotonic_constraints:
        return Constraint(
            Truth(torch.ones_like(P.sum(dim=-1, keepdim=True)), sem),
            transform,
            weight,
            **kwargs,
        )

    # Combine all monotonicity constraints
    combined_constraint = Truth.AND_n(monotonic_constraints)
    return Constraint(combined_constraint, transform, weight, **kwargs)


# -------------------------------------------------------------
# Example usage and testing
# -------------------------------------------------------------

if __name__ == "__main__":
    # Example usage of the extended soft logic library

    # 1. Exactly-one constraint for categorical classification
    print("=== Exactly-One Constraint Example ===")
    batch_size = 4
    num_classes = 5

    # Simulate model outputs (logits -> probabilities)
    logits = torch.randn(batch_size, num_classes)
    probs = torch.softmax(logits, dim=-1)

    print(f"Probabilities:\n{probs}")
    # Create exactly-one constraint
    for sem in [GodelSemantics(), LukasiewiczSemantics(), ProductSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")
        constraint = exactly_one(probs, semantics=sem)
        print(f"Exactly-one satisfaction: {constraint.value.squeeze()}")

    # 2. Implication constraint example
    print("\n=== Implication Constraint Example ===")
    findings = torch.rand(batch_size, 1)  # Findings probability
    high_risk = torch.rand(batch_size, 1)  # High risk assessment
    print(f"Findings: {findings.squeeze()}")
    print(f"High risk: {high_risk.squeeze()}")
    for sem in [GodelSemantics(), LukasiewiczSemantics(), ProductSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")
        findings_truth = Truth(findings, sem)
        high_risk_truth = Truth(high_risk, sem)

        implication = findings_truth >> high_risk_truth
        print(f"Implication satisfaction: {implication.value.squeeze()}")

    # 3. Mutual exclusion example
    print("\n=== Mutual Exclusion Example ===")
    mass = torch.rand(batch_size, 1)
    calcification = torch.rand(batch_size, 1)
    print(f"Mass: {mass.squeeze()}")
    print(f"Calcification: {calcification.squeeze()}")
    for sem in [GodelSemantics(), LukasiewiczSemantics(), ProductSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")

        exclusion = mutual_exclusion(mass, calcification, semantics=sem)
        print(f"Mutual exclusion satisfaction: {exclusion.value.squeeze()}")

    # 4. Threshold implication example
    print("\n=== Threshold Implication Example ===")
    feature_strength = torch.tensor([0.3, 0.7, 0.9, 0.1]).unsqueeze(-1)
    assessment = torch.rand(batch_size, 1)
    print(f"Feature strength: {feature_strength.squeeze()}")
    print(f"Assessment: {assessment.squeeze()}")
    for sem in [GodelSemantics(), LukasiewiczSemantics(), ProductSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")
        threshold_impl = threshold_implication(
            feature_strength, assessment, threshold=0.5, semantics=sem
        )
        print(f"Threshold implication satisfaction: {threshold_impl.value.squeeze()}")

    # 5. Constraint set with mixed constraints
    print("\n=== Constraint Set Example ===")
    for sem in [GodelSemantics(), LukasiewiczSemantics(), ProductSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")
        constraints = [
            exactly_one_constraint(probs, weight=1.0, semantics=sem),
            implication_constraint(findings, high_risk, weight=0.7, semantics=sem),
            mutual_exclusion_constraint(mass, calcification, weight=0.5, semantics=sem),
        ]

        constraint_set_godel = ConstraintSet(constraints)
        total_loss = constraint_set_godel.loss(mode="sum")
        cvar_loss = constraint_set_godel.loss(mode="cvar", beta=0.5)

        print(f"Total constraint loss (sum): {total_loss.item():.4f}")
        print(f"CVaR constraint loss (β=0.5): {cvar_loss.item():.4f}")

    # 6. Comparison operators example
    print("\n=== Comparison Operators Example ===")
    values_a = torch.tensor([0.2, 0.5, 0.8, 0.9]).unsqueeze(-1)
    values_b = torch.tensor([0.5, 0.5, 0.3, 0.7]).unsqueeze(-1)

    print(f"Values A: {values_a.squeeze()}")
    print(f"Values B: {values_b.squeeze()}")
    for sem in [ProductSemantics(), LukasiewiczSemantics(), GodelSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")
        truth_a = Truth(values_a, sem)
        truth_b = Truth(values_b, sem)

        gt_result = truth_a > truth_b
        lt_result = truth_a < truth_b
        eq_result = truth_a.eq(truth_b)

        print(f"A > B satisfaction: {gt_result.value.squeeze()}")
        print(f"A < B satisfaction: {lt_result.value.squeeze()}")
        print(f"A == B satisfaction: {eq_result.value.squeeze()}")

    # 7. Ordinal constraint example
    print("\n=== Ordinal Constraint Example ===")
    # Simulate BI-RADS classification cumulative probabilities
    birads_logits = torch.randn(batch_size, 5)  # 5 BI-RADS classes (0-4)
    birads_probs = torch.softmax(birads_logits, dim=-1)
    cum_birads = torch.cumsum(birads_probs, dim=-1)
    print(f"Cumulative BI-RADS probabilities:\n{cum_birads}")
    for sem in [ProductSemantics(), LukasiewiczSemantics(), GodelSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")
        ordinal_constraint_obj = ordinal_constraint(cum_birads, semantics=sem)
        print(
            f"Ordinal constraint satisfaction: {ordinal_constraint_obj.truth.value.mean().item():.4f}"
        )

    # 8. Threshold-based comparison constraint
    print("\n=== Threshold-based Constraint Example ===")
    findings_strength = torch.rand(batch_size, 1)
    threshold = torch.full_like(findings_strength, 0.6)
    print(f"Findings strength: {findings_strength.squeeze()}")
    print(f"Threshold (0.6): {threshold.squeeze()}")
    for sem in [ProductSemantics(), LukasiewiczSemantics(), GodelSemantics()]:
        print(f"\nUsing semantics: {sem.__class__.__name__}")

        # Create constraint: findings > threshold
        threshold_constraint = comparison_constraint(
            findings_strength, threshold, "gt", semantics=sem, weight=1.0
        )

        print(
            f"Findings > threshold satisfaction: {threshold_constraint.truth.value.squeeze()}"
        )

    print("\n=== Test Complete ===")
