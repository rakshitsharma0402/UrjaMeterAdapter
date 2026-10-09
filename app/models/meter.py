from pydantic import BaseModel, ConfigDict, Field


class Meter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    meter_id: str
    serial_no: str
    make: str
    phase_type: str
    install_status: str
    dt_code: str


class MeterSearchResponse(BaseModel):
    data: list[Meter]
    total: int
    page: int
    page_size: int


class EnergyReading(BaseModel):
    timestamp: str
    kwh: str
    kvah: str
    volt_r: str = Field(validation_alias="voltR")


class EnergyResponse(BaseModel):
    data: list[EnergyReading]


class GeoData(BaseModel):
    latitude: str
    longitude: str


class GeoResponse(BaseModel):
    data: GeoData

