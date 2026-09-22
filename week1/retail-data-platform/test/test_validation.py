import unittest
from datetime import datetime

from retail_ingestion.validation import (
    InvalidDatetimeError,
    is_present,
    parse_datetime,
)


class TestValidation(unittest.TestCase):
    def test_missing_values_are_not_present(self) -> None:
        for value in (None, "", "   "):
            with self.subTest(value=value):
                self.assertFalse(is_present(value))

    def test_non_empty_value_is_present(self) -> None:
        self.assertTrue(is_present("sale-123"))

    def test_parse_iso_datetime(self) -> None:
        result = parse_datetime("2026-09-18T09:15:00")

        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.hour, 9)

    def test_invalid_datetime_raises_domain_error(self) -> None:
        with self.assertRaisesRegex(
            InvalidDatetimeError,
            "Invalid datetime format: not-a-date",
        ):
            parse_datetime("not-a-date")