"""Run the monthly menu cost and profitability calculations."""

from decimal import Decimal
from typing import Any, Sequence

from backend.services import formula


def _decimal(value: float | int | Decimal) -> Decimal:
    return Decimal(str(value))


def calculate(
    menu_items: Sequence[tuple[str, str, str, float]],
    recipes: dict[tuple[str, str, str], list[tuple[str, str, str, float, str]]],
    ingredients: Sequence[tuple[str, str, float, float, str, float]],
    costs: Sequence[dict[str, Any]],
    sales: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate per-item results and monthly menu totals from importer data."""
    ingredient_by_id = {ingredient[0]: ingredient for ingredient in ingredients}
    recipe_by_food_id: dict[str, list[tuple[str, str, str, float, str]]] = {}
    for recipe_details in recipes.values():
        for detail in recipe_details:
            recipe_by_food_id[detail[0]] = recipe_details

    sales_by_food_id = {
        sale["food_id"]: _decimal(sale["quantity_sold"])
        for sale in sales
    }

    items: list[dict[str, Any]] = []
    quantities: list[Decimal] = []
    unit_margins: list[Decimal] = []
    item_revenues: list[Decimal] = []
    item_cogs: list[Decimal] = []

    for food_id, food_name, food_size, raw_price in menu_items:
        recipe_details = recipe_by_food_id.get(food_id)
        if not recipe_details:
            raise ValueError(f"Menu item '{food_id}' has no recipe")

        line_costs: list[Decimal] = []
        for detail in recipe_details:
            _, ingredient_id, ingredient_name, raw_quantity, _ = detail
            ingredient = ingredient_by_id.get(ingredient_id)
            if ingredient is None:
                raise ValueError(
                    f"Recipe for '{food_id}' uses unknown ingredient "
                    f"'{ingredient_id}' ({ingredient_name})"
                )
            _, _, raw_package_price, raw_package_quantity, _, raw_waste_rate = ingredient
            usable = formula.usable_quantity(
                _decimal(raw_package_quantity), _decimal(raw_waste_rate)
            )
            effective_cost = formula.effective_unit_cost(
                usable, _decimal(raw_package_price)
            )
            line_costs.append(
                formula.ingredient_line_cost(_decimal(raw_quantity), effective_cost)
            )

        unit_cost = formula.unit_cogs(line_costs)
        price = _decimal(raw_price)
        quantity = sales_by_food_id.get(food_id, Decimal("0"))
        revenue = formula.revenue(quantity, price)
        sold_cogs = formula.cogs(quantity, unit_cost)
        margin = formula.contribution_margin_item(sold_cogs, revenue)
        unit_margin = formula.contribution_margin_unit(price, unit_cost)

        items.append({
            "food_id": food_id,
            "food_name": food_name,
            "food_size": food_size,
            "quantity_sold": quantity,
            "food_price": price,
            "unit_cogs": unit_cost,
            "revenue": revenue,
            "cogs": sold_cogs,
            "contribution_margin": margin,
        })
        quantities.append(quantity)
        unit_margins.append(unit_margin)
        item_revenues.append(revenue)
        item_cogs.append(sold_cogs)

    total_revenue = formula.total_revenue(item_revenues)
    total_cogs = formula.total_cogs(item_cogs)
    total_margin = formula.total_contribution_margin(total_revenue, total_cogs)
    monthly_fixed_costs = [
        _decimal(cost["monthly_amount"])
        for cost in costs
        if cost["cost_type"] == "FIXED"
    ]
    monthly_variable_costs = [
        _decimal(cost["monthly_amount"])
        for cost in costs
        if cost["cost_type"] == "VARIABLE"
    ]
    fixed_cost = formula.total_fixed_cost(monthly_fixed_costs, [])
    variable_cost = sum(monthly_variable_costs, Decimal("0"))
    operating_cost = formula.operating_cost(total_cogs, fixed_cost)
    profit = formula.operating_profit(operating_cost, total_revenue)

    classifications = formula.menu_classification(quantities, unit_margins)
    for item, classification in zip(items, classifications):
        item["classification"] = classification

    return {
        "items": items,
        "summary": {
            "total_volume": formula.total_volume(quantities),
            "total_revenue": total_revenue,
            "total_cogs": total_cogs,
            "total_contribution_margin": total_margin,
            "total_fixed_cost": fixed_cost,
            "total_variable_cost": variable_cost,
            "operating_cost": operating_cost,
            "operating_profit": profit,
            "contribution_margin_ratio": formula.contribution_margin_ratio(
                total_margin, total_revenue
            ),
            "operating_profit_margin": formula.operating_profit_margin(
                profit, total_revenue
            ),
            "fixed_cost_ratio": formula.fixed_cost_ratio(fixed_cost, total_revenue),
        },
    }


def main() -> None:
    """Load the workbook through the importer and print monthly results."""
    from backend.importers import excel_reader

    result = calculate(
        excel_reader.menu,
        excel_reader.recipe_dict,
        excel_reader.ingredients,
        excel_reader.costs,
        excel_reader.sales,
    )

    print("Monthly menu results")
    for item in result["items"]:
        print(
            f"{item['food_id']}: sold={item['quantity_sold']}, "
            f"unit COGS={formula.round_money(item['unit_cogs'])}, "
            f"revenue={formula.round_money(item['revenue'])}, "
            f"contribution={formula.round_money(item['contribution_margin'])}, "
            f"class={item['classification']}"
        )

    summary = result["summary"]
    print("Monthly summary")
    for name in (
        "total_volume", "total_revenue", "total_cogs",
        "total_contribution_margin", "total_fixed_cost",
        "total_variable_cost", "operating_cost", "operating_profit",
    ):
        value = summary[name]
        display_value = value if name == "total_volume" else formula.round_money(value)
        print(f"{name}: {display_value}")


if __name__ == "__main__":
    main()
