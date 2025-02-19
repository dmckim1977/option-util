"""Futures Contract Helper

This module is for working with futures contracts, expirations, and contract codes for various exchanges.

Example:


Todo:
    * Implement CBOT
    * Implement ICE
    * Implement EUREX

"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Literal, Union
import logging

# Module-level logger
logger = logging.getLogger(__name__)

# Define supported exchanges
ExchangeType = Literal["CME", "ICE", "EUREX"]


class ContractError(Exception):
    """Base exception for contract-related errors"""
    pass


class ExchangeNotSupported(ContractError):
    """Raised when exchange is not supported"""
    pass


class ContractRollover:
    """
    Manages futures contract code generation and rollover dates.
    """

    # Exchange month codes mapping
    _MONTH_CODES = {
        "CME": {
            3: 'H',  # March
            6: 'M',  # June
            9: 'U',  # September
            12: 'Z'  # December
        },
        "ICE": {
            3: 'H',
            6: 'M',
            9: 'U',
            12: 'Z'
        },
        "EUREX": {
            3: 'H',
            6: 'M',
            9: 'U',
            12: 'Z'
        }
    }

    def __init__(self, exchange: ExchangeType):
        """
        Initialize contract rollover for specific exchange.

        Args:
            exchange: Trading exchange ("CME", "ICE", "EUREX")

        Raises:
            ExchangeNotSupported: If exchange is not implemented
        """
        if exchange not in self._MONTH_CODES:
            raise ExchangeNotSupported(f"Exchange {exchange} is not supported")

        self.exchange = exchange
        logger.info(f"Initialized {exchange} contract rollover")

    def get_next_contract(self, symbol: str, reference_date: Optional[datetime] = None,
                          days_before: int = 7) -> Dict[str, Union[str, int]]:
        """
        Get next contract information based on reference date and rollover days.

        Determines whether to stay in current contract or roll to next based on
        expiry date and rollover period. Returns contract components as dictionary
        for flexible contract code formatting.

        Args:
            symbol: Contract symbol (e.g. 'ES', 'NQ')
            reference_date: Date to check against, defaults to current date
            days_before: Number of days before expiration to roll to next contract

        Returns:
            Dictionary containing contract components:
                - symbol (str): Contract symbol
                - month_code (str): Month code for contract (H, M, U, Z)
                - year (int): Contract year

        Examples:
            >>> rollover = ContractRollover("CME")
            >>> # March 1st, 2024
            >>> contract = rollover.get_next_contract("ES", datetime(2024, 3, 1))
            >>> print(contract)
            {'symbol': 'ES', 'month_code': 'H', 'year': 2024}
        """
        date = reference_date or datetime.now()
        current_quarter = self._get_contract_quarter(date)
        expiry = self._get_expiry_date(date.year, current_quarter)

        if date > (expiry - timedelta(days=days_before)):
            # Roll to next quarter
            if current_quarter == 12:
                next_quarter = 3
                year = date.year + 1
            else:
                next_quarter = current_quarter + 3
                year = date.year

            month_code = self._MONTH_CODES[self.exchange][next_quarter]
            return {
                "symbol": symbol,
                "month_code": month_code,
                "year": year,
            }

        # Stay in current quarter
        month_code = self._MONTH_CODES[self.exchange][current_quarter]

        return {
            "symbol": symbol,
            "month_code": month_code,
            "year": date.year,
        }

    def ironbeam_contract_format(self, contract: Dict[str, Union[str, int]] = None) -> str:
        """ Formats a contract dictionary to IronBeams API symbol format.

        If no contract is possed it will return `None` and logs an example.

        Args:
            contract: Contract dictionary. i.e. {'symbol': 'ES', 'month_code': 'H', 'year': 2024}

        Returns:

        """

        if contract is None:
            logger.error(f"Contract dictionary is empty. Contract format "
                         f"{'symbol': 'ES', 'month_code': 'H', 'year': 2024}")
            return None

        else:
            return f"XCME:{contract['symbol']}.{contract['month_code']}{str(contract['year'])[2:]}"


    def _get_contract_quarter(self, date: datetime) -> int:
        """Get current quarterly contract month"""
        return ((date.month - 1) // 3) * 3 + 3

    def _get_expiry_date(self, year: int, month: int) -> datetime:
        """
        Get contract expiration date.

        For CME: Third Friday of contract month
        For others: Raises NotImplementedError
        """
        if self.exchange == "CME":
            return self._get_third_friday(year, month)

        raise NotImplementedError(f"Expiry calculation not implemented for {self.exchange}")

    @staticmethod
    def _get_third_friday(year: int, month: int) -> datetime:
        """Calculate third Friday of given month"""
        first_day = datetime(year, month, 1)
        friday = first_day + timedelta(days=((4 - first_day.weekday() + 7) % 7))
        return friday + timedelta(weeks=2)


# Usage example
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Get the current contract
    try:
        # Create CME contract manager
        cme = ContractRollover("CME")

        # Get next contract code
        next_es = cme.get_next_contract(
            symbol="ES",
            days_before=5,
            reference_date=datetime(2025, 3, 17),
        )
        print(f"Next ES contract: {next_es}")

    except ContractError as e:
        logger.error(f"Contract error: {e}")


    # Test for an error
    try:
        # Create CME contract manager
        cme = ContractRollover("CBOT")

        # Get next contract code
        next_es = cme.get_next_contract(
            symbol="YM",
            days_before=5,
            reference_date=datetime(2025, 3, 17),
        )
        print(f"Next ES contract: {next_es}")

    except ContractError as e:
        logger.error(f"Contract error: {e}")


    # Format a contract for Ironbeam
    try:
        # Create CME contract manager
        cme = ContractRollover("CME")

        # Get next contract code
        next_es = cme.get_next_contract(
            symbol="ES",
            days_before=5,
            reference_date=datetime(2025, 2, 17),
        )

        ironbeam_contract = cme.ironbeam_contract_format(contract=next_es)
        print(f'Ironbeam contract format: {ironbeam_contract}')

    except ContractError as e:
        logger.error(f"Contract error: {e}")

