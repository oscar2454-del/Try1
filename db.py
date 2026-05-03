import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise Exception("MONGO_URL no está configurado")

client = AsyncIOMotorClient(MONGO_URL)

db = client["1"]         
collection = db["MOLO"] 