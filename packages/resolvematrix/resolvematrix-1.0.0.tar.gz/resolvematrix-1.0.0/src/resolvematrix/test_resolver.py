import logging

import pytest

from . import ServerDestination
from .client import ClientResolver, server_from_user_id
from .err import ResolutionError
from .server import ServerResolver


@pytest.mark.parametrize(
    "user_id,extra,expected,fail",
    [
        ("@github:maunium.net", True, "https://api.mau.chat", None),
        ("@nex:timedout.uk", True, "https://timedout.uk", None),
        ("@nex:timedout.uk:69", True, "https://timedout.uk:69", None),
        ("@nex:nexy7574.co.uk", True, "https://matrix.nexy7574.co.uk", None),
        ("@nex:transgender.ing", True, "https://matrix.transgender.ing", None),
        ("@nex:localhost:8448", False, "https://localhost:8448", ResolutionError),
        ("@nex:localhost", False, "https://localhost", ResolutionError),
        ("@nex:localhost..invalid", True, "", ValueError),
    ],
)
def test_client_resolver(user_id: str, extra: bool, expected: str, fail: Exception | None):
    server_name = server_from_user_id(user_id)
    resolver = ClientResolver()
    if fail:
        with pytest.raises(fail):
            resolver.resolve(server_name, extra_validation=extra)
    else:
        resolved = resolver.resolve(server_name, extra_validation=extra)
        assert resolved == expected, f"Expected {expected}, got {resolved}"


@pytest.mark.parametrize(
    "server_name,fail",
    [
        ("maunium.net", None),
        ("timedout.uk", None),
        ("timedout.uk:69", None),
        ("nexy7574.co.uk", None),
        ("transgender.ing", None),
        ("matrix.org", None),
        ("2.s.resolvematrix.dev:7652", None),
        ("3b.s.resolvematrix.dev", None),
        ("3c.s.resolvematrix.dev", None),
        ("3d.s.resolvematrix.dev", None),
        ("4.s.resolvematrix.dev", None),
        ("5.s.resolvematrix.dev", None),
        ("3c.msc4040.s.resolvematrix.dev", None),
        ("4.msc4040.s.resolvematrix.dev", None),
    ],
)
def test_server_resolver(caplog, server_name: str, fail: Exception | None):
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("resolvematrix.test")
    resolver = ServerResolver()
    if fail:
        with pytest.raises(fail):
            resolver.resolve(server_name)
    else:
        resolved = resolver.resolve(server_name)
        logger.info("Resolved %s to %r", server_name, resolved)
        logger.info(
            "Fetching %s/_matrix/federation/v1/version (%r, base_url=%r)",
            resolved.base_url,
            resolved,
            resolved.base_url,
        )
        key_req = resolver.client.build_request(
            "GET",
            f"{resolved.base_url}/_matrix/federation/v1/version",
            headers={"Host": resolved.host_header},
            extensions={"sni_hostname": resolved.sni} if resolved.sni else None,
        )
        response = resolver.client.send(key_req)
        logger.debug("Response: %s", response.text)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        # assert response.json()["server_name"] == server_name


def test_resolver_cache():
    res = ClientResolver()
    res.resolve("maunium.net")
    res.resolve("timedout.uk")
    assert res.cache.size == 2
    assert res.cache.get("maunium.net") is not None
    assert isinstance(res.cache.get("timedout.uk"), str)

    res.cache.clear()
    assert res.cache.size == 0
    assert res.cache.get("maunium.net") is None
    assert res.cache.get("timedout.uk") is None

    res = ServerResolver()
    res.resolve("maunium.net")
    res.resolve("timedout.uk")
    assert res.cache.size == 2
    assert res.cache.get("maunium.net") is not None
    assert isinstance(res.cache.get("timedout.uk"), ServerDestination)
    assert res.cache.get_entry("maunium.net").offline is False
    assert res.cache.get_entry("maunium.net").expires.timestamp() > 0


@pytest.mark.parametrize(
    "server_name,expect_name",
    [
        ("maunium.net", "Synapse"),
        ("timedout.uk", ""),
        ("nexy7574.co.uk", "continuwuity"),
        ("dendrite.matrix.org", "Dendrite")
    ]
)
def test_server_version_fetcher(server_name: str, expect_name: str):
    resolver = ServerResolver()
    dest = resolver.resolve(server_name)
    ver = resolver.get_server_version(dest)
    assert ver[0] == expect_name, f"Expected {expect_name}, got {ver[0]}"


@pytest.mark.parametrize(
    "server_name",
    [
        "maunium.net",
        "timedout.uk",
        "nexy7574.co.uk",
        "dendrite.matrix.org"
    ]
)
def test_client_version_fetcher(server_name: str):
    resolver = ClientResolver()
    loc = resolver.resolve(server_name)
    ver = resolver.get_client_versions(loc)
    assert len(ver.versions) > 0, "Expected at least one version"
