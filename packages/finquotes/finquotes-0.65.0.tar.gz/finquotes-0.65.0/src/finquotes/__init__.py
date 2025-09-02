"""Retrieves data from various financial sources."""

import abc
import csv
import dataclasses
import datetime as dt
import decimal
import enum
import functools
import importlib
import importlib.abc
import importlib.metadata
import importlib.resources
import io
import logging
import os
import typing as t
import zoneinfo
from decimal import Decimal as D  # noqa: N817
from pathlib import Path

import pytest_socket
import urllib3.exceptions

from . import localhttp
from .network_config import NetworkConfigMixin as NetworkConfigMixin

__version__ = importlib.metadata.version("finquotes")
log = logging.getLogger("finquotes")
# See Python cookbook, 3rd Edition, 13.12.
log.addHandler(logging.NullHandler())


# Configure where the API keys are found
api_key_file = Path("~/.finquotes/api_keys.txt").expanduser()


def default_timezone() -> zoneinfo.ZoneInfo:
    """Return default to EST time zone because prices are usually available in US markets.

    Will eventually be replaced wit a more flexible solution.

    """
    return zoneinfo.ZoneInfo("America/New_York")


def default_timezone_offset() -> dt.timedelta | None:
    """Return default timezone offset for EST time zone."""
    return default_timezone().utcoffset(dt.datetime.now(default_timezone()))


def default_timezone_offset_str() -> str:
    """Return the default timezone offset as a string."""
    offset = default_timezone_offset()
    if offset is None:
        return "+00:00"  # Default to UTC if no offset is available
    total_seconds = int(offset.total_seconds())
    hours = total_seconds // 3600  # Convert seconds to hours
    minutes = (total_seconds % 3600) // 60
    sign = "-" if total_seconds < 0 else "+"
    return f"{sign}{abs(hours):02d}:{abs(minutes):02d}"


def get_api_key(api_name: str, encoding: str | None = None) -> str:
    """Retrieve API key.

    :param api_name: name of the API
    :param encoding: encoding to use when reading the API key file, defaults to utf-8

    :return: api key for that api name.

    :raises KeyError: if the API key is not found
    """
    encoding = encoding or "utf-8"
    uc_api_name = api_name.replace("finquotes.", "").upper()
    api_key_env_var = f"FINQUOTES_{uc_api_name}_API_KEY"
    api_key_from_env = os.getenv(api_key_env_var)
    if api_key_from_env:
        log.info("using api key in environment variable %s", api_key_env_var)
        return api_key_from_env
    log.debug("cannot find api key in environment %s", api_key_env_var)
    try:
        with Path(api_key_file).open(encoding=encoding) as fh:
            lines = fh.read()
            for line in lines.split("\n"):
                if "=" not in line:
                    continue
                api, key = line.split("=")
                if api == api_name:
                    log.info("using api key in file %s", api_key_file)
                    return key
    except (ValueError, TypeError) as error:
        log.debug("failed to read api key from %s: %s", api_key_file, error)
    except FileNotFoundError as error:
        log.debug("failed to open %s for reading: %s", api_key_file, error)
    log.error(
        "failed to find an api key for api %s. Try to set %s or update the file %s with a value for %s=<your key>",
        api_name,
        api_key_env_var,
        api_key_file,
        api_name,
    )
    raise KeyError("api key for " + api_name + " not found or empty!")


def now() -> dt.datetime:
    """Return current timestamp as tz-aware datetime.datetime."""
    return dt.datetime.now(default_timezone())


def today() -> dt.date:
    """Return today's date."""
    return now().date()


def compute_default_dates(
    end_date: dt.date | None,
    begin_date: dt.date | None,
) -> tuple[dt.date, dt.date]:
    """Defaults the dates if they are different from None."""
    if end_date is None:
        end_date = today()
    if begin_date is None:
        begin_date = end_date
    assert isinstance(
        begin_date,
        dt.date,
    ), f"begin_date: date expected, got {type(begin_date)}"
    if isinstance(begin_date, dt.datetime):
        begin_date = begin_date.date()
    assert isinstance(
        end_date,
        dt.date,
    ), f"end_date: date expected, got {type(end_date)}"
    if isinstance(end_date, dt.datetime):
        end_date = end_date.date()
    assert begin_date <= end_date, (
        f"begin_date {begin_date:%Y-%m-%d} must be earlier than end_date {end_date:%Y-%m-%d}"
    )
    return end_date, begin_date


class Field(enum.Enum):
    """Common interface for the field names coming from different sources."""

    SYMBOL = "symbol"
    DATE = "date"
    CLOSE = "close"
    TIME = "time"
    TIME_STAMP = "time_stamp"
    OPEN = "open"
    LOW = "low"
    HIGH = "high"
    VOLUME = "volume"
    SOURCE = "source"
    BID = "bid"
    BID_SIZE = "bid_size"
    ASK = "ask"
    ASK_SIZE = "ask_size"
    PCT_CHANGE = "pct_change"
    CHANGE = "change"
    PREVIOUS_CLOSE = "previous_close"
    SPLIT_ADJ = "split_adj"
    DIST_ADJ = "dist_adj"
    EX_DATE = "ex_date"
    PAY_DATE = "pay_date"
    AMOUNT = "amount"
    NAME = "name"
    N_SHARES_OUTSTANDING = "n_shares_outstanding"
    EXCHANGE = "exchange"
    CURRENCY = "currency"


def to_decimal(val: D | str | float) -> D:
    """Convert val to decimal.Decimal."""
    if isinstance(val, D):
        return val
    if isinstance(val, int | float):
        return D(str(val))
    return D(val)


def to_decimal_or_none(val: None | D | str | float) -> D | None:
    """Convert val to decimal.Decimal."""
    if val is None:
        return None
    try:
        return to_decimal(val)
    except (ValueError, TypeError, decimal.InvalidOperation) as err:
        if val is not None:
            log.warning("cannot convert %s to decimal: %s", val, err)
    return None


def to_int_or_none(val: None | str | float) -> int | None:
    """Convert val to int."""
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError, decimal.InvalidOperation):
        try:
            return int(float(val))
        except (ValueError, TypeError, decimal.InvalidOperation) as err:
            if val is not None:
                log.warning("cannot convert %s to int: %s", val, err)
    return None


@functools.total_ordering
class Price:  # pylint: disable=R0902, R0903
    """Hold price information.

    Use vars(historical_result) to cached_get a dict-like interface.

    All numeric fields are expected to be decimal.Decimal.

    Time is present and separate from date because the data may be known for
    intraday data but it is usually not specified for end of day data.

    """

    # Slots limits memory usage and ensures mispelling are caught.
    __slots__ = [
        "_close",
        "_date_or_datetimetz",
        "_high",
        "_low",
        "_open",
        "_volume",
        "dist_adj",
        "source",
        "split_adj",
        "symbol",
    ]
    # https://en.wikipedia.org/wiki/ISO_8601
    __date_fmt = "%Y-%m-%d"
    __datetime_fmt = "%Y-%m-%dT%H:%M:%S"
    # Length of a date-only string in YYYY-MM-DD format
    _DATE_ONLY_LENGTH = 10

    @classmethod
    def __convert_date_internal(cls, date: dt.date | dt.datetime) -> dt.date | dt.datetime:
        """Convert date or datetime to tz-aware datetime."""
        if isinstance(date, dt.datetime):
            if date.tzinfo is None:
                return date.replace(tzinfo=default_timezone())
            return date
        if isinstance(date, dt.date):
            return date
        msg = f"date or datetime expected, got {type(date)}"
        raise TypeError(msg)

    # pylint: disable=R0913
    def __init__(
        self: t.Self,
        symbol: str,
        date: dt.date | dt.datetime,
        close: D | float | str,
        open_: D | float | str | None = None,
        low: D | float | str | None = None,
        high: D | float | str | None = None,
        volume: int | None = None,
        source: str | None = None,
    ) -> None:
        """Initialize Price.

        :param symbol: security symbol
        :param date: price observation date, can be a date or a tz-aware datetime.
        :param close: close price (unadjusted)
        :param open_: open price (unadjusted)
        :param high: high price (unadjusted)
        :param low: low price (unadjusted)
        :param volume: volume for that bar (unadjusted)
        :param source: data source

        Note that close may refer to the last or to the close depending on the
        context (e.g. day close, or interval close or last price).

        """
        if not isinstance(symbol, str):
            msg = f"symbol: str expected, got {type(symbol)}"
            raise TypeError(msg)
        self.symbol = symbol
        self._date_or_datetimetz: dt.date | dt.datetime = self.__convert_date_internal(date)
        # close is required, so we need to give it a value even if it is 0.0.
        self._close = to_decimal(close)
        self._open = to_decimal_or_none(open_)
        self._high = to_decimal_or_none(high)
        self._low = to_decimal_or_none(low)
        self._volume = int(volume) if volume is not None else None
        self.source = source

    def __repr__(self: t.Self) -> str:
        """Representation of Price.

        Looks like code needed to instatiate the same object.

        """

        def __quote(val: None | int | D | str) -> str:
            return f"'{val}'" if val is not None else "None"

        return (
            f"{self.__class__.__name__}(symbol={__quote(self.symbol)}, "
            f"date={self.date!r}, close={__quote(self.close)}, "
            f"open_={__quote(self.open)}, "
            f"low={__quote(self.low)}, high={__quote(self.high)}, "
            f"volume={__quote(self.volume)}, source={__quote(self.source)})"
        )

    def __str__(self: t.Self) -> str:
        """Forward to to_csv()."""
        return self.to_csv()

    def to_csv(self: t.Self, date_format: str | None = None) -> str:
        """Conversion to string."""
        date_format = date_format or (self.__datetime_fmt if self.time else self.__date_fmt)
        retval = f"{self.symbol}," if self.symbol else ","
        if self.date:
            if self.time:
                comb = dt.datetime.combine(self.date, self.time)
                retval += f"{dt.datetime.strftime(comb, date_format)},"
            else:
                retval += f"{dt.date.strftime(self.date, date_format)},"
        retval += f"{self.close}," if self.close else ","
        retval += f"{self.open}," if self.open else ","
        retval += f"{self.high}," if self.high else ","
        retval += f"{self.low}," if self.low else ","
        retval += f"{self.volume:.0f}," if self.volume else ","
        retval += f"{self.source}" if self.source else ","
        return retval

    @classmethod
    def get_datetime(cls, datetimestr: str, date_format: str | None = None) -> dt.datetime:
        """Get tz-aware datetime from string.

        :param datetimestr: date string in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format
        :param date_format: overrides the Price.__date_fmt or Price.__datetime_fmt
        :return: datetime object with timezone info if available, otherwise date and None for time

        :raises ValueError: if the date string is not in the expected format
        """
        date_format = date_format or (
            Price.__datetime_fmt if len(datetimestr) > Price._DATE_ONLY_LENGTH else Price.__date_fmt
        )
        try:
            dt_obj = dt.datetime.strptime(datetimestr, date_format).replace(tzinfo=default_timezone())
        except ValueError as error:
            msg = f"invalid date string: {datetimestr} with format {date_format}"
            raise ValueError(msg) from error
        else:
            return dt_obj

    @classmethod
    def from_csv(
        cls,
        price_str: str,
        date_format: str | None = None,
    ) -> "Price":  # pylint: disable=too-many-locals
        """Convert csv string to finquotes.Price.

        This function reverse str(). If no the format is a date, the time is set
        to None to avoid tz issues.

        :param price_str: pice string defined as:
            symbol, date (YYYY-MM-DD), close, open, high, low, volume, source
        :param date_format: overrides the Price.__date_fmt or Price.__datetime_fmt

        """
        symbol, date_str, close, open_, high, low, volume, *other = price_str.split(",")
        date_str = date_str.strip()
        dt_obj = cls.get_datetime(date_str, date_format)
        date = dt_obj.date()
        time = None
        if len(date_str) > cls._DATE_ONLY_LENGTH:
            # If the date string is longer than the date format, it contains time.
            time = dt_obj.timetz()
        source = None
        if other:
            source = other[0]
        price = Price(symbol, date, D(close), source=source)
        price.open = D(open_) if open_ else None
        price.high = D(high) if high else None
        price.low = D(low) if low else None
        price.volume = int(volume) if volume else None
        price.time = time
        return price

    def __lt__(self: t.Self, other: t.Any) -> bool:
        """Compare based on symbol, then date, time, and close."""
        if not isinstance(self, type(other)):
            return NotImplemented
        return (self.symbol, self.date, self.time) < (
            other.symbol,
            other.date,
            other.time,
        )

    def __eq__(self: t.Self, other: object) -> bool:
        """Equal if every field is the same (including symbol)."""
        if not isinstance(other, Price):
            return False
        return (
            self.symbol == other.symbol
            and self.close == other.close
            and self.date == other.date
            and self._open == other._open
            and self._high == other._high
            and self._low == other._low
            and self._volume == other._volume
            and self.source == other.source
        )

    def __hash__(self: t.Self) -> int:
        """Hash based on all fields used in equality comparison."""
        return hash(
            (
                self.symbol,
                self.close,
                self.date,
                self._open,
                self._high,
                self._low,
                self._volume,
                self.source,
            ),
        )

    @property
    def datetime(self: t.Self) -> dt.datetime | None:
        """Get tz-aware datetime for price."""
        if isinstance(self._date_or_datetimetz, dt.datetime):
            return self._date_or_datetimetz
        assert self._date_or_datetimetz is not None
        return dt.datetime.combine(self._date_or_datetimetz, dt.time(0, 0), tzinfo=default_timezone())

    @datetime.setter
    def datetime(self: t.Self, value: dt.datetime) -> None:
        """Set the datetime of the price.

        :param value: datetime with timezone info.

        """
        self._date_or_datetimetz = self.__convert_date_internal(value)

    @property
    def date(self: t.Self) -> dt.date:
        """Get date for price."""
        if isinstance(self._date_or_datetimetz, dt.datetime):
            return self._date_or_datetimetz.date()
        assert self._date_or_datetimetz is not None
        return self._date_or_datetimetz

    @date.setter
    def date(self: t.Self, value: dt.date | dt.datetime) -> None:
        """Set the date of the price.

        :param value: date.

        Accept a tz-aware datetime as well and forwards the call to the .datetime property in that case.

        """
        self._date_or_datetimetz = self.__convert_date_internal(value)

    @property
    def time(self: t.Self) -> dt.time | None:
        """Get tz-aware time of price."""
        if isinstance(self._date_or_datetimetz, dt.datetime):
            return self._date_or_datetimetz.timetz()
        return None

    @time.setter
    def time(self: t.Self, value: dt.time | None) -> None:
        """Set time of price.

        :param value: time with timezone info or None

        If the time is not tz-aware, it will be combined with the date and follow
        the logic of .date assignment.

        :raises AssertionError: if value is not None and not a datetime.time

        """
        if value is None:
            self._date_or_datetimetz = self.date
            return
        assert isinstance(value, dt.time), f"time: time expected, got {type(value)}"
        self.date = dt.datetime.combine(self.date, value)

    @property
    def close(self: t.Self) -> D:
        """Get the close or last depending on context."""
        assert self._close is not None  # for mypy
        return self._close

    @close.setter
    def close(self: t.Self, value: D | str | float) -> None:
        """Set the price or last depending on context."""
        self._close = to_decimal(value)

    @property
    def open(self: t.Self) -> D | None:
        """Get the price interval open."""
        return self._open

    @open.setter
    def open(self: t.Self, value: D | None) -> None:
        """Set the price interval open."""
        assert value is None or isinstance(value, D)
        self._open = value

    @property
    def low(self: t.Self) -> D | None:
        """Get the price interval low."""
        return self._low

    @low.setter
    def low(self: t.Self, value: D | None) -> None:
        """Set the price interval low."""
        assert value is None or isinstance(value, D)
        self._low = value

    @property
    def high(self: t.Self) -> D | None:
        """Get the price interval high."""
        return self._high

    @high.setter
    def high(self: t.Self, value: D | None) -> None:
        """Set the price interval high."""
        assert value is None or isinstance(value, D)
        self._high = value

    @property
    def volume(self: t.Self) -> int | None:
        """Get the interval volume."""
        return self._volume

    @volume.setter
    def volume(self: t.Self, value: int | None) -> None:
        """Set the interval volume."""
        assert value is None or isinstance(value, int)
        self._volume = value


class PriceValidationDiagnosticLevel(enum.Enum):
    """Validation level."""

    OK = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()


@dataclasses.dataclass
class PriceValidationDiagnostic:
    """Validation status."""

    level: PriceValidationDiagnosticLevel
    message: str

    def __init__(
        self: t.Self,
        level: PriceValidationDiagnosticLevel = PriceValidationDiagnosticLevel.OK,
        message: str = "",
    ) -> None:
        """Initialize."""
        self.message = message
        self.level = level


def check_relative_attribute_values(
    price: t.Any,
    tol: D = D("0.01"),
) -> PriceValidationDiagnostic:
    """Check that the relative attributes are consistent."""
    if price.low is not None:
        if price.close and price.close < price.low - tol:
            return PriceValidationDiagnostic(
                PriceValidationDiagnosticLevel.WARNING,
                f"close {price.close:.2f} lower than low {price.low:.2f}",
            )
        if price.open and price.open < price.low - tol:
            return PriceValidationDiagnostic(
                PriceValidationDiagnosticLevel.WARNING,
                f"open {price.open:.2f} lower than low {price.low:.2f}",
            )
    if price.high is not None:
        if price.close and price.close > price.high + tol:
            return PriceValidationDiagnostic(
                PriceValidationDiagnosticLevel.WARNING,
                f"close {price.close:.2f} higher than high {price.high:.2f}",
            )
        if price.open and price.open > price.high + tol:
            return PriceValidationDiagnostic(
                PriceValidationDiagnosticLevel.WARNING,
                f"open {price.open:.2f} higher than high {price.high:.2f}",
            )
    return PriceValidationDiagnostic(PriceValidationDiagnosticLevel.OK, "")


def check_date_too_old(price: Price) -> PriceValidationDiagnostic:
    """Check that the date is not too old."""
    if price.date is not None and price.date < dt.date(1900, 1, 1):
        return PriceValidationDiagnostic(
            PriceValidationDiagnosticLevel.ERROR,
            f"date {price.date} is earlier than 1900-01-01",
        )
    return PriceValidationDiagnostic(PriceValidationDiagnosticLevel.OK, "")


def _make_default_checks() -> list[t.Callable[[t.Any], PriceValidationDiagnostic]]:
    """Make default checks."""
    checks: list[t.Callable[[t.Any], PriceValidationDiagnostic]] = []

    def _create_missing_attribute_check(
        attribute: str,
        level: PriceValidationDiagnosticLevel,
    ) -> t.Callable[[t.Any], PriceValidationDiagnostic]:
        """Create a function to check for missing attributes."""

        def check_missing_attribute(price: t.Any) -> PriceValidationDiagnostic:
            return (
                PriceValidationDiagnostic(level, f"missing {attribute}")
                if not getattr(price, attribute)
                else PriceValidationDiagnostic()
            )

        return check_missing_attribute

    for attribute, level in [
        ("symbol", PriceValidationDiagnosticLevel.ERROR),
        ("date", PriceValidationDiagnosticLevel.ERROR),
        ("close", PriceValidationDiagnosticLevel.ERROR),
        ("source", PriceValidationDiagnosticLevel.WARNING),
        ("time", PriceValidationDiagnosticLevel.WARNING),
        ("open", PriceValidationDiagnosticLevel.WARNING),
        ("low", PriceValidationDiagnosticLevel.WARNING),
        ("high", PriceValidationDiagnosticLevel.WARNING),
        ("volume", PriceValidationDiagnosticLevel.WARNING),
    ]:
        checks.append(_create_missing_attribute_check(attribute, level))

    def _wrapped_relative_check(price: t.Any) -> PriceValidationDiagnostic:
        return check_relative_attribute_values(price)

    def _wrapped_date_check(price: t.Any) -> PriceValidationDiagnostic:
        return check_date_too_old(price)

    checks.append(_wrapped_relative_check)
    checks.append(_wrapped_date_check)
    return checks


class PriceValidator:
    """Validate price data."""

    _default_checks = _make_default_checks()

    def __init__(
        self: t.Self,
        checks: list[t.Callable[..., PriceValidationDiagnostic]] | None = None,
        as_of_date: dt.date | None = None,
    ) -> None:
        """Initialize the validator."""
        self.checks = checks or self._default_checks
        self.as_of_date = as_of_date or today()
        self.checks.append(self.check_date_is_in_past)

    def check_date_is_in_past(self: t.Self, price: Price) -> PriceValidationDiagnostic:
        """Check that the date is in the past."""
        if price.date is not None and price.date > self.as_of_date:
            return PriceValidationDiagnostic(
                PriceValidationDiagnosticLevel.ERROR,
                f"date {price.date} is in the future",
            )
        return PriceValidationDiagnostic()

    def detect_issues(
        self: t.Self,
        price: Price,
    ) -> t.Iterable[PriceValidationDiagnostic]:
        """Loops on checks and yield all detected issues."""
        for check in self.checks:
            result = check(price)
            if result and result.level != PriceValidationDiagnosticLevel.OK:
                yield result


@functools.total_ordering
class Distribution:  # pylint: disable=R0903
    """Hold a historical dividend record.

    Note: use vars(Distribution) to cached_get a dict-like interface.

    """

    # Slots limits memory usage and ensures mispelling are caught.
    __slots__ = ["_amount", "_ex_date", "_pay_date", "symbol"]

    def __init__(
        self: t.Self,
        symbol: str,
        ex_date: dt.date,
        amount: D,
        pay_date: dt.date | None = None,
    ) -> None:
        """Create new distribution result.

        :param str symbol: security identifier
        :param datetime.date ex_date: ex-date of the distribution
        :param decimal.Decimal amount: amount paid
        :param pay_date: pay date
        :type pay_date: None or datetime.date

        """
        self.symbol = symbol
        self._ex_date = ex_date
        self._amount = to_decimal_or_none(amount)
        self._pay_date = pay_date

    @property
    def ex_date(self: t.Self) -> dt.date:
        """Get ex-date of distribution."""
        return self._ex_date

    @ex_date.setter
    def ex_date(self: t.Self, value: dt.date) -> None:
        """Set ex-date of distribution."""
        assert isinstance(value, dt.date)
        self._ex_date = value

    @property
    def amount(self: t.Self) -> D | None:
        """Get amount of distribution."""
        return self._amount

    @amount.setter
    def amount(self: t.Self, value: D) -> None:
        """Set amount of distribution."""
        assert isinstance(value, D)
        self._amount = value

    @property
    def pay_date(self: t.Self) -> dt.date | None:
        """Get pay date of distribution."""
        return self._pay_date

    @pay_date.setter
    def pay_date(self: t.Self, value: dt.date) -> None:
        """Set pay date of distribution."""
        assert isinstance(value, dt.date)
        self._pay_date = value

    def __repr__(self: t.Self) -> str:
        """Representation of object."""
        return f"<{self.__class__.__name__} {self.symbol} {self.ex_date} {self.amount}>"

    def __str__(self: t.Self) -> str:
        """Representation of object."""
        return f"{self.symbol},{self.ex_date},{self.amount}"

    def __lt__(self: t.Self, other: object) -> bool:
        """Compare for ordering based on symbol, ex_date, then amount."""
        if not isinstance(other, Distribution):
            return NotImplemented
        return (self.symbol, self.ex_date, self.amount) < (
            other.symbol,
            other.ex_date,
            other.amount,
        )

    def __eq__(self: t.Self, other: object) -> bool:
        """Compare symbol, ex-date and amount."""
        if not isinstance(other, Distribution):
            return False
        return self.symbol == other.symbol and self.ex_date == other.ex_date and self.amount == other.amount

    def __hash__(self: t.Self) -> int:
        """Hash based on symbol, ex_date, and amount."""
        return hash((self.symbol, self.ex_date, self.amount))


@functools.total_ordering
class Split:  # pylint: disable=R0903
    """Hold a historical dividend record.

    Note: use vars(Split) to cached_get a dict-like interface.

    """

    # Slots limits memory usage and ensures mispelling are caught.
    __slots__ = ["_ex_date", "_new_quantity", "_old_quantity", "symbol"]

    def __init__(
        self: t.Self,
        symbol: str,
        ex_date: dt.date,
        new_quantity: int,
        old_quantity: int,
    ) -> None:
        """Create new distribution result.

        :param symbol: security symbol
        :param ex_date: ex-date of the split
        :param new_quantity: number of shares after split
        :param old_quantity: number of shares before split

        """
        assert isinstance(new_quantity, int)
        assert isinstance(old_quantity, int)
        assert isinstance(ex_date, dt.date)
        self.symbol = symbol
        self.ex_date = ex_date
        self.new_quantity = new_quantity
        self.old_quantity = old_quantity

    @staticmethod
    def from_ratio(symbol: str, ex_date: dt.date, ratio: D) -> "Split":
        """Create new distribution result.

        :param symbol: security symbol
        :param ex_date: ex-date of the split
        :param ratio: ratio of the split: >1 for split, <1 for reverse split

        """
        assert isinstance(ratio, D)
        assert isinstance(ex_date, dt.date)
        new_quantity, old_quantity = ratio.as_integer_ratio()
        reverse_ratio = (1 / ratio).quantize(D("0.0001"))
        reverse_old_quantity, reverse_new_quantity = reverse_ratio.as_integer_ratio()
        if new_quantity + old_quantity < reverse_new_quantity + reverse_old_quantity:
            return Split(
                symbol=symbol,
                ex_date=ex_date,
                new_quantity=int(new_quantity),
                old_quantity=int(old_quantity),
            )
        return Split(
            symbol=symbol,
            ex_date=ex_date,
            new_quantity=int(reverse_new_quantity),
            old_quantity=int(reverse_old_quantity),
        )

    @property
    def ex_date(self: t.Self) -> dt.date:
        """Get ex-date of distribution."""
        return self._ex_date

    @ex_date.setter
    def ex_date(self: t.Self, value: dt.date) -> None:
        """Set ex-date of distribution."""
        assert isinstance(value, dt.date)
        self._ex_date = value

    @property
    def new_quantity(self: t.Self) -> int:
        """Get new shares quantity."""
        return self._new_quantity

    @new_quantity.setter
    def new_quantity(self: t.Self, value: int) -> None:
        """Set new shares quantity."""
        assert isinstance(value, int)
        self._new_quantity = value

    @property
    def old_quantity(self: t.Self) -> int:
        """Get old shares quantity."""
        return self._old_quantity

    @old_quantity.setter
    def old_quantity(self: t.Self, value: int) -> None:
        """Set old shares quantity."""
        assert isinstance(value, int)
        self._old_quantity = value

    def __repr__(self: t.Self) -> str:
        """Representation of object."""
        return f"<{self.__class__.__name__} {self.symbol} {self.ex_date} {self.new_quantity}/{self.old_quantity}>"

    def __str__(self: t.Self) -> str:
        """Representation of object."""
        return f"{self.symbol},{self.ex_date},{self.new_quantity}/{self.old_quantity}"

    def __lt__(self: t.Self, other: object) -> bool:
        """Compare for ordering based on symbol, ex_date, then ratio."""
        if not isinstance(other, Split):
            return NotImplemented
        return (self.symbol, self.ex_date, self.new_quantity, self.old_quantity) < (
            other.symbol,
            other.ex_date,
            other.new_quantity,
            other.old_quantity,
        )

    def __eq__(self: t.Self, other: object) -> bool:
        """Compare symbol, ex-date and new and old quantity."""
        if not isinstance(other, Split):
            return False
        return (
            self.symbol == other.symbol
            and self.ex_date == other.ex_date
            and self.new_quantity == other.new_quantity
            and self.old_quantity == other.old_quantity
        )

    def __hash__(self: t.Self) -> int:
        """Hash based on symbol, ex_date, new_quantity, and old_quantity."""
        return hash((self.symbol, self.ex_date, self.new_quantity, self.old_quantity))


@dataclasses.dataclass(frozen=True)
class _ExchangeData:
    iso_country: str
    mic: str
    operating_mic: str
    acronym: str
    city: str


def _get_exchanges() -> dict[str, _ExchangeData]:
    """Get a list of valid exchanges.

    See https://www.iso20022.org/sites/default/files/ISO10383_MIC/ISO10383_MIC.csv

    """

    def __parse_io(fh: t.Iterable[str]) -> dict[str, _ExchangeData]:
        reader = csv.reader(fh)
        next(reader)  # skip header
        return {
            row[2]: _ExchangeData(
                iso_country=row[1],
                mic=row[2],
                operating_mic=row[3],
                acronym=row[6],
                city=row[7],
            )
            for row in reader
        }

    def parse_csv(
        file_or_buffer: importlib.abc.Traversable | str | io.TextIOBase,
        encoding: str | None = None,
    ) -> dict[str, _ExchangeData]:
        """Parse a csv file or buffer and return a dict of exchanges.

        :param file_or_buffer: path to csv file, buffer containing the csv data, or file-like object.
        :param encoding: encoding of the csv file.
        :return: dict of exchanges.
        """
        # Check if file_or_buffer is a string that contains CSV data
        if isinstance(file_or_buffer, str):
            str_data: str = file_or_buffer
            if str_data.startswith('"COUNTRY"'):
                return __parse_io(io.StringIO(file_or_buffer))
            with Path(str_data).open(encoding=encoding) as fh:
                return __parse_io(fh)
        # Check if file_or_buffer is a Traversable object (e.g., from importlib.resources)
        if isinstance(file_or_buffer, importlib.abc.Traversable):
            with file_or_buffer.open("r", encoding=encoding) as fh:
                return __parse_io(fh)
        # Assume file_or_buffer is a file-like object (e.g., io.StringIO or io.BytesIO)
        if isinstance(file_or_buffer, io.IOBase):
            return __parse_io(file_or_buffer)
        msg = "Unsupported type for file_or_buffer: must be a file path, buffer, or file-like object."
        raise ValueError(
            msg,
        )

    url = "https://www.iso20022.org/sites/default/files/ISO10383_MIC/ISO10383_MIC.csv"
    try:
        data = localhttp.request(localhttp.cached_session, "GET", url).text
        exchanges = parse_csv(data)
    except (
        OSError,
        csv.Error,
        AttributeError,
        pytest_socket.SocketBlockedError,
        urllib3.exceptions.HTTPError,
    ) as error:
        log.info("failed to fetch %s: %s. Falling back to embeded file", url, error)
        iso10383 = importlib.resources.files(__name__) / "data/ISO10383_MIC.csv"
        assert iso10383.is_file(), str(iso10383) + " file not found"
        exchanges = parse_csv(iso10383, encoding="utf-8")
    return exchanges


@functools.cache
def get_exchanges() -> dict[str, _ExchangeData]:
    """Cache layer for _get_exchanges()."""
    return _get_exchanges()


@dataclasses.dataclass(frozen=True)
class Exchange:
    """Hold an exchange record.

    The mic value validity is checked only in the constructor so you will need to change that
    check if you want to change the mic.  Seems more efficient to require to create new instances
    of this class instead of modifying its only field.

    :seealso: get_operating_exchange()

    """

    mic: str

    def __post_init__(self: t.Self) -> None:
        """Check mic value."""
        if self.mic is None:
            msg = "mic is required"
            raise ValueError(msg)
        if self.mic not in get_exchanges():
            msg = f"invalid mic: {self.mic}"
            raise ValueError(msg)

    @property
    def name(self: t.Self) -> str:
        """Get name of exchange."""
        return get_exchanges()[self.mic].acronym

    @property
    def city(self: t.Self) -> str:
        """Get country of exchange."""
        return get_exchanges()[self.mic].city

    @property
    def operating_mic(self: t.Self) -> str:
        """Get operating MIC."""
        return get_exchanges()[self.mic].operating_mic

    def __str__(self: t.Self) -> str:
        """MIC code for the exchange."""
        return f"{self.mic}"


def get_operating_exchange(exchange: Exchange) -> Exchange:
    """Consolidate exchange record to the operating exchange."""
    return Exchange(mic=exchange.operating_mic)


@dataclasses.dataclass
class Security:
    """Hold security information."""

    symbol: str
    name: str
    type: str | None = None
    currency: str | None = None
    exchange: Exchange | None = None
    country: str | None = None
    sector: str | None = None
    industry: str | None = None
    source: str | None = None
    # If the source has an identifier for that security, slot it here.
    source_id: str | None = None

    def __post_init__(self: t.Self) -> None:
        """Set attribute to lower case and run checks."""
        self._assert_invariants()

    def _assert_invariants(self: t.Self) -> None:
        """Assert invariants."""
        assert self.source is not None, "source is None!"

    def __str__(self: t.Self) -> str:
        """Representation of object as csv string."""
        return to_csv(self)


@functools.total_ordering
class ShortInterest:  # pylint: disable=too-few-public-methods
    """Hold short interest."""

    # Slots limits memory usage and ensures mispelling are caught.
    __slots__ = ["as_of_date", "n_shares", "name", "symbol"]

    def __init__(
        self: t.Self,
        symbol: str,
        as_of_date: dt.date,
        n_shares: D,
        *args: t.Sequence[t.Any],
        **kwargs: t.Any,
    ) -> None:
        """Create new short interest information.

        :param symbol: security ticker.
        :param as_of_date: date for which short interest was measured.
        :param n_shares: numbed of shares sold short.
        :param args: optional parameters to set attributes.

        """
        assert isinstance(symbol, str)
        self.symbol = symbol
        self.n_shares = n_shares
        assert isinstance(as_of_date, dt.date)
        self.as_of_date = as_of_date
        for akey, avalue in zip(self.__slots__, args, strict=False):
            setattr(self, akey, avalue)
        for kwkey, kwvalue in kwargs.items():
            setattr(self, kwkey, kwvalue)

    def __str__(self: t.Self) -> str:
        """Output of str() function.

        :rtype: str.

        """
        return f"{self.symbol} {self.as_of_date} {self.n_shares}"

    def __repr__(self: t.Self) -> str:
        """Output of repr() function.

        :rtype: str.

        """
        return "<{self.__class__.__name__} symbol:{self.symbol} as_of_date:{self.as_of_date} n_shares:{self.n_shares}>"

    def __eq__(self: t.Self, other: object) -> bool:
        """Check equality with another ShortInterest object."""
        if not isinstance(other, ShortInterest):
            return False
        return self.symbol == other.symbol and self.as_of_date == other.as_of_date

    def __hash__(self: t.Self) -> int:
        """Hash based on symbol and as_of_date."""
        return hash((self.symbol, self.as_of_date))

    def __lt__(self: t.Self, other: object) -> bool:
        """Compare for ordering based on symbol, as_of_date, then n_shares."""
        if not isinstance(other, ShortInterest):
            return NotImplemented
        return (self.symbol, self.as_of_date, self.n_shares) < (
            other.symbol,
            other.as_of_date,
            other.n_shares,
        )


class AbstractFeed(metaclass=abc.ABCMeta):  # pylint: disable=R0903
    """Factor common attributes to all finquotes.Feed.

    Actual abstract method will be defined in the subclasses of AbstractFeed.

    .. seealso::
        AbstractCloseFeed, AbstractHistoricalFeed, AbstractDistributionFeed,
        AbstractSplitFeed.

    """

    def __init__(
        self: t.Self,
        name: str,
        source: str,
    ) -> None:
        """Initialize the close class.

        :param name: identify the feed (e.g. finquotes.yahoo).
        :param source: identify the data source (e.g. yahoo).

        """
        self.name = name
        self.source = source

    @property
    @abc.abstractmethod
    def timeout(self: t.Self) -> float:
        """Get timeout in seconds for network operations."""
        msg = "Implement timeout property or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)

    @timeout.setter
    @abc.abstractmethod
    def timeout(self: t.Self, value: float) -> None:
        """Set timeout in seconds for network operations."""
        msg = "Implement timeout setter or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)

    @property
    @abc.abstractmethod
    def max_retries(self: t.Self) -> int:
        """Get maximum number of retries for network operations."""
        msg = "Implement max_retries property or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)

    @max_retries.setter
    @abc.abstractmethod
    def max_retries(self: t.Self, value: int) -> None:
        """Set maximum number of retries for network operations."""
        msg = "Implement max_retries setter or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)

    @property
    @abc.abstractmethod
    def retry_delay(self: t.Self) -> float:
        """Get delay between retries in seconds."""
        msg = "Implement retry_delay property or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)

    @retry_delay.setter
    @abc.abstractmethod
    def retry_delay(self: t.Self, value: float) -> None:
        """Set delay between retries in seconds."""
        msg = "Implement retry_delay setter or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)

    @property
    @abc.abstractmethod
    def api_key(self: t.Self) -> str | None:
        """Get API key for authentication."""
        msg = "Implement api_key property or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)

    @api_key.setter
    @abc.abstractmethod
    def api_key(self: t.Self, value: str | None) -> None:
        """Set API key for authentication."""
        msg = "Implement api_key setter or inherit from NetworkConfigMixin for default implementation"
        raise NotImplementedError(msg)


class AbstractCloseFeed(AbstractFeed):
    """Interface for drivers implementing retrieval of close prices.

    Note those closes may be (and often are) available after the close only.
    They still qualify as close prices.
    """

    def __init__(
        self: t.Self,
        name: str,
        source: str,
        as_of_date: dt.date | None = None,
        batch_size: int | None = None,
    ) -> None:
        """Initialize the close class.

        :param name: passed to AbstractFeed.
        :param source: passed to AbstractFeed.
        :param as_of_date: as of date being looked for.
        :param batch_size: number of securities in each request.

        """
        self.as_of_date = as_of_date or today()
        self.batch_size = batch_size or 100
        AbstractFeed.__init__(self, name, source)

    @abc.abstractmethod
    def fetch_close_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: dt.date | None = None,
        **kwargs: t.Any,
    ) -> t.Generator[Price, None, None]:
        """Retrieve current prices.

        :param symbols: symbols to looked up.
        :param date: date for which to look up prices (defaults to as_of_date).

        Yield a generator iterating over Price.

        """
        raise NotImplementedError


class AbstractIntraDayFeed(AbstractFeed):
    """Interface for drivers implementing retrieval of intraday prices."""

    def __init__(
        self: t.Self,
        name: str,
        source: str,
    ) -> None:
        """Initialize."""
        AbstractFeed.__init__(self, name, source)

    @abc.abstractmethod
    def fetch_intraday_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        as_of_ts: dt.datetime | None = None,
        fields: t.Sequence[Field] | None = None,
    ) -> t.Generator[Price, None, None]:
        """Retrieve current prices.

        :param symbols: symbols looked up
        :param as_of_ts: expected as_of_date
        :param fields: optional list of fields to retrieve

        :return: generator of Price objects
        """
        raise NotImplementedError


class AbstractHistoricalFeed(AbstractFeed):  # pylint: disable=R0903
    """Interface of historical price feed.

    Derived class must implement:

    def fetch_hist_prices(
        self,
        symbol,
        end_date=None,
        begin_date=None,
        frequency=None,
        splits=None,
        distributions=None,
    )
    """

    def __init__(
        self: t.Self,
        name: str,
        source: str,
    ) -> None:
        """Initialize the feed."""
        AbstractFeed.__init__(self, name, source)

    # pylint: disable=R0913
    @abc.abstractmethod
    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,
        splits: t.Sequence[Split] | None = None,
        distributions: t.Sequence[Distribution] | None = None,
    ) -> t.Generator[Price, None, None]:
        """Retrieve price history.

        :return: generator of Price objects

        """
        raise NotImplementedError


class AbstractDistributionFeed(AbstractFeed):
    """Interface of distribution feeds."""

    def __init__(
        self: t.Self,
        name: str,
        source: str,
    ) -> None:
        """Initialize the feed."""
        AbstractFeed.__init__(self, name, source)

    @abc.abstractmethod
    def fetch_hist_dists(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[Distribution, None, None]:
        """Retrieve distribution history (dividend, capital gains, ...).

        :param symbol: Security symbol
        :param end_date: End date for the period to retrieve (inclusive)
        :param begin_date: Start date for the period to retrieve (inclusive)
        :return: Generator of Distribution objects
        """
        raise NotImplementedError


class AbstractSplitFeed(AbstractFeed):
    """Interface of distribution feeds."""

    def __init__(
        self: t.Self,
        name: str,
        source: str,
    ) -> None:
        """Initialize the feed."""
        AbstractFeed.__init__(self, name, source)

    @abc.abstractmethod
    def fetch_hist_splits(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[Split, None, None]:
        """Retrieve split history.

        :param symbol: Security symbol
        :param end_date: End date for the period to retrieve (inclusive)
        :param begin_date: Start date for the period to retrieve (inclusive)

        :return: generator of Split objects
        """
        raise NotImplementedError


class AbstractShortInterestFeed(AbstractFeed):
    """Interface of short interest feeds."""

    def __init__(
        self: t.Self,
        name: str,
        source: str,
    ) -> None:
        """Initialize the feed."""
        AbstractFeed.__init__(self, name, source)

    @abc.abstractmethod
    def fetch_shortints(
        self: t.Self,
        symnexchs: list[tuple[str, str, str]],
        as_of_date: dt.date,
    ) -> t.Generator[ShortInterest, None, None]:
        """Retrieve short interests.

        :param symnexchs: List of (symbol, exchange, exchange_code) triplets to identify stocks
        :param as_of_date: Date to retrieve short interest for

        :return: Generator of ShortInterest objects
        """
        raise NotImplementedError


class AbstractSecurityFeed(AbstractFeed):
    """Interface to security feed.

    Retrieve security information with this feed.

    """

    def __init__(
        self: t.Self,
        name: str,
        source: str,
    ) -> None:
        """Initialize the feed."""
        AbstractFeed.__init__(self, name, source)

    @abc.abstractmethod
    def fetch_securities(
        self: t.Self,
        symbols: t.Iterable[str],
    ) -> t.Generator[Security, None, None]:
        """Retrieve security information.

        :param symbols: Symbols to retrieve information for
        :return: Generator of Security objects
        """
        raise NotImplementedError


class FeedType(enum.Enum):
    """Identify feed type when calling get_feed()."""

    CLOSE = enum.auto()
    INTRADAY = enum.auto()
    HISTORICAL = enum.auto()
    DISTRIBUTION = enum.auto()
    SPLIT = enum.auto()
    SECURITY = enum.auto()
    SHORT = enum.auto()

    def __str__(self: t.Self) -> str:
        """Return simpe string representation so it plays nice with pytest (no dot, no FeedType)."""
        return self.name.lower()


def build_feed(
    feed_name: str,
    feed_type: FeedType,
    **kwargs: t.Any | None,
) -> AbstractFeed:
    """Create and return a new instance of a feed class.

    Consider using build_* functions instead because they return a typed feed.

    :param feed_name: module name with entry point(s) to build concrete feeds
    :param feed_type: type of feed
    :param kwargs: additional parameters passed to the concrete feed constructor

    :return: An instance of the requested feed type
    :raises ImportError: if the module cannot be imported
    :raises ValueError: if no valid feed can be created
    :raises AttributeError: if the module doesn't implement the requested feed builder
    """
    if not isinstance(feed_type, FeedType):
        msg = f"feed_type must be a FeedType enum, got {type(feed_type)}"
        raise TypeError(msg)
    if not isinstance(feed_name, str):
        msg = f"feed_name must be a string, got {type(feed_name)}"
        raise TypeError(msg)

    log.info("loading %s %s ...", feed_name, feed_type)
    module: t.Any = None
    try:
        module = importlib.import_module(feed_name)
    except ImportError:
        log.exception("cannot import %s", feed_name)
        raise

    builder_map = {
        FeedType.CLOSE: "build_close_feed",
        FeedType.INTRADAY: "build_intraday_feed",
        FeedType.HISTORICAL: "build_historical_feed",
        FeedType.DISTRIBUTION: "build_distribution_feed",
        FeedType.SPLIT: "build_split_feed",
        FeedType.SECURITY: "build_security_feed",
        FeedType.SHORT: "build_short_interest_feed",
    }

    builder_name = builder_map[feed_type]
    try:
        builder = getattr(module, builder_name)
        feed = builder(**kwargs)
    except AttributeError:
        log.exception("Module %s doesn't implement %s", feed_name, builder_name)
        raise

    if not feed:
        msg = f"failed to retrieve a valid {feed_type} feed in {feed_name}"
        raise ValueError(msg)

    return feed


def build_close_feed(
    feed_name: str,
    **kwargs: t.Any,
) -> AbstractCloseFeed:
    """Forward call to get_feed() for and cast result to AbstractCloseFeed."""
    return t.cast(
        "AbstractCloseFeed",
        build_feed(
            feed_name,
            FeedType.CLOSE,
            **kwargs,
        ),
    )


def build_intraday_feed(
    feed_name: str,
    **kwargs: t.Any,
) -> AbstractIntraDayFeed:
    """Forward call to get_feed() for and cast result to AbstractIntraDayFeed."""
    return t.cast(
        "AbstractIntraDayFeed",
        build_feed(
            feed_name,
            FeedType.INTRADAY,
            **kwargs,
        ),
    )


def build_historical_feed(
    feed_name: str,
    **kwargs: t.Any,
) -> AbstractHistoricalFeed:
    """Forward call to get_feed() for and cast result to AbstractHistoricalFeed."""
    return t.cast(
        "AbstractHistoricalFeed",
        build_feed(
            feed_name,
            FeedType.HISTORICAL,
            **kwargs,
        ),
    )


def build_distribution_feed(
    feed_name: str,
    **kwargs: t.Any,
) -> AbstractDistributionFeed:
    """Forward call to get_feed() for and cast result to AbstractDistributionFeed."""
    return t.cast(
        "AbstractDistributionFeed",
        build_feed(
            feed_name,
            FeedType.DISTRIBUTION,
            **kwargs,
        ),
    )


def build_split_feed(
    feed_name: str,
    **kwargs: t.Any,
) -> AbstractSplitFeed:
    """Forward call to get_feed() for and cast result to AbstractSplitFeed."""
    return t.cast(
        "AbstractSplitFeed",
        build_feed(
            feed_name,
            FeedType.SPLIT,
            **kwargs,
        ),
    )


def build_security_feed(
    feed_name: str,
    **kwargs: t.Any,
) -> AbstractSecurityFeed:
    """Forward call to get_feed() for and cast result to AbstractSecurityFeed."""
    return t.cast(
        "AbstractSecurityFeed",
        build_feed(
            feed_name,
            FeedType.SECURITY,
            **kwargs,
        ),
    )


def build_short_interest_feed(
    feed_name: str,
    **kwargs: t.Any,
) -> AbstractShortInterestFeed:
    """Forward call to get_feed() for and cast result to AbstractShortInterestFeed."""
    return t.cast(
        "AbstractShortInterestFeed",
        build_feed(
            feed_name,
            FeedType.SHORT,
            **kwargs,
        ),
    )


def to_csv(dataclass_obj: t.Any) -> str:
    """Return a CSV representation of a dataclass object.

    :param dataclass_obj: An instance of a dataclass
    :return: A CSV string with all dataclass fields
    :raises TypeError: If the object is not a dataclass
    """
    if not dataclasses.is_dataclass(dataclass_obj):
        msg = f"Expected a dataclass instance, got {type(dataclass_obj)}"
        raise TypeError(msg)

    return ",".join(str(getattr(dataclass_obj, field.name) or "") for field in dataclasses.fields(dataclass_obj))


class FeedError(RuntimeError):
    """Error related to a feed behaviour (E.g. not available)."""

    def __init__(self: t.Self, msg: str) -> None:
        super().__init__(msg)
