import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app import exceptions
from app.crud import GeoLocationCRUD
from app.database import MONGO_CLIENT, get_db, init_db
from app.geolocation import GeolocationFetcher
from app.models import Geolocation, GeolocationRequest, ManyGeolocations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Connecting to MongoDB...")
    try:
        await init_db()
    except exceptions.DBError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )
    yield

    # Shutdown
    if MONGO_CLIENT:
        logger.info("Closing MongoDB connection...")
        MONGO_CLIENT.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def main():
    return {"message": "Welcome to the Geolocation API!"}


@app.post("/geolocations", status_code=201, response_model=Geolocation)
async def create_geolocation(
    data: GeolocationRequest, db: AsyncIOMotorDatabase = Depends(get_db)
):
    crud = GeoLocationCRUD(db)
    geo_fetcher = GeolocationFetcher(data.geo_identifier)

    try:
        geolocation_data = await geo_fetcher.fetch_geolocation()
    except exceptions.IPStackAPIConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )
    except exceptions.WrongDataFormatError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        geolocation = await crud.create(geolocation_data)
    except exceptions.AlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )
    except exceptions.DBError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return geolocation


@app.get("/geolocations", status_code=200, response_model=ManyGeolocations)
async def list_geolocations(db: AsyncIOMotorDatabase = Depends(get_db)):
    crud = GeoLocationCRUD(db)

    try:
        geolocations = await crud.list_all()
    except exceptions.DBError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return ManyGeolocations(geolocations=geolocations)


@app.get(
    "/geolocations/{geo_identifier}",
    status_code=200,
    response_model=Geolocation,
)
async def get_geolocation(
    geo_identifier: str, db: AsyncIOMotorDatabase = Depends(get_db)
):
    crud = GeoLocationCRUD(db)
    geo_fetcher = GeolocationFetcher(geo_identifier)

    try:
        ip = geo_fetcher.get_ip_address()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        geolocation = await crud.get_by_ip(ip)
    except exceptions.NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except exceptions.DBError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return geolocation


@app.delete("/geolocations/{geo_identifier}", status_code=204)
async def delete_geolocation_data(
    geo_identifier: str, db: AsyncIOMotorDatabase = Depends(get_db)
):
    crud = GeoLocationCRUD(db)
    geo_fetcher = GeolocationFetcher(geo_identifier)

    try:
        ip = geo_fetcher.get_ip_address()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        await crud.delete(ip)
    except exceptions.DBError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
