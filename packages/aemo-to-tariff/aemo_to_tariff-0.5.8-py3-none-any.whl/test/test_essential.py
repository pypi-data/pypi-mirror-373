import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
import aemo_to_tariff.essential as essential

class TestEssentualPower(unittest.TestCase):
    def test_some_essential_functionality(self):
        interval_time = datetime(2025, 2, 20, 9, 10, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLNT3AL'
        rrp = -100.0
        expected_price = 3.858878319999999
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.168, expected_price, places=1)

    def test_seven_pm(self):
        # 2025-05-12 19:25:00+10
        interval_time = datetime(2025, 5, 12, 19, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 135.36
        expected_price = 37.60955297
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.68, expected_price, places=1)

    def test_seven_am(self):
        # 2025-05-12 07:25:00+10
        interval_time = datetime(2025, 5, 12, 7, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 153.88
        expected_price = 34.06917696
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.6, expected_price, places=1)

    def test_four_am(self):
        # 2025-05-10 04:15:00+10
        interval_time = datetime(2025, 5, 20, 4, 15, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = 67.73
        expected_price = 15.23709699
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.48, expected_price, places=1)

    def test_later_day(self):
        # 2025-05-10 12:25:00+10
        interval_time = datetime(2025, 5, 20, 12, 25, tzinfo=ZoneInfo('Australia/Sydney'))
        tariff_code = 'BLND1AR'
        rrp = -16.13
        expected_price = 6.21313241
        price = essential.convert(interval_time, tariff_code, rrp)
        loss_factor = expected_price / price
        self.assertAlmostEqual(price * 1.447, expected_price, places=1)
