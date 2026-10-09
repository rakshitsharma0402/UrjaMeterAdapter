# Urja Meter Adapter

A FastAPI-based API adapter for the Urja Meter Ops portal. It exposes meter search, energy, and geolocation data through a REST API while handling upstream authentication, request validation, and errors.

**Documentation:** [Protocol Documentation](PROTOCOL.md) · [OpenAPI Specification](openapi.json) · [MIT License](LICENSE)

## Features

- Search meters using a query and pagination.
- Retrieve energy readings for a specific meter.
- Retrieve geolocation data for a specific meter.
- Authenticate with the upstream Urja Meter Ops portal.
- Retry a failed request once after receiving an upstream HTTP 401 response.
- Handle authentication failures and invalid meter requests.
- Validate request parameters using FastAPI.
- Test API endpoints and authentication recovery using pytest.

## Tech Stack

- **Python** — application language
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI development server
- **HTTPX** — asynchronous HTTP client
- **Pydantic** — data validation and serialization
- **python-dotenv** — environment variable loading
- **pytest** — automated testing

## Architecture

The adapter acts as an intermediary between API consumers and the Urja Meter Ops portal.

```text
API Consumer
     |
     v
FastAPI Adapter
     |
     v
UrjaClient
     |
     | Authentication and HTTP requests
     v
Urja Meter Ops Portal
     |
     v
Meter Data
```

The adapter exposes its own REST endpoints and uses the upstream portal to retrieve meter information.

## Project Structure

```text
UrjaMeterAdapter/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   └── meters.py
│   ├── models/
│   │   └── meter.py
│   └── services/
│       └── urja_client.py
├── tests/
│   ├── test_meters_api.py
│   └── test_urja_client.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- Python installed on your system
- Access to the Urja Meter Ops portal
- Valid upstream portal credentials

## Installation

### 1. Clone the repository

```bash
git clone git@github.com:rakshitsharma0402/UrjaMeterAdapter.git
cd UrjaMeterAdapter
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root:

```dotenv
URJA_BASE_URL=https://urja-ops.flockenergy.tech
URJA_EMAIL=your_email@example.com
URJA_PASSWORD=your_password
```

| Variable | Required | Description |
|---|---|---|
| `URJA_BASE_URL` | No | Base URL of the upstream portal. Defaults to `https://urja-ops.flockenergy.tech`. |
| `URJA_EMAIL` | Yes | Email address used to authenticate with the upstream portal. |
| `URJA_PASSWORD` | Yes | Password used to authenticate with the upstream portal. |

The application loads environment variables using `python-dotenv`. If `URJA_BASE_URL` is not set, the default URL is used. Valid upstream credentials are required to retrieve meter data.

**Security:** Never commit your real `.env` file or expose credentials, passwords, or session cookies in source code, logs, screenshots, or API responses.

## Running the Application

Start the development server from the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

| Resource | URL |
|---|---|
| Base URL | `http://127.0.0.1:8000/` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |
| Health check | `http://127.0.0.1:8000/health` |

These addresses are for local development. The application must be deployed to make it accessible to external users.

## API Reference

All meter endpoints use the `/api/v1` prefix. The root and health endpoints are outside this prefix.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns basic application information |
| GET | `/health` | Checks whether the adapter is running |
| GET | `/api/v1/meters` | Searches meters with pagination |
| GET | `/api/v1/meters/{meter_id}/energy` | Retrieves energy readings |
| GET | `/api/v1/meters/{meter_id}/geo` | Retrieves geolocation data |

### 1. Root Endpoint

**`GET /`**

Returns basic application information and links to useful resources.

Example request:

```bash
curl http://127.0.0.1:8000/
```

### 2. Health Check

**`GET /health`**

Checks whether the adapter is running.

Example request:

```bash
curl http://127.0.0.1:8000/health
```

Example response:

```json
{
  "status": "ok"
}
```

### 3. Search Meters

**`GET /api/v1/meters`**

Searches for meters using a query and page number.

Query parameters:

| Parameter | Type | Description |
|---|---|---|
| `q` | String | Meter search query |
| `page` | Integer | Page number; must be at least 1 |

Example request:

```bash
curl "http://127.0.0.1:8000/api/v1/meters?q=J100019&page=1"
```

Example response:

```json
{
  "data": [
    {
      "meter_id": "J100019",
      "serial_no": "GE24621",
      "make": "L&T",
      "phase_type": "single",
      "install_status": "Decommissioned",
      "dt_code": "DT-020"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

The example illustrates the response structure; actual results depend on the upstream portal.

### 4. Retrieve Energy Data

**`GET /api/v1/meters/{meter_id}/energy`**

Retrieves energy readings for the specified meter.

Example request:

```bash
curl "http://127.0.0.1:8000/api/v1/meters/J100019/energy"
```

Example response structure:

```json
{
  "data": [
    {
      "timestamp": "2026-10-09T12:00:00",
      "kwh": "125.50",
      "kvah": "132.75",
      "volt_r": "230.4"
    }
  ]
}
```

The values are illustrative, not verified readings from the upstream portal. The model represents these fields as strings.

### 5. Retrieve Geolocation Data

**`GET /api/v1/meters/{meter_id}/geo`**

Retrieves geographical coordinates for the specified meter.

Example request:

```bash
curl "http://127.0.0.1:8000/api/v1/meters/J100019/geo"
```

Example response:

```json
{
  "data": {
    "latitude": "27.01089",
    "longitude": "75.83053"
  }
}
```

The coordinates are illustrative. Actual values depend on the upstream response.

## Response Models

The adapter uses Pydantic models to validate and structure its responses.

| Model | Fields |
|---|---|
| `MeterSearchResponse` | `data`, `total`, `page`, `page_size` |
| `Meter` | `meter_id`, `serial_no`, `make`, `phase_type`, `install_status`, `dt_code` |
| `EnergyResponse` | `data` — a list of energy readings |
| `EnergyReading` | `timestamp`, `kwh`, `kvah`, `volt_r` |
| `GeoResponse` | `data` containing `latitude` and `longitude` |

The energy model maps the upstream field `voltR` to the adapter's `volt_r` field.

## Error Handling

The adapter handles invalid requests and upstream failures.

| HTTP status | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `404 Not Found` | Requested meter was not found |
| `422 Unprocessable Entity` | Request validation failed, such as an invalid page number |
| `502 Bad Gateway` | Upstream authentication failed or an upstream service error occurred |

When an upstream GET request returns HTTP 401, the client attempts to authenticate again and retries the request once. If the retry also fails, the upstream HTTP error is propagated and handled by the adapter.

Authentication failures are returned without exposing upstream credentials or session cookies.

## Running Tests

Run the complete test suite from the project root:

```bash
python -m pytest -v
```

The current test suite contains seven tests covering:

- Successful meter searches
- Empty search results
- Authentication failure responses
- Pagination validation
- Re-authentication after an upstream HTTP 401
- Failure after a second HTTP 401
- Login failure when a valid session cookie is not established

The suite has been verified with **7 passing tests**.

## Security Considerations

- Store credentials in environment variables rather than hardcoding them.
- Keep `.env` excluded from version control.
- Never log passwords or session cookies.
- Avoid exposing sensitive upstream responses to API consumers.
- Use appropriate secret management and HTTPS configuration when deploying the application.

## Design Trade-offs

- **Session-cookie authentication:** The adapter reuses the upstream portal's session cookie instead of requiring API consumers to authenticate directly with the portal. This simplifies client integration but couples the adapter to the upstream authentication mechanism.
- **Single retry:** The client reauthenticates and retries once after HTTP 401. This handles expired sessions without risking an unbounded retry loop.
- **Pydantic response models:** Explicit response models provide a predictable API contract and normalize upstream field names. However, changes in the upstream response structure may require corresponding model updates.
- **Thin adapter architecture:** The adapter focuses on authentication, data retrieval, validation, and error translation rather than storing data locally. This keeps the implementation simple but makes request availability dependent on the upstream service.

## Reflection

This project provided practical experience building an asynchronous REST API adapter with FastAPI and HTTPX. It involved integrating with a session-based upstream service, translating upstream responses into stable Pydantic models, handling authentication failures, and testing retry behavior.

One important lesson was that a successful HTTP response alone does not guarantee successful authentication; the adapter also needs to verify that the expected session cookie was established. Automated tests helped validate both successful requests and failure scenarios.

Potential future improvements include more comprehensive handling of network errors, structured logging, and additional tests for upstream response variations.

## License

MIT