from pydantic import BaseModel, model_validator


class GeolocationRequest(BaseModel):
    ip: str | None = None
    url: str | None = None

    @model_validator(mode="before")
    def en(cls, values):
        ip = values.get("ip")
        url = values.get("url")

        # Check that at least one of the fields is set
        if not ip and not url:
            raise ValueError("Provide 'ip' or 'url'.")

        return values


class GeolocationResponse(BaseModel):
    ip: str
    ip_type: str
    city: str
    country: str
    latitude: float
    longitude: float
    timezone: str
