"""Command line interface useful for testing."""

__author__ = "Jerome Lecomte"
__license__ = "MIT"

import datetime as dt
import logging.config
import sys
import typing as t

import click

import finquotes as fq

LOGGING_CONFIG: dict[str, t.Any] = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "warning": {"format": "%(asctime)s [%(levelname)s]: %(message)s"},
        "info": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        "debug": {
            "format": "%(asctime)s [%(levelname)s] %(name)s %(pathname)s:%(lineno)d: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "formatter": "warning",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": "WARNING",
        },
        "finquotes": {"propagate": True},
        "requests": {"propagate": True},
        "urllib3": {"propagate": True},
        "__main__": {
            "propagate": False,
        },
    },
}

log = logging.getLogger("finquotes")


def str_to_feed_type_enum(feed: str) -> fq.FeedType:
    """Convert str to finquotes.FeedType."""
    try:
        return fq.FeedType[feed.upper()]
    except KeyError:
        types = " ".join(str(f).split(".")[1].lower() for f in fq.FeedType)
        fq.log.error("%s is not a valid feed type. Pick from %s", feed, types)
        raise


class _SymbolsNotSeen:
    """Helper class to mark a symbol as not seen."""

    def __init__(self: t.Self, symbols: list[str]) -> None:
        self.symbols = set(symbols)

    def __str__(self: t.Self) -> str:
        return ", ".join(self.symbols)

    def to_str(
        self: t.Self,
        price: fq.Price | fq.Security | fq.Split | fq.Distribution,
        *,
        discard: bool = True,
    ) -> str:
        """Mark a symbol as seen and return its string representation."""
        if discard:
            self.symbols.discard(price.symbol)
        return str(price)


def _fetch_close_data(
    feed: "fq.AbstractCloseFeed",
    symbols: list[str],
    end_date: dt.date,
    not_seen: "_SymbolsNotSeen",
) -> list[str]:
    """Fetch close price data."""
    return [not_seen.to_str(price) for price in feed.fetch_close_prices(symbols, date=end_date)]


def _fetch_security_data(
    feed: "fq.AbstractSecurityFeed",
    symbols: list[str],
    not_seen: "_SymbolsNotSeen",
) -> list[str]:
    """Fetch security data."""
    return [not_seen.to_str(security) for security in feed.fetch_securities(symbols)]


def _fetch_historical_data(
    feed: "fq.AbstractHistoricalFeed",
    symbols: list[str],
    begin_date: dt.date,
    end_date: dt.date,
    not_seen: "_SymbolsNotSeen",
) -> list[str]:
    """Fetch historical price data."""
    output: list[str] = []
    for sym in symbols:
        output.extend(
            not_seen.to_str(price)
            for price in feed.fetch_hist_prices(
                sym,
                begin_date=begin_date,
                end_date=end_date,
            )
        )
    return output


def _fetch_split_data(
    feed: "fq.AbstractSplitFeed",
    symbols: list[str],
    begin_date: dt.date,
    end_date: dt.date,
    not_seen: "_SymbolsNotSeen",
) -> list[str]:
    """Fetch split data."""
    output: list[str] = []
    for sym in symbols:
        output.extend(
            not_seen.to_str(price)
            for price in feed.fetch_hist_splits(
                sym,
                begin_date=begin_date,
                end_date=end_date,
            )
        )
    return output


def _fetch_distribution_data(
    feed: "fq.AbstractDistributionFeed",
    symbols: list[str],
    begin_date: dt.date,
    end_date: dt.date,
    not_seen: "_SymbolsNotSeen",
) -> list[str]:
    """Fetch distribution data."""
    output: list[str] = []
    for sym in symbols:
        output.extend(
            not_seen.to_str(price)
            for price in feed.fetch_hist_dists(
                sym,
                begin_date=begin_date,
                end_date=end_date,
            )
        )
    return output


def _fetch_data_by_feed_type(
    feed_type: fq.FeedType,
    feed: t.Any,
    symbols: list[str],
    begin_date: dt.date,
    end_date: dt.date,
    not_seen: "_SymbolsNotSeen",
) -> list[str]:
    """Fetch data based on feed type."""
    if feed_type == fq.FeedType.CLOSE:
        close_feed = t.cast("fq.AbstractCloseFeed", feed)
        return _fetch_close_data(close_feed, symbols, end_date, not_seen)
    if feed_type == fq.FeedType.SECURITY:
        security_feed = t.cast("fq.AbstractSecurityFeed", feed)
        return _fetch_security_data(security_feed, symbols, not_seen)
    if feed_type == fq.FeedType.HISTORICAL:
        historical_feed = t.cast("fq.AbstractHistoricalFeed", feed)
        return _fetch_historical_data(historical_feed, symbols, begin_date, end_date, not_seen)
    if feed_type == fq.FeedType.SPLIT:
        split_feed = t.cast("fq.AbstractSplitFeed", feed)
        return _fetch_split_data(split_feed, symbols, begin_date, end_date, not_seen)
    if feed_type == fq.FeedType.DISTRIBUTION:
        distribution_feed = t.cast("fq.AbstractDistributionFeed", feed)
        return _fetch_distribution_data(distribution_feed, symbols, begin_date, end_date, not_seen)
    log.error("feed type %s not handled right now", feed_type)
    return []


def protected_cli(
    feed_name: str,
    symbols_iter: t.Iterable[str],
    source: str,
    end_datetime: dt.datetime | None,
    begin_datetime: dt.datetime | None,
    **kwargs: t.Any,
) -> None:
    """Inner function may throw."""
    feed_type = str_to_feed_type_enum(feed_name)
    feed = fq.build_feed(source, feed_type=feed_type, **kwargs)
    end_date, begin_date = fq.compute_default_dates(
        end_datetime.date() if end_datetime else None,
        begin_datetime.date() if begin_datetime else None,
    )
    symbols = list(symbols_iter)
    if len(symbols) == 0:
        msg = "at least one symbol required.  See --help"
        raise click.UsageError(msg)

    not_seen = _SymbolsNotSeen(symbols)
    output = _fetch_data_by_feed_type(feed_type, feed, symbols, begin_date, end_date, not_seen)

    for line in sorted(output):
        click.echo(line)
    if not_seen.symbols:
        msg = f"symbol(s) not found for feed {feed_name} between date {begin_date} and {end_date}: {not_seen}"
        raise ValueError(msg)


def setup_logging(*, verbose: bool) -> None:
    """Set up logging based on verbose level.

    :param: verbose 0 (WARNING, default), 1 (INFO) or 2 (DEBUG) is the number of -v.

    """
    logging.config.dictConfig(LOGGING_CONFIG)
    level = logging.WARNING - max(0, min(2, verbose)) * 10
    log.setLevel(level)
    level_name = logging.getLevelName(level).lower()
    logging_format = LOGGING_CONFIG["formatters"][level_name]["format"]
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(logging_format))


@click.command(name="python -m finquotes")
@click.argument(
    "feed",
    # rename close to snap or snapshot everywhere?
    type=click.Choice(["close", "historical", "distribution", "split", "security"]),
)
@click.argument(
    "symbols",
    nargs=-1,
    metavar="SYMBOLS",
)
@click.option(
    "-s",
    "--source",
    help="price source to use",
    metavar="MODULE",
    default="finquotes.yahoo",
)
@click.option(
    "-d",
    "--end-date",
    " --date",
    help="end of period of interest",
    type=click.DateTime(["%Y-%m-%d"]),
)
@click.option(
    "-b",
    "--begin-date",
    help="start of period of interest",
    type=click.DateTime(["%Y-%m-%d"]),
)
@click.option(
    "-v",
    "--verbose",
    help="increases verbosity",
    count=True,
)
@click.option("--api-key", help="set API key for the specific source")
@click.option("--debug", is_flag=True, help="raise exceptions on error")
@click.option("--timeout", type=float, help="set timeout in seconds")
@click.option("--max-retries", type=int, help="set max retries")
@click.option("--retry-delay", type=float, help="set retry delay in seconds")
@click.version_option(version=fq.__version__, message="v%(version)s")
def main(
    feed: str,
    symbols: t.Iterable[str],
    source: str,
    end_date: dt.datetime,
    begin_date: dt.datetime,
    verbose: int,
    **kwargs: t.Any,
) -> None:
    """Command line interface for finquotes is useful for testing."""
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    debug = kwargs.pop("debug")
    try:
        setup_logging(verbose=verbose > 0)
        protected_cli(
            feed,
            symbols,
            source,
            end_date,
            begin_date,
            **kwargs,
        )
    except Exception as error:  # pylint: disable=broad-except
        if debug:
            raise
        # Otherwise, only show the error.
        log.info(
            "error detected and absorbed, use --debug option to show the stack trace",
        )
        log.exception("%s", type(error).__name__)
        click.get_current_context().exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])  # pylint: disable=no-value-for-parameter
