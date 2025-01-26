import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from datetime import datetime

# Konfiguration
DISCORD_BOT_TOKEN = 'MTMzMjI3OTc5MzkzMjA0MjI0MA.GG9Yql.o22iClg7ZKnDcdS4RSE5iCHdVj_QHT6RNTnfVo'
DISCORD_CHANNEL_ID = 123456789012345678  # Erstat med din Discord-kanal ID
BATTLEMETRICS_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6Ijk1NWRiNTg4NmMyYzgwOTkiLCJpYXQiOjE3Mzc5MjI5NjIsIm5iZiI6MTczNzkyMjk2MiwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjo2NjUxNzkifQ.cKLLsRemkE6aRrC9novsvRyJ7OWA_EVA4XgREtcmtLE'
CHECK_INTERVAL = 60  # Tjek hvert 60. sekund

# Overvågede servere og whitelistede spillere
servers_to_monitor = set()
whitelisted_players = {}

# Opsætning af botten
intents = discord.Intents.default()
intents.messages = True  # Enable message content intent
intents.guilds = True    # Allow guild-related events
intents.message_content = True  # Required for reading message content

bot = commands.Bot(command_prefix='!', intents=intents)

async def check_servers():
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)

    while not bot.is_closed():
        for server_id in servers_to_monitor:
            url = f'https://api.battlemetrics.com/servers/{server_id}'
            headers = {'Authorization': f'Bearer {BATTLEMETRICS_API_KEY}'}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()

                    try:
                        if 'data' in data and 'attributes' in data['data']:
                            player_count = data['data']['attributes'].get('players', 0)
                            current_players = set()

                            for player in data['data']['relationships']['players']['data']:
                                player_name = player['attributes']['name']
                                if player_name in whitelisted_players:
                                    current_players.add(player_name)
                                    
                                    # Håndtering af dynamisk start-/stop-tid
                                    if not whitelisted_players[player_name]['online']:
                                        whitelisted_players[player_name]['online'] = True
                                        whitelisted_players[player_name]['start_time'] = datetime.now()
                                        await channel.send(f'\ud83d\udfe2 **{player_name}** er nu online på server {server_id}!')

                            for player in list(whitelisted_players.keys()):
                                if player not in current_players and whitelisted_players[player]['online']:
                                    whitelisted_players[player]['online'] = False
                                    whitelisted_players[player]['stop_time'] = datetime.now()
                                    await channel.send(f'\ud83d\udd34 **{player}** er nu offline. Spilletid: {whitelisted_players[player]["stop_time"] - whitelisted_players[player]["start_time"]}')
                        else:
                            print(f"Server {server_id} har ingen spillere eller fejl i API-responsen.")

                    except KeyError as e:
                        print(f"Fejl ved behandling af server {server_id}: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

# Kommando: Tilføj en server til overvågning
@bot.command()
async def addserver(ctx, server_id: str):
    if server_id not in servers_to_monitor:
        servers_to_monitor.add(server_id)
        await ctx.send(f'Server **{server_id}** tilføjet til overvågning!')
    else:
        await ctx.send(f'Server **{server_id}** overvåges allerede!')

# Kommando: Tilføj en spiller til whitelist
@bot.command()
async def addplayer(ctx, player_name: str):
    if player_name not in whitelisted_players:
        whitelisted_players[player_name] = {'online': False, 'start_time': None, 'stop_time': None}
        await ctx.send(f'**{player_name}** er nu på whitelist!')
    else:
        await ctx.send(f'**{player_name}** er allerede på whitelist!')

# Kommando: Liste alle whitelistede spillere
@bot.command()
async def listplayers(ctx):
    if whitelisted_players:
        player_list = ', '.join(whitelisted_players.keys())
        await ctx.send(f'Whitelistede spillere: {player_list}')
    else:
        await ctx.send('Ingen spillere er på whitelist i øjeblikket.')

# Når botten er klar
@bot.event
async def on_ready():
    print(f'Bot er logget ind som {bot.user}')
    bot.loop.create_task(check_servers())

# Start botten
bot.run(DISCORD_BOT_TOKEN)
