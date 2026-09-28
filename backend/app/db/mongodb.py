import os
import urllib.parse
from motor.motor_asyncio import AsyncIOMotorClient

# Get MONGODB_URL strictly from environment variables
mongodb_url = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017/smart_university"
)

mongo_client = AsyncIOMotorClient(mongodb_url)
mongo_db = mongo_client.get_database("smart_university")

def get_mongodb():
    return mongo_db
