"""Retrieves data from http://www.morningstar.com.

Currently only security names. Need to leverage undocumented API for historical
prices and distributions.

"""

__author__ = "Jerome Lecomte"
__license__ = "MIT"


import typing as t

import bs4  # type: ignore[import-untyped]
import requests

import finquotes as fq

SOURCE = "finquotes.morningstar"


def html_to_security(html: str, source: str) -> fq.Security:
    """Extract security information from html.

    :param html: html page retrieved from Morningstar.
    :returns: finquotes.Security.

    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    element = soup.find("h1")
    if element is None:
        msg = "element not found in html"
        raise AttributeError(msg)
    parent_element = element.parent
    if parent_element is None:
        msg = "parent element not found in html"
        raise AttributeError(msg)
    name, symbol = parent_element.text.split("\xa0")
    return fq.Security(source=source, symbol=symbol.strip(), name=name.strip())


class MorningstarSecurityFeed(fq.NetworkConfigMixin, fq.AbstractSecurityFeed):
    """Retrieves security data from morningstar.com."""

    url = "http://financials.morningstar.com/company-profile/c.action?t="

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        fq.AbstractSecurityFeed.__init__(self, __name__, SOURCE, *args, **kwargs)
        fq.NetworkConfigMixin.__init__(self)

    def fetch_securities(
        self: t.Self,
        symbols: t.Iterable[str],
    ) -> t.Generator[fq.Security, None, None]:
        """Fetch html data from the url and extract security information.

        :param symbols: security symbols.
        :type symbols: list of str.

        :rtype: yield finquotes.Security.

        """
        assert iter(symbols)
        assert not isinstance(symbols, str)
        with requests.Session() as session:
            for symbol in symbols:
                security = self.fetch_security(session, symbol)
                if security:
                    yield security

    def fetch_security(
        self: t.Self,
        session: requests.Session,
        symbol: str,
    ) -> fq.Security | None:
        """Retrieve and return a finquotes.Security from a url.

        :param session: requests session.
        :type session: requests.Session.
        :param symbol: symbol to fetch.
        :type symbol: str.
        :returns: finquotes.Security for that url.

        """
        url = self.url + symbol
        try:
            request = session.get(url, allow_redirects=True)
            request.raise_for_status()
            return html_to_security(request.text, self.source)
        except requests.exceptions.RequestException as error:
            fq.log.warning("fail to retrieve %s: %s", url, str(error))
        except AttributeError as error:
            fq.log.warning("%s not found in %s: %s", symbol, url, str(error))
        return None


def build_security_feed() -> MorningstarSecurityFeed:
    """Create and return a MorningstarSecurityFeed object."""
    return MorningstarSecurityFeed()
