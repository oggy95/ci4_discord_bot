import asyncio
import logging
import random
import json

import pytz
import discord
from aiohttp import ClientSession
from discord.ext import commands


with open("config.json") as file:
    config = json.load(file)
    TELEGRAM_TOKEN = config["telegram_token"]
    TOKEN = config["api_token"]
    CHANNEL_ID = config["main_channel"]
    CYTATY_CHANNEL = config["channel_quotes"]


client = commands.Bot(command_prefix='!')


@client.command(aliases=['випити', 'drink'], help='Прибухнем? | Cheers? :)')
async def command_drink(ctx):
    smiles = [r":champagne_glass:", r":beers:", r":wine_glass:",
              r":cocktail:", r":beer:", r":champagne:", r":tumbler_glass:"]
    await ctx.send(random.choice(smiles))


@client.command(aliases=['будьмо', 'cheers'], help='Cheers :)')
async def command_drink2(ctx):
    await ctx.send(r":beers:")


@client.command(aliases=['в', 'вузол', 'n', 'node'], help='["в", "вузол", "n", "node"] Calling to alert for node war!')
async def command_node_war(ctx, arg):
    await ctx.send(f"@everyone у нас вузол о {arg}!!!\n@everyone В ДІСКОРДІ БУТИ ОБОВ'ЯЗКОВО!")


@client.command(aliases=['х', 'храм', 'shrine', 's', 'Х', 'S'], help="['х', 'храм', 'shrine', 's'] Calling to the srine in great desert!")
async def command_shrine(ctx):
    await ctx.send("@everyone SHRINE|ХРАМ!!!")


@client.command(name='смерть', help='')
async def command_death(ctx):
    await ctx.send("Смерть москалям!")


@client.command(aliases=['чс', 'сонце', 'bs', 'sun', 'BS', 'ЧС'], help="['чс', 'сонце', 'bs', 'sun'] Calling to black sun")
async def black_sun(ctx, arg):
    await ctx.send(f"@everyone Чорне Сонце сьогодні в {arg}!")


@client.command(aliases=['мем', 'meme'], help="['мем', 'memes'] Випадковий мем")
async def memes(ctx):
    async with ClientSession() as cs:
        async with cs.get("https://meme-api.herokuapp.com/gimme/wholesomememes") as r:
            res = await r.json()  # returns dict
            await ctx.send(res['url'])


@client.command(aliases=['р', 'l', 'Р', 'L'], help="['р', 'l'] Calling to Laytenn")
async def laytenn(ctx, *args):
   await ctx.send("@everyone РАЙТЕН! | LAYTENN!")


@client.command(name='рандом', help='Випадкова цитата гільдії')
async def bosses(ctx, *args):
    id = client.get_channel(CYTATY_CHANNEL)
    messages = await id.history(limit=123).flatten()
    await ctx.send(ctx.message.author.mention + ", що ти хочеш? От тобі цитата: " + random.choice(messages).content)
           

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
         await ctx.send("шо, бля? | wtf!?")


logging.basicConfig(level=logging.INFO)
client.run(TOKEN)