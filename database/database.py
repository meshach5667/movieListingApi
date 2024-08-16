from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# Load the MongoDB connection URL from the environment variable
MONGODB_URL = os.getenv("MONGODB_URL")

# Create a Motor client
client = AsyncIOMotorClient(MONGODB_URL)

# Specify the database name
database = client.my_database

# Example of accessing a collection
my_collection = database.my_collection

# Dependency function to get the database
def get_db():
    return database
