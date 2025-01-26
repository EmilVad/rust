import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio

# Konfiguration
DISCORD_BOT_TOKEN = 'MTMzMjI3OTc5MzkzMjA0MjI0MA.GG9Yql.o22iClg7ZKnDcdS4RSE5iCHdVj_QHT6RNTnfVo'
DISCORD_CHANNEL_ID = 123456789012345678  # Erstat med din Discord-kanal ID
BATTLEMETRICS_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6Ijk1NWRiNTg4NmMyYzgwOTkiLCJpYXQiOjE3Mzc5MjI5NjIsIm5iZiI6MTczNzkyMjk2MiwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjo2NjUxNzkifQ.cKLLsRemkE6aRrC9novsvRyJ7OWA_EVA4XgREtcmtLE'
CHECK_INTERVAL = 60  # Tjek hvert 60. sekund

# Overvågede servere og whitelistede spillere
servers_to_monitor = set()
whitelisted_players = set()

# Opsætning af botten
intents = discord.Intents.default()
intents.messages = True  # Enable message content intent
intents.guilds = True    # Allow guild-related events
intents.message_content = True  # Required for reading message content

bot = commands.Bot(command_prefix='!', intents=intents)

# Tjek Rust-servere
async def check_servers():
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)

    while not bot.is_closed():
        for server_id in servers_to_monitor:
            url = f'https://api.battlemetrics.com/servers/{server_id}/players'
            headers = {'Authorization': f'Bearer {BATTLEMETRICS_API_KEY}'}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()

                    try:
                        if 'data' in data:
                            players_data = data['data']
 
                            if players_data:  # Tjek om players_data ikke er tom
                                current_players = set()

                                for player in players_data:
                                    current_players.add(player['attributes']['name'])
 
                                # Player count check
                                num_players = len(players_data)
                                if num_players > 0:
                                    print(f"Serveren har {num_players} spillere online.")
                                    print("their names are: \n")
                                    for player in current_players:
                                        print(player)
                                    #await channel.send(f'\ud83d\udfe2 {player} har joinet serveren {server_id}!')
                                else:
                                    print(f"Server {server_id} har ingen spillere online i øjeblikket.")
                            else:
                                print(f"Server {server_id} har ingen spillere online.")
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
