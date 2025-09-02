"""Retrieves data from Yahoo! Finance."""

__author__ = "Jerome Lecomte"
__license__ = "MIT"


import datetime as dt
import functools
import typing as t
from collections.abc import Generator, Sequence
from decimal import Decimal as D  # noqa: N817

import requests

import finquotes as fq

get_api_key = functools.partial(fq.get_api_key, api_name="quandl")
SOURCE = "finquotes.quandl"


class QuandlFeedMixin(fq.NetworkConfigMixin):
    """Finquotes feed to download data from Quandl.

    See http://www.quandl.com

    You will need and API key to be able to use that feed.

    Implements both historical and close price retrieval interface.

    """

    base_url = "https://www.quandl.com/api/v3"
    date_fmt = "%Y-%m-%d"

    def __init__(
        self: t.Self,
        data_set: str | None = None,
        **kwargs: t.Any,
    ) -> None:
        """Initialize quandl API.

        :param api_key: Quandl API key.
        :type api_key: str or None
        :param str dataset: Date set of interest (defaults to WIKI)

        If not specified the API key will be looked up in the
        FINQUOTES_QUANDL_API_KEY variable or in the file apikeys.txt.

        See also: `finquotes.quandl.get_api_key`

        """
        network_kwargs, _ = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        if self.api_key is None:
            self.api_key = get_api_key()
        self.data_set = data_set or "WIKI"

    def fetch_hist_price(self: t.Self, symbol: str, line: str) -> fq.Price:
        """Convert line returned by quandl to HistoricalPrice."""
        date_str, open_, high, low, close, volume, *_ = line.split(",")
        date = dt.date.fromisoformat(date_str)
        return fq.Price(
            symbol,
            date,
            D(close),
            open_=D(open_),
            low=D(low),
            high=D(high),
            volume=fq.to_int_or_none(volume),
            source=SOURCE,
        )

    def fetch_close_price(self: t.Self, line: str) -> fq.Price:
        """Convert line returned by quandl to HistoricalPrice."""
        symbol, date_str, open_, high, low, close, volume, *_ = line.split(",")
        date = dt.date.fromisoformat(date_str)
        return fq.Price(
            symbol,
            date,
            D(close),
            open_=D(open_),
            low=D(low),
            high=D(high),
            volume=fq.to_int_or_none(volume),
            source=SOURCE,
        )


class QuandlHistFeed(QuandlFeedMixin, fq.AbstractHistoricalFeed):
    """Historical feed from Quandl."""

    def __init__(
        self: t.Self,
        data_set: str | None = None,
        **kwargs: t.Any,
    ) -> None:
        """Initialize quandl API.

        :param api_key: Quandl API key.
        :param str dataset: Date set of interest (defaults to WIKI)

        If not specified the API key will be looked up in the
        FINQUOTES_QUANDL_API_KEY variable or in the file apikeys.txt.

        See also: `finquotes.quandl.get_api_key`

        """
        data_set = data_set or "WIKI"
        QuandlFeedMixin.__init__(
            self,
            data_set=data_set,
            **kwargs,
        )
        fq.AbstractHistoricalFeed.__init__(
            self,
            __name__,
            SOURCE + "/" + data_set,
        )

    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,  # noqa: ARG002
        splits: t.Sequence[fq.Split] | None = None,  # noqa: ARG002
        distributions: t.Sequence[fq.Distribution] | None = None,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve prices from  Quandl.

        :param str symbol: symbol to get prices for
        :param datetime.date begin_date: start date of the serie
        :param datetime.date end_date: end date of the serie

        If end_date is not specified, it defaults to today. If begin_date is
        not specified, it defaults to end_date.

        """
        assert isinstance(symbol, str), f"expected str, not {type(symbol)}"
        if not end_date:
            end_date = fq.today()
        if not begin_date:
            begin_date = end_date
        params = (
            f"start_date={begin_date.strftime(self.date_fmt)}"
            f"&end_date={end_date.strftime(self.date_fmt)}"
            f"&api_key={self.api_key}"
        )
        url = f"{self.base_url}/datasets/{self.data_set}/{symbol}/data.csv?{params}"
        fq.log.debug("fetching %s...", url)
        response = requests.get(url, timeout=self.timeout)
        for line in response.text.split("\n"):
            if not line or line.startswith("Date"):
                continue
            if line.startswith("code"):
                raise ValueError(response.text.split("\n")[1])
            try:
                price = self.fetch_hist_price(symbol, line)
            except ValueError as err:
                fq.log.warn("failed to process %s for %s: %s", line, symbol, err)
                raise
            yield price


def build_historical_feed(*args: t.Any, **kwargs: t.Any) -> QuandlHistFeed:
    """Build finquotes.quandl.HistQuandlFeedMixin."""
    return QuandlHistFeed(*args, **kwargs)


class QuandlCloseFeed(QuandlFeedMixin, fq.AbstractCloseFeed):
    """Close feed from Quandl."""

    def __init__(
        self: t.Self,
        as_of_date: dt.date | None = None,
        api_key: str | None = None,
        data_set: str | None = None,
        **kwargs: t.Any,
    ) -> None:
        """Initialize quandl API.

        :param as_of_date: as of date for retrieval.
        :param api_key: Quandl API key.
        :param str dataset: Date set of interest (defaults to WIKI)

        If not specified the API key will be looked up in the
        FINQUOTES_QUANDL_API_KEY variable or in the file apikeys.txt.

        See also: `finquotes.quandl.get_api_key`

        """
        data_set = data_set or "WIKI"
        quandl_kwargs = {"api_key": api_key, "data_set": data_set}
        fq.AbstractCloseFeed.__init__(
            self,
            __name__,
            SOURCE + "/" + data_set,
            as_of_date=as_of_date,
            **kwargs,
        )
        QuandlFeedMixin.__init__(
            self,
            **quandl_kwargs,
        )

    def fetch_close_prices(
        self: t.Self,
        symbols: Sequence[str],
        date: dt.date | None = None,  # noqa: ARG002
        **kwargs: t.Any,  # noqa: ARG002
    ) -> Generator[fq.Price, None, None]:
        """Retrieve close prices for context as of date.

        :param symbols: symbols whose price is to be retrieved.
        :param date: date for which we want the prices.

        """
        not_found = set(symbols)
        symbols_str = ",".join(symbols)
        params = {
            "date": self.as_of_date.strftime(self.date_fmt),
            "ticker": symbols_str,
            "api_key": self.api_key,
        }
        url = f"{self.base_url}/datatables/{self.data_set}/PRICES.csv"
        response = requests.get(url, params=params, timeout=self.timeout)
        for line in response.text.split("\n"):
            if line.startswith("ticker"):
                continue
            if line.startswith("code"):
                quandl_msg = response.text.split("\n")[1]
                raise RuntimeError(quandl_msg)
            if not line:
                continue
            price = self.fetch_close_price(line)
            not_found.remove(price.symbol)
            yield price
        fq.log.warning("no price found for: %s", ",".join(not_found))


def build_close_feed(*args: t.Any, **kwargs: t.Any) -> QuandlCloseFeed:
    """Build finquotes.quandl.QuandlFeedMixin."""
    return QuandlCloseFeed(*args, **kwargs)
