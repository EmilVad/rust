import discord
from discord.ext import commands, tasks
import requests
import asyncio

# Konfiguration
DISCORD_BOT_TOKEN = 'MTMzMjI3OTc5MzkzMjA0MjI0MA.GG9Yql.o22iClg7ZKnDcdS4RSE5iCHdVj_QHT6RNTnfVo'
DISCORD_CHANNEL_ID = 1332282278969348106  # Erstat med din Discord-kanal ID
BATTLEMETRICS_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6ImQ2ZjNkOTU0MzA1MTgyNmMiLCJpYXQiOjE3Mzc3MTE3MTEsIm5iZiI6MTczNzcxMTcxMSwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjo2NjUxNzkifQ.K5r7Scg0ZoREaIZgRGT2ks1r5rXHhotMpoxgNyxG-tQ'
CHECK_INTERVAL = 60  # Tjek hvert 60. sekund

# Overvågede servere og whitelistede spillere
servers_to_monitor = set()
whitelisted_players = set()

# Opsætning af botten
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Tjek Rust-servere
async def check_servers():
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)

    while not bot.is_closed():
        for server_id in servers_to_monitor:
            url = f'https://api.battlemetrics.com/servers/{server_id}'
            headers = {'Authorization': f'Bearer {BATTLEMETRICS_API_KEY}'}
            response = requests.get(url, headers=headers)
            data = response.json()

            if 'data' in data and 'relationships' in data['data']:
                current_players = set(
                    player['attributes']['name']
                    for player in data['data']['relationships']['players']['data']
                    if player['attributes']['name'] in whitelisted_players
                )

                for player in current_players:
                    await channel.send(f'🟢 **{player}** har joinet serveren {server_id}!')

        await asyncio.sleep(CHECK_INTERVAL)

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

# Når botten er klar
@bot.event
async def on_ready():
    print(f'Bot er logget ind som {bot.user}')
    bot.loop.create_task(check_servers())

# Start botten
bot.run(DISCORD_BOT_TOKEN)
