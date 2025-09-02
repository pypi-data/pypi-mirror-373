"""Retrieves data from Yahoo. Finance."""

__author__ = "Jerome Lecomte"
__license__ = "MIT"

import contextlib
import datetime as dt
import decimal
import functools
import json
import re
import time
import typing as t
from decimal import Decimal as D  # noqa: N817

import requests
import requests.sessions

# Needed to be handle parsing times like 4:00pm and such.
import finquotes as fq

SOURCE = "finquotes.yahoo"

# Year threshold for 2-digit year conversion
YEAR_2000 = 2000

# See http://www.gummy-stuff.org/Yahoo-data.htm for more information.
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


def to_yahoo_timestamp(
    begin_date: dt.date,
    end_date: dt.date,
) -> tuple[str, str]:
    """Convert the date to as_of_date since epoch.

    Yahoo. stores data as timestamp of seconds sine epoch 1st Jan 1970.

    :param begin_ts: begin time stamp to convert to time stamp.
    :param end_ts: end time stamp to convert to time stamp.

    :return: time stamp of the day after date at 00:00 UTC.

    """
    begin_ts = dt.datetime.combine(begin_date, dt.time(), tzinfo=dt.UTC)
    end_ts = dt.datetime.combine(
        end_date,
        dt.time(),
        tzinfo=dt.UTC,
    ) + dt.timedelta(1)
    return f"{begin_ts.timestamp():.0f}", f"{end_ts.timestamp():.0f}"


def from_yahoo_timestamp(datestr: str) -> dt.datetime:
    """Convert a string representing an integer of seconds since epoch.

    Localize to yahoo.timezone.

    :return: datetime.datetime

    """
    try:
        n_secs = int(datestr)
        return dt.datetime.fromtimestamp(n_secs, tz=dt.UTC)
    except (ValueError, OverflowError) as err:
        fq.log.warning("failed to convert %s to a dt.datetime: %s", datestr, err)
        raise


# Convenience functions
def parse_date(datestr: str, **kw: t.Any) -> dt.date:
    """Parse a date retrieved from Yahoo."""
    matches = re.match(r"^(\d\d?)[/-]?(\d\d?)[/-]?(\d+)?$", datestr)
    date = None
    if matches:
        year = fq.today().year
        if matches.group(3):
            year = int(matches.group(3))
        if year < YEAR_2000:
            year += YEAR_2000
        month = matches.group(1)
        day = matches.group(2)
        with contextlib.suppress(ValueError):
            date = dt.date(int(year), int(month), int(day))
        if kw.get("as_of_date"):
            as_of_date = kw["as_of_date"]
            assert as_of_date <= fq.today()
            diff = fq.today() - as_of_date
            date = (date - diff).date()
    if not date:
        msg = f"cannot convert {datestr} to a date"
        raise TypeError(msg)
    return date


def replace_comma_within_prices(string: str) -> str:
    """Replace comma in the names of companies."""
    in_prices = False
    new_line = ""
    for char in string:
        if char == '"':
            in_prices = not in_prices
        new_char = " " if char == "," and in_prices else char
        new_line += new_char
    return new_line


def decode(raw_line: str) -> str:
    """Decode and strip spaces in argument.

    Assumes UTF-8 if the line is an instance of bytes.
    """
    line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
    return str(line).strip()  # removes blanks.


class CrumbAndCookies(t.NamedTuple):
    """Container for crumb and cookies data."""

    crumb: str
    cookies: t.Any


@functools.lru_cache
def get_crumb_and_cookies(
    symbol: str,
    session: requests.sessions.Session,
) -> CrumbAndCookies:
    """Retrieve the main Yahoo. markers."""
    url = f"https://finance.yahoo.com/quote/{symbol}"
    content_text = fq.localhttp.request(session, "GET", url).text
    search = re.search(
        r'"CrumbStore":\{"crumb":"(.*)"\},"CompositeStore"',
        content_text,
    )
    if search is None:
        msg = "No crumb found in initial response"
        raise ValueError(msg)
    crumb = search.group(1)
    # For some reason does not get converted back to string.
    crumb = crumb.replace("\\u002F", "/")
    fq.log.info("using Yahoo. crumb %s", crumb)
    return CrumbAndCookies(crumb, session.cookies)


def make_session() -> requests.sessions.Session:
    """Get a context to retrieve internet data.

    Factors session customization needed to query Yahoo.

    """
    session = requests.sessions.Session()
    fq.localhttp.set_retries(session)
    return session


URLS = {
    "v7": {
        "quote": "https://query1.finance.yahoo.com/v7/finance/quote",
        "history": "https://query1.finance.yahoo.com/v7/finance/download/",
    },
}


class YahooFeedMixin(fq.NetworkConfigMixin):
    """Retrieves data from Yahoo."""

    markers = None
    size_re = re.compile(r"(,[1-9]\d?),(\d00)(\\r)")
    date_re = re.compile(r"((\d+)[-\s]+)?([A-Z][a-z]{2})[-\s]+(\d+)")

    def __init__(
        self: t.Self,
        session: requests.Session | None = None,
        crumb_and_cookies: CrumbAndCookies | None = None,
        *,
        adjust_highs: bool = False,
        adjust_lows: bool = False,
        version: str = "v7",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 30.0,
    ) -> None:
        """Initialize YahooFeedMixin."""
        fq.NetworkConfigMixin.__init__(self, timeout=timeout, max_retries=max_retries, retry_delay=retry_delay)
        self.session = session or make_session()
        self.snap_url = URLS[version]["quote"]
        self.sec_url = URLS[version]["quote"]
        self.hist_url = URLS[version]["history"]
        self.fields = [
            fq.Field.SYMBOL,
            fq.Field.OPEN,
            fq.Field.HIGH,
            fq.Field.LOW,
            fq.Field.CLOSE,
            fq.Field.VOLUME,
            fq.Field.TIME_STAMP,
        ]
        self._crumb_and_cookies = crumb_and_cookies
        self.adjust_highs = adjust_highs
        self.adjust_lows = adjust_lows

    @property
    def crumb_and_cookies(self: t.Self) -> CrumbAndCookies:
        """Retrieve the main Yahoo. markers if not retrieved already."""
        if not self._crumb_and_cookies:
            self._crumb_and_cookies = get_crumb_and_cookies("SPY", self.session)
        return self._crumb_and_cookies

    @staticmethod
    def split_kwargs(kwargs: dict) -> tuple[dict, dict]:
        """Split kwargs between those known by YahooFeedMixin and everything else.

        Return:
        ------
            Tuple of yahoo keyword arguments, then the other keyword arguments.

        """
        yahoo_kwargs = {}
        yahoo_kwargs["crumb_and_cookies"] = kwargs.pop("crumb_and_cookies", None)
        yahoo_kwargs["session"] = kwargs.pop("session", make_session())
        for param in ["max_retries", "retry_delay", "timeout"]:
            if param in kwargs:
                yahoo_kwargs[param] = kwargs.pop(param)
        return yahoo_kwargs, kwargs

    def _request_text(self: t.Self, url: str, params: dict | None = None) -> str:
        """Forward call to _open_url with protection against HTTPError.

        Also check the status of the response. Logs the error as a warning and
        return an empty string as reponse if an issue occured.

        """
        text = ""
        for retry in range(self.max_retries):
            try:
                fq.log.debug(url)
                if retry > 0:
                    time.sleep(self.retry_delay)
                    fq.log.debug("trying %d of %d ...", retry, self.max_retries)
                text = fq.localhttp.request(
                    self.session,
                    "GET",
                    url,
                    params=params,
                ).text
                break
            except requests.exceptions.HTTPError as error:
                response = error.response
                if response is not None and response.status_code in {401, 404}:
                    msg = f"invalid url: {error}"
                    raise fq.FeedError(msg) from error
                fq.log.info("failed get for %s: %s", url, error)
                if retry >= self.max_retries - 1:
                    break
            except (
                ConnectionError,
                TimeoutError,
                requests.exceptions.Timeout,
                ValueError,
            ) as error:
                fq.log.warning("failed get for %s: %s", url, error)
                if retry >= self.max_retries - 1:
                    raise
        return text

    def get_cookies(self: t.Self) -> requests.cookies.RequestsCookieJar:
        """Get cookies for http call."""
        return self.crumb_and_cookies.cookies

    def _parse_line(self: t.Self, line: str) -> fq.Price:
        """Parse one line in the content returned by Yahoo."""
        line = line.strip()
        fq.log.debug(line)
        modline = replace_comma_within_prices(line)
        modline = modline.replace("&nbsp;", " ")
        values = modline.split(",")
        checked_values = {}
        for field, unstripped_value in zip(self.fields, values, strict=False):
            value = unstripped_value.strip('"').strip().rstrip("+").rstrip("-")
            try:
                checked_value: str | D | dt.date | dt.time | int | None = None
                if checked_value == "N/A":
                    pass
                elif field in [fq.Field.DATE, fq.Field.EX_DATE, fq.Field.PAY_DATE]:
                    checked_value = parse_date(value)
                elif field in [fq.Field.TIME, fq.Field.TIME_STAMP]:
                    checked_value = dt.datetime.strptime(value + "-04:00", "%I:%M%p%z").time()
                elif field not in [fq.Field.SYMBOL, fq.Field.NAME, fq.Field.EXCHANGE]:
                    checked_value = D(value)
            except (TypeError, ValueError, decimal.InvalidOperation) as err:
                fq.log.warning(
                    "failed to interpret %s as %s in %s %s",
                    value,
                    field,
                    line,
                    err,
                )
                checked_value = None
            if checked_value is not None:
                checked_values[field.name] = checked_value
        price = fq.Price(source=SOURCE, **checked_values)  # type: ignore[arg-type]
        fq.log.debug("%s", price)
        return price

    def _parse_csv(
        self: t.Self,
        content: list,
        symbols: list,
    ) -> t.Generator[fq.Price, None, None]:
        """Parse content returned by Yahoo."""
        for raw_line in content:
            line = decode(raw_line)
            # Silently skips empty lines.
            if not line:
                continue
            # Handles known errors.
            if line.startswith("Sorry"):
                fq.log.error("Server not available: %s", line)
                break
            try:
                data = self._parse_line(line)
            except ValueError as err:
                fq.log.error("Failed to parse %s: %s", line, str(err))
                continue
            if not data.symbol:
                fq.log.warning("no symbol found in %s", line)
                continue
            if data.symbol not in symbols:
                fq.log.warning("unexpected symbol %s in %s", data.symbol, line)
                continue
            if not data.date and "date" in self.fields:
                fq.log.warning("no date found in %s", line)
                continue
            yield data

    def _parse_json_price(
        self: t.Self,
        item: dict,
        fields: t.Iterable[fq.Field],
    ) -> fq.Price:
        """Parse single element in the JSON response looking for price info."""
        timestamp = from_yahoo_timestamp(item["regularMarketTime"])
        timestamp_date: dt.date | None = None
        # Set the date as a date() without time if time is not requested.
        if fq.Field.DATE in fields and fq.Field.TIME not in fields:
            timestamp_date = timestamp.date()
        assert timestamp is not None, "date is required either as DATE or TIME_STAMP"
        close = D(item["regularMarketPrice"])
        price = fq.Price(
            item["symbol"],
            date=timestamp_date or timestamp,
            close=close,
            source=SOURCE,
        )
        if fq.Field.OPEN in fields and "regularMarketOpen" in item and item["regularMarketOpen"] != "0.0":
            price.open = D(item["regularMarketOpen"])
        if fq.Field.HIGH in fields and "regularMarketDayHigh" in item and item["regularMarketDayHigh"] != "0.0":
            price.high = D(item["regularMarketDayHigh"])
        if fq.Field.LOW in fields and "regularMarketDayLow" in item and item["regularMarketDayLow"] != "0.0":
            price.low = D(item["regularMarketDayLow"])
        if fq.Field.VOLUME in fields and "regularMarketVolume" in item:
            price.volume = int(item["regularMarketVolume"]) if item["regularMarketVolume"] is not None else None
        return price

    def _parse_json_security(self: t.Self, content: dict) -> fq.Security:
        """Parse single elemenet in JSON response looking for security info."""
        name = content["shortName"]
        if "longName" in content:
            name = content["longName"]
        security = fq.Security(
            symbol=content["symbol"],
            name=name,
            source=SOURCE,
        )
        security.exchange = "X" + content["exchange"]
        security.type = content["quoteType"].lower()
        security.currency = content["currency"].upper()
        return security

    def _parse_results(self: t.Self, content: str) -> list:
        # No conversion of float because we handle the string later in Price
        # constructor with decimal.Decimal.
        fq.log.debug("%s", content)
        data = json.loads(content, parse_float=lambda x: x)
        if "quoteResponse" not in data:
            msg = f"no quoteRespose in {content}"
            raise ValueError(msg)
        data = data["quoteResponse"]
        if data.get("error"):
            fq.log.warning("error detected: %s", data["error"])
        if "result" not in data:
            msg = f"not result found in {data}"
            raise ValueError(msg)
        if not data["result"]:
            msg = f"result is empty in {data}"
            raise ValueError(msg)
        return data["result"]

    def _parse_json_prices(
        self: t.Self,
        content: str,
        _: t.Iterable[str],
        fields: t.Iterable[fq.Field],
    ) -> t.Generator[fq.Price, None, None]:
        """Parse json response looking for prices."""
        for result in self._parse_results(content):
            try:
                yield self._parse_json_price(result, fields)
            # OSError when regularMarketTime is 0.
            except (ValueError, KeyError, OSError) as err:
                fq.log.warning("failed to process %s: %s", json.dumps(result), err)

    def _parse_json_securities(
        self: t.Self,
        content: str,
    ) -> t.Generator[fq.Security, None, None]:
        """Parse json response looking for securities."""
        for result in self._parse_results(content):
            try:
                yield self._parse_json_security(result)
            except (ValueError, KeyError) as err:
                fq.log.warning("failed to process %s: %s", json.dumps(result), err)

    def _fetch_batch(
        self: t.Self,
        symbols: t.Iterable[str],
        fields: t.Iterable[fq.Field],
        mapped_fields: t.Iterable[str],
    ) -> t.Generator[fq.Price, None, None]:
        """Retrieve self.fields relative to symbols (internal use)."""
        symbolstr = ",".join(symbols)
        params = {
            "fields": mapped_fields,
            "symbols": symbolstr,
        }
        response = self._request_text(self.snap_url, params=params)
        if response:
            yield from self._parse_json_prices(response, symbols, fields)

    def fetch_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: None | dt.date = None,  # noqa: ARG002
        as_of_ts: None | dt.datetime = None,  # noqa: ARG002
        fields: t.Iterable[fq.Field] | None = None,
        batch_size: int = 195,
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch information about the securities from Yahoo.

        :param symbols: list or single symbol because the same function is used
            for historical, and close prices.
        :param date: date for the prices looked up (not used, always as_of_date).
        :param as_of_ts: expected time stamp for the prices (not used).
        :param fields: list of fields being looked up (e.g. last, volume, ...)
        :param batch_size: max size of one request.

        Converts the argument to a list and call _fetch_batch to retrieve the
        data by block of 25 (Yahoo requirement).

        Note this function is both used as fetch_intraday_prices and
        fetch_close_prices.

        """
        if fields is None:
            fields = self.fields
        dedup_symbols = list(dict.fromkeys(symbols))
        mapped_fields = ",".join([fields_map[fld] for fld in fields])
        for idx in range(0, len(dedup_symbols), batch_size):
            yield from self._fetch_batch(
                dedup_symbols[idx : idx + batch_size],
                fields,
                mapped_fields,
            )

    def fetch_hist_dists(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Distribution, None, None]:
        """Fetch distribution history from Yahoo.

        If begin_date is not specified, the algorithm uses end_date.
        If end_date is not specified, the algorithm uses today.

        Returns the number of distributions succesfully retrieved.
        """
        if end_date is None:
            end_date = fq.today()
        if begin_date is None:
            begin_date = end_date
        begin, end = to_yahoo_timestamp(begin_date, end_date)
        params = {"period1": begin, "period2": end, "interval": "1d", "events": "div"}
        url = self.hist_url + symbol
        response = self._request_text(url, params=params)
        for raw_line in response.split("\n"):
            line = decode(raw_line).strip()
            if not raw_line:
                continue
            fq.log.debug("retrieved data: %s", line)
            vals = line.split(",")
            if vals[0] == "Date":
                continue  # Header line.
            try:
                date = dt.date.fromisoformat(vals[0])
            except ValueError as err:
                msg = "{}: cannot convert {} to a date: {}"
                msg = msg.format(line, vals[0], err)
                fq.log.warning(msg)
                continue
            if date > end_date or date < begin_date:
                msg = "{}: distribution date not between {} and {}"
                msg = msg.format(line, begin_date, end_date)
                fq.log.warning(msg)
                continue
            yield fq.Distribution(symbol, date, D(vals[1]), None)

    def fetch_hist_splits(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
    ) -> t.Generator[fq.Split, None, None]:
        """Fetch distribution history from Yahoo.

        If begin_date is not specified, the algorithm uses end_date.
        If end_date is not specified, the algorithm uses today.

        Returns the number of distributions succesfully retrieved.
        """
        if end_date is None:
            end_date = fq.today()
        if begin_date is None:
            begin_date = end_date
        begin, end = to_yahoo_timestamp(begin_date, end_date)
        params = {"period1": begin, "period2": end, "interval": "1d", "events": "split"}
        url = self.hist_url + symbol
        response = self._request_text(url, params=params)
        for raw_line in response.split("\n"):
            line = decode(raw_line)
            # Silently skips empty lines.
            if not line:
                continue
            fq.log.debug("retrieved data: %s", line)
            vals = line.split(",")
            if vals[0] == "Date":
                continue  # Header line.
            try:
                date = dt.date.fromisoformat(vals[0])
            except ValueError as err:
                msg = "{}: cannot convert {} to a date: {}"
                msg = msg.format(line, vals[0], err)
                fq.log.warning(msg)
                continue
            if date > end_date or date < begin_date:
                msg = "{}: distribution date not between {} and {}"
                msg = msg.format(line, begin_date, end_date)
                fq.log.warning(msg)
                continue
            match = re.match(r"(\d+)\D(\d+)", vals[1])
            if match is None:
                msg = f"cannot interpret {vals[1]} as split"
                raise ValueError(msg)
            newq, oldq = match.group(1), match.group(2)
            yield fq.Split(symbol, date, int(newq), int(oldq))

    def fetch_securities(
        self: t.Self,
        symbols: t.Iterable[str],
    ) -> t.Generator[fq.Security, None, None]:
        """Fetch a security from Yahoo."""
        if symbols:
            symbolstr = ",".join(symbols)
            params = {
                "symbols": symbolstr,
            }
            response = self._request_text(self.snap_url, params=params)
            if not response:
                fq.log.error("no data returned for %s", symbolstr)
                msg = f"no data returned for {symbolstr}"
                raise fq.FeedError(msg)
            yield from self._parse_json_securities(response)


class YahooCloseFeed(YahooFeedMixin, fq.AbstractCloseFeed):
    """Implements finquotes.CloseFeed with YahooFeedMixin."""

    def __init__(self: t.Self, /, **kwargs: t.Any) -> None:
        yahoo_kwargs, other_kwargs = YahooFeedMixin.split_kwargs(kwargs)
        fq.AbstractCloseFeed.__init__(self, __name__, SOURCE, **other_kwargs)
        YahooFeedMixin.__init__(self, **yahoo_kwargs)

    def fetch_close_prices(
        self: t.Self,
        symbols: t.Sequence[str],
        date: dt.date | None = None,
        as_of_ts: dt.datetime | None = None,
        fields: t.Iterable[fq.Field] | None = None,
        batch_size: int = 195,
        **kwargs: t.Any,
    ) -> t.Generator[fq.Price, None, None]:
        """Adapts fetch_prices to fetch_close_prices function."""
        return YahooFeedMixin.fetch_prices(
            self,
            symbols,
            date,
            as_of_ts,
            fields,
            batch_size,
            **kwargs,
        )


def build_close_feed(*args: t.Any, **kwargs: t.Any) -> YahooCloseFeed:
    """Forward to build_feed."""
    return YahooCloseFeed(*args, **kwargs)


class YahooHistFeed(YahooFeedMixin, fq.AbstractHistoricalFeed):
    """Implements finquotes.AbstractHistFeed via Yahoo."""

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        yahoo_kwargs, other_kwargs = YahooFeedMixin.split_kwargs(kwargs)
        fq.AbstractHistoricalFeed.__init__(
            self,
            __name__,
            SOURCE,
            *args,
            **other_kwargs,
        )
        YahooFeedMixin.__init__(self, **yahoo_kwargs)

    def _validate_date_range(
        self,
        as_of_date: dt.date,
        begin_date: dt.date,
        end_date: dt.date,
    ) -> bool:
        """Validate if the date is within the specified range."""
        if as_of_date > end_date:
            fq.log.warning(
                "ignored price for %s later than end date %s",
                as_of_date,
                end_date,
            )
            return False
        if as_of_date < begin_date:
            fq.log.warning(
                "ignored price for %s earlier than begin date %s",
                as_of_date,
                begin_date,
            )
            return False
        return True

    def _calculate_split_factor(
        self,
        splits: t.Sequence[fq.Split] | None,
        as_of_date: dt.date,
    ) -> D:
        """Calculate the split factor for the given date."""
        split_factor = D("1.0")
        if splits is not None:
            for split in splits:
                assert isinstance(split, fq.Split)
                if split.ex_date > as_of_date:
                    split_factor *= D(split.new_quantity / split.old_quantity)
        return split_factor

    def _create_price_object(
        self,
        symbol: str,
        as_of_date: dt.date,
        vals: list[str],
        split_factor: D,
    ) -> fq.Price:
        """Create and populate a Price object with the given data."""
        close = D.quantize(D(vals[4]) * split_factor, D("0.0000"))
        price = fq.Price(symbol, as_of_date, close, source=SOURCE)
        # Open, high, and low are dividend adjusted but not split adjusted.
        # http://blog.fosstrading.com/2017/06/yahoo-finance-alternatives.html
        price.open = D.quantize(D(vals[1]) * split_factor, D("0.0000"))
        price.high = D.quantize(D(vals[2]) * split_factor, D("0.0000"))
        price.low = D.quantize(D(vals[3]) * split_factor, D("0.0000"))
        price.volume = int(int(vals[6]) / float(split_factor)) if vals[6] is not None else None
        return price

    def _adjust_price_bounds(self, price: fq.Price) -> None:
        """Adjust price high and low values if needed."""
        if self.adjust_lows and price.low is not None and price.low > price.close:
            fq.log.warning(
                "adjusting low %s to close price %s",
                price.low,
                price.close,
            )
            price.low = price.close
        if self.adjust_highs and price.high is not None and price.high < price.close:
            fq.log.warning(
                "adjusting high %s to close price %s",
                price.high,
                price.close,
            )
            price.high = price.close

    def fetch_hist_price(
        self: t.Self,
        raw_line: str,
        symbol: str,
        begin_date: dt.date,
        end_date: dt.date,
        distributions: t.Sequence[fq.Distribution] | None = None,
        splits: t.Sequence[fq.Split] | None = None,
    ) -> fq.Price | None:
        """Convert string to price."""
        assert distributions is None or hasattr(distributions, "__iter__")
        assert splits is None or hasattr(splits, "__iter__")
        line = decode(raw_line)
        fq.log.debug("retrieved data: %s", line)
        # Silently skips empty lines.
        if not line:
            return None
        vals = line.split(",")
        as_of_date = dt.date.fromisoformat(vals[0])

        if not self._validate_date_range(as_of_date, begin_date, end_date):
            return None

        split_factor = self._calculate_split_factor(splits, as_of_date)
        price = self._create_price_object(symbol, as_of_date, vals, split_factor)
        self._adjust_price_bounds(price)
        return price

    # pylint: disable=R0913
    def fetch_hist_prices(
        self: t.Self,
        symbol: str,
        end_date: dt.date | None = None,
        begin_date: dt.date | None = None,
        frequency: str | None = None,
        splits: t.Sequence[fq.Split] | None = None,
        distributions: t.Sequence[fq.Distribution] | None = None,
    ) -> t.Generator[fq.Price, None, None]:
        """Fetch history from Yahoo.

        :param begin_date: if not specified, the algorithm uses end_date.
        :param end_date: if not specified, the algorithm uses today.
        :param frequency: defaults to d[aily].  Can be w[eekly] or m[onthly].

        :return: iterable on finquotes.Price

        """
        assert symbol is not None, "symbol argument is None"
        assert isinstance(
            symbol,
            str,
        ), f"got symbol of type {type(symbol)} expected str"
        end_date, begin_date = fq.compute_default_dates(end_date, begin_date)
        if not frequency:
            frequency = "d"
        if frequency[0] not in ["d", "w", "m"]:
            msg = f"invalid frequency {frequency}"
            raise TypeError(msg)
        begin, end = to_yahoo_timestamp(begin_date, end_date)
        params = {
            "period1": begin,
            "period2": end,
            "interval": "1" + frequency[0],
            "events": "history",
        }
        url = self.hist_url + symbol
        response = self._request_text(url, params=params)
        for raw_line in response.split("\n"):
            if raw_line.startswith("Date"):
                continue
            if "null" in raw_line:
                continue
            if not raw_line:
                continue
            try:
                price = self.fetch_hist_price(
                    raw_line,
                    symbol,
                    begin_date,
                    end_date,
                    splits=splits,
                    distributions=distributions,
                )
            except ValueError as err:
                fq.log.warning(err)
                continue
            if price is None:
                continue
            yield price


def build_historical_feed(*args: t.Any, **kwargs: t.Any) -> YahooHistFeed:
    """Forward to build_feed."""
    return YahooHistFeed(*args, **kwargs)


class YahooDistFeed(YahooFeedMixin, fq.AbstractDistributionFeed):
    """Implements finquotes.AbstractDistFeed with YahooFeedMixin."""

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        yahoo_kwargs, other_kwargs = YahooFeedMixin.split_kwargs(kwargs)
        fq.AbstractDistributionFeed.__init__(
            self,
            __name__,
            SOURCE,
            *args,
            **other_kwargs,
        )
        YahooFeedMixin.__init__(self, **yahoo_kwargs)

    fetch_hist_dists = YahooFeedMixin.fetch_hist_dists


def build_distribution_feed(*args: t.Any, **kwargs: t.Any) -> YahooDistFeed:
    """Forward to build_feed."""
    return YahooDistFeed(*args, **kwargs)


class YahooSplitFeed(YahooFeedMixin, fq.AbstractSplitFeed):
    """Implements finquotes.AbstractSplitFeed with YahooFeedMixin."""

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        yahoo_kwargs, other_kwargs = YahooFeedMixin.split_kwargs(kwargs)
        fq.AbstractSplitFeed.__init__(self, __name__, SOURCE, *args, **other_kwargs)
        YahooFeedMixin.__init__(self, **yahoo_kwargs)

    fetch_hist_splits = YahooFeedMixin.fetch_hist_splits


def build_split_feed(*args: t.Any, **kwargs: t.Any) -> YahooSplitFeed:
    """Forward to build_feed."""
    return YahooSplitFeed(*args, **kwargs)


class YahooSecurityFeed(YahooFeedMixin, fq.AbstractSecurityFeed):
    """Implements finquotes.AbstractSecurityFeed with YahooFeedMixin."""

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        yahoo_kwargs, other_kwargs = YahooFeedMixin.split_kwargs(kwargs)
        fq.AbstractSecurityFeed.__init__(self, __name__, SOURCE, *args, **other_kwargs)
        YahooFeedMixin.__init__(self, **yahoo_kwargs)

    fetch_securities = YahooFeedMixin.fetch_securities


def build_security_feed(*args: t.Any, **kwargs: t.Any) -> YahooSecurityFeed:
    """Forward to build_feed."""
    return YahooSecurityFeed(*args, **kwargs)
