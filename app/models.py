from pydantic import BaseModel


class GeolocationRequest(BaseModel):
    geo_identifier: str  # IP address or url


class Geolocation(BaseModel):
    ip: str
    ip_type: str
    city: str
    country: str
    region: str | None
    latitude: float
    longitude: float


class ManyGeolocations(BaseModel):
    geolocations: list[Geolocation]
