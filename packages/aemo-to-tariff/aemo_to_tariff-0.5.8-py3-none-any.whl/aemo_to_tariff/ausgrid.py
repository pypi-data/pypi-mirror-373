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
        return 'EA025'
    elif customer_type == 'Business':
        return 'EA225'
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")

tariffs = {
    'EA010': {
        'name': 'Residential flat',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.8007)
        ]
    },
    'EA025': {
        'name': 'Residential ToU',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 29.2450),
            ('Off-peak', time(21, 0), time(15, 0), 5.1535)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    },
    'EA111': {
        'name': 'Residential demand (introductory)',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 10.7805)
        ]
    },
    'EA116': {
        'name': 'Residential demand',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 2.3370)
        ]
    },
    'EA225': {
        'name': 'Small Business ToU',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 34.8921),
            ('Off-peak', time(21, 0), time(15, 0), 5.7619)
        ],
        'peak_months': [11, 12, 1, 2, 3, 6, 7, 8]  # November–March and June–August
    },
    'EA305': {
        'name': 'Small Business LV',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 7.3723),
            ('Off-Peak', time(21, 0), time(14, 59), 1.6800)
        ]
    }
}

demand_tariffs = {
    'EA116': {
        'name': 'Residential Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 33.2942),  # ¢/kW/day
        ]
    },
    'EA305': {
        'name': 'Small Business LV Demand',
        'periods': [
            ('Peak', time(15, 0), time(22, 59), 49.4399),  # ¢/kW/day
        ]
    }
}

daily_fixed_charges = {
    'EA010': 47,
    'EA025': 57,
    'EA111': 51,
    'EA116': 60,
    'EA225': 184,
    'EA305': 2047.0434
}

def get_periods(tariff_code: str):
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    rrp_c_kwh = rrp / 10
    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    tariff = tariffs.get(tariff_code)

    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    current_month = interval_datetime.month

    # Determine if current month is within peak months
    is_peak_month = current_month in tariff.get('peak_months', [])

    for period_name, start, end, rate in tariff['periods']:
        if period_name == 'Peak' and not is_peak_month:
            continue  # Skip peak period if not in peak months

        if start <= end:
            if start <= interval_time < end:
                return rrp_c_kwh + rate
        else:
            # Over midnight
            if interval_time >= start or interval_time < end:
                return rrp_c_kwh + rate

    # If no period matches, apply default approximation
    slope = 1.037869032618134
    intercept = 5.586606750833143
    return rrp_c_kwh * slope + intercept

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30):
    """
    Calculate the demand fee for a given tariff code, demand amount, and time period.

    Parameters:
    - tariff_code (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for 8100 and 8300 tariffs).
    - days (int): The number of days for the billing period (default is 30).

    Returns:
    - float: The demand fee in dollars.
    """
    tariff = demand_tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    fee = 0.0
    for period_name, start, end, rate in tariff['periods']:
        if period_name == 'Peak':
            fee += rate * demand_kw * days / 100  # Convert ¢/kW/day to $/kW/day

    return fee

def get_daily_fee(tariff_code: str, annual_usage: float = None):
    """
    Calculate the daily fee for a given tariff code.

    Parameters:
    - tariff_code (str): The tariff code.
    - annual_usage (float): Annual usage in kWh, required for Wide IFT and ToU Energy tariffs.

    Returns:
    - float: The daily fee in dollars.
    """
    fee = daily_fixed_charges.get(tariff_code)
    if fee is None:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return fee / 100  # Convert ¢ to $ for daily fixed charge
