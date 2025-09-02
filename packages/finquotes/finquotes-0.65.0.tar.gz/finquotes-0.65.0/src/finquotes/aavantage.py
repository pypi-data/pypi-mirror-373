"""AlphaVantageMixin API.

See https://www.alphavantage.co/

"""

__author__ = "Jerome Lecomte"
__license__ = "MIT"


import contextlib
import datetime as dt
import typing as t
from decimal import Decimal as D  # noqa: N817

import requests

import finquotes as fq

SOURCE = "finquotes.aavantage"


def _open_url(*args: t.Any, **kwargs: t.Any) -> str:
    """Leverages requests to interact with AlphaVantageMixin API."""
    # Extract timeout to make it explicit for mypy
    timeout = kwargs.pop("timeout", 30.0)
    response = requests.get(*args, timeout=timeout, **kwargs)
    fq.log.debug("fetched %s", response.url)
    response.raise_for_status()
    return response.text


class AlphaVantageMixinFeed(fq.NetworkConfigMixin):
    """AlphaVantageMixin feed."""

    base_url = "https://www.alphavantage.co/query"

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize AlphaVantageMixin feed."""
        # Don't call super().__init__() here - let the concrete classes handle initialization order

    def parse_hist_price(
        self: t.Self,
        symbol: str,
        date: dt.date,
        values: list[str],
    ) -> fq.Price:
        """Parse specific line and return finquotes.Price."""
        volume = None
        with contextlib.suppress(IndexError):
            volume = int(values[5])
        open_, high, low, close = values[:4]
        return fq.Price(
            symbol,
            date,
            close=D(close),
            open_=D(open_),
            high=D(high),
            low=D(low),
            volume=volume,
            source=SOURCE,
        )

    def parse_hist_dist(
        self: t.Self,
        symbol: str,
        date: dt.date,
        values: list[str],
    ) -> fq.Distribution | None:
        """Parse specific line and return finquotes.Distribution."""
        try:
            dividend_amt = D(values[6])
        except IndexError:
            return None
        if dividend_amt == D("0.0"):
            return None
        return fq.Distribution(
            symbol,
            date,
            dividend_amt,
        )

    def parse_hist_split(
        self: t.Self,
        symbol: str,
        date: dt.date,
        values: list[str],
    ) -> fq.Split | None:
        """Parse specific line and return finquotes.Distribution."""
        try:
            split_factor = D(values[7])
        except IndexError:
            return None
        if split_factor == D("1.0"):
            return None
        new_q, old_q = split_factor.as_integer_ratio()
        return fq.Split(symbol, date, new_quantity=new_q, old_quantity=old_q)

    def fetch_url_content(
        self: t.Self,
        symbol: str,
        begin_date: dt.date,
        frequency: str | None,
    ) -> str:
        """Compute begin_date, end_date and makes the call to the web api.

        :param symbol: ticker of the security.
        :param begin_date: start of the period of interest.
        :param frequency: defaults to d[aily].  Can be w[eekly] or m[onthly].

        :return: content as text

        """
        if frequency is None:
            frequency = "d"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "datatype": "csv",
            "apikey": fq.get_api_key(SOURCE),
        }
        compact_days = 90 * 5 / 7
        if frequency == "w":
            params["funtion"] = "TIME_SERIES_WEEKLY_ADJUSTED"
            compact_days = 90 * 5
        elif frequency == "m":
            params["funtion"] = "TIME_SERIES_MONTHLY_ADJUSTED"
            compact_days = 90 * 5 * 30
        # If we requires_more_than_hundred_rows:
        if begin_date < fq.today() - dt.timedelta(days=compact_days):
            params["outputsize"] = "full"
        url = self.base_url
        return _open_url(url, params=params, timeout=self.timeout)

    def fetch_all(
        self: t.Self,
        symbol: str,
        parse_line: t.Callable,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,
    ) -> t.Generator[fq.Price | fq.Distribution | fq.Split, None, None]:
        """Retrieve price history.

        :param symbol: ticker of the security.
        :param parse_line: method to use to retrieve data of interest.
        :param end_date: end of period of interest.
        :param begin_date: begining of period of interest.
        :param frequency: defaults to d[aily].  Can be w[eekly] or m[onthly].

        :return: generator of Price objects

        """
        end_date, begin_date = fq.compute_default_dates(end_date, begin_date)
        content = self.fetch_url_content(symbol, begin_date, frequency)
        for line in content.split("\n"):
            if not line or line.startswith("timestamp"):
                continue
            try:
                ts_str, *values = line.split(",")
                date = dt.date.fromisoformat(ts_str)
                if date < begin_date:
                    break
                if end_date < date:
                    continue
                data_point = parse_line(symbol, date, values)
                if data_point is None:
                    continue
                yield data_point
            except ValueError:
                fq.log.warning("%s: failed to process line: %s", symbol, line)


class AlphaVantageMixinHistPriceFeed(AlphaVantageMixinFeed, fq.AbstractHistoricalFeed):
    """Specialize AlphaVantageMixinFeed for historical price retrieval."""

    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        network_kwargs, other_kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        fq.AbstractHistoricalFeed.__init__(self, __name__, SOURCE)

    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,
        splits: t.Sequence[fq.Split] | None = None,  # noqa: ARG002
        distributions: t.Sequence[fq.Distribution] | None = None,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve price history.

        :param symbol: ticker of the security.
        :param end_date: if not specified, the algorithm uses today.
        :param begin_date: if not specified, the algorithm uses end_date.
        :param frequency: defaults to d[aily].  Can be w[eekly] or m[onthly].

        :return: generator of Price objects

        """
        for value in self.fetch_all(
            symbol,
            self.parse_hist_price,
            end_date,
            begin_date,
            frequency,
        ):
            if isinstance(value, fq.Price):
                yield value
            else:
                fq.log.info(
                    "expected fq.Price, not %s: %s",
                    type(value).__name__,
                    value,
                )


class AlphaVantageMixinDistFeed(AlphaVantageMixinFeed, fq.AbstractDistributionFeed):
    """Specialize AlphaVantageMixinFeed for historical distributions retrieval."""

    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        network_kwargs, other_kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        fq.AbstractDistributionFeed.__init__(self, __name__, SOURCE)

    def fetch_hist_dists(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Distribution, None, None]:
        """Retrieve distribution history.

        :param symbol: ticker of the security.
        :param end_date: if not specified, the algorithm uses today.
        :param begin_date: if not specified, the algorithm uses end_date.

        :return: generator of Distribution objects

        """
        for value in self.fetch_all(symbol, self.parse_hist_dist, end_date, begin_date):
            if isinstance(value, fq.Distribution):
                yield value
            else:
                fq.log.info(
                    "expected fq.Distribution, not %s: %s",
                    type(value).__name__,
                    value,
                )


class AlphaVantageMixinSplitFeed(AlphaVantageMixinFeed, fq.AbstractSplitFeed):
    """Specialize AlphaVantageMixinFeed for historical splits."""

    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        network_kwargs, other_kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        fq.AbstractSplitFeed.__init__(self, __name__, SOURCE)

    def fetch_hist_splits(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Split, None, None]:
        """Retrieve split history.

        :param symbol: ticker of the security.
        :param end_date: if not specified, the algorithm uses today.
        :param begin_date: if not specified, the algorithm uses end_date.

        :return: generator of Distribution objects

        """
        for value in self.fetch_all(
            symbol,
            self.parse_hist_split,
            end_date,
            begin_date,
        ):
            if isinstance(value, fq.Split):
                yield value
            else:
                fq.log.info(
                    "expected fq.Split, not %s: %s",
                    type(value).__name__,
                    value,
                )


def build_historical_feed(
    *args: t.Any,
    **kwargs: t.Any,
) -> AlphaVantageMixinHistPriceFeed:
    """Create new AlphaVantageMixinFeed for historical prices."""
    return AlphaVantageMixinHistPriceFeed(*args, **kwargs)


def build_distribution_feed(*args: t.Any, **kwargs: t.Any) -> AlphaVantageMixinDistFeed:
    """Create new AlphaVantageMixinFeed for historical prices."""
    return AlphaVantageMixinDistFeed(*args, **kwargs)


def build_split_feed(*args: t.Any, **kwargs: t.Any) -> AlphaVantageMixinSplitFeed:
    """Create new AlphaVantageMixinFeed for splits."""
    return AlphaVantageMixinSplitFeed(*args, **kwargs)
