option-util
========

**option-util** is a simple library to make simple scripts easily available for working with options.

Examples
========

Return the next expiration by type of expiration.
-------------------------------------------------

- The available options are `friday`, `third_friday`, `quarter_end`, `next_bus_day`, `wednesday`, `quarter_third_friday`.::


    >>> # Return the next expiration by type.
    >>> next_exp_by_type = expirations.next_expiration(
    ...    expiration_type='friday', from_date=datetime(2024,10,27)
    ...    )
    >>> print(f'Next Expiration by Type: {next_exp_by_type}')
    Next Expiration by Type: 2024-11-01


### Return the next expiration by all types.::


    >>> # Get future expirations
    >>> all_expirations = expirations.future_expirations(
    ...    from_date=datetime(2024, 10, 27)
    ...)
    >>> print(f'Future expirations: {all_expirations}')

    Future expirations: {'from_date': datetime.date(2024, 10, 27), 'previous_business_day': datetime.date(2024, 10, 25), 'next_business_day': datetime.date(2024, 10, 28), 'next_friday': datetime.date(2024, 11, 1), 'next_quarter_end': datetime.date(2024, 12, 27), 'next_monthly_expiration': datetime.date(2024, 11, 15), 'next_quarter_third_friday': datetime.date(2024, 12, 20)}



Features
--------

- Easy access to common scripts

Installation
------------

Install option-util by running::


    pip install option-util



Support
-------

Let us know if you have issues.

License
-------

The project is licensed under the BSD license.