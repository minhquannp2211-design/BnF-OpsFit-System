import shutil
import tempfile
import unittest
from pathlib import Path

import openpyxl

from backend.importers.excel_reader import load_costs_and_sales


ROOT = Path(__file__).resolve().parents[1]
TEST_WORKBOOK = ROOT / "data" / "tests" / "BnF_Opsfit_Test_Data.xlsx"
FOOD_IDS = {"COM_TAM_L", "TRA_DAO_M", "CA_PHE_SUA_DA_M"}


class TestCostsAndSalesImport(unittest.TestCase):
    def test_loads_and_normalizes_costs_and_sales(self) -> None:
        costs, sales = load_costs_and_sales(TEST_WORKBOOK, FOOD_IDS)

        self.assertEqual([cost["monthly_amount"] for cost in costs], [
            6000000, 8000000, 2000000, 1000000, 900000,
        ])
        self.assertEqual(costs[-1]["cost_type"], "VARIABLE")
        self.assertEqual(
            [(item["food_id"], item["quantity_sold"]) for item in sales],
            [
                ("COM_TAM_L", 1350),
                ("TRA_DAO_M", 900),
                ("CA_PHE_SUA_DA_M", 1100),
            ],
        )

    def edit_workbook(self, edit) -> Path:
        temporary_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_dir.cleanup)
        output = Path(temporary_dir.name) / "invalid.xlsx"
        shutil.copyfile(TEST_WORKBOOK, output)
        workbook = openpyxl.load_workbook(output)
        edit(workbook)
        workbook.save(output)
        workbook.close()
        return output

    def test_requires_allocation_period_for_regular_costs(self) -> None:
        def edit(workbook) -> None:
            workbook["costs"]["F2"] = None

        path = self.edit_workbook(edit)
        with self.assertRaisesRegex(ValueError, "period_months"):
            load_costs_and_sales(path, FOOD_IDS)

    def test_rejects_zero_allocation_period(self) -> None:
        def edit(workbook) -> None:
            workbook["costs"]["F2"] = 0

        path = self.edit_workbook(edit)
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            load_costs_and_sales(path, FOOD_IDS)

    def test_rejects_missing_required_header(self) -> None:
        def edit(workbook) -> None:
            workbook["costs"]["F1"] = "Kỳ phân bổ"

        path = self.edit_workbook(edit)
        with self.assertRaisesRegex(ValueError, "Missing columns"):
            load_costs_and_sales(path, FOOD_IDS)

    def test_rejects_unknown_item_code(self) -> None:
        def edit(workbook) -> None:
            workbook["sales"]["A2"] = "UNKNOWN_ITEM"

        path = self.edit_workbook(edit)
        with self.assertRaisesRegex(ValueError, "Unknown item_code"):
            load_costs_and_sales(path, FOOD_IDS)

    def test_rejects_duplicate_cost_ids(self) -> None:
        def edit(workbook) -> None:
            workbook["costs"]["A3"] = workbook["costs"]["A2"].value

        path = self.edit_workbook(edit)
        with self.assertRaisesRegex(ValueError, "Duplicated cost_id"):
            load_costs_and_sales(path, FOOD_IDS)


if __name__ == "__main__":
    unittest.main()
