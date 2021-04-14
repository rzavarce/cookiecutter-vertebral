from .basemodel import BaseModel
from motor import motor_asyncio


class MongoModel(BaseModel):
    """
    Mongo Database Model
    """

    def __init__(self):
        """Get collection instance from db."""
        self.client = motor_asyncio.AsyncIOMotorClient

    def setup_client(self, uri, dbname):
        """
        Handle mongo set up and tear down.

        :param uri: uri mongo setup
        """
        self.client = motor_asyncio.AsyncIOMotorClient(uri)[dbname]

        return self.client

    async def find(self, cond: dict):
        auth = await self.client.find_one(cond)
        return auth

