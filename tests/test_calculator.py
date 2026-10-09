import unittest
from decimal import Decimal

from backend.importers import excel_reader
from backend.services.calculator import calculate


class TestCalculator(unittest.TestCase):
    def test_calculates_monthly_menu_results_from_importer_data(self) -> None:
        result = calculate(
            excel_reader.menu,
            excel_reader.recipe_dict,
            excel_reader.ingredients,
            excel_reader.costs,
            excel_reader.sales,
        )

        self.assertEqual(len(result["items"]), len(excel_reader.menu))
        self.assertEqual(result["items"][0]["classification"], "STAR")
        self.assertEqual(
            result["summary"]["total_revenue"], Decimal("40500000.0")
        )
        self.assertEqual(
            result["summary"]["total_fixed_cost"], Decimal("17000000.0")
        )
        self.assertEqual(
            result["summary"]["operating_profit"].quantize(Decimal("1")),
            Decimal("2865354"),
        )


if __name__ == "__main__":
    unittest.main()
