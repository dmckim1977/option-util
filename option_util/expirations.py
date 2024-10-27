import re
from datetime import datetime, timedelta
from enum import Enum
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
from typing import List, Optional

from dateutil.relativedelta import FR, relativedelta


class SecurityType(Enum):
    EQUITY = "equity"
    FUTURE = "future"
    VOLATILITY = "volatility"

def get_previous_business_day(date_str):
    # Convert input string to datetime object
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Create a custom business day object that excludes weekends and US federal holidays
    us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())

    # Subtract one business day
    previous_business_day = date - us_bd

    # Convert back to string format
    return previous_business_day.strftime("%Y-%m-%d")


def get_next_expiration(
        security_type: SecurityType,
        from_date: Optional[datetime] = None,
        return_format: None | str = None,
) -> datetime | str:
    """
    Get the next expiration date based on the security type.

    Args:
        security_type (SecurityType): The type of security (EQUITY, FUTURE, or VOLATILITY).
        from_date (Optional[datetime]): The starting date. If None, uses the current date.
        return_format (None | str): The format string is used to format the date or return a datetime if None.
            Example of inputs, "%Y-%m-%d" or "%Y%m%d"

    Returns:
        datetime | str: The next expiration date.

    Raises:
        NotImplementedError: If the security type is not yet implemented.
        ValueError: If an invalid security type is provided.
    """

    if security_type == SecurityType.EQUITY.value:
        exp = get_next_friday(from_date)
    elif security_type == SecurityType.FUTURE.value:
        exp = get_next_trading_day(from_date)
    elif security_type == SecurityType.VOLATILITY.value:
        raise NotImplementedError("Volatility products are not yet implemented.")
    else:
        raise ValueError(f"Invalid security type: {security_type}")

    if return_format:
        try:
            return exp.strftime(return_format)
        except Exception as e:
            print(f'Error get_next_expiration: {e}')
    else:
        return exp


def get_next_trading_day(from_date: Optional[datetime] = None) -> datetime:
    """Get the next trading day from the given date."""

    next_day = from_date + timedelta(days=1)
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += timedelta(days=1)
    return next_day


def get_next_friday(from_date: Optional[datetime] = None) -> datetime:
    """Get the date of the next Friday from the given date."""

    days_ahead = 4 - from_date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return from_date + timedelta(days=days_ahead)


def get_next_monthly_expiration(from_date: Optional[datetime] = None) -> datetime:
    """Get the date of the next monthly options expiration (third Friday of the month)."""

    third_friday = from_date.replace(day=1) + relativedelta(weekday=FR(3))
    if from_date >= third_friday:
        third_friday = from_date.replace(day=1) + relativedelta(months=1, weekday=FR(3))
    return third_friday


def get_next_quarter_end(from_date: Optional[datetime] = None) -> datetime:
    """Get the last Friday of the last month in the current quarter."""

    quarter_month = ((from_date.month - 1) // 3) * 3 + 3
    quarter_end = from_date.replace(month=quarter_month, day=1) + relativedelta(months=1, days=-1)
    last_friday = quarter_end + relativedelta(weekday=FR(-1))

    if from_date > last_friday or (from_date.date() == last_friday.date() and from_date.time() >= last_friday.time()):
        next_quarter_end = quarter_end + relativedelta(months=3)
        last_friday = next_quarter_end + relativedelta(weekday=FR(-1))

    return last_friday


def get_next_quarter_third_friday(from_date: Optional[datetime] = None) -> datetime:
    """Get the third Friday of the last month of the current quarter."""

    quarter_month = ((from_date.month - 1) // 3) * 3 + 3
    third_friday = from_date.replace(month=quarter_month, day=1) + relativedelta(weekday=FR(3))

    if from_date >= third_friday:
        next_quarter_month = (quarter_month % 12) + 3
        next_quarter_year = from_date.year + (1 if next_quarter_month < quarter_month else 0)
        third_friday = datetime(next_quarter_year, next_quarter_month, 1) + relativedelta(weekday=FR(3))

    return third_friday


def get_future_expirations(from_date: Optional[datetime] = None) -> List[datetime]:
    """Get a list of future options expiration dates."""

    return [
        get_next_trading_day(from_date),
        get_next_friday(from_date),
        get_next_monthly_expiration(from_date),
        get_next_quarter_third_friday(from_date),
        get_next_quarter_end(from_date)
    ]


def parse_contract_symbol(symbol: str) -> float:
    """
    Parse the contract symbol to extract the strike price.

    Args:
        symbol (str): The contract symbol string.

    Returns:
        float: The strike price extracted from the symbol.
    """
    pattern = r'([\w ]{6})((\d{2})(\d{2})(\d{2}))([PC])(\d{8})'
    match = re.match(pattern, symbol)
    if match:
        return float(match.group(7)) / 1000  # Divide by 1000 to get the correct strike price
    return float('nan')
