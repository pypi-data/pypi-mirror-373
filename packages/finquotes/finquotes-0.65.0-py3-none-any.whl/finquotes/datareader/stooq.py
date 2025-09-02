"""Interface to pandas pddatareader.

:seealso: https://pandas-datareader.readthedocs.io/en/latest/

"""

__author__ = "Jerome Lecomte"
__license__ = "MIT"


import datetime as dt
import typing as t

import pandas_datareader as pdr

import finquotes as fq

SOURCE = "finquotes.datareader.stooq"


class PandasDataReaderFeed(fq.NetworkConfigMixin, fq.AbstractHistoricalFeed, fq.AbstractCloseFeed):
    """Historical close prices from pandas datareader."""

    def __init__(
        self: t.Self,
        as_of_date: dt.date | None = None,
        **kwargs: t.Any,
    ) -> None:
        """Initialize the feed."""
        network_kwargs, other_kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        fq.AbstractHistoricalFeed.__init__(self, __name__, SOURCE, **other_kwargs)
        fq.AbstractCloseFeed.__init__(self, __name__, SOURCE, **other_kwargs)
        self.as_of_date = as_of_date or fq.today()

    def subsource(self: t.Self) -> str:
        """Remove the finquotes.datareader. part of the source."""
        return SOURCE[len("finquotes.datareader.") :]

    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,
        splits: t.Sequence[fq.Split] | None = None,
        distributions: t.Sequence[fq.Distribution] | None = None,
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch historical prices."""
        fq.log.debug(
            f"fetch_hist_prices({symbol}, {begin_date}, {end_date}, {frequency}, {splits}, {distributions})",
        )
        df = pdr.data.DataReader(symbol, self.subsource(), begin_date, end_date)
        for date, row in df.iterrows():
            yield fq.Price(
                symbol=symbol,
                date=date.to_pydatetime().date(),
                close=fq.to_decimal(row["Close"]),
                open_=fq.to_decimal_or_none(row["Open"]),
                high=fq.to_decimal_or_none(row["High"]),
                low=fq.to_decimal_or_none(row["Low"]),
                volume=fq.to_int_or_none(row["Volume"]),
                source=self.source,
            )

    def fetch_close_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: dt.date | None = None,
        **kwargs: t.Any,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch close prices."""
        df = pdr.data.DataReader(symbols, self.subsource(), date, date).stack(
            future_stack=True,
        )
        for (as_of_date, symbol), row in df.iterrows():
            yield fq.Price(
                symbol=symbol,
                date=as_of_date.to_pydatetime().date(),
                close=fq.to_decimal(row["Close"]),
                open_=fq.to_decimal_or_none(row["Open"]),
                high=fq.to_decimal_or_none(row["High"]),
                low=fq.to_decimal_or_none(row["Low"]),
                volume=fq.to_int_or_none(row["Volume"]),
                source=self.source,
            )


def build_historical_feed(*args: t.Any, **kwargs: t.Any) -> PandasDataReaderFeed:
    """Forward to build_feed."""
    return PandasDataReaderFeed(*args, **kwargs)


def build_close_feed(*args: t.Any, **kwargs: t.Any) -> PandasDataReaderFeed:
    """Forward to build_feed."""
    return PandasDataReaderFeed(*args, **kwargs)
