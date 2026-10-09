import unittest
from decimal import Decimal

from backend.services.formula import menu_classification


class TestMenuEngineering(unittest.TestCase):
    def test_classifies_menu_items(self) -> None:
        quantity_sold = [
            Decimal("10"), Decimal("8"), Decimal("2"), Decimal("0")
        ]
        unit_margin = [
            Decimal("10"), Decimal("2"), Decimal("8"), Decimal("5")
        ]

        self.assertEqual(
            menu_classification(quantity_sold, unit_margin),
            ["STAR", "PLOWHORSE", "PUZZLE", "DOG"],
        )

    def test_threshold_equality_is_inclusive(self) -> None:
        self.assertEqual(
            menu_classification(
                [Decimal("1"), Decimal("1")],
                [Decimal("2"), Decimal("2")],
            ),
            ["STAR", "STAR"],
        )

    def test_empty_menu_returns_empty_result(self) -> None:
        self.assertEqual(menu_classification([], []), [])

    def test_rejects_zero_sales_and_mismatched_inputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "no sales"):
            menu_classification(
                [Decimal("0")], [Decimal("3")]
            )
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            menu_classification([Decimal("1")], [])


if __name__ == "__main__":
    unittest.main()
