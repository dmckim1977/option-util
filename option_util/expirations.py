import re
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional

from dateutil.relativedelta import FR, relativedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

ExpirationType = Literal[
    'friday', 'third_friday', 'quarter_end', 'next_bus_day', 'wednesday',
    'quarter_third_friday',
]


def previous_business_day(date: datetime) -> datetime.date:
    """Uses pandas calendars to get the previous business day.

    `date` can be any day of the week including weekends.
    US Federal holidays are excluded from the results.

    :param date: The day to start from.
        YYYY-MM-DD format.
    :return: datetime

    :Example:

    >>> # Get the previous business day from date
    >>> prev_bus_day = expirations.previous_business_day(
    >>> date=datetime(2024, 10, 27)) # Sunday
    >>> print(prev_bus_day) # Previous bus day is Friday

    Next business day: 2024-10-25

    """

    # Custom business day object that excludes weekends and US federal holidays
    us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())

    # Subtract one business day
    previous_business_day = date - us_bd

    # Convert back to string format
    return previous_business_day.date()


def next_expiration(
        expiration_type: ExpirationType,
        from_date: Optional[datetime] = None,
) -> datetime.date:
    """Get the next expiration date based on the expiration type.

    :param expiration_type: When the option will expire.
        options: 'friday', 'third_friday', 'quarterly', 'next_bus_day',
        'wednesday'
    :param from_date: The date to make the calculation from.
    :return: datetime.date

    :Example:

    >>> # Return the next expiration by type.
    >>> next_exp_by_type = expirations.next_expiration(
    ...    expiration_type='friday', from_date=datetime(2024,10,27)
    ...    )
    >>> print(f'Next Expiration by Type: {next_exp_by_type}')
    Next Expiration by Type: 2024-11-01

    :raises:
        NotImplementedError: If the expiration type is not yet implemented.
        ValueError: If an invalid expiration type is provided.

    """

    """
    Get the next expiration date based on the security type.

    Args:
        security_type (SecurityType): The type of security (EQUITY, FUTURE,
            or VOLATILITY).
        from_date (Optional[datetime]): The starting date.
            If None, uses the current date.
        return_format (None | str): The format string is used to format the
            date or return a datetime if None.
            Example of inputs, "%Y-%m-%d" or "%Y%m%d"

    Returns:
        datetime | str: The next expiration date.

    Raises:
        NotImplementedError: If the security type is not yet implemented.
        ValueError: If an invalid security type is provided.

    """

    if expiration_type == "friday":
        exp = next_friday(from_date)
    elif expiration_type == "next_bus_day":
        exp = next_business_day(from_date)
    elif expiration_type == "third_friday":
        exp = next_monthly_expiration(from_date)
    elif expiration_type == "quarter_end":
        exp = next_quarter_end(from_date)
    elif expiration_type == "quarter_third_friday":
        exp = next_quarter_third_friday(from_date)
    elif expiration_type == "wednesday":
        raise NotImplementedError("Wednesday expirations are not implemented "
                                  "yet.")
    else:
        raise ValueError(f"Invalid security type: {expiration_type}")

    return exp


def next_business_day(from_date: Optional[datetime] = None) -> datetime.date:
    """Get the next trading day from the given date."""

    next_day = from_date + timedelta(days=1)
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += timedelta(days=1)
    return next_day.date()


def next_friday(from_date: Optional[datetime] = None) -> datetime.date:
    """Get the date of the next Friday from the given date."""

    days_ahead = 4 - from_date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return (from_date + timedelta(days=days_ahead)).date()


def next_monthly_expiration(
        from_date: Optional[datetime] = None) -> datetime.date:
    """
    Get the date of the next monthly options expiration
    (third Friday of the month).

    """

    third_friday = from_date.replace(day=1) + relativedelta(weekday=FR(3))
    if from_date >= third_friday:
        third_friday = from_date.replace(day=1) + relativedelta(months=1,
                                                                weekday=FR(3))
    return third_friday.date()


def next_quarter_end(from_date: Optional[datetime] = None) -> datetime.date:
    """
    Get the last Friday of the last month in the current quarter.

    """

    quarter_month = ((from_date.month - 1) // 3) * 3 + 3
    quarter_end = from_date.replace(month=quarter_month,
                                    day=1) + relativedelta(months=1, days=-1)
    last_friday = quarter_end + relativedelta(weekday=FR(-1))

    if from_date > last_friday or (
            from_date.date() == last_friday.date() and
            from_date.time() >= last_friday.time()):
        next_quarter_end = quarter_end + relativedelta(months=3)
        last_friday = next_quarter_end + relativedelta(weekday=FR(-1))

    return last_friday.date()


def next_quarter_third_friday(
        from_date: Optional[datetime] = None) -> datetime.date:
    """Get the third Friday of the last month of the current quarter."""

    quarter_month = ((from_date.month - 1) // 3) * 3 + 3
    third_friday = from_date.replace(month=quarter_month,
                                     day=1) + relativedelta(weekday=FR(3))

    if from_date >= third_friday:
        next_quarter_month = (quarter_month % 12) + 3
        next_quarter_year = from_date.year + (
            1 if next_quarter_month < quarter_month else 0)
        third_friday = datetime(next_quarter_year, next_quarter_month,
                                1) + relativedelta(weekday=FR(3))

    return third_friday.date()


def future_expirations(from_date: Optional[datetime] = None
                       ) -> Dict[str, datetime]:
    """Get a list of future options expiration dates."""

    return {
        'from_date': from_date.date(),
        'previous_business_day': previous_business_day(from_date),
        'next_business_day': next_business_day(from_date),
        'next_friday': next_friday(from_date),
        'next_quarter_end': next_quarter_end(from_date),
        'next_monthly_expiration': next_monthly_expiration(from_date),
        'next_quarter_third_friday': next_quarter_third_friday(from_date)
    }



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
        return float(match.group(
            7)) / 1000  # Divide by 1000 to get the correct strike price
    return float('nan')
