import unittest
from decimal import Decimal

from backend.importers.excel_reader import (
    costs,
    ingredients,
    menu,
    recipe_dict,
    sales,
)
from backend.services import formula


def decimal(value: object) -> Decimal:
    return Decimal(str(value))


class TestFinancialFormulas(unittest.TestCase):
    def test_cost_and_margin_flow_from_template(self) -> None:
        ingredient_by_id = {item[0]: item for item in ingredients}
        recipe_details = next(iter(recipe_dict.values()))
        line_costs = []
        for detail in recipe_details:
            ingredient = ingredient_by_id[detail[1]]
            self.assertEqual(detail[4], ingredient[4])
            usable = formula.usable_quantity(
                decimal(ingredient[3]), decimal(ingredient[5])
            )
            unit_cost = formula.effective_unit_cost(
                usable, decimal(ingredient[2])
            )
            line_costs.append(
                formula.ingredient_line_cost(decimal(detail[3]), unit_cost)
            )

        unit_cogs = formula.unit_cogs(line_costs)
        food_price = decimal(menu[0][3])
        quantity_sold = decimal(sales[0]["quantity_sold"])
        monthly_revenue = formula.revenue(quantity_sold, food_price)
        monthly_cogs = formula.cogs(quantity_sold, unit_cogs)
        fixed_costs = [
            decimal(cost["monthly_amount"])
            for cost in costs
            if cost["cost_type"] == "FIXED"
        ]
        monthly_fixed_cost = formula.total_fixed_cost(fixed_costs, [])
        contribution = formula.total_contribution_margin(
            monthly_revenue, monthly_cogs
        )
        profit = formula.operating_profit(
            formula.operating_cost(monthly_cogs, monthly_fixed_cost),
            monthly_revenue,
        )

        self.assertGreater(unit_cogs, Decimal("0"))
        self.assertEqual(
            unit_cogs,
            Decimal("15284.92268041237113402061856"),
        )
        self.assertEqual(monthly_revenue, Decimal("40500000.0"))
        self.assertEqual(
            profit,
            contribution - monthly_fixed_cost,
        )

    def test_rejects_invalid_denominators_and_waste_rate(self) -> None:
        with self.assertRaises(ValueError):
            formula.raw_unit_cost(Decimal("10"), Decimal("0"))
        with self.assertRaises(ValueError):
            formula.monthly_depreciation(Decimal("100"), Decimal("0"))
        with self.assertRaises(ValueError):
            formula.usable_quantity(Decimal("100"), Decimal("1"))
        with self.assertRaises(ValueError):
            formula.contribution_margin_ratio(Decimal("10"), Decimal("0"))

    def test_rounds_displayed_money_half_up_to_whole_vnd(self) -> None:
        self.assertEqual(formula.round_money(Decimal("12.5")), Decimal("13"))
        self.assertEqual(formula.round_money(Decimal("12.4")), Decimal("12"))


if __name__ == "__main__":
    unittest.main()
