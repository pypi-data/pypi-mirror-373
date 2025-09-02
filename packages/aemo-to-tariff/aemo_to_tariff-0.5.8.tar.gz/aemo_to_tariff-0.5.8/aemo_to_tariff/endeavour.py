from datetime import time, datetime
from zoneinfo import ZoneInfo


def time_zone():
    return 'Australia/Sydney'

def battery_tariff(customer_type: str):
    """
    Get the battery tariff for a given customer type.

    Parameters:
    - customer_type (str): The customer type ('Residential' or 'Business').

    Returns:
    - str: The battery tariff code.
    """
    if customer_type == 'Residential':
        return 'N71'
    elif customer_type == 'Business':
        return 'N91'
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")


tariffs = {
    'N70': {
        'name': 'Residential Flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.96)
        ]
    },
    'N71': {
        'name': 'Residential Seasonal TOU',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 21.7964),
            ('Low-season Peak', time(16, 0), time(20, 0),  13.8419),
            ('Solar Soak', time(10, 0), time(14, 0), 3.4252),
            ('Off Peak', time(0, 0), time(10, 0), 10.4931),
            ('Off Peak', time(14, 0), time(16, 0), 10.4931),
            ('Off Peak', time(20, 0), time(23, 59), 10.4931)
        ],
        'fixed_daily_charge': 55.5325,
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    },
    'N90': {
        'name': 'General Supply Block',
        'periods': [
            ('Block 1', time(0, 0), time(23, 59), 11.46),
            ('Block 2', time(0, 0), time(23, 59), 13.39)
        ]
    },
    'N91': {
        'name': 'GS Seasonal TOU',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 23.5007),
            ('Low-season Peak', time(16, 0), time(20, 0), 15.5462),
            ('Solar Soak', time(10, 0), time(14, 0), 4.1635),
            ('Off Peak', time(0, 0), time(10, 0), 12.1974),
            ('Off Peak', time(14, 0), time(16, 0), 12.1974),
            ('Off Peak', time(20, 0), time(23, 59), 12.1974)
        ],
        'fixed_daily_charge': 78.0125,
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    },
    'N19': {
        'name': 'LV Seasonal STOU Demand',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 5.4400),
            ('Low-season Peak', time(16, 0), time(20, 0), 4.8861),
            ('Off Peak', time(0, 0), time(10, 0), 3.6458),
            ('Off Peak', time(14, 0), time(16, 0), 3.6458),
            ('Off Peak', time(20, 0), time(23, 59), 3.6458)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    }
}

feed_in_tariffs = {
    'N61': {
        'name': 'Residential Electrify',
        'periods': [
            ('High-season Peak', time(16, 0), time(20, 0), 11.3033),
            ('Low-season Peak', time(16, 0), time(20, 0), 3.3488),
            ('Off Peak', time(0, 0), time(10, 0), -1.7900)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    }
}

def calculate_daily_fee(tariff_code: str):
    """
    Calculate the daily fee for a given tariff.

    Parameters:
    - tariff_code (str): The tariff code.

    Returns:
    - float: The daily fee in dollars.
    """
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return 39.7300

def calculate_demand_fee(tariff: str, demand_kw: float, days=30):
    """
    Calculate the demand fee for a given tariff, demand amount, and time period.

    Parameters:
    - tariff (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for some tariffs).
    - days (int): The number of days for the billing period (default is 30).

    Returns:
    - float: The demand fee in dollars.
    """
    tariff = tariffs[tariff]

    # Find the applicable rate
    for period, start, end, rate in tariff['periods']:
        if start <= demand_kw < end:
            return rate * days

    raise ValueError(f"Unknown demand amount: {demand_kw}")

def get_periods(tariff_code: str):
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for SA Power Networks.

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    rrp_c_kwh = rrp / 10
    
    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for endeavour.

    Parameters:
    - interval_datetime (datetime): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    tariff = tariffs[tariff_code]

    # Determine if it's high season (November to March) or low season (April to October)
    current_month = interval_datetime.month
    is_high_season = current_month in [11, 12, 1, 2, 3]

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end:
            if 'season' in tariff['name'].lower():
                if is_high_season and 'high' in period.lower():
                    total_price = rrp_c_kwh + rate
                    return total_price
                elif 'low' in period.lower() and not is_high_season:
                    total_price = rrp_c_kwh + rate
                    return total_price
                elif 'off' in period.lower():
                    total_price = rrp_c_kwh + rate
                    return total_price
                else:
                    continue
            else:
                total_price = rrp_c_kwh + rate
                return total_price

    # Otherwise, this terrible approximation
    slope = 1.037869032618134
    intecept = 5.586606750833143
    return rrp_c_kwh * slope + intecept
