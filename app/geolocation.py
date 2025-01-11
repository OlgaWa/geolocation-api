import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from app import exceptions
from app.config import IPSTACK_API_KEY, IPSTACK_URL
from app.models import Geolocation


class GeolocationFetcher:
    geo_identifier: str

    def __init__(self, geo_identifier: str):
        self.geo_identifier = geo_identifier

    async def fetch_geolocation(self) -> Geolocation:
        ip = self.get_ip_address()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{IPSTACK_URL}/{ip}?access_key={IPSTACK_API_KEY}"
                )
            except Exception as e:
                raise exceptions.IPStackAPIConnectionError(
                    f"Error while calling IPStack API: {str(e)}."
                )
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error from IPStack API: {response.text}.",
                )

            try:
                data: dict = response.json()
                return Geolocation(
                    ip=ip,
                    ip_type=data.get("type"),
                    country=data.get("country_name", ""),
                    city=data.get("city", ""),
                    region=data.get("region", ""),
                    latitude=data.get("latitude"),
                    longitude=data.get("longitude"),
                )
            except:
                raise exceptions.WrongDataFormatError(
                    f"Unexpected response from IPStack API: {data}."
                )

    def get_ip_address(self) -> str:
        try:
            ipaddress.ip_address(self.geo_identifier)
            ip = self.geo_identifier
        except:
            ip = self._get_ip_from_url(self.geo_identifier)
        return ip

    def _get_ip_from_url(self, url: str) -> str:
        """Resolve an URL to an IP address"""
        if url.startswith("http"):
            parsed_url = urlparse(url)
            host = parsed_url.netloc.split(":")[0]
        else:
            host = url.split("/")[0]

        try:
            ip = socket.gethostbyname(host)
            return ip
        except socket.gaierror:
            raise ValueError(f"Could not resolve URL {url} to an IP address.")
