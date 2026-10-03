"""Single-product profit optimization under a safe-capacity limit.

The current model is linear in quantity. SLSQP solves it within the configured
safe-capacity constraint.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from math import isfinite
from numbers import Real
from typing import TypeAlias

from scipy.optimize import minimize

NumericInput: TypeAlias = Decimal | int | float
DEFAULT_SAFE_CAPACITY_FRACTION = Decimal("0.8")


@dataclass(frozen=True)
class OptimalProfitResult:
    """Result returned by :func:`optimize_optimal_profit_point`."""

    optimal_quantity: Decimal
    target_profit: Decimal
    unit_net_margin: Decimal
    safe_capacity_limit: Decimal
    solver_method: str
    solver_message: str


def _require_decimal(
    value: NumericInput,
    field_name: str,
    *,
    minimum: Decimal | None = None,
    exclusive_minimum: bool = False,
) -> Decimal:
    """Convert a supported numeric input and report field-specific errors."""
    if isinstance(value, bool) or not isinstance(value, (Decimal, Real)):
        raise ValueError(f"'{field_name}' must be a finite number")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(
            f"Invalid numeric value '{value}' for '{field_name}'"
        ) from error

    if not number.is_finite():
        raise ValueError(f"'{field_name}' must be a finite number")

    if minimum is not None:
        is_invalid = number <= minimum if exclusive_minimum else number < minimum
        if is_invalid:
            comparator = "greater than" if exclusive_minimum else "at least"
            raise ValueError(
                f"'{field_name}' must be {comparator} {minimum}"
            )

    return number


def calculate_target_profit(
    quantity: NumericInput,
    avg_food_price: NumericInput,
    avg_unit_cogs: NumericInput,
    staff_bonus_per_unit: NumericInput,
    total_fixed_cost: NumericInput,
) -> Decimal:
    """Calculate profit using ``Q * (P - VC - b) - FC``.

    In this initial model, ``staff_bonus_per_unit`` is deducted for every
    optimized unit, matching the supplied formula. A bonus paid only after
    break-even would need an explicit break-even quantity and a piecewise
    objective.
    """
    normalized_quantity = _require_decimal(
        quantity, "quantity", minimum=Decimal("0")
    )
    normalized_price = _require_decimal(
        avg_food_price, "avg_food_price", minimum=Decimal("0")
    )
    normalized_unit_cogs = _require_decimal(
        avg_unit_cogs, "avg_unit_cogs", minimum=Decimal("0")
    )
    normalized_bonus = _require_decimal(
        staff_bonus_per_unit,
        "staff_bonus_per_unit",
        minimum=Decimal("0"),
    )
    normalized_fixed_cost = _require_decimal(
        total_fixed_cost, "total_fixed_cost", minimum=Decimal("0")
    )

    unit_net_margin = (
        normalized_price - normalized_unit_cogs - normalized_bonus
    )
    return normalized_quantity * unit_net_margin - normalized_fixed_cost


def get_safe_capacity_limit(
    max_capacity_units: NumericInput,
    safe_capacity_fraction: NumericInput = DEFAULT_SAFE_CAPACITY_FRACTION,
) -> Decimal:
    """Return the operating limit (80% of capacity by default)."""
    normalized_capacity = _require_decimal(
        max_capacity_units,
        "max_capacity_units",
        minimum=Decimal("0"),
        exclusive_minimum=True,
    )
    normalized_fraction = _require_decimal(
        safe_capacity_fraction,
        "safe_capacity_fraction",
        minimum=Decimal("0"),
        exclusive_minimum=True,
    )
    if normalized_fraction > 1:
        raise ValueError("'safe_capacity_fraction' must be at most 1")

    return normalized_capacity * normalized_fraction


def is_within_safe_capacity(
    quantity: NumericInput,
    max_capacity_units: NumericInput,
    safe_capacity_fraction: NumericInput = DEFAULT_SAFE_CAPACITY_FRACTION,
) -> bool:
    """Return whether quantity is non-negative and within the safe limit."""
    normalized_quantity = _require_decimal(
        quantity, "quantity", minimum=Decimal("0")
    )
    capacity_limit = get_safe_capacity_limit(
        max_capacity_units, safe_capacity_fraction
    )
    return normalized_quantity <= capacity_limit


def optimize_optimal_profit_point(
    avg_food_price: NumericInput,
    avg_unit_cogs: NumericInput,
    staff_bonus_per_unit: NumericInput,
    total_fixed_cost: NumericInput,
    max_capacity_units: NumericInput,
    safe_capacity_fraction: NumericInput = DEFAULT_SAFE_CAPACITY_FRACTION,
) -> OptimalProfitResult:
    """Find the profit-maximizing continuous quantity within safe capacity.

    Quantity is bounded by ``0 <= Q <= max_capacity_units * fraction``.
    This first version treats capacity as the only production constraint; it
    does not model demand, prep time, or an integer-unit requirement.
    """
    normalized_price = _require_decimal(
        avg_food_price, "avg_food_price", minimum=Decimal("0")
    )
    normalized_unit_cogs = _require_decimal(
        avg_unit_cogs, "avg_unit_cogs", minimum=Decimal("0")
    )
    normalized_bonus = _require_decimal(
        staff_bonus_per_unit,
        "staff_bonus_per_unit",
        minimum=Decimal("0"),
    )
    normalized_fixed_cost = _require_decimal(
        total_fixed_cost, "total_fixed_cost", minimum=Decimal("0")
    )
    capacity_limit = get_safe_capacity_limit(
        max_capacity_units, safe_capacity_fraction
    )
    unit_net_margin = (
        normalized_price - normalized_unit_cogs - normalized_bonus
    )

    def calculate_profit_at(quantity: Decimal) -> Decimal:
        return calculate_target_profit(
            quantity=quantity,
            avg_food_price=normalized_price,
            avg_unit_cogs=normalized_unit_cogs,
            staff_bonus_per_unit=normalized_bonus,
            total_fixed_cost=normalized_fixed_cost,
        )

    safe_limit_float = float(capacity_limit)
    margin_float = float(unit_net_margin)
    fixed_cost_float = float(normalized_fixed_cost)
    capacity_profit_range = safe_limit_float * margin_float
    if not all(
        isfinite(value)
        for value in (
            safe_limit_float,
            margin_float,
            fixed_cost_float,
            capacity_profit_range,
        )
    ):
        raise ValueError(
            "Optimization inputs exceed the numeric range supported by SciPy"
        )

    def objective(quantity_values: list[float]) -> float:
        quantity = quantity_values[0]
        return -(quantity * margin_float - fixed_cost_float)

    def capacity_constraint(quantity_values: list[float]) -> float:
        return safe_limit_float - quantity_values[0]

    initial_quantity = [safe_limit_float / 2]
    result = minimize(
        objective,
        initial_quantity,
        method="SLSQP",
        bounds=[(0.0, safe_limit_float)],
        constraints=(
            {"type": "ineq", "fun": capacity_constraint},
        ),
        options={"maxiter": 100, "ftol": 1e-9},
    )

    if not result.success:
        raise RuntimeError(
            f"SLSQP failed to find an optimal quantity: {result.message}"
        )

    quantity_float = float(result.x[0])
    tolerance = max(1e-8, safe_limit_float * 1e-9)
    if not isfinite(quantity_float):
        raise RuntimeError("SLSQP returned a non-finite quantity")
    if (
        quantity_float < -tolerance
        or quantity_float > safe_limit_float + tolerance
    ):
        raise RuntimeError(
            "SLSQP returned a quantity outside the safe capacity bounds"
        )

    quantity_float = min(max(quantity_float, 0.0), safe_limit_float)
    if abs(quantity_float) <= tolerance:
        quantity = Decimal("0")
    elif abs(quantity_float - safe_limit_float) <= tolerance:
        quantity = capacity_limit
    else:
        quantity = Decimal(str(quantity_float))

    if not is_within_safe_capacity(
        quantity, max_capacity_units, safe_capacity_fraction
    ):
        raise RuntimeError("Optimized quantity violates safe capacity")

    return OptimalProfitResult(
        optimal_quantity=quantity,
        target_profit=calculate_profit_at(quantity),
        unit_net_margin=unit_net_margin,
        safe_capacity_limit=capacity_limit,
        solver_method="SLSQP",
        solver_message=str(result.message),
    )
