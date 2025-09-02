# aemo_to_tariff/essential.py
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
        return 'BLNT3AL'
    elif customer_type == 'Business':
        return 'BLNT2AL'

# BLNREX2 is a feed-in tariff, not a TOU tariff. -11.5725 - 0.8172
feed_in_tariffs = {
    'BLNREX2': {
        'name': 'LV Residential Solar Export',
        'periods': [
            ('Peak', time(16, 0), time(20, 0), 11.5725),
            ('Off Peak', time(0, 0), time(10, 0), -0.8172)
        ]
    }
}

tariffs = {
    # ------------------------------
    # Residential Anytime (Flat)
    # ------------------------------
    'BLNN2AU': {
        'name': 'LV Residential Anytime',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 12.6808),  # c/kWh
        ]
    },

    # ---------------------------------------------------
    # LV Residential TOU (Basic Meter) - Legacy
    # Peak windows: 7–9am, 5–8pm; Shoulder: 9am–5pm, 8–10pm; Off-peak: 10pm–7am
    # ---------------------------------------------------
    'BLNT3AU': {
        'name': 'LV Residential TOU (Basic Meter)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 17.7676),
            ('Shoulder', time(9, 0), time(17, 0), 13.8149),
            ('Peak', time(17, 0), time(20, 0), 17.7676),
            ('Shoulder', time(20, 0), time(22, 0), 13.8149),
            ('Off-Peak', time(22, 0), time(7, 0), 5.4026),
        ]
    },

    # -----------------------------------------------------
    # LV Residential TOU (Interval Meter) - Legacy
    # Peak: 5–8pm; Shoulder: 7am–5pm, 8–10pm; Off-peak: 10pm–7am
    # -----------------------------------------------------
    'BLNT3AL': {
        'name': 'LV Residential TOU (Interval Meter)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 13.3044),
            ('Peak', time(17, 0), time(20, 0), 18.4298),
            ('Shoulder', time(20, 0), time(22, 0), 13.3044),
            ('Off-Peak', time(22, 0), time(7, 0), 5.4026),
        ]
    },

    # ------------------------------------------------------
    # LV Residential TOU – Sun Soaker
    # Peak: 3–10pm weekdays; Off-Peak: all other times
    # (No shoulder in this simpler design)
    # ------------------------------------------------------
    'BLNRSS2': {
        'name': 'LV Residential Sun Soaker',
        'periods': [
            ('Peak', time(15, 0), time(22, 0), 15.8671),
            ('Off-Peak', time(22, 0), time(15, 0), 5.4026),
        ]
    },

    # ------------------------------------------------------
    # LV Residential Demand (Opt-in)
    # Usage rates: Peak 8.8434, Shoulder 5.9050, Off-Peak 3.5188
    # Peak window: 5–8pm
    # ------------------------------------------------------
    'BLND1AR': {
        'name': 'LV Residential Demand',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 5.9050),
            ('Peak', time(17, 0), time(20, 0), 8.8434),
            ('Shoulder', time(20, 0), time(22, 0), 5.9050),
            ('Off-Peak', time(22, 0), time(7, 0), 3.5188),
        ]
    },

    # ------------------------------------------------------
    # Controlled Load 1 (restricted ~5–9 hours supply)
    # ------------------------------------------------------
    'BLNC1AU': {
        'name': 'Controlled Load 1',
        'periods': [
            ('Controlled Load 1', time(0, 0), time(23, 59), 2.7130),
        ]
    },

    # ------------------------------------------------------
    # Controlled Load 2 (restricted ~10–19 hours supply)
    # ------------------------------------------------------
    'BLNC2AU': {
        'name': 'Controlled Load 2',
        'periods': [
            ('Controlled Load 2', time(0, 0), time(23, 59), 5.7748),
        ]
    },

    # -------------------------------
    # Small Business Anytime (Flat)
    # -------------------------------
    'BLNN1AU': {
        'name': 'LV Small Business Anytime',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 17.4231),
        ]
    },

    # --------------------------------------------------------
    # LV Small Business TOU (Basic Meter) - Legacy
    # Peak: 7–9am, 5–8pm; Shoulder: 9am–5pm, 8–10pm; Off-Peak: 10pm–7am
    # --------------------------------------------------------
    'BLNT2AU': {
        'name': 'LV Small Business TOU (Basic Meter)',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 18.8112),
            ('Shoulder', time(9, 0), time(17, 0), 14.7236),
            ('Peak', time(17, 0), time(20, 0), 18.8112),
            ('Shoulder', time(20, 0), time(22, 0), 14.7236),
            ('Off-Peak', time(22, 0), time(7, 0), 7.8256),
        ]
    },

    # --------------------------------------------------------
    # LV Small Business TOU (Interval Meter) - Legacy
    # Peak: 5–8pm; Shoulder: 7am–5pm, 8–10pm; Off-Peak: 10pm–7am
    # --------------------------------------------------------
    'BLNT2AL': {
        'name': 'LV Small Business TOU (Interval Meter)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 14.1904),
            ('Peak', time(17, 0), time(20, 0), 19.5029),
            ('Shoulder', time(20, 0), time(22, 0), 14.1904),
            ('Off-Peak', time(22, 0), time(7, 0), 7.5707),
        ]
    },

    # --------------------------------------------------------
    # LV Small Business TOU (100–160 MWh) - Legacy
    # Peak: 5–8pm; Shoulder: 7am–5pm, 8–10pm; Off-Peak: 10pm–7am
    # --------------------------------------------------------
    'BLNT1AO': {
        'name': 'LV Small Business TOU (100–160 MWh)',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 14.7236),
            ('Peak', time(17, 0), time(20, 0), 18.8112),
            ('Shoulder', time(20, 0), time(22, 0), 14.7236),
            ('Off-Peak', time(22, 0), time(7, 0), 7.8256),
        ]
    },

    # ------------------------------------------------------
    # LV Small Business TOU – Sun Soaker
    # Peak: 3–10pm; Off-Peak: all other times
    # ------------------------------------------------------
    'BLNBSS1': {
        'name': 'LV Small Business Sun Soaker',
        'periods': [
            ('Peak', time(15, 0), time(22, 0), 16.8466),
            ('Off-Peak', time(22, 0), time(15, 0), 7.5707),
        ]
    },

    # ------------------------------------------------------
    # LV Small Business Demand (Opt-in)
    # Usage Rates: Peak 12.3583, Shoulder 8.6714, Off-Peak 5.1286
    # ------------------------------------------------------
    'BLND1AB': {
        'name': 'LV Small Business Demand',
        'periods': [
            ('Shoulder', time(7, 0), time(17, 0), 8.6714),
            ('Peak', time(17, 0), time(20, 0), 12.3583),
            ('Shoulder', time(20, 0), time(22, 0), 8.6714),
            ('Off-Peak', time(22, 0), time(7, 0), 5.1286),
        ]
    },
# ------------------------------
    # LV Residential ToU - Sun Soaker 
    # ------------------------------
    'BLNRSS2': {
        'name': 'LV Residential ToU - Sun Soaker',
        'periods': [
            ('Peak', time(7, 0), time(9, 0), 16.9522),\
            ('Off-Peak', time(22, 0), time(7, 0), 5.8530),
        ]
    },

    # -----------------------------------------------------
    # BLNBSS1 LV Small Business ToU - Sun Soaker 
    # Peak: 5–8pm; Shoulder: 7am–5pm, 8–10pm; Off-peak: 10pm–7am
    # -----------------------------------------------------
    'BLNBSS1': {
        'name': 'LV Small Business TOU - Sun Soaker',
        'periods': [
            ('Peak', time(17, 0), time(20, 0), 17.9646),
            ('Off-Peak', time(22, 0), time(7, 0), 8.1015),
        ]
    },

}


def get_periods(tariff_code: str):
    """
    Retrieve the list of TOU periods for the given tariff code.
    Each period is (period_name, start_time, end_time, rate_cents_kwh).
    """
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
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    tariff = tariffs[tariff_code]
    if tariff_code in feed_in_tariffs:
        tariff = feed_in_tariffs[tariff_code]
        for period, start, end, rate in tariff['periods']:
            if start <= interval_time < end:
                total_price = rrp_c_kwh + rate
                return total_price
    return rrp_c_kwh  # Fallback if no specific feed-in tariff found

# Daily fees in dollars per day
daily_fees = {
    'BLNN2AU': 1.2788,
    'BLNT3AU': 1.2788,
    'BLNT3AL': 1.2788,
    'BLNRSS2': 1.2788,
    'BLND1AR': 1.2788,
    'BLNC1AU': 0.1148,
    'BLNC2AU': 0.1148,
    'BLNN1AU': 2.0579,
    'BLNT2AU': 2.0579,
    'BLNT2AL': 2.0579,
    'BLNT1AO': 2.0579,
    'BLNBSS1': 2.0579,
    'BLND1AB': 2.0579,
}

# Demand charges in dollars per kW per day (approx. conversions from $/kVA/month)
demand_charges = {
    'BLND1AR': 0.16,  # ~4.77 $/kVA/month => ~$0.16 /kW/day
    'BLND1AB': 0.30,  # ~8.92 $/kVA/month => ~$0.30 /kW/day
}

def get_periods(tariff_code: str):
    """
    Retrieve the list of TOU periods for the given tariff code.
    Each period is (period_name, start_time, end_time, rate_cents_kwh).
    """
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

def convert(interval_datetime: datetime, tariff_code: str, rrp: float) -> float:
    """
    Convert RRP from $/MWh to c/kWh for an Essential Energy tariff.

    Parameters:
    - interval_datetime (datetime): The interval datetime in UTC or any tz.
    - tariff_code (str): The tariff code (e.g. 'BLNT3AL', 'BLNRSS2').
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The total price in c/kWh.
    """
    # Convert interval time to Australia/Sydney
    local_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10.0  # $/MWh => c/kWh

    tariff = tariffs.get(tariff_code)
    if not tariff:
        # Fallback if unknown tariff code
        slope = 1.037869032618134
        intercept = 5.586606750833143
        return rrp_c_kwh * slope + intercept

    # Match the period whose start-end covers local_time
    for period_name, start, end, rate_cents in tariff['periods']:
        # Handle normal range if start < end
        if start < end:
            if start <= local_time < end:
                return rrp_c_kwh + rate_cents
        else:
            # Period crosses midnight
            if local_time >= start or local_time < end:
                return rrp_c_kwh + rate_cents

    # Default to first period’s rate if none matched
    return rrp_c_kwh + tariff['periods'][0][3]

def get_daily_fee(tariff_code: str) -> float:
    """
    Get the daily fixed fee for the given tariff code (in dollars per day).
    """
    return daily_fees.get(tariff_code, 0.0)

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30) -> float:
    """
    Calculate the demand charge for a given tariff code, maximum demand (kW), and billing period (days).

    Returns:
    - float: The demand fee in dollars (i.e. demand_charge $/kW/day * demand_kw * days).
    """
    daily_charge = demand_charges.get(tariff_code, 0.0)
    return daily_charge * demand_kw * days
