# Logic Language Documentation

![Logo](logo.png)

## Overview

The Logic Language is a domain-specific language (DSL) designed for defining soft/fuzzy logic constraints in mammography classification. It allows you to replace hard-coded constraint logic with flexible, interpretable logic scripts that can be modified without changing Python code.

## Installation

Install the package using pip:

```bash
pip install logic-lang
```

### Requirements

- Python 3.8 or higher
- PyTorch 1.9.0 or higher
- NumPy 1.20.0 or higher

### Quick Start

```python
from logic_lang import RuleInterpreter

interpreter = RuleInterpreter()
features = {"predictions": torch.tensor([[0.8, 0.1, 0.1]])} 
script = "constraint exactly_one(predictions);" # also can load from .logic files
constraint_set = interpreter.execute(script, features)
```

## Syntax Reference

### Comments

Comments start with `#` and continue to the end of the line:
```
# This is a comment
define findings_L = mass_L | mc_L  # Inline comment
```

### Variable Definitions

Define new variables using logical combinations of existing features:
```
define variable_name = expression
```

### Constant Definitions

Define constants for reusable literal values:
```
const constant_name = value
```

### Variable Expectations

Declare which variables (features) the script expects to be provided:
```
expect variable_name
expect variable1, variable2, variable3
```

Examples:
```
# Declare expected variables at the beginning of the script
expect left_birads, right_birads, mass_L, mc_L

# Or declare them individually
expect comp
expect risk_score

# Define constants for thresholds
const high_threshold = 0.8
const low_threshold = 0.2
const birads_cutoff = 4

# Basic logical operations with literals
define findings_L = mass_L | mc_L
define high_risk = risk_score > 0.7  # Using literal number
define moderate_risk = risk_score > low_threshold  # Using constant

# Function calls with mixed literals and variables
define high_birads = sum(birads_L, [4, 5, 6])
define threshold_check = risk_score >= high_threshold
```

### Constraints

Define constraints that will be enforced during training:
```
constraint expression [weight=value] [transform="type"] [param=value ...]
```

Examples:
```
# Basic constraint
constraint exactly_one(birads_L)

# Constraint with weight and transform
constraint findings_L >> high_birads weight=0.7 transform="logbarrier"

# Constraint with multiple parameters
constraint exactly_one(comp) weight=1.5 transform="hinge" alpha=2.0
```

## Operators

### Logical Operators (in order of precedence, lowest to highest)

1. **Implication (`>>`)**: A >> B (if A then B)
   ```
   constraint findings_L >> high_birads_L
   ```

2. **OR (`|`)**: A | B (A or B)
   ```
   define findings = mass_L | mc_L
   ```

3. **XOR (`^`)**: A ^ B (A exclusive or B)
   ```
   define exclusive = mass_L ^ mc_L
   ```

4. **Comparison Operators**: `>`, `<`, `==`, `>=`, `<=`
   ```
   define high_risk = risk_score > threshold_value
   define similar_scores = score_a == score_b
   define within_range = score >= min_val & score <= max_val
   ```

5. **AND (`&`)**: A & B (A and B)
   ```
   define strict_findings = mass_L & high_confidence
   ```

6. **AND_n (`& variable`)**: AND across all elements in a tensor
   ```
   # All radiologists must agree (consensus)
   define consensus = & radiologist_assessments
   
   # All imaging modalities must show findings
   define all_modalities_positive = & imaging_results
   ```

7. **OR_n (`| variable`)**: OR across all elements in a tensor  
   ```
   # Any radiologist found something
   define any_concern = | radiologist_assessments
   
   # Any imaging modality shows findings
   define any_positive = | imaging_results
   ```

8. **NOT (`~`)**: ~A (not A)
   ```
   define no_findings = ~findings_L
   ```

9. **Indexing (`variable[...]`)**: Access tensor elements using numpy/pytorch syntax
   ```
   # IMPORTANT: When indexing tensors from RuleMammoLoss, you MUST account for the batch dimension!
   # Tensors have shape (batch_size, ...), so the first index is always the batch dimension
   
   # Access specific features for all batch items (CORRECT)
   define birads_class_4 = features[:, 4]        # All batches, class 4
   define high_birads = features[:, 4:7]         # All batches, classes 4-6
   define view_data = assessments[:, 1, :]       # All batches, view 1, all features
   
   # Multi-dimensional indexing with batch preservation
   define patient_features = batch_data[:, 0, 2] # All batches, patient 0, feature 2
   define cc_view = assessments[:, :, 0]         # All batches, all views, radiologist 0
   
   # WRONG - These would try to access specific batch items instead of features:
   # define birads_class_4 = features[4]         # Would access batch item 4!
   # define high_birads = features[4:7]          # Would access batch items 4-6!
   ```

## ⚠️ Important Cautions

### Batch Dimension Handling

When using the `RuleMammoLoss` or `RuleBasedConstraintsLoss` with tensor indexing in your logic scripts, **you must explicitly account for the batch dimension**:

```python
# ✅ CORRECT: Always preserve batch dimension with ':' 
define birads_4 = features[:, 4]           # Access feature 4 for all batch items
define classes_4to6 = features[:, 4:7]     # Access features 4-6 for all batch items
define view_cc = assessments[:, 0, :]      # Access CC view for all batch items

# ❌ WRONG: These access batch items, not features!
define birads_4 = features[4]              # Accesses batch item 4, not feature 4!
define classes_4to6 = features[4:7]        # Accesses batch items 4-6!
```

**Why this matters:**
- `RuleMammoLoss`/`RuleBasedConstraintsLoss` pass tensors with shape `(batch_size, ...)` to the interpreter
- The first dimension is always the batch dimension
- Logic operations need to work across the entire batch
- Incorrect indexing will cause shape mismatches and unexpected behavior

### Tensor Shape Awareness

Always be aware of your tensor shapes when writing logic scripts:

```python
# If your features have shape (B, 7) for 7 BI-RADS classes:
define high_birads = features[:, 4:]       # ✅ Classes 4,5,6 for all batches

# If your assessments have shape (B, 2, 3) for 2 views, 3 radiologists:
define cc_radiologist_1 = assessments[:, 0, 1]  # ✅ CC view, radiologist 1, all batches
define mlo_consensus = assessments[:, 1, :]      # ✅ MLO view, all radiologists, all batches
```

### Parentheses

Use parentheses to override operator precedence:
```
define complex = (mass_L | mc_L) & ~(birads_L >> findings_L)
```

### Negative Numbers

Logic-lang supports negative numbers in all numeric contexts:

```
# Negative constants
const negative_threshold = -0.5
const offset = -10

# Negative literals in expressions
define below_zero = risk_score > -0.1
define centered = features[:, 0] >= -1.0

# Negative weights in constraints
constraint findings_L >> high_birads weight=-0.3

# Complex expressions with negative numbers
define adjusted_score = risk_score > (-threshold + 0.1)
define negative_range = score >= -5 & score <= -1
```

**Note:** Negative numbers work in:
- Constant definitions (`const neg = -5`)
- Literal values in expressions (`score > -0.5`)
- Constraint weights (`weight=-0.3`)
- Constraint parameters (`alpha=-2.0`)
- Complex arithmetic expressions (`value + (-10)`)

The unary minus operator has high precedence, so `-5 + 3` is parsed as `(-5) + 3 = -2`.

### Arithmetic Operations

Logic-lang supports basic arithmetic operations with proper precedence:

```
# Basic arithmetic in constants
const sum_result = 5 + 3        # Addition: 8
const diff_result = 10 - 3      # Subtraction: 7 
const prod_result = 4 * 2       # Multiplication: 8
const div_result = 8 / 2        # Division: 4

# Complex expressions with parentheses
const complex = (5 + 3) * 2 - 1 # Result: 15

# Arithmetic with variables (tensors)
define sum_scores = score_a + score_b
define scaled_score = risk_score * 2.0
define normalized = (score - min_val) / (max_val - min_val)

# Mixed arithmetic and logical operations
define high_combined = (score_a + score_b) > threshold
define weighted_decision = prediction * weight > 0.5
```

**Operator Precedence (highest to lowest):**
1. Parentheses `()`
2. Unary operators `-, +, ~`
3. Multiplication and Division `*, /`
4. Addition and Subtraction `+, -`
5. Comparisons `>, <, ==, >=, <=`
6. Logical AND `&`
7. Logical XOR `^`
8. Logical OR `|`
9. Implication `>>`

**Type Handling:**
- **Numbers + Numbers**: Returns number (`5 + 3 = 8`)
- **Tensors + Tensors**: Returns tensor (`tensor([[2]]) + tensor([[3]]) = tensor([[5]])`)
- **Numbers + Tensors**: Returns tensor (broadcasting applies)
- **Truth + Truth**: Returns Truth object with arithmetic on underlying values

## Statement Separation

### Semicolons

You can use semicolons (`;`) to separate multiple statements on a single line, similar to Python:

```
# Multiple statements on one line
expect a, b; define c = a | b; constraint c

# Mix of semicolons and newlines
const threshold = 0.5; expect risk_score
define high_risk = risk_score > threshold
constraint high_risk weight=0.8

# Multiple constants and definitions
const low = 0.2; const high = 0.8; define range_check = value >= low & value <= high
```

### Line-based Separation

Statements can also be separated by newlines (traditional approach):
```
expect findings_L, findings_R
define bilateral = findings_L & findings_R
constraint bilateral weight=0.6
```

### Trailing Semicolons

Trailing semicolons are optional and ignored:
```
expect variables;
define result = expression;
constraint result;
```

## Built-in Functions

### `sum(probabilities, indices)`

Sum probabilities for specified class indices along the last dimension:
```
define high_birads_L = sum(birads_L, [4, 5, 6])
define very_high_birads = sum(birads_L, [5, 6])
```

### `exactly_one(probabilities)`

Create exactly-one constraint for categorical probabilities along the last dimension:
```
constraint exactly_one(birads_L) weight=1.0
```

### `mutual_exclusion(...probabilities)`

Create mutual exclusion constraint between multiple probabilities:
```
constraint mutual_exclusion(mass_L, mc_L) weight=0.5
```

### `at_least_k(probabilities, k)`

Create constraint that at least k elements must be true along the last dimension:
```
define min_two_findings = at_least_k(findings_combined, 2)
constraint min_two_findings weight=0.6
```

**Caution:** `at_least_k` uses combinatorial logic and may be slow for large tensors or high k values.

### `at_most_k(probabilities, k)`

Create constraint that at most k elements can be true along the last dimension:
```
define max_one_high_birads = at_most_k(high_birads_indicators, 1)
constraint max_one_high_birads weight=0.7
```

**Caution:** `at_most_k` uses combinatorial logic and may be slow for large tensors or high k values.

### `exactly_k(probabilities, k)`

Create constraint that exactly k elements must be true along the last dimension:
```
define exactly_two_radiologists = exactly_k(radiologist_agreement, 2)
constraint exactly_two_radiologists weight=0.8
```

**Caution:** `exactly_k` uses combinatorial logic and may be slow for large tensors or high k values.

### `threshold_implication(antecedent, consequent, threshold)`

Create threshold-based implication constraint:
```
define strong_implication = threshold_implication(high_risk_L, findings_L, 0.7)
constraint strong_implication weight=0.9
```

### `conditional_probability(condition, event, target_prob)`

Create conditional probability constraint:
```
define conditional_findings = conditional_probability(high_birads_L, findings_L, 0.85)
constraint conditional_findings weight=0.8
```

### `clamp(tensor, min_val, max_val)`

Clamp tensor values to specified range:
```
define clamped_mass = clamp(mass_L, 0.1, 0.9)
```

### `threshold(tensor, threshold)`

Apply threshold to tensor:
```
define binary_mass = threshold(mass_L, 0.5)
```

### `greater_than(left, right)`

Create soft greater than comparison between two tensors:
```
define high_confidence = greater_than(confidence, baseline)
```

### `less_than(left, right)`

Create soft less than comparison between two tensors:
```
define low_risk = less_than(risk_score, threshold_low)
```

### `equals(left, right)`

Create soft equality comparison between two tensors:
```
define similar_scores = equals(score_a, score_b)
```

### `threshold_constraint(tensor, threshold, operator)`

Create threshold constraint with specified comparison operator:
```
define high_birads = threshold_constraint(birads_score, 0.7, ">")
define exact_match = threshold_constraint(prediction, 0.5, "==")
define within_bounds = threshold_constraint(value, 0.3, ">=")
```

## Data Types

### Numbers

Integer or floating-point numbers can be used directly in expressions:
```
define high_risk = risk_score > 0.8
define moderate = value >= 0.3 & value <= 0.7
constraint threshold_check weight=1.5  # Literal number as parameter
```

### Strings

Text values enclosed in quotes:
```
transform="logbarrier"
transform='hinge'
const model_type = "transformer"
```

### Lists

Arrays of values:
```
[1, 2, 3]
[4, 5, 6]
const important_classes = [4, 5, 6]  # Can store list constants
```

### Mixed Type Expressions

The logic language automatically handles mixed types in expressions:
```
# Tensor compared with literal number
define high_values = predictions > 0.5

# Tensor compared with constant
const threshold = 0.7
define above_threshold = scores >= threshold

# Combining constants and variables
const low_cut = 0.2
const high_cut = 0.8
define in_range = (values >= low_cut) & (values <= high_cut)
```

## Constraint Parameters

### `weight` (float)

Relative importance of the constraint:
```
constraint exactly_one(birads_L) weight=2.0  # Higher weight = more important
```

### `transform` (string)

Loss transformation method:
- `"logbarrier"`: Logarithmic barrier (default, smooth penalties)
- `"hinge"`: Hinge loss (softer penalties)
- `"linear"`: Linear loss (proportional penalties)

```
constraint findings >> high_birads transform="hinge"
```

### Custom Parameters

Additional parameters specific to constraint types:
```
constraint exactly_one(birads_L) weight=1.0 alpha=2.0 beta=0.5
```

## Complete Example

```
# Mammography Constraint Rules
# ============================

# Declare expected variables from model output
expect mass_L, mass_R, mc_L, mc_R
expect birads_L, birads_R, birads_score_L, birads_score_R
expect comp

# Define constants for reusable thresholds
const high_risk_threshold = 0.7
const low_risk_threshold = 0.3
const birads_high_cutoff = 4
const birads_very_high_cutoff = 5

# Feature definitions - combine findings per breast
define findings_L = mass_L | mc_L
define findings_R = mass_R | mc_R

# BI-RADS probability groups using constants
define high_birads_L = sum(birads_L, [4, 5, 6])
define high_birads_R = sum(birads_R, [4, 5, 6])
define very_high_birads_L = sum(birads_L, [5, 6])
define very_high_birads_R = sum(birads_R, [5, 6])
define low_birads_L = sum(birads_L, [1, 2])
define low_birads_R = sum(birads_R, [1, 2])

# Threshold-based risk assessments using literals and constants
define high_risk_L = birads_score_L > high_risk_threshold
define high_risk_R = birads_score_R > high_risk_threshold  
define very_low_risk_L = birads_score_L < low_risk_threshold
define very_low_risk_R = birads_score_R < low_risk_threshold
define balanced_assessment = equals(risk_L, risk_R)

# Range constraints using multiple comparisons with literals
define valid_risk_range_L = (birads_score_L >= 0.0) & (birads_score_L <= 1.0)
define valid_risk_range_R = (birads_score_R >= 0.0) & (birads_score_R <= 1.0)

# No findings (negation of findings)
define no_findings_L = ~findings_L
define no_findings_R = ~findings_R

# Categorical exclusivity constraints
constraint exactly_one(birads_L) weight=1.0 transform="logbarrier"
constraint exactly_one(birads_R) weight=1.0 transform="logbarrier"
constraint exactly_one(comp) weight=0.7 transform="logbarrier"

# Logical implication constraints using threshold variables
constraint high_risk_L >> findings_L weight=0.8 transform="logbarrier"
constraint high_risk_R >> findings_R weight=0.8 transform="logbarrier"

# Very High BI-RADS (5-6) -> Findings  
constraint very_high_birads_L >> findings_L weight=0.7 transform="logbarrier"
constraint very_high_birads_R >> findings_R weight=0.7 transform="logbarrier"

# Low BI-RADS with literal thresholds -> No findings (gentle constraint)
constraint very_low_risk_L >> no_findings_L weight=0.3 transform="logbarrier"
constraint very_low_risk_R >> no_findings_R weight=0.3 transform="logbarrier"

# Range validation constraints
constraint valid_risk_range_L weight=2.0 transform="logbarrier"
constraint valid_risk_range_R weight=2.0 transform="logbarrier"

# Comparison-based constraints using constants
constraint balanced_assessment weight=0.4 transform="hinge"
```

## Usage Patterns

### 1. Variable Expectations

Declare required variables at the beginning of scripts for better error handling:
```
# Declare all expected model outputs in one line
expect left_mass_prob, right_mass_prob, left_birads, right_birads, composition

# Now use these variables with confidence
define findings_L = left_mass_prob > 0.5
constraint exactly_one(left_birads)
```

### 2. Categorical Constraints

Ensure exactly one category is selected:
```
constraint exactly_one(birads_L) weight=1.0
constraint exactly_one(composition) weight=0.8
```

### 2. Implication Rules

Model domain knowledge as if-then relationships:
```
# If findings present, then high BI-RADS likely
constraint findings_L >> high_birads_L weight=0.7

# If very high BI-RADS, then findings must be present
constraint very_high_birads_L >> findings_L weight=0.8
```

### 3. Mutual Exclusion

Prevent conflicting classifications:
```
constraint mutual_exclusion(mass_L, calc_L) weight=0.5
```

### 4. Threshold Rules

Apply domain-specific thresholds:
```
define suspicious = threshold(combined_score, 0.7)
constraint suspicious >> high_birads weight=0.6
```

### 5. Comparison Constraints

Use soft comparison operators for ordinal and threshold relationships:
```
# Risk stratification with thresholds
define high_risk = risk_score > 0.8
define low_risk = risk_score < 0.2
constraint high_risk >> findings weight=0.7
```

### 6. Consensus and Agreement (AND_n)

Model situations where all elements must be true:
```
# All radiologists must agree for high confidence
define consensus = & radiologist_assessments
constraint consensus > 0.7 >> definitive_diagnosis weight=0.9

# All imaging modalities must show findings
define multi_modal_positive = & imaging_results
constraint multi_modal_positive >> high_confidence weight=0.8
```

### 7. Any Evidence Detection (OR_n)

Model situations where any element being true is significant:
```
# Any radiologist expressing concern triggers review
define any_concern = | radiologist_assessments  
constraint any_concern > 0.5 >> requires_review weight=0.6

# Any modality showing findings suggests pathology
define any_positive = | imaging_modalities
constraint any_positive >> potential_pathology weight=0.7
```

### 8. Tensor Indexing and Slicing

Access specific elements, patients, or subsets of multi-dimensional data:
```
# REMEMBER: First dimension is always batch when using RuleMammoLoss or RuleBasedConstraintsLoss! Use [:, ...] to preserve batch dimension

# Feature-wise access (CORRECT - preserves batch dimension)
define birads_4 = features[:, 4]              # Feature 4 for all batch items
define high_classes = features[:, 4:7]        # Features 4-6 for all batch items
define first_half = features[:, :3]           # Features 0-2 for all batch items

# Multi-dimensional indexing with batch preservation
define cc_assessments = assessments[:, 0, :]  # CC view for all patients
define mlo_assessments = assessments[:, 1, :] # MLO view for all patients  
define radiologist_1 = assessments[:, :, 0]   # Radiologist 1 across all views/patients

# View-specific analysis preserving batch dimension
define cc_consensus = & cc_assessments        # Consensus across CC view features
define mlo_consensus = & mlo_assessments      # Consensus across MLO view features
constraint cc_consensus & mlo_consensus >> high_confidence weight=0.9

# Feature subset analysis
define feature_subset = features[:, 2:5]      # Specific feature range for all batches
define subset_consensus = & feature_subset
constraint subset_consensus >> specialized_finding weight=0.8

# WRONG - These would access batch items instead of features when using RuleMammoLoss or RuleBasedConstraintsLoss:
# define birads_4 = features[4]              # Accesses batch item 4!
# define patient_subset = features[2:5]      # Accesses batch items 2-4!
```

### 9. Ordinal Relationships

Model ordered classifications with comparison operators:
```
# BI-RADS ordering constraints
define birads_3_higher = birads_3 >= birads_2
define birads_4_higher = birads_4 >= birads_3
constraint birads_3_higher & birads_4_higher weight=0.8
```

## Error Handling

The logic language provides helpful error messages for common issues:

### Syntax Errors

```
define x = mass_L |  # Error: Missing right operand
```

### Undefined Variables

```
define x = undefined_var  # Error: Variable 'undefined_var' is not defined
```

### Type Mismatches

```
constraint exactly_one(5)  # Error: Expected Truth object, got number
```

### Invalid Functions

```
define x = unknown_func()  # Error: Unknown function 'unknown_func'
```

### Batch Dimension Errors

```
# Wrong indexing - accessing batch items instead of features
define birads_4 = features[4]     # Error: May cause shape mismatch
# Correct indexing - preserving batch dimension  
define birads_4 = features[:, 4]  # ✅ Correct: Access feature 4 for all batches
```

## Advanced Features

### Custom Functions

Add domain-specific functions to the interpreter:
```python
def custom_risk_score(mass_prob, calc_prob, birads_prob):
    # Custom risk calculation
    return combined_risk

interpreter.add_builtin_function('risk_score', custom_risk_score)
```
**Note**: Custom functions must handle batch dimensions appropriately and return either a PyTorch tensor or a Truth object. See `soft_logic.py` for reference on Truth objects.

### Dynamic Rule Updates

Modify rules at runtime:
```python
loss_fn.update_rules(new_rules_string)
```

### Multiple Semantics

Choose different logical semantics (the default is "Gödel"):
- **Gödel**: min/max operations (sharp/tunable decision boundaries)
- **Łukasiewicz**: bounded sum operations (smoother but easy to saturate)
- **Product**: multiplication operations (independent probabilities)

```python
loss_fn = RuleMammoLoss(
    feature_indices=indices,
    rules=rules,
    semantics="lukasiewicz"  # or "godel", "product"
)
```

## Best Practices

1. **Start Simple**: Begin with basic constraints and add complexity gradually
2. **Use Comments**: Document the medical reasoning behind each constraint
3. **Test Incrementally**: Add constraints one at a time and validate behavior
4. **Meaningful Names**: Use descriptive variable names that reflect medical concepts
5. **Balanced Weights**: Start with equal weights and adjust based on domain importance
6. **Appropriate Transforms**: Use "logbarrier" for strict constraints, "hinge" for softer ones
7. **⚠️ Mind the Batch Dimension**: Always use `[:, ...]` when indexing tensors from `RuleMammoLoss` or `RuleBasedConstraintsLoss`
8. **Validate Tensor Shapes**: Print tensor shapes during development to verify indexing
9. **Test with Different Batch Sizes**: Ensure your logic works with various batch sizes
10. **Leverage Built-in Functions**: Use provided functions like `sum`, `exactly_one`, etc., to make the code cleaner and more efficient
11. **Do Not Use Unbounded Variables**: The package is not designed for values outside $\mathbb{R}^{[0,1]}$ and you might get unexpected results and clipping issues.
12. **Cautious Use of Arithmetic**: Since the logic language is primarily for $x \in \mathbb{R}^{[0,1]}$, be careful when using arithmetic operations to avoid values going out of bounds. Try to keep intermediate results within [0,1] and use built-in functions for common patterns.

## Migration from Hard-coded Constraints

To convert existing hard-coded constraints to logic language:

1. **Identify logical patterns** in your constraint code
2. **Extract variable definitions** for reused expressions
3. **Convert constraints** to logic language syntax
4. **Test equivalence** with the original implementation
5. **Refine and optimize** weights and transforms
