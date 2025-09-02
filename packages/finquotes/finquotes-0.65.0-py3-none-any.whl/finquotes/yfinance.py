"""Retrieves data from Yahoo! Finance using yfinance module."""

__author__ = "Jerome Lecomte"
__license__ = "MIT"

import datetime as dt
import typing as t
import zoneinfo

import yfinance as yf

import finquotes as fq

SOURCE = "finquotes.yfinance"


class YFinanceFeedMixin(fq.NetworkConfigMixin):
    """Retrieves data from Yahoo using yfinance."""

    def __init__(
        self: t.Self,
        as_of_date: dt.date | None = None,
        *,
        auto_adjust: bool = False,
        **kwargs: t.Any,
    ) -> None:
        """Initialize YFinanceFeedMixin."""
        network_kwargs, _ = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        self.as_of_date = as_of_date or fq.today()
        self.auto_adjust = auto_adjust

    @staticmethod
    def split_kwargs(kwargs: dict) -> tuple[dict, dict]:
        """Split kwargs between those known by YFinanceFeedMixin and everything else.

        Return:
        ------
            Tuple of yfinance keyword arguments, then the other keyword arguments.

        """
        yfinance_kwargs, kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        yfinance_kwargs["as_of_date"] = kwargs.pop("as_of_date", None)
        yfinance_kwargs["auto_adjust"] = kwargs.pop("auto_adjust", False)
        return yfinance_kwargs, kwargs

    def mixin_fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,
        tzinfo: zoneinfo.ZoneInfo | None = None,
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch current prices using yfinance."""
        frequency = frequency or "1d"
        end_date = end_date or self.as_of_date
        begin_date = begin_date or end_date
        assert isinstance(begin_date, dt.date), "begin_date must be a date"
        assert isinstance(end_date, dt.date), "end_date must be a date"
        tzinfo = tzinfo or fq.default_timezone()
        ticker = yf.Ticker(symbol)
        hist = ticker.history(
            auto_adjust=self.auto_adjust,
            start=begin_date,
            end=end_date + dt.timedelta(days=1),
            interval=frequency,
        ).rename_axis("date")
        # begin_date and end_date are used in dataframe query.
        begin_timestamp = dt.datetime.combine(  # noqa: F841
            begin_date,
            dt.time.min,
            tzinfo=tzinfo,
        )
        end_timestamp = dt.datetime.combine(  # noqa: F841
            end_date,
            dt.time.max,
            tzinfo=tzinfo,
        )
        filtered_hist = hist.query("@begin_timestamp <= date & date <= @end_timestamp")
        for index, row in filtered_hist.iterrows():
            yield fq.Price(
                symbol=symbol,
                date=index.date(),
                close=row["Close"],
                open_=row["Open"],
                high=row["High"],
                low=row["Low"],
                volume=row["Volume"],
                source=SOURCE,
            )

    def fetch_hist_splits(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Split, None, None]:
        """Fetch historical splits using yfinance."""
        ticker = yf.Ticker(symbol)
        splits = ticker.splits

        if splits.empty:
            fq.log.debug("no dividends found for %s", symbol)
            return

        # Filter splits by date range if necessary
        if begin_date or end_date:
            mask = True
            if begin_date:
                mask = mask & (splits.index.date >= begin_date)
            if end_date:
                mask = mask & (splits.index.date <= end_date)
            splits = splits[mask]

        for date, ratio in splits.items():
            # Convert from pandas Timestamp to date object
            ex_date = date.date() if hasattr(date, "date") else date
            # Create a Split object using the from_ratio method
            yield fq.Split.from_ratio(symbol, ex_date, fq.to_decimal(str(ratio)))

    def fetch_hist_dists(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Distribution, None, None]:
        """Fetch historical distributions (dividends) using yfinance."""
        ticker = yf.Ticker(symbol)
        dividends = ticker.dividends

        if dividends.empty:
            fq.log.debug("no dividends found for %s", symbol)
            return

        # Filter dividends by date range if necessary
        if begin_date or end_date:
            mask = True
            if begin_date:
                mask = mask & (dividends.index.date >= begin_date)
            if end_date:
                mask = mask & (dividends.index.date <= end_date)
            dividends = dividends[mask]

        for date, amount in dividends.items():
            # Convert from pandas Timestamp to date object
            ex_date = date.date() if hasattr(date, "date") else date
            yield fq.Distribution(
                symbol=symbol,
                ex_date=ex_date,
                amount=fq.to_decimal(str(amount)),
            )

    def fetch_close_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: dt.date | None = None,
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch current prices using yfinance."""
        date = date or self.as_of_date
        tickers = yf.Tickers(symbols)
        prices = tickers.history(
            auto_adjust=self.auto_adjust,
            group_by="ticker",
            start=date - dt.timedelta(days=1),
            progress=False,
        )
        try:
            today_prices = prices.loc[f"{date:%Y-%m-%d}"]
        except KeyError as ex:
            msg = f"No data for {date} and {', '.join(symbols)}"
            raise ValueError(msg) from ex
        for symbol in symbols:
            row = today_prices.loc[symbol]
            yield fq.Price(
                symbol=symbol,
                date=date,
                close=row["Close"],
                open_=row["Open"],
                high=row["High"],
                low=row["Low"],
                volume=row["Volume"],
                source=SOURCE,
            )

    def fetch_securities(
        self: t.Self,
        symbols: t.Iterable[str],
    ) -> t.Generator[fq.Security, None, None]:
        """Fetch security info using yfinance."""
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            yield fq.Security(
                symbol=symbol,
                name=info["shortName"],
                type=info["quoteType"].lower(),
                currency=info["currency"],
                exchange=fq.Exchange("X" + info["exchange"]),
                sector=info["sector"],
                industry=info["industry"],
                country=info["country"],
                source=SOURCE,
            )


class YFinanceHistFeed(
    YFinanceFeedMixin,
    fq.AbstractHistoricalFeed,
    fq.AbstractSplitFeed,
    fq.AbstractDistributionFeed,
):
    """Implements finquotes.CloseFeed with YFinanceFeedMixin."""

    def __init__(self: t.Self, /, **kwargs: t.Any) -> None:
        yfinance_kwargs, other_kwargs = YFinanceFeedMixin.split_kwargs(kwargs)
        fq.AbstractHistoricalFeed.__init__(self, __name__, SOURCE, **other_kwargs)
        YFinanceFeedMixin.__init__(self, **yfinance_kwargs)

    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,
        splits: t.Sequence[fq.Split] | None = None,  # noqa: ARG002
        distributions: t.Sequence[fq.Distribution] | None = None,  # noqa: ARG002
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch historical prices using yfinance."""
        return YFinanceFeedMixin.mixin_fetch_hist_prices(
            self,
            symbol,
            end_date,
            begin_date,
            frequency,
        )

    def fetch_hist_splits(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Split, None, None]:
        """Fetch historical splits using yfinance."""
        return YFinanceFeedMixin.fetch_hist_splits(self, symbol, end_date, begin_date)

    def fetch_hist_dists(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Distribution, None, None]:
        """Fetch historical distributions using yfinance."""
        return YFinanceFeedMixin.fetch_hist_dists(self, symbol, end_date, begin_date)


def build_historical_feed(*args: t.Any, **kwargs: t.Any) -> YFinanceHistFeed:
    """Forward to build_feed."""
    return YFinanceHistFeed(*args, **kwargs)


def build_split_feed(*args: t.Any, **kwargs: t.Any) -> YFinanceHistFeed:
    """Forward to build_feed."""
    return YFinanceHistFeed(*args, **kwargs)


def build_distribution_feed(*args: t.Any, **kwargs: t.Any) -> YFinanceHistFeed:
    """Forward to build_feed."""
    return YFinanceHistFeed(*args, **kwargs)


class YFinanceCloseFeed(YFinanceFeedMixin, fq.AbstractCloseFeed):
    """Implements finquotes.CloseFeed with YFinanceFeedMixin."""

    def __init__(self: t.Self, /, **kwargs: t.Any) -> None:
        yfinance_kwargs, other_kwargs = YFinanceFeedMixin.split_kwargs(kwargs)
        fq.AbstractCloseFeed.__init__(
            self,
            __name__,
            SOURCE,
            **other_kwargs,
        )
        YFinanceFeedMixin.__init__(self, **yfinance_kwargs)

    def fetch_close_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: dt.date | None = None,
        **kwargs: t.Any,
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch close prices using yfinance."""
        yield from YFinanceFeedMixin.fetch_close_prices(self, symbols, date, **kwargs)


def build_close_feed(*args: t.Any, **kwargs: t.Any) -> YFinanceCloseFeed:
    """Forward to build_feed."""
    return YFinanceCloseFeed(*args, **kwargs)


class YFinanceSecurityFeed(YFinanceFeedMixin, fq.AbstractSecurityFeed):
    """Implements finquotes.SecurityFeed with YFinanceFeedMixin."""

    def __init__(self: t.Self, /, **kwargs: t.Any) -> None:
        yfinance_kwargs, other_kwargs = YFinanceFeedMixin.split_kwargs(kwargs)
        fq.AbstractSecurityFeed.__init__(self, __name__, SOURCE, **other_kwargs)
        YFinanceFeedMixin.__init__(self, **yfinance_kwargs)

    def fetch_securities(
        self: t.Self,
        symbols: t.Iterable[str],
    ) -> t.Generator[fq.Security, None, None]:
        """Fetch security information for the given symbols.

        :param symbols: An iterable of symbol strings to fetch security data for.

        Yields Security objects containing information about each symbol.

        """
        return YFinanceFeedMixin.fetch_securities(self, symbols)


def build_security_feed(*args: t.Any, **kwargs: t.Any) -> YFinanceSecurityFeed:
    """Forward to build_feed."""
    return YFinanceSecurityFeed(*args, **kwargs)
