import logging
import random
import json

from aiohttp import ClientSession
from discord.ext import commands
from textblob import TextBlob

with open("config.json") as file:
    config = json.load(file)
    TELEGRAM_TOKEN = config["telegram_token"]
    TOKEN = config["api_token"]
    CHANNEL_ID = config["main_channel"]
    CYTATY_CHANNEL = config["channel_quotes"]
    GAME_ALERT_CHANNEL = config["game_alert"]
    ENGLISH_CHANNEL = config["english_channel"]

API_LINK = "https://meme-api.herokuapp.com/gimme/wholesomememes"

client = commands.Bot(command_prefix='!')

NODE_WAR_TEXT_ENGLISH = '''@⚔️Ci4⚔️ Hi everyone :slight_smile:
Today we go T2 node at 19:00 by server time! Please be ready!
If you can't be at NW tomorrow, write about it in #⛺day-offs
Gather at voice channel in discord at 18:40 to discuss strategy on NW!
Guild bosses will be after NW!'''

NODE_WAR_TEXT_UKRAINIAN = '''@⚔️Ci4⚔️ Всім привіт 
Сьогодні ми йдемо на вузол 2 рівня на 19:00 по серверному часу (21:00 по нашому). Тому просимо вашої активності!
Якщо у вас не виходить бути на вузлі, відпишіть про це в #⛺day-offs
Збирайтесь у голосовому чаті в 20:40 для обговорення тактики на вузлі!
Гільд боси будуть сьогодні, відразу після вузла!'''


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


@client.command(aliases=['х', 'храм', 'shrine', 's', 'Х', 'S'], help="['х', 'храм', 'shrine', 's'] Calling to the "
                                                                     "shrine in great desert!")
async def command_shrine(ctx):
    await ctx.send("@everyone SHRINE|ХРАМ!!!")


@client.command(name='смерть', help='')
async def command_death(ctx):
    await ctx.send("Смерть москалям!")


@client.command(aliases=['чс', 'сонце', 'bs', 'sun', 'BS', 'ЧС'], help="['чс', 'сонце', 'bs', 'sun'] Calling to black "
                                                                       "sun")
async def black_sun(ctx, arg):
    await ctx.send(f"@everyone Чорне Сонце сьогодні в {arg}!")


@client.command(aliases=['мем', 'meme'], help="['мем', 'memes'] Випадковий мем")
async def memes(ctx):
    async with ClientSession() as cs:
        async with cs.get(API_LINK) as r:
            res = await r.json()  # returns dict
            await ctx.send(res['url'])


@client.command(aliases=['р', 'l', 'Р', 'L'], help="['р', 'l'] Calling to Laytenn")
async def laytenn(ctx):
    await ctx.send("@everyone РАЙТЕН! | LAYTENN!")


@client.command(name='рандом', help='Випадкова цитата гільдії')
async def bosses(ctx):
    channel_id = client.get_channel(CYTATY_CHANNEL)
    messages = await channel_id.history(limit=123).flatten()
    await ctx.send(ctx.message.author.mention + ", що ти хочеш? От тобі цитата: " + random.choice(messages).content)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("шо, бля? | wtf!?")


@client.event
async def on_message(message):
    restricted_authors = ["Smoogle Translate#1934", "Бандерівець#4954"]
    language = TextBlob(message.content).detect_language()
    if not message.content.startswith("!") and str(message.author) not in restricted_authors and message.channel.id != int(ENGLISH_CHANNEL):
        if language == "en":
            # emoji ua
            await message.add_reaction('\U0001f1fa\U0001f1e6')
        elif language == "uk":
            # emoji us
            await message.add_reaction('\U0001f1fa\U0001f1f8')
        elif language == "ru":
            # emoji us
            await message.add_reaction('\U0001f1fa\U0001f1f8')
    await client.process_commands(message)


logging.basicConfig(level=logging.INFO)
client.run(TOKEN)
