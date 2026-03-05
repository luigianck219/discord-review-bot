import discord
import asyncio
import json
import random
import os
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIGURAZIONE — modifica questi valori
# ─────────────────────────────────────────
BOT_TOKEN = "IL_TUO_TOKEN_QUI"          # Token del bot da Discord Developer Portal
CHANNEL_ID = 123456789012345678         # ID del canale dove postare le recensioni
REVIEWS_FILE = "reviews.json"           # File con le recensioni

MIN_MINUTES = 30   # intervallo minimo in minuti
MAX_MINUTES = 50   # intervallo massimo in minuti
# ─────────────────────────────────────────

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def load_reviews():
    with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def stars_to_emoji(n):
    return "⭐" * n + "☆" * (5 - n)

def format_review(review):
    now = datetime.now()
    date_str = now.strftime("%-d/%-m/%y, %-H:%M %p")  # es. 3/5/26, 4:34 PM
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
    pool = []  # pool vuoto, si riempie quando esaurisce

    while not client.is_closed():
        # Quando il pool è vuoto, rimescola tutte le recensioni
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

        # Aspetta un tempo casuale tra MIN e MAX minuti
        wait_seconds = random.randint(MIN_MINUTES * 60, MAX_MINUTES * 60)
        minutes = wait_seconds // 60
        print(f"⏳ Prossima recensione tra {minutes} minuti...")
        await asyncio.sleep(wait_seconds)

client.run(BOT_TOKEN)
