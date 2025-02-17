import discord
import os
from discord.ext import commands
import aiohttp
import asyncio
from datetime import datetime, timedelta

# Konfiguration
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CHANNEL_ID = 1332282278969348106  # Erstat med din Discord-kanal ID
BATTLEMETRICS_API_KEY = os.environ["BATTLEMETRICS_API_KEY"]
CHECK_INTERVAL = 60  # Tjek hvert 60. sekund

# Server der overvåges
servers_to_monitor = set()
whitelisted_players = set()

# Opsætning af botten
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def check_players():
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)

    if channel is None:
        print("Fejl: Kunne ikke finde Discord-kanalen.")
        return

    while not bot.is_closed():
        for SERVER_ID in servers_to_monitor:
            stop_time = datetime.utcnow()  # Brug UTC tid
            start_time = stop_time - timedelta(minutes=30)

            # Formatér datoer i ISO 8601 format med 'Z' for UTC
            start_str = start_time.isoformat() + "Z"
            stop_str = stop_time.isoformat() + "Z"

            url = (f'https://api.battlemetrics.com/servers/{SERVER_ID}/relationships/sessions'
                   f'?start={start_str}&stop={stop_str}')
            headers = {'Authorization': f'Bearer {BATTLEMETRICS_API_KEY}'}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        print(f"Fejl ved API-anmodning: {response.status} - {await response.text()}")
                        await asyncio.sleep(CHECK_INTERVAL)
                        continue

                    data = await response.json()
                    if 'data' not in data:
                        print("Ingen data blev returneret fra API'et.")
                        await asyncio.sleep(CHECK_INTERVAL)
                        continue

                    for player in data['data']:
                        player_name = player['attributes']['name']
                        if player['attributes']['stop'] is None:
                            await channel.send(f'\ud83d\udfe2 **{player_name}** har joinet serveren!')
                        else:
                            await channel.send(f'\ud83d\udd34 **{player_name}** har forladt serveren!')

        await asyncio.sleep(CHECK_INTERVAL)

@bot.event
async def on_ready():
    print(f'Bot er logget ind som {bot.user}')
    bot.loop.create_task(check_players())

# Kommando: Tilføj en server til overvågning
@bot.command()
async def addserver(ctx, server_id: str):
    if server_id not in servers_to_monitor:
        servers_to_monitor.add(server_id)
        await ctx.send(f'Server **{server_id}** tilføjet til overvågning!')
    else:
        await ctx.send(f'Server **{server_id}** overvåges allerede!')

# Kommando: Fjern en server fra overvågning
@bot.command()
async def removeserver(ctx, server_id: str):
    if server_id in servers_to_monitor:
        servers_to_monitor.remove(server_id)
        await ctx.send(f'Server **{server_id}** fjernet fra overvågning!')
    else:
        await ctx.send(f'Server **{server_id}** findes ikke på listen.')

# Kommando: Tilføj en spiller til whitelist
@bot.command()
async def addplayer(ctx, player_name: str):
    if player_name not in whitelisted_players:
        whitelisted_players.add(player_name)
        await ctx.send(f'**{player_name}** er nu på whitelist!')
    else:
        await ctx.send(f'**{player_name}** er allerede på whitelist!')

# Kommando: Fjern en spiller fra whitelist
@bot.command()
async def removeplayer(ctx, player_name: str):
    if player_name in whitelisted_players:
        whitelisted_players.remove(player_name)
        await ctx.send(f'**{player_name}** fjernet fra whitelist!')
    else:
        await ctx.send(f'**{player_name}** findes ikke på whitelist.')

# Kommando: Liste alle overvågede servere
@bot.command()
async def listservers(ctx):
    if servers_to_monitor:
        await ctx.send(f'Overvågede servere: {", ".join(servers_to_monitor)}')
    else:
        await ctx.send('Ingen servere overvåges i øjeblikket.')

# Kommando: Liste alle whitelistede spillere
@bot.command()
async def listplayers(ctx):
    if whitelisted_players:
        await ctx.send(f'Whitelistede spillere: {", ".join(whitelisted_players)}')
    else:
        await ctx.send('Ingen spillere er på whitelist i øjeblikket.')

bot.run(DISCORD_BOT_TOKEN)
