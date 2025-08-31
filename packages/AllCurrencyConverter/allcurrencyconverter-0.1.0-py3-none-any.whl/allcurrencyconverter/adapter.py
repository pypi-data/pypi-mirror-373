from typing import Any, Dict, Optional
from datetime import datetime

from typeguard import typechecked

from logging import Logger
from httpwr import HTTPClient, HTTPResponse
from enums import ExchangeRatesAPIURLS
from exceptions import LegacyLibError, NotCorrectArgumentError


@typechecked
class ExchangeRatesAPIAdapter:
    """Adapter to ExchangeRatesAPI API methods"""

    def __init__(self, api_key: str, logger: Any = None) -> None:
        """
        API-key required

        Args:
            api_key (str): API-key for ExchangeRatesAPI
            logger (LoggerLike, optional): Logger. If not specified using default logger
        """
        self._api_key: str = api_key
        self._logger = Logger(name=self.__class__.__name__) if logger is None else logger
        self._http = HTTPClient(attempts=5, logger=self._logger)

    def change_api_key(self, api_key: str) -> None:
        """Changing used api-key"""
        self._api_key = api_key

    @staticmethod
    def _raise_deprecated_error() -> None:
        """Raise this error"""
        raise LegacyLibError(
            "See like this library is deprecated. \n"
            "Also may be exchangeratesapi.io is raised it.\n"
            "Please check your arguments(like API key!). \n"
            "If all is correct please create issue"
        )

    @staticmethod
    def _check_response(response: Optional[HTTPResponse]) -> None:
        """Check correct this response"""
        if response is None:
            ExchangeRatesAPIAdapter._raise_deprecated_error()

    @staticmethod
    def _check_correctness_dates(*dates: str) -> None:
        for date in dates:
            try:
                datetime.strptime(date, "%Y-%m-%d")
                continue
            except ValueError:
                raise NotCorrectArgumentError(f"Date {date} have not correct format. Must be YYYY-MM-DD") from None

    @staticmethod
    def _get_value_from_response(response: HTTPResponse, key: str) -> Any:
        """Get value from response. If this key is not in response raising deprecated error"""
        return_value = response.json.get(key, None)
        if return_value is None:
            ExchangeRatesAPIAdapter._raise_deprecated_error()  # noqa
        else:
            return return_value

    async def symbols(self) -> Optional[Dict[str, str]]:
        """
        Get list of current currencies

        Return:
            Dict like {"AED": "United Arab Emirates Dirham"}
        """
        response = await self._http.get(url=ExchangeRatesAPIURLS.SYMBOLS, params={"access_key": self._api_key})
        self._check_response(response=response)
        return self._get_value_from_response(response=response, key="symbols")

    async def latest_rates(self, base: str = "EUR") -> Optional[Dict[str, float]]:
        """
        Get latest rates for this base currency

        Return:
            Dict like {"GBP": 0.72007}
        """
        response = await self._http.get(url=ExchangeRatesAPIURLS.LATEST_RATES, params={"access_key": self._api_key, "base": base})
        self._check_response(response=response)
        return self._get_value_from_response(response=response, key="rates")

    async def get_historical_rates(self, date: str, base: str = "USD") -> Optional[Dict[str, float]]:
        """
        Get rates for date for this base currency

        Args:
            date (str): date in format YYYY-MM-DD
            base (str): three-letters code currency
        Return:
            Dict like {"GBP": 0.72007}
        """
        self._check_correctness_dates(date)
        response = await self._http.get(
            url=ExchangeRatesAPIURLS.HISTORICAL_RATES.format(date=date), params={"access_key": self._api_key, "base": base}
        )
        self._check_response(response=response)
        return self._get_value_from_response(response=response, key="rates")

    async def get_timeseries_rates(self, start_date: str, end_date: str, base: str) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Get daily historical rates between two dates

        Args:
            start_date (str): start date in format YYYY-MM-DD
            end_date (str): end date in format YYYY-MM-DD
            base (str): three-letters code currency
        Return:
            Dict like {"2012-05-01": {"GBP": 0.72007}}
        """
        self._check_correctness_dates(start_date, end_date)
        response = await self._http.get(
            url=ExchangeRatesAPIURLS.TIMESERIES_RATES,
            params={"access_key": self._api_key, "start_date": start_date, "end_date": end_date, "base": base},
        )
        self._check_response(response=response)
        return self._get_value_from_response(response=response, key="rates")

    async def get_fluctuation(self, start_date: str, end_date: str, base: str) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Get fluctuation on a day-to-day basis

        Args:
            start_date (str): start date in format YYYY-MM-DD
            end_date (str): end date in format YYYY-MM-DD
            base (str): three-letters code currency
        Return:
            Dict like {
            "USD": {
                "start_rate":1.228952,
                "end_rate":1.232735,
                "change":0.0038,
                "change_pct":0.3078
            }
        }
        """
        self._check_correctness_dates(start_date, end_date)
        response = await self._http.get(
            url=ExchangeRatesAPIURLS.FLUCTUATION,
            params={"access_key": self._api_key, "start_date": start_date, "end_date": end_date, "base": base},
        )
        self._check_response(response=response)
        return self._get_value_from_response(response=response, key="rates")

    async def cleanup(self) -> None:
        """CLeanup"""
        if self._http is not None:  # type: ignore[reportUnnecessaryComparison]
            try:
                await self._http.down()
            except Exception:
                pass
