import discord
from discord.ext import commands, tasks
import requests
import os
import sys
import asyncio

API_URL = 'https://metaforge.app/api/arc-raiders/event-timers'
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
previous_events = []

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    check_events.start()

@tasks.loop(minutes=10)
async def check_events():
    global previous_events

    try:
        response = requests.get(API_URL)
        data = response.json()
    except Exception as e:
        print("Błąd przy pobieraniu danych:", e)
        return

    current_events = data.get('data', [])
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("Nie znaleziono kanału.")
        return

    if current_events != previous_events:
        embed = discord.Embed(title="Nowe Eventy w ARC Raiders!", color=0x00ff00)
        for event in current_events:
            name = event.get("name", "Brak nazwy")
            map_name = event.get("map", "Brak mapy")
            times = event.get("times", [])
            time_str = "\n".join([f"{t['start']} - {t['end']}" for t in times]) or "Brak harmonogramu"

            embed.add_field(
                name=f"{name} ({map_name})",
                value=time_str,
                inline=False
            )
        await channel.send(embed=embed)
        previous_events = current_events.copy()
        print("✉️ Nowe eventy wysłane!")

# Komenda testowa
@bot.command()
async def testevent(ctx):
    print("🔍 Wywołano komendę !testevent")
    try:
        response = requests.get(API_URL)
        data = response.json()
        events = data.get('data', [])
        print("📡 EVENTY Z API:")
        for event in events:
            print(f"- {event.get('name')} | Mapa: {event.get('map')}")
            for t in event.get('times', []):
                print(f"   Godziny: {t['start']} - {t['end']}")

        embed = discord.Embed(title="🧪 Testowe eventy", color=0x00ffff)
        for event in events[:5]:  # ogranicz do 5 dla testów
            name = event.get("name", "Brak nazwy")
            map_name = event.get("map", "Brak mapy")
            times = event.get("times", [])
            time_str = "\n".join([f"{t['start']} - {t['end']}" for t in times]) or "Brak harmonogramu"
            embed.add_field(
                name=f"{name} ({map_name})",
                value=time_str,
                inline=False
            )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("❌ Błąd przy pobieraniu eventów")
        print("❌ Błąd:", e)

# Funkcja do testowania eventów w terminalu
async def print_events_to_console():
    try:
        response = requests.get(API_URL)
        data = response.json()
        events = data.get('data', [])
        print("\n📡 EVENTY Z API ARC RAIDERS:")
        print("=" * 50)
        for event in events:
            name = event.get("name", "Brak nazwy")
            map_name = event.get("map", "Brak mapy")
            times = event.get("times", [])
            print(f"🔹 Nazwa: {name}")
            print(f"   Mapa: {map_name}")
            for t in times:
                print(f"   Godzina: {t['start']} - {t['end']}")
            print("-" * 30)
    except Exception as e:
        print("❌ Błąd przy pobieraniu danych:", e)

# Główne uruchomienie
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(print_events_to_console())
    else:
        bot.run(DISCORD_TOKEN)
