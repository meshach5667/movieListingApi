from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

# Load the MongoDB connection URL from the environment variable
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# Check if the MONGODB_URL is correctly loaded
if not MONGO_DB_URL:
    raise ValueError("MONGO_DB_URL environment variable not set")

# Create a Motor client
client = AsyncIOMotorClient(MONGO_DB_URL)

# Access a specific database
database = client.get_database("my_database")  # Change to your database name

# Access a specific collection
my_collection = database.get_collection("my_collection")  # Change to your collection name

def get_db():
    return database

async def test_connection():
    try:
        # Perform a ping operation to confirm a successful connection
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print("An error occurred:", e)

# Run the test connection function if this module is executed directly
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_connection())
