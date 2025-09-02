"""CSV module.

This module provides a simple interface to ingest prices from CSV files.

Was renamed csvdata from csv because of unresolved conflicts with the builtin csv module.
"""

import csv
import datetime as dt
import sys
import typing as t

from dateutil import parser

import finquotes as fq

SOURCE = "finquotes.csv"


class CsvCloseFeed(fq.NetworkConfigMixin, fq.AbstractCloseFeed):
    """Read close prices from a CSV input.

    Expected input is expected to contain the following columns not necessarily in this order
    but the name of the columns is expected to be as shown:
    - symbol: security ticker or symbol
    - date: date in YYYY-MM-DD format
    - open: open price
    - high: high price
    - low: low price
    - close: close price
    - volume: volume

    """

    def __init__(
        self: t.Self,
        input_: t.IO[str] | None = None,
        **kwargs: t.Any,
    ) -> None:
        """Initialize the CSV feed."""
        network_kwargs, other_kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        fq.AbstractCloseFeed.__init__(self, __name__, SOURCE, **other_kwargs)
        if not input_:
            input_ = sys.stdin
        self.input = input_

    def fetch_close_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: dt.date | None = None,
        **kwargs: t.Any,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch the close prices for the given symbols.

        See fq.AbstractCloseFeed.fetch_close_prices for more details.

        """
        symbols_of_interest = set(symbols)
        lines = [line.rstrip("\r\n") for line in self.input or []]
        csv_reader = csv.DictReader(lines)
        for row in csv_reader:
            if row["symbol"] in symbols_of_interest:
                date = parser.parse(row["date"]).date()
                yield fq.Price(
                    symbol=row["symbol"],
                    date=date,
                    close=row["close"],
                    open_=row["open"],
                    high=row["high"],
                    low=row["low"],
                    volume=fq.to_int_or_none(row["volume"]),
                    source=self.source,
                )

    def to_price(self: t.Self, line: str) -> fq.Price:
        """Convert price as string to a price."""
        symbol, date_str, open_, high, low, close, volume = line.split(",")
        date = dt.date.fromisoformat(date_str)
        return fq.Price(
            symbol,
            date,
            close,
            open_=open_,
            low=low,
            high=high,
            volume=int(volume),
            source=self.source,
        )


def build_close_feed(*args: t.Any, **kwargs: t.Any) -> CsvCloseFeed:
    """Create an EodDataCloseFeed object."""
    return CsvCloseFeed(*args, **kwargs)
