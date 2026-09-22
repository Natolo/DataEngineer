import unittest
from pathlib import Path

from retail_ingestion.paths import get_data_file


class TestPaths(unittest.TestCase):
    def test_get_data_file_builds_expected_path(self) -> None:
        result = get_data_file("sales.csv")

        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, "sales.csv")
        self.assertEqual(result.parent.name, "data")
        self.assertTrue(result.exists())