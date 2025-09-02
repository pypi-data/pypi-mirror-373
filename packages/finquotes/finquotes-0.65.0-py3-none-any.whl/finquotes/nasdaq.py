"""Interface to nasdaq.com."""

import dataclasses
import typing
import typing as t

import finquotes as fq

SOURCE = "finquotes.nasdaq"


@dataclasses.dataclass(frozen=True)
class Stock:
    """Listed stock data."""

    symbol: str
    name: str
    country: str
    industry: str
    sector: str

    @classmethod
    def from_dict(cls, json_data: dict[str, typing.Any]) -> "Stock":
        """Convert a dict (could be coming from JSON data) to a Stock class."""
        return cls(
            symbol=json_data["symbol"],
            name=json_data["name"].replace(" Common Stock", "").strip(),
            country=json_data["country"],
            industry=json_data["industry"],
            sector=json_data["sector"],
        )


def _read_json(
    url: str,
    headers: dict | None = None,
    params: t.Any = None,
) -> dict[str, Stock]:
    """Download nasdaq screener data (csv url) or directly json data."""
    json = fq.localhttp.request(
        fq.localhttp.cached_session,
        "GET",
        url,
        headers=headers,
        params=params,
    ).json()
    return {stock["symbol"]: Stock.from_dict(stock) for stock in json["data"]["rows"]}


class NasdaqSecurityFeed(fq.NetworkConfigMixin, fq.AbstractSecurityFeed):
    """Interface to https://api.nasdaq.com.

    From https://github.com/ranaroussi/yfinance/issues/606/ for details.

    """

    __default_url = "https://api.nasdaq.com/api/screener/stocks"
    __default_headers: t.ClassVar[dict[str, str]] = {
        "authority": "api.nasdaq.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "origin": "https://www.nasdaq.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.nasdaq.com/",
        "accept-language": "en-US,en;q=0.9",
    }
    __default_params = params = (
        ("tableonly", "true"),
        ("limit", "25"),
        ("offset", "0"),
        ("download", "true"),
    )

    def __init__(
        self: t.Self,
        url: str | None = None,
        headers: dict | None = None,
        params: t.Any = None,
        **kwargs: t.Any,
    ) -> None:
        """Initialize."""
        network_kwargs, other_kwargs = fq.NetworkConfigMixin.separate_network_kwargs(kwargs)
        fq.NetworkConfigMixin.__init__(self, **network_kwargs)
        fq.AbstractSecurityFeed.__init__(self, __name__, SOURCE, **other_kwargs)
        self.url = url or self.__default_url
        self.headers = headers or self.__default_headers
        self.params = params or self.__default_params
        self.__stocks: dict[str, Stock] = {}

    @property
    def stocks(self: t.Self) -> dict[str, Stock]:
        """Get nasdaq screener csv."""
        if not self.__stocks:
            assert self.url is not None
            self.__stocks = _read_json(self.url, self.headers, self.params)
        assert self.__stocks is not None
        return self.__stocks

    def approximate_shares_outstanding(
        self: t.Self,
        df: t.Any,
        symbol: str,
    ) -> float | None:
        """Approximate shares outstanding from market cap and price."""
        # Approximation
        try:
            shares_outstanding = df["market_cap"].astype(float) / df["price"].astype(
                float,
            )
        except ValueError as err:
            fq.log.warning(
                "Could not calculate shares outstanding for %s: %s",
                symbol,
                err,
            )
            shares_outstanding = None
        return shares_outstanding

    def fetch_security(self: t.Self, symbol: str) -> fq.Security:
        """Import stock data from https://www.nasdaq.com/market-activity/stocks/screener."""
        stock = self.stocks[symbol]
        return fq.Security(
            source=self.source,
            type="equity",
            **dataclasses.asdict(stock),
        )

    def fetch_securities(
        self: t.Self,
        symbols: t.Iterable[str],
    ) -> t.Generator[fq.Security, None, None]:
        """Fetch securities from the internet."""
        for symbol in symbols:
            try:
                yield self.fetch_security(symbol)
            except (KeyError, ValueError) as err:
                fq.log.warning("failed to fetch %s: %s", symbol, err)


def build_security_feed(*args: t.Any, **kwargs: t.Any) -> NasdaqSecurityFeed:
    """Build a security feed."""
    return NasdaqSecurityFeed(*args, **kwargs)
