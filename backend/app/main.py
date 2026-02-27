from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder
import os

from .bot import build_application
from .database import Base, engine

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://yourdomain.com{WEBHOOK_PATH}"

telegram_app = build_application()

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    print("Webhook set:", WEBHOOK_URL)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}