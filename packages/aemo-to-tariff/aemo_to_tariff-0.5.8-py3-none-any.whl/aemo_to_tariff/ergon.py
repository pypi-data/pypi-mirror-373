# aemo_to_tariff/ergon.py
from datetime import time, datetime
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/Brisbane'

def battery_tariff(customer_type: str):
    """
    Get the battery tariff for a given customer type.

    Parameters:
    - customer_type (str): The customer type ('Residential' or 'Business').

    Returns:
    - str: The battery tariff code.
    """
    if customer_type == 'Residential':
        return 'ERTOUET1'
    elif customer_type == 'Business':
        return 'EBTOUET1'
    else:
        raise ValueError("Invalid customer type. Must be 'Residential' or 'Business'.")

daily_fees = {
    'ERTOUET1': 1.808,
    'WRTOUET1': 7.210,
    'MRTOUET4': 1.698,
    'EBTOUET1': 3.337,
    'WBTOUET1': 13.675,
    'MBTOUET4': 3.149,
}

tariffs = {
    'ERTOUET1': {
        'name': 'Residential Battery ToU',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.524),
            ('Peak', time(16, 0), time(21, 0), 18.564),
            ('Shoulder', time(21, 0), time(11, 0), 4.065)
        ],
        'rate': {'Off-Peak': 0.524, 'Peak': 18.564, 'Shoulder': 4.065}
    },
    'WRTOUET1': {
        'name': 'Residential Wide ToU',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.524),
            ('Peak', time(16, 0), time(21, 0), 18.564),
            ('Shoulder', time(21, 0), time(11, 0), 4.065)
        ],
        'rate': {'Off-Peak': 0.524, 'Peak': 18.564, 'Shoulder': 4.065}
    },
    'MRTOUET4': {
        'name': 'Residential Multi ToU',
        'periods': [
            ('Off-Peak', time(11, 0), time(16, 0), 0.524),
            ('Peak', time(16, 0), time(21, 0), 0.17671),
            ('Shoulder', time(21, 0), time(11, 0), 0.03172)
        ],
        'rate': {'Off-Peak': 0.524, 'Peak': 0.17671, 'Shoulder': 0.03172}
    },
    '6900': {
        'name': 'Residential Time of Use Energy',
        'periods': [
            ('Evening', time(16, 0), time(21, 0), 19.367),
            ('Overnight', time(21, 0), time(11, 0), 4.868),
            ('Day', time(11, 0), time(16, 0), 0.00476)
        ],
        'rate': {'Evening': 19.367, 'Overnight': 4.868, 'Day': 0.00476}
    },
}

# Add this to your existing code

demand_charges = {
    '3700': { 'Peak': 8.998},  # Residential Demand
    '3900': { 'Peak': 5.127},  # Residential Transitional Demand
    '3600': { 'Peak': 10.289},  # Small Business Demand
    '3800': { 'Peak': 4.975},  # Small Business Transitional Demand
    '7200': {
        'Off-Peak': 0.000,    # 11:00 to 13:00
        'Peak': 14.919,       # 17:00 to 20:00
        'Shoulder': 3.333     # Other times
    },
    '8100': 15.773,  # Demand Large
    '8300': 15.704,  # Demand Small
}

def translate_tariff(tariff_code: str):
    """
    Translate a tariff code to its canonical form for lookup.

    Parameters:
    - tariff_code (str): The input tariff code.

    Returns:
    - str: The canonical tariff code for lookup.
    """
    code = str(tariff_code)
    if len(code) == 4:
        prefix = code[:2]
        return prefix + '00'
    return code

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30, tou='peak'):
    """
    Calculate the demand fee for a given tariff code, demand amount, and time period.

    Parameters:
    - tariff_code (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for 8100 and 8300 tariffs).
    - days (int): The number of days for the billing period (default is 30).

    Returns:
    - float: The demand fee in dollars.
    """
    tariff_code = translate_tariff(str(tariff_code))

    if tariff_code not in demand_charges:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge

    charge = demand_charges[tariff_code]
    if isinstance(charge, dict):
        charge_per_kw_per_month = charge.get(tou, 0.0)
    else:
        charge_per_kw_per_month = charge

    # Convert the charge to a daily rate and then calculate for the given number of days
    daily_rate = charge_per_kw_per_month / 30
    total_charge = demand_kw * daily_rate * days

    return total_charge

def get_daily_fee(tariff_code: str, annual_usage: float = None):
    """
    Calculate the daily fee for a given tariff code.

    Parameters:
    - tariff_code (str): The tariff code.
    - annual_usage (float): Annual usage in kWh, required for Wide IFT and ToU Energy tariffs.

    Returns:
    - float: The daily fee in dollars.
    """
    tariff_code = translate_tariff(str(tariff_code))
    fee = daily_fees.get(tariff_code)

    if isinstance(fee, dict):
        if annual_usage is None:
            raise ValueError("Annual usage is required for this tariff.")

        if annual_usage <= 20000:
            return fee['band1']
        elif annual_usage <= 40000:
            return fee['band2']
        elif annual_usage <= 60000:
            return fee['band3']
        elif annual_usage <= 80000:
            return fee['band4']
        else:
            return fee['band5']

    return fee


def get_periods(tariff_code: str):
    tariff_code = translate_tariff(str(tariff_code))
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
    Convert RRP from $/MWh to c/kWh for Ergon.

    Parameters:
    - interval_time (str): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10

    tariff = tariffs.get(tariff_code)

    if not tariff:
        # Handle unknown tariff codes
        slope = 1.037869032618134
        intercept = 5.586606750833143
        return rrp_c_kwh * slope + intercept

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            total_price = rrp_c_kwh + rate
            return total_price

    # If no period is found, use the default rate
    if isinstance(tariff['rate'], dict):
        # For Time-of-Use tariffs, use the first rate as default
        rate = list(tariff['rate'].values())[0]
    else:
        rate = tariff['rate']

    return rrp_c_kwh + rate
