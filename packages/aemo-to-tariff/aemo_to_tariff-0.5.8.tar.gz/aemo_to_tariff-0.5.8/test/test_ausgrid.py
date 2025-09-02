import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from aemo_to_tariff.ausgrid import convert_feed_in_tariff, time_zone, convert, calculate_demand_fee

class TestAusgrid(unittest.TestCase):
    def test_ea_025_peak(self):
        interval_time = datetime(2025, 4, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA025'
        rrp = 136.7
        expected_price = 22.13
        price = convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.12, expected_price, places=1)
    
    def test_ea_025_peak_summer(self):
        interval_time = datetime(2025, 1, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA025'
        rrp = 136.7
        expected_price = 48.0648
        price = convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.12, expected_price, places=1)
    
    def test_feed_ausgrid_functionality(self):
        interval_time = datetime(2023, 1, 15, 17, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'N71'
        feed_in_price = convert_feed_in_tariff(interval_time, tariff_code, 100.0)
        self.assertAlmostEqual(feed_in_price, 10.00, places=1)

    def test_ea_305_demand(self):
        tariff_code = 'EA305'
        expected_price = 2655.66
        price = calculate_demand_fee(tariff_code, 179.05, 30)
        self.assertAlmostEqual(price, expected_price, places=1)

    def test_ea_305_peak(self):
        interval_time = datetime(2025, 4, 22, 17, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA305'
        rrp = 136.7
        expected_price = 22.1471
        price = convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.12, expected_price, places=1)
    
    def test_ea_305_off_peak(self):
        interval_time = datetime(2025, 4, 22, 12, 45, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'EA305'
        rrp = 136.7
        expected_price = 17.192
        price = convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.12, expected_price, places=1)