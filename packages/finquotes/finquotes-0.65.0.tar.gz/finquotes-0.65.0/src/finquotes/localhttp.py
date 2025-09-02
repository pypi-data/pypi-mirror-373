"""Factor http connectivity.

Internal module that wraps requests and requests_html.

Named localhttp to avoid name conflict with requests.

"""

import logging
import typing as t

import requests
import requests.adapters
import requests_cache
from urllib3.util import retry

log = logging.getLogger("finquotes")


cached_session = requests_cache.CachedSession(
    "finquotes",
    backend="filesystem",
    expire_after=3600,
    use_cache_dir=True,
)


def set_retries(session: requests.Session, **kwargs: t.Any) -> None:
    """Update session with retry policy.

    **kwargs are passed to the urllib3.Retry constructor:
    https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry

    """
    if "total" not in kwargs:
        kwargs["total"] = 5
    if "backoff_factor" not in kwargs:
        kwargs["backoff_factor"] = 1
    if "status_forcelist" not in kwargs:
        kwargs["status_forcelist"] = [502, 503, 504]
    retry_policy = retry.Retry(**kwargs)
    http_adapter = requests.adapters.HTTPAdapter(max_retries=retry_policy)
    session.mount("http://", http_adapter)
    session.mount("https://", http_adapter)


def request(
    session: requests.Session,
    *args: t.Any,
    **kwargs: t.Any,
) -> requests.Response:
    """Forward call to requests and return the response itself.

    The only additional argument is a session.

    :param session: requests session.

    From requests.Request:
    :param method: HTTP method to use.
    :param url: URL to send.
    :param headers: dictionary of headers to send.
    :param files: dictionary of {filename: fileobject} files to multipart upload.
    :param data: the body to attach to the request. If a dictionary or list of tuples [(key, value)] is provided,
        form-encoding will take place.
    :param params: URL parameters to append to the URL. If a dictionary or list of tuples [(key, value)] is provided,
        form-encoding will take place.
    :param auth: Auth handler or (user, pass) tuple.
    :param cookies: dictionary or CookieJar of cookies to attach to this request.
    :param hooks: dictionary of callback hooks, for internal usage.
    :param json: json for the body to attach to the request (if files or data is not specified).

    """
    log.debug("args=%s", args)
    log.debug("kwargs=%s", kwargs)
    req = requests.Request(*args, **kwargs)
    prepared = req.prepare()
    log.info("%s %s ...", prepared.method, prepared.url)
    assert session is not None, "session is None!"
    response = session.send(prepared)
    log.debug("response.status_code=%s", response.status_code)
    response.raise_for_status()
    return response


def get(
    session: requests.sessions.Session,
    url: str,
    params: dict[str, str] | None = None,
) -> str:
    """Log url being fetched with requests.get and return response.text.

    The session is generated on the fly.

    :param session: requests session.
    :param url: url being looked up.
    :param params: parameters passed wit the query.
    :param session: requests session, one will be created if none passed.

    :return: Response from the request.

    """
    req = requests.Request("GET", url, params=params)
    prepared = req.prepare()
    log.info("fetching %s ...", prepared.url)
    response = session.send(prepared)
    response.raise_for_status()
    return response.text
