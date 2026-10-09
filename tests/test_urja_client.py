
import httpx
import pytest

from app.services.urja_client import UrjaClient


@pytest.mark.asyncio
async def test_get_reauthenticates_after_401():
    client = UrjaClient()
    login_calls = 0
    get_calls = 0

    async def fake_login():
        nonlocal login_calls
        login_calls += 1
        client._authenticated = True

    async def fake_get(path, params=None):
        nonlocal get_calls
        get_calls += 1

        request = httpx.Request("GET", f"https://example.com{path}")

        if get_calls == 1:
            return httpx.Response(401, request=request)

        return httpx.Response(
            200,
            json={"data": []},
            request=request,
        )

    client.login = fake_login
    client._client.get = fake_get

    # Simulate a client that already has an authenticated session.
    client._authenticated = True

    try:
        result = await client._get("/portal/meters/search")

        assert result == {"data": []}
        assert login_calls == 1
        assert get_calls == 2
        assert client._authenticated is True
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_get_stops_after_second_401():
    client = UrjaClient()
    login_calls = 0
    get_calls = 0

    async def fake_login():
        nonlocal login_calls
        login_calls += 1
        client._authenticated = True

    async def fake_get(path, params=None):
        nonlocal get_calls
        get_calls += 1

        request = httpx.Request(
            "GET",
            f"https://example.com{path}",
        )
        return httpx.Response(401, request=request)

    client.login = fake_login
    client._client.get = fake_get
    client._authenticated = True

    try:
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client._get("/portal/meters/search")

        assert exc_info.value.response.status_code == 401
        assert login_calls == 1
        assert get_calls == 2
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_login_raises_authentication_error_without_session_cookie():
    from app.services.urja_client import UrjaAuthenticationError

    client = UrjaClient()

    async def fake_post(*args, **kwargs):
        request = httpx.Request("POST", "https://example.com/login")
        return httpx.Response(
            200,
            json={
                "type": "failure",
                "status": 401,
                "data": "Invalid email or password.",
            },
            request=request,
        )

    client._client.post = fake_post

    try:
        with pytest.raises(UrjaAuthenticationError):
            await client.login()

        assert client._authenticated is False
    finally:
        await client.close()

