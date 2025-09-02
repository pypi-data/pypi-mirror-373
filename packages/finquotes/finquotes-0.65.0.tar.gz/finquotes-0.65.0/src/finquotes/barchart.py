"""Retrieve data from http://www.barchartondemand.com."""

__author__ = "Jerome Lecomte"
__license__ = "MIT"


import datetime as dt
import functools
import json
import typing as t
from collections.abc import Sequence
from decimal import Decimal as D  # noqa: N817

import requests
from dateutil import parser as dtparser

import finquotes as fq

SOURCE = "finquotes.barchart"
get_api_key = functools.partial(fq.get_api_key, api_name=SOURCE)


class BarChartMixin(fq.NetworkConfigMixin):
    """Get historical price from barchart."""

    base_url = "http://marketdata.websol.barchart.com"
    index_url = "https://core-api.barchart.com/v1/quotes/get"

    def __init__(
        self: t.Self,
        api_key: str | None = None,
    ) -> None:
        super().__init__()
        self.batch_size = 99
        self.api_key = api_key
        if self.api_key is None:
            self.api_key = get_api_key()

    def get_name(self: t.Self) -> str:
        """Return barchart as the symbolic name."""
        return SOURCE

    def parse_hist_prices_line(
        self: t.Self,
        symbol: str,
        line: str,
    ) -> t.Generator[fq.Price, None, None]:
        """Parse line returned by barchart API."""
        vals = line.split(",")
        vals = [val.strip()[1:-1] for val in vals]  # remove quotes.
        date = dt.date.fromisoformat(vals[2])
        if symbol != vals[0]:
            msg = f"found value {vals[0]} where {symbol} expected in {line}"
            raise ValueError(msg)
        if not vals[6]:
            msg = f"price not found in {line}"
            raise ValueError(msg)
        price = fq.Price(
            symbol=symbol,
            date=date,
            open_=D(vals[3]),
            high=D(vals[4]),
            low=D(vals[5]),
            close=D(vals[6]),
            volume=fq.to_int_or_none(vals[7]),
            source=self.get_name(),
        )
        yield price

    def parse_close_prices_line(
        self: t.Self,
        line: str,
    ) -> t.Generator[fq.Price, None, None]:
        """Parse line returned by barchart API."""
        vals = line.split(",")
        vals = [val.strip()[1:-1] for val in vals]  # remove quotes.
        vals[7] = vals[7][:-6]  # remove time zone for date.
        date = dt.datetime.strptime(vals[7] + "+00:00", "%Y-%m-%dT%H:%M:%S%z").date()
        price = fq.Price(
            symbol=vals[0],
            date=date,
            open_=D(vals[11]),
            high=D(vals[12]),
            low=D(vals[13]),
            close=D(vals[14]),
            volume=fq.to_int_or_none(vals[16]),
            source=self.get_name(),
        )
        yield price

    def fetch_close_prices_batched(
        self: t.Self,
        symbols: list[str],
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve current prices for a batch.

        Note that client should call `fetch_close_prices` instead of this
        function directly.

        :param list(str) symbols: list of `self.batch_size` symbols or less.

        """
        assert len(symbols) <= self.batch_size, "too many symbols"
        url = f"{self.base_url}/getQuote.csv"
        params = {"key": self.api_key or "", "symbols": ",".join(symbols)}
        params = {k: v for k, v in params.items() if v is not None}
        params = {k: str(v) for k, v in params.items()}
        with requests.Session() as session:
            response_text = fq.localhttp.get(session, url, params=params)
        for line in response_text.split("\n"):
            if not line or line.startswith("symbol"):
                continue
            try:
                yield from self.parse_close_prices_line(line)
            except (IndexError, TypeError, ValueError) as err:
                fq.log.warn("failed to process %d: %s", line, err)

    def __fetch_index_prices_in(
        self: t.Self,
        page: str,
        symbols: set[str],
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve prices in a partcular barchart page.

        :param str page: page name to fetch.
        :param set(str) symbols: remaining symbols to be fetched.

        """
        params = {
            "list": page,
            "fields": (
                "symbol,symbolName,lastPrice,priceChange,openPrice,highPrice,lowPrice,tradeTime,symbolCode,symbolType"
            ),
            "orderBy": "",
            "orderDir": "desc",
            "page": "1",
            "limit": "100",
            "raw": "0",
        }
        params = {k: v for k, v in params.items() if v is not None}
        params = {k: str(v) for k, v in params.items()}
        with requests.Session() as session:
            response_text = fq.localhttp.get(session, self.index_url, params)
        content = json.loads(response_text)
        if content["errors"]:
            fq.log.warning(content["errors"])
        data = content["data"]
        for value in data:
            if value["symbol"] not in symbols:
                continue
            try:
                trade_time = dtparser.parse(value["tradeTime"])
                if not trade_time.tzinfo:
                    trade_time = trade_time.replace(tzinfo=dt.UTC)
            except (ValueError, TypeError, OverflowError) as error:
                fq.log.info(
                    "failed to parse %s as datetime: %s",
                    value["tradeTime"],
                    error,
                )
                continue
            symbol = value["symbol"]
            price = fq.Price(
                symbol=symbol,
                date=trade_time.date(),
                close=value["lastPrice"].replace(",", ""),
                open_=value["openPrice"].replace(",", ""),
                low=value["lowPrice"].replace(",", ""),
                high=value["highPrice"].replace(",", ""),
                source=SOURCE,
            )
            symbols.remove(symbol)
            yield price

    def fetch_index_prices(
        self: t.Self,
        symbols: set[str],
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve index prices.

        :param set(str) symbols: list of symols (all indexes)

        """
        pages = ["stocks.indices.us", "stocks.markets.volatility"]
        for page in pages:
            if len(symbols) == 0:
                break
            yield from self.__fetch_index_prices_in(page, symbols)

    @staticmethod
    def is_index(symbol: str) -> bool:
        """Check if the symbol is an index."""
        return symbol.startswith("$")


class BarChartHistFeed(BarChartMixin, fq.AbstractHistoricalFeed):
    """Retrieve historical prices from barchart."""

    def __init__(self: t.Self, api_key: str | None = None, **kwargs: t.Any) -> None:
        fq.AbstractHistoricalFeed.__init__(self, __name__, SOURCE, **kwargs)
        BarChartMixin.__init__(self, api_key=api_key, **kwargs)

    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,  # noqa: ARG002
        splits: Sequence[fq.Split] | None = None,  # noqa: ARG002
        distributions: Sequence[fq.Distribution] | None = None,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve historical prices.

        :param str symbol: symbol of the price serie.
        :param end_date: end of the period.
        :param begin_date: start of the period.
        :param splits: ignored.
        :param distributions: ignored
        :return: list(finquotes.HistoricalPrice)

        """
        end_date, begin_date = fq.compute_default_dates(end_date, begin_date)
        url = f"{self.base_url}/getHistory.csv"
        params = {
            "key": self.api_key or "",
            "symbol": symbol,
            "type": "daily",
            "startDate": begin_date.strftime("%Y%m%d%H%M%S"),
            "endDate": end_date.strftime("%Y%m%d%H%M%S"),
            "splits": "false",
            "dividends": "false",
        }
        params = {k: v for k, v in params.items() if v is not None}
        params = {k: str(v) for k, v in params.items()}
        with requests.Session() as session:
            response_text = fq.localhttp.get(session, url, params=params)
        for line in response_text.split("\n"):
            if not line or line.startswith("symbol"):
                continue
            if "maximum number of requests" in line:
                raise RuntimeError(line)
            try:
                yield from self.parse_hist_prices_line(symbol, line)
            except (IndexError, TypeError, ValueError) as err:
                fq.log.warning("failed to process %d: %s", line, err)


def build_historical_feed(*args: t.Any, **kwargs: t.Any) -> BarChartHistFeed:
    """Return a BarChartHistFeed instance."""
    return BarChartHistFeed(*args, **kwargs)


class BarChartCloseFeed(BarChartMixin, fq.AbstractCloseFeed):
    """Retrieve current prices from barchart."""

    def __init__(
        self: t.Self,
        api_key: str | None = None,
        **kwargs: t.Any,
    ) -> None:
        fq.AbstractCloseFeed.__init__(self, __name__, SOURCE, **kwargs)
        BarChartMixin.__init__(self, api_key=api_key, **kwargs)

    def fetch_close_prices(
        self: t.Self,
        symbols: Sequence[str],
        date: dt.date | None = None,  # noqa: ARG002
        **kwargs: t.Any,
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve current prices.

        :param symbols: symbols looked up.

        Yield a generator iterating over `finquotes.Price`.

        """

        def is_index(symbol: str) -> bool:
            """Check if the symbol is an index."""
            return symbol.startswith("$")

        index_syms, stock_syms = set(), []
        for symbol in symbols:
            if is_index(symbol):
                index_syms.add(symbol)
            else:
                stock_syms.append(symbol)
        yield from self.fetch_index_prices(index_syms, **kwargs)
        for start in range(0, len(stock_syms), self.batch_size):
            finish = start + self.batch_size
            yield from self.fetch_close_prices_batched(
                stock_syms[start:finish],
                **kwargs,
            )


def build_close_feed(*args: t.Any, **kwargs: t.Any) -> BarChartCloseFeed:
    """Return a BarChartCloseFeed instance."""
    return BarChartCloseFeed(*args, **kwargs)
