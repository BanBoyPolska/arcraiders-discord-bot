import discord
from discord.ext import commands, tasks
import requests
import json
import os

# Konfiguracja
API_URL = 'https://metaforge.app/api/arc-raiders/event-timers'
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Umieść token w zmiennej środowiskowej!
CHANNEL_ID = 820618265436356639  # ID kanału, gdzie bot ma wysyłać info

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Przechowujemy poprzednią listę eventów, by porównać później
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

    current_events = data.get('events', [])

    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("Nie znaleziono kanału.")
        return

    # Sprawdź, czy coś się zmieniło
    if current_events != previous_events:
        embed = discord.Embed(title="Nowe Eventy w ARC Raiders!", color=0x00ff00)
        for event in current_events:
            name = event.get("name", "Brak nazwy")
            start_time = event.get("start_time", "Brak daty")
            end_time = event.get("end_time", "Brak daty")
            description = event.get("description", "")
            embed.add_field(
                name=name,
                value=f"{description}\nStart: {start_time}\nKoniec: {end_time}",
                inline=False
            )
        await channel.send(embed=embed)
        previous_events = current_events.copy()

bot.run(DISCORD_TOKEN)
