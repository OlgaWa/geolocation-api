import httpx
from fastapi import HTTPException

from app.config import IPSTACK_API_KEY, IPSTACK_URL


async def fetch_geolocation(ip: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{IPSTACK_URL}/{ip}?access_key={IPSTACK_API_KEY}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"Error while calling ipstack API: {str(e)}."
            )
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from ipstack API: {response.text}.",
            )
        return response.json()
