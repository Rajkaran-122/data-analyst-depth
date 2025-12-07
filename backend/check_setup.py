
import sys
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_mongo():
    try:
        # Check environment
        print("Checking imports...")
        import fastapi
        import uvicorn
        import pydantic
        import pandas
        import matplotlib
        print("Imports successful.")
    except ImportError as e:
        print(f"Import Error: {e}")
        return

    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    print(f"Checking MongoDB connection at {mongo_url}...")
    
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
        # Force a connection
        await client.server_info()
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection FAILED: {e}")
        print("Please ensure MongoDB is running (e.g., via Docker or local service).")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_mongo())
