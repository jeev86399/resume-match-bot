from fastapi import FastAPI
from app.bot import setup_bot
import asyncio

app = FastAPI(title="ResumeMatch AI")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "ResumeMatch AI"
    }

# The Telegram bot polling will be started from run.py alongside FastAPI
