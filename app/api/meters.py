
import httpx

from fastapi import APIRouter, HTTPException, Query, Request
from app.services.urja_client import UrjaAuthenticationError

from app.models.meter import (
    EnergyResponse,
    GeoResponse,
    MeterSearchResponse,
)

router = APIRouter(prefix="/api/v1/meters", tags=["Meters"])



def handle_upstream_error(exc: httpx.HTTPStatusError) -> HTTPException:
    status = exc.response.status_code

    if status == 404:
        return HTTPException(
            status_code=404,
            detail="Meter not found.",
        )

    if status == 401:
        return HTTPException(
            status_code=502,
            detail="Upstream authentication failed.",
        )

    return HTTPException(
        status_code=502,
        detail=f"Upstream request failed with status {status}.",
    )


@router.get("", response_model=MeterSearchResponse)
async def search_meters(
    request: Request,
    q: str = Query(default=""),
    page: int = Query(default=1, ge=1),
):
    client = request.app.state.urja_client

    try:
        result = await client.search_meters(q=q, page=page)

        return {
            "data": [
                {
                    "meter_id": meter["meterId"],
                    "serial_no": meter["serialNo"],
                    "make": meter["make"],
                    "phase_type": meter["phaseType"],
                    "install_status": meter["installStatus"],
                    "dt_code": meter["dtCode"],
                }
                for meter in result["data"]
            ],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["pageSize"],
        }

    except UrjaAuthenticationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Upstream authentication failed.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise handle_upstream_error(exc) from exc


@router.get("/{meter_id}/energy", response_model=EnergyResponse)
async def get_meter_energy(
    meter_id: str,
    request: Request,
):
    client = request.app.state.urja_client

    try:
        return await client.get_energy(meter_id)

    except UrjaAuthenticationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Upstream authentication failed.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise handle_upstream_error(exc) from exc


@router.get("/{meter_id}/geo", response_model=GeoResponse)
async def get_meter_geo(
    meter_id: str,
    request: Request,
):
    client = request.app.state.urja_client

    try:
        return await client.get_geo(meter_id)

    except UrjaAuthenticationError as exc:
        raise HTTPException(
            status_code=502,
            detail="Upstream authentication failed.",
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise handle_upstream_error(exc) from exc

