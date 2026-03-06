from fastapi import FastAPI, Request
import os
import asyncpg

DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "secret")

app = FastAPI()
pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

@app.post("/events")
async def receive_event(request: Request):
    data = await request.json()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO event_data(ts, component_id, temperature, humidity) VALUES($1, $2, $3, $4)",
            data.get("ts"),
            data.get("component_id"),
            data.get("temperature"),
            data.get("humidity")
        )
    return {"status": "ok"}