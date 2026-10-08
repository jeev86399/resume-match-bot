import asyncio
import uvicorn
from app.main import app
from app.bot import setup_bot
from app.config import settings

async def start_telegram():
    print("Starting Telegram Bot Polling...")
    bot_app = setup_bot()
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("Telegram Bot Polling Started.")
    
    # Keep the task running
    while True:
        await asyncio.sleep(3600)

async def main():
    if not settings.TELEGRAM_BOT_TOKEN or not settings.GROQ_API_KEY:
        print("ERROR: TELEGRAM_BOT_TOKEN or GROQ_API_KEY is missing.")
        return

    import os
    port = int(os.environ.get("PORT", 8000))
    # Start FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run both server and bot polling concurrently
    await asyncio.gather(
        server.serve(),
        start_telegram()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down...")
