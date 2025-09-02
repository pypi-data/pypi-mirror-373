import unittest
from datetime import datetime, time
from zoneinfo import ZoneInfo

from aemo_to_tariff.ergon import (
    time_zone,
    get_daily_fee,
    calculate_demand_fee,
    get_periods,
    convert_feed_in_tariff,
    convert,
)

class TestErgonFunctions(unittest.TestCase):
    def test_time_zone(self):
        self.assertEqual(time_zone(), 'Australia/Brisbane')

    def test_get_daily_fee(self):
        self.assertEqual(get_daily_fee('WRTOUET1'), 7.21)
        self.assertEqual(get_daily_fee('ERTOUET1'), 1.808)

    
    def test_get_periods(self):
        periods = get_periods('WRTOUET1')
        self.assertEqual(len(periods), 3)
        self.assertEqual(periods[0], ('Off-Peak', time(11, 0), time(16, 0), 0.524))
        with self.assertRaises(ValueError):
            get_periods('UNKNOWN')

    def test_convert_feed_in_tariff(self):
        interval_datetime = datetime(2023, 1, 1, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        self.assertEqual(convert_feed_in_tariff(interval_datetime, 'WRTOUET1', 100), 10.0)

    def test_ERTOUET1_tariff(self):
        # 11:30 RRP $-31.99/MWh
        interval_datetime = datetime(2025, 4, 5, 11, 30, tzinfo=ZoneInfo('Australia/Brisbane'))
        rrp = -31.99
        actual = convert(interval_datetime, 'ERTOUET1', rrp=rrp)
        self.assertAlmostEqual(actual, -2.675, places=2)
        # 18:30 RRP $-31.99/MWh
        interval_datetime = datetime(2025, 4, 5, 18, 30, tzinfo=ZoneInfo('Australia/Brisbane'))
        rrp = 31.99
        actual = convert(interval_datetime, 'ERTOUET1', rrp=rrp)
        self.assertAlmostEqual(actual, 21.76, places=2)

    def test_WRTOUET1_tariff(self):
        # 13:00 27.25c/kWh v -3.66c/kWh for RRP $-31.99/MWh
        interval_datetime = datetime(2025, 4, 5, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        self.assertAlmostEqual(convert(interval_datetime, 'WRTOUET1', -31.99), -2.675, places=2)
    
    def test_MRTOUET4_tariff(self):
        # 13:00 27.25c/kWh v -3.66c/kWh for RRP $-31.99/MWh
        interval_datetime = datetime(2025, 4, 5, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        self.assertAlmostEqual(convert(interval_datetime, 'MRTOUET4', -31.99), -2.675, places=2)
    