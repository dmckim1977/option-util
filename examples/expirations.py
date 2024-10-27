"""
These examples illustrate some of the ways to get different expiration dates
from a known date. This can be used for past, present, and future expirations.

We have also included a couple functions for getting the previous and next
business dates to help with other calculations when querying APIs or databases.

"""

from datetime import datetime

from option_util import expirations


# Get the previous business day from date.
prev_bus_day = expirations.previous_business_day(
    date=datetime(2024,  10,  27))  # Sunday
print(f'Previous business day: {prev_bus_day}')  # Previous bus day is Friday


# Get the next business day from date.
next_bus_day = expirations.next_business_day(
    datetime(2024, 10, 27))
print("Next business day:", next_bus_day)


# Return the next Friday Expiration.
next_exp_by_type = expirations.next_expiration(
    expiration_type='friday', from_date=datetime(2024, 10, 27)
)
print(f'Next Friday: {next_exp_by_type}')


# Return the next third Friday expiration.
next_exp_by_type = expirations.next_expiration(
    expiration_type='third_friday',
    from_date=datetime(2024, 10, 27)
)
print(f'Next third Friday: {next_exp_by_type}')


# Return the next third Friday expiration.
next_exp_by_type = expirations.next_expiration(
    expiration_type='quarter_third_friday',
    from_date=datetime(2024, 10, 27)
)
print(f'Next Quarter third Friday: {next_exp_by_type}')


# Get future expirations
all_expirations = expirations.future_expirations(
    from_date=datetime(2024, 10, 27)
)
print(f'Future expirations: {all_expirations}')

