import importlib.metadata
import json
import logging
import re
import typing

import httpx
import pydantic

from .cache import BaseCache, BasicResolutionCache
from .err import ResolutionError

__all__ = (
    "ClientResolver",
    "server_from_user_id",
    "__version__",
    "SERVER_NAME_REGEX",
)
try:
    from .__version__ import __version__
except ImportError:
    try:
        __version__ = importlib.metadata.version("resolvematrix")
    except importlib.metadata.PackageNotFoundError:
        __version__ = "unknown"

SERVER_NAME_REGEX = re.compile(
    r"^(?:\[([0-9A-Fa-f:.]{2,45})]|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|([0-9A-Za-z.-]{1,255}))(?::(\d{1,5}))?$"
)


class ClientVersionsResponse(pydantic.BaseModel):
    versions: list[str]
    unstable_features: dict[str, bool] = pydantic.Field(default_factory=dict)


def server_from_user_id(user_id: str) -> str:
    """Extracts the server name from a Matrix user ID."""
    if not user_id.startswith("@") or ":" not in user_id:
        raise ValueError("Invalid user ID")
    return user_id.split(":", 1)[1]


def handle_client_well_known(well_known: typing.Any) -> str | None:
    # str = found, None = IGNORE, raise = FAIL
    if not isinstance(well_known, dict):
        # Step 3.3.1: Parse the response body as a JSON object, if the content cannot be parsed, then FAIL.
        raise ResolutionError("Well-known is not a JSON object")

    # 3.4: Extract the base_url value from the m.homeserver property
    if "m.homeserver" not in well_known or not isinstance(well_known["m.homeserver"], dict):
        # 4.1: If this value is not provided, then FAIL.
        raise ResolutionError("Well-known missing m.homeserver")

    homeserver: dict = well_known["m.homeserver"]
    if not (base_url := homeserver.get("base_url")) or not isinstance(base_url, str):
        # 4.1: If this value is not provided, then FAIL.
        raise ResolutionError("Well-known missing base_url in m.homeserver")

    # 5: Validate the homeserver base URL
    # 5.1: Parse it as a URL. If it is not a URL, then FAIL.
    parsed = httpx.URL(base_url)
    if parsed.host == "" or parsed.scheme not in ("http", "https"):
        raise ResolutionError("Well-known base_url is not a valid URL")
    return str(parsed).rstrip("/")


def limited_read(response: httpx.Response, limit: int, chunk_size: int) -> typing.Any:
    """
    Attempts to read and parse a JSON response while limiting the total size read.
    Prevents zip bombs and whatnot.

    :param response: The response to read from.
    :param limit: The maximum number of bytes to read.
    :param chunk_size: The size of each chunk to read.
    :return: The parsed JSON data.
    :raises: IOError if the response is too large or cannot be parsed.
    """
    data = b""
    for chunk in response.iter_bytes(chunk_size=chunk_size):
        data += chunk
        if len(data) > limit:
            raise IOError("Response too large (>%d KiB)" % round(limit / 1024))

    try:
        return response.json()
    except ValueError as e:
        raise IOError("Failed to parse JSON") from e


class ClientResolver:
    """
    Resolves a Matrix server's client-to-server API endpoint using the client well-known method,
    falling back to a default (https://{server_name}:8448).

    Caches results in a provided cache backend (or an in-memory cache by default).

    :param client: An optional httpx.Client instance to use for HTTP requests. If not provided, a default client
    will be created.
    :param cache: An optional cache backend implementing the BaseCache interface. If not provided, an in-memory
    cache will be used.
    :param verify_tls: Whether to verify TLS certificates. Defaults to True.
    """
    RESPONSE_SIZE_LIMIT = 1024 * 64  # 64 KiB
    RESPONSE_CHUNK_SIZE = 1024 * 8  # 8 KiB

    def __init__(
            self,
            client: httpx.Client | None = None,
            cache: BaseCache | None = None,
            verify_tls: bool = True
    ):
        self.client = client or httpx.Client(
            headers={
                "User-Agent": f"resolvematrix/{__version__}",
                "Accept": "application/json",
            },
            timeout=10.0,
            follow_redirects=False,
            max_redirects=30,  # MSC2499 (can't be overridden per-call for some reason)
            trust_env=True,
            verify=verify_tls,
        )
        self.cache = cache or BasicResolutionCache()
        self.log = logging.getLogger("resolvematrix.client")

    def get_client_versions(self, base_url: str) -> ClientVersionsResponse:
        """
        Attempts to fetch the /_matrix/client/versions endpoint from a given base URL, and validates the response.
        :param base_url: The base URL of the Matrix server.
        :return: True if the endpoint was fetched and parsed successfully, False otherwise.
        """
        url = base_url.rstrip("/") + "/_matrix/client/versions"
        response = self.client.get(url).raise_for_status()
        data = limited_read(response, self.RESPONSE_SIZE_LIMIT, self.RESPONSE_CHUNK_SIZE)
        v = ClientVersionsResponse.model_validate(data, strict=True)
        self.log.debug("Client versions at %s: %s", base_url, v)
        return v

    def get_well_known(self, server_name: str, msc4299: bool = False) -> tuple[typing.Any, int]:
        """
        Fetches and returns the well-known configuration for a given Matrix server.

        :param server_name: The domain name of the Matrix server.
        :param msc4299: Whether to use the MSC4299 changes for well-known lookups.
        :return: The parsed JSON data if available.
        """
        url = f"https://{server_name}/.well-known/matrix/client"
        response = self.client.get(url, follow_redirects=msc4299).raise_for_status()
        expires = 0
        if "Cache-Control" in response.headers:
            cache_control = response.headers["Cache-Control"]
            match = re.search(r"max-age=(\d+)", cache_control)
            if match:
                try:
                    expires = int(match.group(1))
                except ValueError:
                    pass
        return (
            limited_read(response, 50 * 1024 if msc4299 else self.RESPONSE_SIZE_LIMIT, self.RESPONSE_CHUNK_SIZE),
            expires,
        )

    def resolve(self, server_name: str, extra_validation: bool = True, unstable_follow_redirects: bool = False) -> str:
        """
        Resolves a Matrix server's client-to-server API endpoint.
        :param server_name: The domain name of the Matrix server.
        :param extra_validation: Whether to perform extra validation on the resolved URL by calling the client versions
        endpoint. Slightly increases response time but ensures the server is actually a Matrix server.
        :param unstable_follow_redirects: Whether to follow HTTP redirects, which is not explicitly defined in the
        specification yet. See: MSC2499
        :return: the resolved base URL without a trailing slash.
        :raises ResolutionError: - the server cannot be resolved.
        :raises ValueError: - the server name format is invalid.
        """
        # Cheat: if the server name is actually a URL, just return that.
        if server_name.startswith("http://") or server_name.startswith("https://"):
            parsed = httpx.URL(server_name)
            if parsed.host != "" and parsed.scheme in ("http", "https"):
                return str(parsed).rstrip("/")

        # Fetch from cache first
        if cached := self.cache.get(server_name):
            self.log.debug("Cache hit for %s: %s", server_name, cached)
            return cached

        # Step 1: Extract the server name from user ID (done before this function is called)
        # Step 2: Extract the hostname from the server name
        match = SERVER_NAME_REGEX.match(server_name.strip())
        if not match:
            raise ValueError("Invalid server name")
        hostname = match.group(0)
        default_dest = "https://" + hostname

        # Step 3: Fetch the well-known file
        try:
            self.log.debug("Resolving well-known for %s", hostname)
            well_known, expires = self.get_well_known(hostname, unstable_follow_redirects)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Step 3.1: If the response status is 404, IGNORE.
                # Our interpretation of "IGNORE" is to just use the default.
                self.log.info("No well-known file found found %s, using default destination", hostname)
                self.cache.add(server_name, default_dest)
                self.cache.mark_offline(server_name)  # forces resolution sooner
                return default_dest
            # Step 3.2: If the response status is not 200, or the response body is invalid, FAIL.
            raise ResolutionError("Failed to fetch well-known", e) from e
        except (httpx.HTTPError, ResolutionError) as e:
            # Step 3.2: If the response status is not 200, or the response body is invalid, FAIL.
            raise ResolutionError("Failed to fetch well-known", e) from e
        except (OSError, json.JSONDecodeError) as e:
            # Step 3.2: If the response status is not 200, or the response body is invalid, FAIL.
            raise ResolutionError("Failed to read or parse well-known", e) from e

        # Step 3-5.1: Parse and validate the well-known
        current_dest = handle_client_well_known(well_known) or default_dest

        # Step 5.2: Clients SHOULD validate that the URL points to a valid homeserver before accepting it by connecting
        # to the /_matrix/client/versions endpoint, ensuring that it does not return an error, and parsing and
        # validating that the data conforms with the expected response format. If any step in the validation fails,
        # then FAIL.
        if extra_validation:
            self.log.debug("Validating resolved base URL %s for %s", current_dest, hostname)
            try:
                self.get_client_versions(current_dest)
            except (httpx.HTTPError, IOError, pydantic.ValidationError) as e:
                raise ResolutionError("Resolved base URL did not validate as a Matrix homeserver", e) from e

        # Return the resolved base URL without a trailing slash
        self.cache.add(server_name, current_dest, expires)
        return current_dest.rstrip("/")
