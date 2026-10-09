
import httpx

from app.config import URJA_BASE_URL, URJA_EMAIL, URJA_PASSWORD


SESSION_COOKIE_NAME = "__Secure-better-auth.session_token"


class UrjaClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=URJA_BASE_URL.rstrip("/"),
            timeout=20.0,
        )
        self._authenticated = False

    async def login(self) -> None:
        """Authenticate and retain the upstream session cookie."""
        if not URJA_EMAIL or not URJA_PASSWORD:
            raise RuntimeError(
                "URJA_EMAIL and URJA_PASSWORD must be configured."
            )

        response = await self._client.post(
            "/login",
            data={
                "email": URJA_EMAIL,
                "password": URJA_PASSWORD,
            },
            headers={
                "Origin": URJA_BASE_URL.rstrip("/"),
                "Referer": f"{URJA_BASE_URL.rstrip('/')}/login",
            },
        )

        if response.status_code >= 400:
            print("Urja login failed:", response.status_code)
            print("Response:", response.text[:500])

        response.raise_for_status()

        # Diagnostic checks: print cookie names, never cookie values.
        session_cookie = self._client.cookies.get(
            SESSION_COOKIE_NAME
        )

        if not session_cookie:
            print("Login response status:", response.status_code)
            print("Login response URL:", response.url)
            print("Login response body:", response.text[:500])
            print(
                "Cookie names received:",
                list(self._client.cookies.keys()),
            )
            raise RuntimeError(
                "Login returned without the expected session cookie."
            )

        self._authenticated = True

    async def ensure_authenticated(self) -> None:
        """Log in if the client is not currently authenticated."""
        if not self._authenticated:
            await self.login()

    async def _get(
            self,
            path: str,
            params: dict | None = None,
    ) -> dict:
        """Make an authenticated GET request with one auth retry."""
        await self.ensure_authenticated()

        response = await self._client.get(path, params=params)

        if response.status_code == 401:
            # The upstream session may have expired.
            self._authenticated = False
            await self.login()

            response = await self._client.get(path, params=params)

        if response.status_code >= 400:
            print("Urja GET failed:", response.status_code)
            print("Path:", path)
            print("Response:", response.text[:500])

        response.raise_for_status()
        return response.json()

    async def search_meters(
        self,
        q: str = "",
        page: int = 1,
    ) -> dict:
        return await self._get(
            "/portal/meters/search",
            params={"q": q, "page": page},
        )

    async def get_energy(self, meter_id: str) -> dict:
        return await self._get(
            f"/portal/meters/{meter_id}/energy"
        )

    async def get_geo(self, meter_id: str) -> dict:
        return await self._get(
            f"/portal/meters/{meter_id}/geo"
        )

    async def close(self) -> None:
        """Release the HTTP connection pool."""
        await self._client.aclose()

