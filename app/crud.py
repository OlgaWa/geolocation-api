import logging

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app import exceptions
from app.models import Geolocation

logger = logging.getLogger(__name__)


class GeoLocationCRUD:
    def __init__(
        self, db: AsyncIOMotorDatabase, collection_name: str = "geolocations"
    ):
        self.collection: AsyncIOMotorCollection = db[collection_name]

    async def create(self, data: Geolocation) -> Geolocation:
        """Create a new geolocation object"""
        data_dict = data.model_dump()
        existing_doc = await self.collection.find_one(
            {"ip": data_dict.get("ip")}
        )
        if existing_doc:
            raise exceptions.AlreadyExistsError(
                f"Object with IP '{data.ip}' already exists in the database."
            )
        try:
            await self.collection.insert_one(data_dict)
        except Exception as e:
            logging.error(f"Database error during document creation: {e}.")
            raise exceptions.DBError(
                f"Failed to insert a document {data_dict} into the database."
            )
        return data

    async def get_by_ip(self, ip: str) -> Geolocation:
        """Find a geolocation object by IP address"""
        try:
            document = await self.collection.find_one({"ip": ip})
        except Exception as e:
            logging.error(f"Database error during document retrieval: {e}.")
            raise exceptions.DBError(
                f"Failed to get a document with IP {ip}.",
            )
        if not document:
            raise exceptions.NotFoundError(
                f"Object with an IP address {ip} not found.",
            )
        return Geolocation(**document)

    async def delete(self, ip: str) -> bool:
        """Delete a geolocation object by IP adress"""
        try:
            delete_result = await self.collection.delete_one({"ip": ip})
        except Exception as e:
            logging.error(f"Database error during document deletion: {e}.")
            raise exceptions.DBError(
                f"Failed to delete a document with ip {ip}.",
            )
        return delete_result.deleted_count > 0

    async def list_all(self) -> list[Geolocation]:
        """List all geolocation objects"""
        try:
            cursor = self.collection.find()
        except Exception as e:
            logging.error(f"Database error during documents retrieval: {e}.")
            raise exceptions.DBError(
                f"Failed to get all the geolocation documents.",
            )
        geolocations = [Geolocation(**doc) async for doc in cursor]
        return geolocations
