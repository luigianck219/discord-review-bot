import discord
import asyncio
import json
import random
import os
from datetime import datetime

# Legge il token e channel ID dalle variabili di Railway
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

REVIEWS_FILE = "reviews.json"
MIN_MINUTES = 30
MAX_MINUTES = 50

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def load_reviews():
    with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def stars_to_emoji(n):
    return "⭐" * n + "☆" * (5 - n)

def format_review(review):
    now = datetime.now()
    date_str = now.strftime("%-d/%-m/%y, %-H:%M %p")
    tag = review.get("tag", "00000")
    lines = [
        f"**{review['username']}**",
        stars_to_emoji(review["stars"]),
        review["text"],
        f"`{tag} • {date_str}`"
    ]
    return "\n".join(lines)

@client.event
async def on_ready():
    print(f"✅ Bot online come {client.user}")
    client.loop.create_task(review_loop())

async def review_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Canale non trovato! Controlla CHANNEL_ID.")
        return

    reviews = load_reviews()
    pool = []

    while not client.is_closed():
        if not pool:
            pool = reviews.copy()
            random.shuffle(pool)

        review = pool.pop()
        message = format_review(review)

        try:
            await channel.send(message)
            print(f"📨 Recensione inviata: {review['username']}")
        except Exception as e:
            print(f"❌ Errore invio: {e}")

        wait_seconds = random.randint(MIN_MINUTES * 60, MAX_MINUTES * 60)
        minutes = wait_seconds // 60
        print(f"⏳ Prossima recensione tra {minutes} minuti...")
        await asyncio.sleep(wait_seconds)

client.run(BOT_TOKEN)
