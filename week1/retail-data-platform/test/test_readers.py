import unittest

from retail_ingestion.csv_reader import read_sales
from retail_ingestion.json_reader import read_orders
from retail_ingestion.paths import get_data_file


class TestCsvReader(unittest.TestCase):
    def test_read_sales_preserves_raw_values(self) -> None:
        sales = read_sales(get_data_file("sales.csv"))

        self.assertEqual(len(sales), 5)
        self.assertEqual(sales[0]["sale_id"], "S001")
        self.assertEqual(sales[0]["amount"], "19.90")
        self.assertEqual(sales[2]["amount"], "")
        self.assertEqual(sales[2]["sale_id"], sales[3]["sale_id"])
        self.assertEqual(sales[4]["sale_date"], "invalid-date")

    def test_iter_sales_yields_one_record_at_a_time(self) -> None:
        from retail_ingestion.csv_reader import iter_sales

        sales = iter_sales(get_data_file("sales.csv"))

        self.assertIs(iter(sales), sales)

        first_sale = next(sales)
        self.assertEqual(first_sale["sale_id"], "S001")
        self.assertEqual(first_sale["amount"], "19.90")

        remaining_sales = list(sales)
        self.assertEqual(len(remaining_sales), 4)
        self.assertEqual(remaining_sales[0]["sale_id"], "S002")
        self.assertEqual(remaining_sales[-1]["sale_id"], "S005")


class TestJsonReader(unittest.TestCase):
    def test_read_orders_preserves_json_types(self) -> None:
        orders = read_orders(get_data_file("orders.json"))

        self.assertEqual(len(orders), 6)
        self.assertEqual(orders[0]["order_id"], "O001")
        self.assertEqual(orders[0]["total"], 49.90)
        self.assertIsNone(orders[2]["customer_id"])
        self.assertEqual(orders[2]["order_id"], orders[3]["order_id"])
        self.assertEqual(orders[4]["total"], "invalid-total")