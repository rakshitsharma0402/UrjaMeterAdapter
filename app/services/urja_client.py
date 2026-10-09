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
        )
        response.raise_for_status()

        if not self._client.cookies.get(SESSION_COOKIE_NAME):
            raise RuntimeError(
                "Login returned without the expected session cookie."
            )

        self._authenticated = True

    async def _get(self, path: str, params: dict | None = None) -> dict:
        """Make an authenticated GET request."""
        if not self._authenticated:
            raise RuntimeError(
                "UrjaClient is not authenticated. Call login() first."
            )

        response = await self._client.get(path, params=params)
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

