import logging
import random
import json

from aiohttp import ClientSession
from discord.ext import commands
from textblob import TextBlob
from googletrans import Translator

with open("config.json") as file:
    config = json.load(file)
    TELEGRAM_TOKEN = config["telegram_token"]
    TOKEN = config["api_token"]
    QUOTES_CHANNEL = config["channel_quotes"]
    ENGLISH_CHANNEL = config["english_channel"]

API_LINK = "https://meme-api.herokuapp.com/gimme/wholesomememes"

client = commands.Bot(command_prefix='!')

LANGUAGE_CHOICE = {
    "en": {
        "uk": ":flag_ua:",
        "pt": ":flag_pt:"
    },
    "pt": {
        "uk": ":flag_ua:",
        "en": ":flag_us:"
    },
    "uk": {
        "en": ":flag_us:",
        "pt": ":flag_pt:"
    },
    "ru": {
        "en": ":flag_us:",
        "pt": ":flag_pt:"
    }
}


@client.command(aliases=['мем', 'meme'], help="['мем', 'memes'] Випадковий мем")
async def memes(ctx):
    async with ClientSession() as cs:
        async with cs.get(API_LINK) as r:
            res = await r.json()  # returns dict
            await ctx.send(res['url'])


@client.command(name='рандом', help='Випадкова цитата гільдії')
async def random_quote(ctx):
    channel_id = client.get_channel(QUOTES_CHANNEL)
    messages = await channel_id.history(limit=123).flatten()
    await ctx.send(ctx.message.author.mention + ", що ти хочеш? От тобі цитата: " + random.choice(messages).content)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("шо, бля? | wtf!?")


@client.event
async def on_message(message):
    if len(message.content) >= 3 \
            and not message.content.startswith(("!", "http")) \
            and message.author != client.user:
        language = TextBlob(message.content).detect_language()
        message_text = ""
        response_message = ""
        if message.channel.id != int(ENGLISH_CHANNEL):
            if language in LANGUAGE_CHOICE.keys():
                for key, value in LANGUAGE_CHOICE[language].items():
                    message_text = message_text + f"{value}{translator.translate(message.content, src=language, dest=key).text}\n"
            response_message = f"{message.author.nick} - sorry, I don't understand you" if message_text == "" else \
                f'{message.author.nick} said:\n>>> {message_text} '
        elif message.channel.id == int(ENGLISH_CHANNEL) and language != "en":
            message_text = f":flag_us: {translator.translate(message.content, src=language, dest='en').text}\n"
            response_message = f'{message.author.nick} said not in English. English text:\n>>> {message_text}'
        if response_message != "":
            await message.channel.send(response_message)
    await client.process_commands(message)


translator = Translator()
logging.basicConfig(level=logging.INFO)
client.run(TOKEN)
