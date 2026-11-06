import re

import httpx

from tyxter import Tyxter, TyxterBootstrap, __version__

# PEP 440: release segment, with optional pre/post/dev suffixes. Asserting the
# shape rather than a literal keeps this test about "the package exports a
# usable version" — its actual subject — instead of failing on every release.
# A malformed version is the real failure here, because hatchling reads
# __version__ as the package version and packaging would break on it.
_PEP440 = re.compile(r"^\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?$")


def test_package_exports_client_and_version() -> None:
    client = Tyxter(api_key="tx_sandbox_test", base_url="http://localhost:3001/")

    assert isinstance(__version__, str)
    assert _PEP440.match(__version__), f"{__version__!r} is not a valid PEP 440 version"
    assert client.api_key == "tx_sandbox_test"
    assert client.base_url == "http://localhost:3001"


def test_package_source_version_tracks_the_shared_0_12_line() -> None:
    assert __version__ == "0.12.0.post1"


def test_both_client_user_agent_paths_derive_from_the_candidate_version() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"status": "pending"})

    client = Tyxter(api_key="tx_sandbox_test")
    bootstrap = TyxterBootstrap(
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )
    try:
        assert (
            client._headers(
                idempotency_key=None,
                trace_id=None,
                has_body=False,
            )["User-Agent"]
            == "tyxter-python/0.12.0.post1"
        )
        bootstrap._request(
            "POST",
            "/v1/agent-api-key-device-authorizations",
            json={},
            trace_id=None,
        )
    finally:
        client.close()
        bootstrap.close()

    assert seen[0].headers["user-agent"] == "tyxter-python/0.12.0.post1"


def test_client_requires_api_key() -> None:
    try:
        Tyxter(api_key="")
    except ValueError as exc:
        assert str(exc) == "api_key is required"
    else:
        raise AssertionError("expected ValueError")
