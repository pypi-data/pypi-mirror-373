"""Interface to stooq.pl.

Provides end-of-day data for stocks and indexes (no ETF)

:seealso: https://stooq.com/db/h/

"""

__author__ = "Jerome Lecomte"
__license__ = "MIT"


import datetime as dt
import typing as t
from decimal import Decimal as D, InvalidOperation  # noqa: N817

import bs4  # type: ignore[import-untyped]
import requests

import finquotes as fq

SOURCE = "finquotes.stooq"


def _open_url(*args: t.Any, **kwargs: t.Any) -> str:
    """Forward the call to requests, check status and decode text."""
    # Extract timeout to make it explicit for mypy
    timeout = kwargs.pop("timeout", 30.0)
    response = requests.get(*args, timeout=timeout, **kwargs)
    fq.log.debug("fetched %s", response.url)
    response.raise_for_status()
    if response.encoding is None:
        response.encoding = "utf-8"
    return response.content.decode(response.encoding)


def parse_polish_date(pol_date_str: str) -> dt.date:
    """Convert a polish date to datetime.datetime.

    We don't rely on locale because it seems that the local needs to be
    installed on the host and we just need to translate week days and months.

    """
    month_translations = {
        "cze": 6,
        "lis": 11,
        "lut": 2,
        "maj": 5,
        "sie": 8,
    }
    _, day, month, year = pol_date_str.split()
    return dt.date(int(year), month_translations[month], int(day))


class StooqFeed(fq.NetworkConfigMixin, fq.AbstractHistoricalFeed, fq.AbstractDistributionFeed):
    """Historical close prices from stooq.pl."""

    base_url = "https://stooq.com/q/"

    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        network_kwargs, other_kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        fq.AbstractHistoricalFeed.__init__(self, __name__, SOURCE)
        fq.AbstractDistributionFeed.__init__(self, __name__, SOURCE)

    def fetch_hist_price(
        self: t.Self,
        symbol: str,
        line: str,
    ) -> t.Generator[fq.Price, None, None]:
        """Parse specific line and return finquotes.Price."""
        datestr, open_, high, low, close, *others = line.split(",")
        date = dt.date.fromisoformat(datestr)
        price = fq.Price(
            source=self.source,
            symbol=symbol,
            date=date,
            close=close,
        )
        price.open = fq.to_decimal_or_none(open_)
        price.high = fq.to_decimal_or_none(high)
        price.low = fq.to_decimal_or_none(low)
        if others:
            price.volume = int(others[0]) if others[0] else None
        yield price

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
        :param begin_date: if not specified, the algorithm uses end_date.
        :param end_date: if not specified, the algorithm uses today.
        :param frequency: defaults to d[aily].  Can be w[eekly] or m[onthly].

        :return: generator of Price objects

        """
        end_date, begin_date = fq.compute_default_dates(end_date, begin_date)
        if frequency is None:
            frequency = "d"
        date_format = "%Y%m%d"
        params = {
            "s": symbol,
            "i": frequency,
            "d1": begin_date.strftime(date_format),
            "d2": end_date.strftime(date_format),
        }
        url = self.base_url + "d/l/"
        content = _open_url(url, params=params, timeout=self.timeout)
        for line in content.split("\n"):
            if not line or line.startswith("Date"):
                continue
            try:
                yield from self.fetch_hist_price(symbol, line)
            except ValueError:
                fq.log.warning("%s: failed to process line: %s", symbol, line)

    def fetch_hist_dists(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Distribution, None, None]:
        """Retrieve distribution history (dividend, capital gains, ...).

        :param symbol: ticker of the security.
        :param end_date: if not specified, the algorithm uses today.
        :param begin_date: if not specified, the algorithm uses end_date.

        :return: generator of Distribution objects

        NOTE: The distribution returned by stooq are adjusted and should
        not be used as actual as-of distributions.
        See https://stooq.com/pomoc/?q=9 (w/ google translate)

        """
        end_date, begin_date = fq.compute_default_dates(end_date, begin_date)
        params = {
            "s": symbol,
        }
        url = self.base_url + "m/"
        content = _open_url(url, params=params, timeout=self.timeout)
        soup = bs4.BeautifulSoup(content, "html.parser")
        table = soup.find("table", attrs={"id": "fth1"})
        if table is None:
            fq.log.warning("No table with id 'fth1' found for symbol: %s", symbol)
            return
        tbody = table.find("tbody")  # type: ignore[attr-defined]
        if tbody is None:
            fq.log.warning("No tbody found in table for symbol: %s", symbol)
            return
        rows = tbody.find_all("tr")  # type: ignore[attr-defined]
        for row in rows:
            cols = [el.text for el in row.find_all("td")]  # type: ignore[attr-defined]
            ex_date, amount = None, None
            try:
                ex_date = parse_polish_date(cols[0])
            except (ValueError, TypeError, IndexError) as err:
                fq.log.warning("failed to convet %s to date: %s", cols[0], err)
            try:
                amount = D(cols[2])
            except (ValueError, TypeError, IndexError, InvalidOperation) as err:
                fq.log.warning("failed to convert %s to decimal: %s", cols[2], err)
            if ex_date and amount:
                dist = fq.Distribution(symbol=symbol, ex_date=ex_date, amount=amount)
                yield dist


def build_historical_feed(*args: t.Any, **kwargs: t.Any) -> StooqFeed:
    """Forward to build_feed."""
    return StooqFeed(*args, **kwargs)
