"""Retrieves data from Yahoo! Finance via yahooquery module."""

__author__ = "Jerome Lecomte"
__license__ = "MIT"

import datetime as dt
import logging
import typing as t
import zoneinfo
from decimal import Decimal as D  # noqa: N817

import pandas as pd
import yahooquery as yq

# Needed to be handle parsing times like 4:00pm and such.
import finquotes as fq

SOURCE = "finquotes.yahooquery"

log = logging.getLogger(SOURCE)

# Market close hour (4 PM in 24-hour format)
MARKET_CLOSE_HOUR = 16

# Expected number of elements in dataframe index tuple (symbol, timestamp)
EXPECTED_INDEX_TUPLE_LENGTH = 2

fields_map = {
    fq.Field.SYMBOL: "symbol",
    fq.Field.NAME: "shortName",
    fq.Field.ASK: "ask",
    fq.Field.ASK_SIZE: "askSize",
    fq.Field.BID: "bid",
    fq.Field.BID_SIZE: "bidSize",
    fq.Field.TIME_STAMP: "regularMarketTime",
    fq.Field.DATE: "regularMarketTime",
    fq.Field.TIME: "regularMarketTime",
    fq.Field.EX_DATE: "dividenDate",
    fq.Field.VOLUME: "regularMarketVolume",
    fq.Field.EXCHANGE: "exchange",
    fq.Field.N_SHARES_OUTSTANDING: "sharesOutstanding",
    fq.Field.PCT_CHANGE: "regularMarketChangePercent",
    fq.Field.CHANGE: "regularMarketChange",
    fq.Field.PREVIOUS_CLOSE: "regularMarketPreviousClose",
    fq.Field.OPEN: "regularMarketOpen",
    fq.Field.HIGH: "regularMarketDayHigh",
    fq.Field.LOW: "regularMarketDayLow",
    fq.Field.CLOSE: "regularMarketPrice",
    fq.Field.CURRENCY: "currency",
}

# 8 decimal places.
DEFAULT_RATIO_QUANTITY_QUANTIZE = D("0.00000001")


def to_yahoo_timestamp(date: dt.date) -> str:
    """Convert the date to as_of_date since epoch.

    Yahoo! stores data as timestamp of seconds sine epoch 1st Jan 1970.

    :param begin_ts: begin time stamp to convert to time stamp.
    :param end_ts: end time stamp to convert to time stamp.

    :return: time stamp of the day after date at 00:00 UTC.

    """
    ts = dt.datetime.combine(date, dt.time(), tzinfo=dt.UTC)
    return f"{ts.timestamp():.0f}"


def from_yahoo_timestamp(datestr: str, tzname: str) -> dt.datetime:
    """Convert a string representing an integer of seconds since epoch.

    Localize to yahoo.timezone.

    :return: datetime.datetime

    """
    try:
        n_secs = int(datestr)
        # yahooquery returns seconds since epoch in EST.
        # Could not find a better way to mark the tz as such.
        return dt.datetime.fromtimestamp(n_secs, tz=dt.UTC).replace(
            tzinfo=zoneinfo.ZoneInfo(tzname),
        )
    except (ValueError, OverflowError) as err:
        fq.log.warning("failed to convert %s to a dt.datetime: %s", datestr, err)
        raise


def quote_to_price(symbol: str, result: dict[str, t.Any]) -> fq.Price | None:
    """Convert yahoo_query dict of single quote dict to a finquotes.Price."""
    log.debug("quote_to_price: symbol=%s result=%s", symbol, result)
    try:
        result_datetime: dt.datetime = from_yahoo_timestamp(
            result["regularMarketTime"],
            result["exchangeTimezoneName"],
        )
        return fq.Price(
            symbol=symbol,
            date=result_datetime,
            close=fq.to_decimal(result["regularMarketPrice"]),
            open_=fq.to_decimal_or_none(result["regularMarketOpen"]),
            low=fq.to_decimal_or_none(result["regularMarketDayLow"]),
            high=fq.to_decimal_or_none(result["regularMarketDayHigh"]),
            volume=(int(result["regularMarketVolume"]) if result["regularMarketVolume"] is not None else None),
            source="finquotes.yahooquery",
        )
    except (KeyError, ValueError, AssertionError, TypeError) as err:
        fq.log.warning("failed to convert %s to a finquotes.Price: %s", result, err)
        return None


def quotes_to_prices(
    result: dict[str, t.Any],
) -> t.Generator[fq.Price | None, None, None]:
    """Convert yahoo_query dict quotes string to a list of finquotes.Price."""
    if not isinstance(result, dict):
        fq.log.warning("invalid result: dict expected, got %s", result)
        msg = f"invalid result: dict expected, got {result}"
        raise fq.FeedError(msg)
    yield from (quote_to_price(quote, result[quote]) for quote in result)


def validate_price(
    price: fq.Price | None,
    as_of_date: dt.date,
    min_as_of_ts: dt.datetime,
) -> bool:
    """Validate that the price is not stale."""
    if not price:
        return False
    if not price.symbol:
        fq.log.warning("price %s has no symbol, skipping", price)
        return False
    if isinstance(as_of_date, dt.datetime):
        msg = "as_of_date must be a dt.date, got dt.datetime"
        raise TypeError(msg)
    if price.date != as_of_date:
        fq.log.warning(
            "price %s %s is different from expected as_of_date %s, skipping",
            price.symbol,
            price.date,
            as_of_date,
        )
        return False
    if price.time is not None:
        price_as_of_ts = dt.datetime.combine(price.date, price.time)
        if price.time.hour < MARKET_CLOSE_HOUR and price_as_of_ts < min_as_of_ts:
            fq.log.warning(
                "price %s %s is too old as of %s, skipping",
                price.symbol,
                price.date,
                price.time,
            )
            return False
    return True


class YahooQueryCloseFeed(fq.NetworkConfigMixin, fq.AbstractCloseFeed):
    """Implements finquotes.CloseFeed with yahooquery."""

    def __init__(self: t.Self, /, **kwargs: t.Any) -> None:
        """Initialize the YahooQueryCloseFeed."""
        fq.AbstractCloseFeed.__init__(self, __name__, SOURCE, **kwargs)
        fq.NetworkConfigMixin.__init__(self)
        self.to_prices = quotes_to_prices
        self.validate = validate_price

    def fetch_close_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: dt.date | None = None,
        min_as_of_ts: dt.datetime | None = None,
        **kwargs: t.Any,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Adapts fetch_prices to fetch_close_prices function."""
        date = date or self.as_of_date
        min_as_of_ts = min_as_of_ts or dt.datetime.now(
            tz=zoneinfo.ZoneInfo("America/New_York"),
        ) - dt.timedelta(hours=1)
        yield from (
            price
            for price in self.to_prices(yq.Ticker([symbols]).quotes)
            if price and self.validate(price, date, min_as_of_ts=min_as_of_ts)
        )


def to_datetime(date_like: pd.Timestamp | dt.datetime | dt.date) -> dt.date:
    """Convert argument to a dt.date."""
    if isinstance(date_like, pd.Timestamp):
        return date_like.to_pydatetime(warn=True).date()
    if isinstance(date_like, dt.datetime):
        return date_like.date()
    assert isinstance(date_like, dt.date), "cannot convert date to dt.date"
    return date_like


def dataframe_to_prices(
    df: pd.DataFrame,
    begin_date: dt.date,
    end_date: dt.date,
) -> t.Generator[fq.Price, None, None]:
    """Convert yahooquery dataframe to a list of finquotes.Price.

    Args:
    ----
        df: yahooquery dataframe returned by yahooquery.
        begin_date: earliest date to include (inclusive).
        end_date: latest date to include (excluded yahooquery convention).
        price_quantize_places: number of decimal places to quantize prices to.

    """
    for index, row in df.iterrows():
        try:
            assert isinstance(index, tuple)
            assert len(index) == EXPECTED_INDEX_TUPLE_LENGTH
            symbol, timestamp = index
            assert isinstance(
                timestamp,
                pd.Timestamp | dt.datetime | dt.date,
            ), "timestamp must be a pd.Timestamp, dt.datetime, or dt.date"
            date = to_datetime(timestamp)
            rowid = f"{symbol}, {date:%Y-%m-%d}"
            if not symbol:
                log.warning("skipping row %d because symbol is %s", rowid, symbol)
            if date < begin_date or end_date <= date:
                log.warning(
                    "skipping row %s because date is %s: %s",
                    rowid,
                    date,
                    row,
                )
                continue
            price = fq.Price(
                symbol=symbol,
                date=date,
                close=fq.to_decimal(row["close"]),
                open_=fq.to_decimal_or_none(row["open"]),
                low=fq.to_decimal_or_none(row["low"]),
                high=fq.to_decimal_or_none(row["high"]),
                volume=fq.to_int_or_none(row["volume"]),
                source=SOURCE,
            )
            yield price
        except (KeyError, ValueError, AssertionError) as err:
            fq.log.warning(
                "failed to convert row %s: %s to finquotes.Price: %s",
                rowid,
                row.to_dict(),
                err,
            )
            continue


def dataframe_to_distributions(
    df: pd.DataFrame,
) -> t.Generator[fq.Distribution, None, None]:
    """Convert yahooquery dataframe to a list of finquotes.Price of distributions."""
    fq.log.debug("dataframe_to_prices: df=%s", df)
    yield from (
        fq.Distribution(
            symbol=row["symbol"],
            ex_date=to_datetime(row["date"]),
            amount=row["dividends"],
        )
        for _, row in df.reset_index().iterrows()
    )


def dataframe_to_splits(
    df: pd.DataFrame,
    ratio_quantize_places: D | None = None,
) -> t.Generator[fq.Split, None, None]:
    """Convert yahooquery dataframe to a list of finquotes.Price of distributions."""
    fq.log.debug("dataframe_to_prices: df=%s", df)
    if "splits" not in df.columns:
        return
    ratio_quantize_places = ratio_quantize_places or DEFAULT_RATIO_QUANTITY_QUANTIZE
    yield from (
        fq.Split.from_ratio(
            symbol=row["symbol"],
            ex_date=to_datetime(row["date"]),
            ratio=D(row["splits"]).quantize(ratio_quantize_places),
        )
        for _, row in df.loc[df["splits"] != 0, ["splits"]].reset_index().iterrows()
    )


class YahooQueryHistFeed(
    fq.NetworkConfigMixin,
    fq.AbstractHistoricalFeed,
    fq.AbstractDistributionFeed,
    fq.AbstractSplitFeed,
):
    """Implements finquotes.YahooQueryHistoricalFeed with yahooquery."""

    def __init__(self: t.Self, /, **kwargs: t.Any) -> None:
        """Initialize the YahooQueryCloseFeed."""
        fq.AbstractHistoricalFeed.__init__(self, __name__, SOURCE, **kwargs)
        fq.NetworkConfigMixin.__init__(self)
        self.period = None
        self.interval = None

    def get_arguments(
        self: t.Self,
        end_date: dt.date | None,
        begin_date: dt.date | None,
    ) -> dict[str, t.Any]:
        """Return arguments to initialize the feed.

        Increase end_date by one day to include the end_date in the results (yahooquery convention).

        """
        end_date, begin_date = fq.compute_default_dates(end_date, begin_date)
        end_date += dt.timedelta(days=1)
        return {"start": begin_date, "end": end_date}

    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,  # noqa: ARG002
        splits: t.Sequence[fq.Split] | None = None,  # noqa: ARG002
        distributions: t.Sequence[fq.Distribution] | None = None,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Adapts fetch_prices to fetch_close_prices function."""
        args = self.get_arguments(end_date, begin_date)
        yield from dataframe_to_prices(
            yq.Ticker([symbol]).history(**args),
            args["start"],
            args["end"],
        )

    def fetch_hist_dists(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Distribution, None, None]:
        """Adapts fetch_prices to fetch_close_prices function."""
        args = self.get_arguments(end_date, begin_date)
        df = yq.Ticker([symbol]).dividend_history(**args)
        assert isinstance(df, pd.DataFrame), "yahooquery did not return a DataFrame"
        yield from dataframe_to_distributions(df)

    def fetch_hist_splits(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Split, None, None]:
        """Adapts fetch_prices to fetch_close_prices function."""
        args = self.get_arguments(end_date, begin_date)
        yield from dataframe_to_splits(yq.Ticker([symbol]).history(**args))


def build_close_feed(*args: t.Any, **kwargs: t.Any) -> YahooQueryCloseFeed:
    """Forward to build_feed."""
    return YahooQueryCloseFeed(*args, **kwargs)


def build_historical_feed(*args: t.Any, **kwargs: t.Any) -> YahooQueryHistFeed:
    """Forward to build_feed."""
    return YahooQueryHistFeed(*args, **kwargs)


def build_distribution_feed(*args: t.Any, **kwargs: t.Any) -> YahooQueryHistFeed:
    """Forward to build_feed."""
    return YahooQueryHistFeed(*args, **kwargs)


def build_split_feed(*args: t.Any, **kwargs: t.Any) -> YahooQueryHistFeed:
    """Forward to build_feed."""
    return YahooQueryHistFeed(*args, **kwargs)
