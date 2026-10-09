# Upstream API Protocol

## 1. Purpose

This document describes how UrjaMeterAdapter communicates with the upstream Urja Meter Ops portal, including authentication, request handling, endpoint mapping, and error translation.

The adapter exposes a separate REST API to its consumers. Its OpenAPI specification is provided in `openapi.json`.

## 2. Upstream Service

- **Base URL:** Configured through `URJA_BASE_URL`
- **Default URL:** `https://urja-ops.flockenergy.tech`
- **HTTP client:** `httpx.AsyncClient`
- **Request timeout:** 20 seconds

The configured base URL is normalized by removing a trailing slash.

## 3. Authentication Protocol

### 3.1 Login Request

The adapter authenticates using `POST /login`.

The request sends form data containing:

| Field | Description |
|---|---|
| `email` | Upstream account email from `URJA_EMAIL` |
| `password` | Upstream account password from `URJA_PASSWORD` |

The request includes these headers:

- `Origin`: Configured upstream base URL
- `Referer`: Configured upstream base URL followed by `/login`

Credentials are loaded from environment configuration. If either credential is missing, the client raises an authentication error before sending the login request.

### 3.2 Session Management

After login, the client checks for the following session cookie:

`__Secure-better-auth.session_token`

The HTTP client retains cookies for subsequent requests. Authentication is considered established only when the expected session cookie is present.

If the login response does not establish the expected session, the client raises `UrjaAuthenticationError`.

### 3.3 Reauthentication and Retry

Before an upstream GET request, the client authenticates if it has not already done so.

If a GET request returns HTTP `401 Unauthorized`:

1. The client marks its authentication state as invalid.
2. It attempts to log in again.
3. It retries the original GET request once.

The client does not perform additional retries if the retried request also fails.

## 4. Upstream Endpoints

All paths below are relative to the configured upstream base URL.

| Operation | Method | Path | Parameters |
|---|---|---|---|
| Login | POST | `/login` | Form fields: `email`, `password` |
| Search meters | GET | `/portal/meters/search` | `q`, `page` |
| Retrieve energy readings | GET | `/portal/meters/{meter_id}/energy` | Meter ID in path |
| Retrieve geolocation | GET | `/portal/meters/{meter_id}/geo` | Meter ID in path |

### 4.1 Meter Search

The client calls `/portal/meters/search` with:

- `q`: Search query; defaults to an empty string.
- `page`: Page number; defaults to `1`.

The adapter maps upstream meter fields to its public response model:

| Upstream field | Adapter field |
|---|---|
| `meterId` | `meter_id` |
| `serialNo` | `serial_no` |
| `make` | `make` |
| `phaseType` | `phase_type` |
| `installStatus` | `install_status` |
| `dtCode` | `dt_code` |
| `pageSize` | `page_size` |

The search response also preserves `data`, `total`, and `page`.

### 4.2 Energy Readings

The client calls:

`GET /portal/meters/{meter_id}/energy`

The upstream response is returned through the adapter's `EnergyResponse` Pydantic model. The documented fields include a list of readings with `timestamp`, `kwh`, `kvah`, and `volt_r`; the upstream field `voltR` is accepted as the validation alias for `volt_r`.

Refer to the adapter's OpenAPI specification for the complete public response schema.

### 4.3 Geolocation

The client calls:

`GET /portal/meters/{meter_id}/geo`

The adapter validates the response using `GeoResponse`, which contains a `data` object with `latitude` and `longitude`.

## 5. Error Handling

The adapter translates selected upstream failures into public HTTP responses.

| Upstream or client condition | Adapter response |
|---|---|
| Upstream HTTP 404 | HTTP 404 — `Meter not found.` |
| Upstream HTTP 401 after retry | HTTP 502 — `Upstream authentication failed.` |
| Missing credentials or missing session cookie | HTTP 502 — `Upstream authentication failed.` |
| Other upstream HTTP status errors | HTTP 502 — `Upstream request failed with status {status}.` |
| Invalid page number (`page < 1`) | HTTP 422 through FastAPI request validation |

The adapter does not expose upstream credentials or session-cookie values in its public error messages.

## 6. Response Validation

Pydantic response models define the adapter's public data contract:

- `MeterSearchResponse`
- `EnergyResponse`
- `GeoResponse`

FastAPI validates and serializes endpoint responses against the configured response models.

## 7. Scope and Limitations

- The adapter currently supports meter search, energy readings, and geolocation.
- Authentication uses the upstream portal's session-cookie mechanism.
- A GET request is retried once after HTTP 401.
- The client explicitly translates `httpx.HTTPStatusError` and `UrjaAuthenticationError` in the API routes.
- Other exceptions, including network-level errors and JSON decoding failures, are not explicitly translated by these route handlers.
- The upstream response schemas are documented only to the extent confirmed by the current client and Pydantic models.

## 8. Related Files

- `app/services/urja_client.py` — upstream HTTP requests and authentication.
- `app/api/meters.py` — adapter routes and error translation.
- `app/models/meter.py` — response models and field mapping.
- `app/config.py` — upstream URL and credential configuration.
- `openapi.json` — machine-readable specification of the adapter's public API.