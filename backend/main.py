# main.py

from fastapi import FastAPI
from database import database  # Import the async database connection object
from databases import Database
from sqlalchemy import MetaData
import asyncpg  # For PostgreSQL support
import os

app = FastAPI()

# Connect to the database on startup
@app.on_event("startup")
async def startup():
    try:
        await database.connect()  # Connect to the PostgreSQL database asynchronously
        print("Connected to the database.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

# Disconnect from the database on shutdown
@app.on_event("shutdown")
async def shutdown():
    try:
        await database.disconnect()  # Disconnect asynchronously
        print("Disconnected from the database.")
    except Exception as e:
        print(f"Error disconnecting from the database: {e}")

# Example endpoint to test DB connection
@app.get("/db_test")
async def test_db_connection():
    try:
        query = "SELECT version();"  # Simple query to check the PostgreSQL version
        result = await database.fetch_one(query)  # Fetch the result asynchronously
        return {"db_version": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Model Evaluation Platform!"}
