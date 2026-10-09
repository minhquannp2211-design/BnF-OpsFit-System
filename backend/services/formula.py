from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence


ZERO = Decimal("0")
ONE = Decimal("1")


def raw_unit_cost(
    package_price: Decimal,
    standard_package_quantity: Decimal,
) -> Decimal:
    if standard_package_quantity <= ZERO:
        raise ValueError("standard_package_quantity must be greater than zero")
    return package_price / standard_package_quantity


def usable_quantity(
    standard_package_quantity: Decimal,
    waste_rate: Decimal,
) -> Decimal:
    if standard_package_quantity <= ZERO:
        raise ValueError("standard_package_quantity must be greater than zero")
    if not ZERO <= waste_rate < ONE:
        raise ValueError("waste_rate must be at least zero and less than one")
    return standard_package_quantity * (ONE - waste_rate)


def effective_unit_cost(
    usable_quantity: Decimal,
    package_price: Decimal,
) -> Decimal:
    if usable_quantity <= ZERO:
        raise ValueError("usable_quantity must be greater than zero")
    return package_price / usable_quantity


def ingredient_line_cost(
    standard_ingredient_quantity: Decimal,
    effective_unit_cost: Decimal,
) -> Decimal:
    if standard_ingredient_quantity < ZERO or effective_unit_cost < ZERO:
        raise ValueError("Ingredient quantity and unit cost cannot be negative")
    return standard_ingredient_quantity * effective_unit_cost


def unit_cogs(ingredient_line_cost: Sequence[Decimal]) -> Decimal:
    return sum(ingredient_line_cost, ZERO)


def monthly_cost(amount: Decimal, month_period: Decimal) -> Decimal:
    if month_period <= ZERO:
        raise ValueError("month_period must be greater than zero")
    return amount / month_period


def monthly_depreciation(
    amount: Decimal,
    useful_life_months: Decimal,
) -> Decimal:
    if useful_life_months <= ZERO:
        raise ValueError("useful_life_months must be greater than zero")
    return amount / useful_life_months


def total_fixed_cost(
    monthly_cost: Sequence[Decimal],
    monthly_depreciation: Sequence[Decimal],
) -> Decimal:
    return sum(monthly_cost, ZERO) + sum(monthly_depreciation, ZERO)


def revenue(quantity_sold: Decimal, food_price: Decimal) -> Decimal:
    return quantity_sold * food_price


def total_revenue(revenue: Sequence[Decimal]) -> Decimal:
    return sum(revenue, ZERO)


def cogs(quantity_sold: Decimal, unit_cogs: Decimal) -> Decimal:
    return quantity_sold * unit_cogs


def total_cogs(cogs: Sequence[Decimal]) -> Decimal:
    return sum(cogs, ZERO)


def operating_cost(total_cogs: Decimal, total_fixed_cost: Decimal) -> Decimal:
    return total_cogs + total_fixed_cost


def operating_profit(operating_cost: Decimal, total_revenue: Decimal) -> Decimal:
    return total_revenue - operating_cost


def contribution_margin_unit(food_price: Decimal, unit_cogs: Decimal) -> Decimal:
    return food_price - unit_cogs


def contribution_margin_item(cogs: Decimal, revenue: Decimal) -> Decimal:
    return revenue - cogs


def total_contribution_margin(
    total_revenue: Decimal,
    total_cogs: Decimal,
) -> Decimal:
    return total_revenue - total_cogs


def contribution_margin_ratio(
    total_contribution_margin: Decimal,
    total_revenue: Decimal,
) -> Decimal:
    if total_revenue == ZERO:
        raise ValueError("total_revenue must not be zero")
    return total_contribution_margin / total_revenue


def operating_profit_margin(
    operating_profit: Decimal,
    total_revenue: Decimal,
) -> Decimal:
    if total_revenue == ZERO:
        raise ValueError("total_revenue must not be zero")
    return operating_profit / total_revenue


def fixed_cost_ratio(
    total_fixed_cost: Decimal,
    total_revenue: Decimal,
) -> Decimal:
    if total_revenue == ZERO:
        raise ValueError("total_revenue must not be zero")
    return total_fixed_cost / total_revenue


def round_money(amount: Decimal) -> Decimal:
    """Round a final displayed VND amount to the nearest dong."""
    return amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def total_volume(quantity_sold: Sequence[Decimal]) -> Decimal:
    if any(
        not quantity.is_finite() or quantity < ZERO
        for quantity in quantity_sold
    ):
        raise ValueError("Sales quantities must be finite and non-negative")
    return sum(quantity_sold, ZERO)


def threshold_popularity(total_volume: Decimal, menu_size: int) -> Decimal:
    if menu_size <= 0:
        raise ValueError("menu_size must be greater than zero")
    if not total_volume.is_finite() or total_volume < ZERO:
        raise ValueError("total_volume must be finite and non-negative")
    return total_volume / menu_size


def threshold_profit(
    total_contribution_margin: Decimal,
    total_volume: Decimal,
) -> Decimal:
    if not total_volume.is_finite() or total_volume <= ZERO:
        raise ValueError("total_volume must be greater than zero")
    if not total_contribution_margin.is_finite():
        raise ValueError("total_contribution_margin must be finite")
    return total_contribution_margin / total_volume


def item_classification(
    popularity_threshold: Decimal,
    profit_threshold: Decimal,
    quantity_sold: Decimal,
    unit_contribution_margin: Decimal,
) -> str:
    values = (
        popularity_threshold,
        profit_threshold,
        quantity_sold,
        unit_contribution_margin,
    )
    if any(not value.is_finite() for value in values):
        raise ValueError("Classification inputs must be finite")
    if quantity_sold < ZERO:
        raise ValueError("quantity_sold must be non-negative")

    if (
        quantity_sold >= popularity_threshold
        and unit_contribution_margin >= profit_threshold
    ):
        return "STAR"
    if quantity_sold >= popularity_threshold:
        return "PLOWHORSE"
    if unit_contribution_margin >= profit_threshold:
        return "PUZZLE"
    return "DOG"


def menu_classification(
    quantity_sold: Sequence[Decimal],
    unit_contribution_margin: Sequence[Decimal],
) -> list[str]:
    if len(quantity_sold) != len(unit_contribution_margin):
        raise ValueError(
            "quantity_sold and unit_contribution_margin must have equal lengths"
        )
    if not quantity_sold:
        return []
    if any(not margin.is_finite() for margin in unit_contribution_margin):
        raise ValueError("Unit contribution margins must be finite")

    volume = total_volume(quantity_sold)
    if volume == ZERO:
        raise ValueError("Cannot classify a menu with no sales")

    total_margin = sum(
        (
            quantity * margin
            for quantity, margin in zip(quantity_sold, unit_contribution_margin)
        ),
        ZERO,
    )
    popularity = threshold_popularity(volume, len(quantity_sold))
    profit = threshold_profit(total_margin, volume)
    return [
        item_classification(popularity, profit, quantity, margin)
        for quantity, margin in zip(quantity_sold, unit_contribution_margin)
    ]
