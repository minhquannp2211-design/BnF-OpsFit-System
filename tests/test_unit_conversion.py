import unittest

from backend.utils.unit_conversion import standardize_quantity


class TestStandardizeQuantity(unittest.TestCase):
    def test_converts_quantity_to_standard_unit(self) -> None:
        self.assertEqual(standardize_quantity(1, "kg"), (1000, "g"))

    def test_checks_compatibility_with_reference_unit(self) -> None:
        with self.assertRaisesRegex(ValueError, "Incompatible units"):
            standardize_quantity(1, "kg", expected_unit="ml")


if __name__ == "__main__":
    unittest.main()
