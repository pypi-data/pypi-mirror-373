import asyncio
import random
import time

from typing import Any, Dict, List, Optional

from adapter import ExchangeRatesAPIAdapter
from logging import Logger
from exceptions import LegacyLibError, NotCorrectArgumentError


class CurrencyConverter:
    """
    Self converter.
    Before converting he's downloading database of currencies.
    He's ensuring downloaded database of currencies.
    He's updating this database every hour(customizable).
    """

    def __init__(self, api_keys: List[str], update_every: int = 60 * 60 * 12, logger: Any = None) -> None:
        """
        Before converting he's downloading database of currencies.

        Args:
            api_keys (List[str]): List of API keys for ExchangeRatesAPI (will be automating rotating for correcting errors)
            update_every (int, optional): Number of seconds. Every $update_every database will be updating (default 60 * 60 * 12)
            logger (LoggerLike, optional): Logger for everything (default built-in logger)
        """
        self._api_keys = api_keys
        self._update_every = update_every
        self._database: Dict[str, Dict[str, float]] = {}

        self._logger = Logger(name=self.__class__.__name__) if logger is None else logger

        self._adapter = ExchangeRatesAPIAdapter(api_key=random.choice(api_keys), logger=self._logger)
        self._last_update_time = 0

    async def update(self) -> None:
        """Update database of currencies"""
        for attempt in range(1, 6):
            try:
                rates = await self._adapter.latest_rates(base="EUR")  # Dict like {"GBP": 0.72007}
                break
            except LegacyLibError:
                self._logger.error(
                    f"Error while try send request to get latest rates for {attempt} attempt. Try again and changing API key.."
                )
                await asyncio.sleep(2**attempt)
                self._adapter.change_api_key(random.choice(self._api_keys))
        else:
            raise LegacyLibError(
                "See like this library is deprecated. \n"
                "Also may be exchangeratesapi.io is raised it.\n"
                "Please check your arguments(like API key!). \n"
                "If all is correct please create issue"
            )
        self._database["EUR"] = rates  # noqa

        for currency, currency_rate in rates.items():
            new_currency_dict = {"EUR": 1 / currency_rate}

            for another_currency, another_currency_rate in rates.items():
                if another_currency == currency:
                    continue
                new_currency_dict[another_currency] = another_currency_rate / currency_rate

            self._database[currency] = new_currency_dict

        self._last_update_time = time.time()

    async def convert(self, currency_from: str, currency_to: str, value: float | int) -> Optional[float | int]:
        """
        Converting. If database if deprecated Converter will be update her.

        Args:
            currency_from (str): Currency from which will be convertation
            currency_to (str): Currency to which will be convertation
            value (float | int): Value for convertation
        Return:
            Value after convertation
        """
        if self._last_update_time + self._update_every < time.time():
            await self.update()

        if currency_from not in self._database:
            raise NotCorrectArgumentError(f"This currency is not available - {currency_from}")
        if currency_to not in self._database:
            raise NotCorrectArgumentError(f"This currency is not available - {currency_to}")

        try:
            rate = self._database[currency_from][currency_to]
            return rate * value
        except Exception as error:
            raise LegacyLibError(f"Unexcepted error: {error}") from error

    async def cleanup(self) -> None:
        """Cleanup"""
        if self._adapter is not None:  # type: ignore[reportUnnecessaryComparison]
            try:
                await self._adapter.cleanup()
            except Exception:
                pass
        if self._logger is not None:
            try:
                self._logger.cleanup()
            except Exception:
                pass
