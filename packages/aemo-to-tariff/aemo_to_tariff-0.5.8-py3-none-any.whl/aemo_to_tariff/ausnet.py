# aemo_to_tariff/ausnet.py

from datetime import time, datetime
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/Melbourne'

# Example tariff: NAST11S (Small residential time‑of‑use with standard feed‑in)
tariffs = {
    'NAST11S': {
        'name': 'Small Business Time of Use',
        'periods': [
            ('Peak', time(15, 0), time(21, 0), 5.5+22.4055),
            ('Off-Peak', time(0, 0), time(15, 0), 14.6394),
            ('Off-Peak', time(21, 0), time(0, 0), 14.6394)
        ]
    }
}

# Optional daily fees if available
daily_fees = {
    'NAST11S': 3.00  # You can update this based on AER data
}

# Optional demand charges if needed
demand_charges = {
    # 'NAST11D': 30.00  # Example if a demand-based tariff exists
}

def get_periods(tariff_code: str):
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return tariff['periods']

def convert(interval_datetime: datetime, tariff_code: str, rrp: float) -> float:
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10.0  # Convert $/MWh to c/kWh

    tariff = tariffs.get(tariff_code)
    if not tariff:
        return rrp_c_kwh * 1.0 + 5.0  # fallback approximation

    for period_name, start, end, rate in tariff['periods']:
        if start < end and start <= interval_time < end:
            return rrp_c_kwh + rate
        elif start > end and (interval_time >= start or interval_time < end):  # overnight window
            return rrp_c_kwh + rate

    return rrp_c_kwh + tariff['periods'][0][3]

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float) -> float:
    return rrp / 10.0  # Simple passthrough unless AusNet has special FiT windows

def get_daily_fee(tariff_code: str, annual_usage: float = None) -> float:
    return daily_fees.get(tariff_code, 0.0)

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30) -> float:
    if tariff_code not in demand_charges:
        return 0.0
    rate = demand_charges[tariff_code] / 30  # Convert monthly rate to daily
    return rate * demand_kw * days
