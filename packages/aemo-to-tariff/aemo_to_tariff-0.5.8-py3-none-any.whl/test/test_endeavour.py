import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from aemo_to_tariff.endeavour import convert, convert_feed_in_tariff, time_zone

class TestEndeavour(unittest.TestCase):
    def test_convert_feed_in(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 100.0)
        self.assertAlmostEqual(feed_in_price, 10.00, places=1)
        
    def test_convert_high_season_peak(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 31.7964
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price)

    def test_convert_low_season_peak(self):
        interval_time = datetime(2024, 8, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 23.8419
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=4)

    def test_convert_off_peak(self):
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        rrp = 100.0
        expected_price = 15.97
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_convert_unknown_tariff(self):
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N999'
        rrp = 100.0
        with self.assertRaises(KeyError):
            convert(interval_time, tariff_code, rrp)
