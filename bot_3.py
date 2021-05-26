import logging
import random
import yaml

from aiohttp import ClientSession
from discord.ext import commands
from googletrans import Translator

client = commands.Bot(command_prefix='!')


@client.command(aliases=['мем', 'meme'], help="['мем', 'memes'] Випадковий мем")
async def memes(ctx):
    async with ClientSession() as cs:
        async with cs.get(config["api_link"]) as r:
            res = await r.json()  # returns dict
            await ctx.send(res['url'])


@client.command(name='рандом', help='Випадкова цитата гільдії')
async def random_quote(ctx):
    channel_id = client.get_channel(config["channel_quotes"])
    messages = await channel_id.history(limit=123).flatten()
    await ctx.send(ctx.message.author.mention + ", що ти хочеш? От тобі цитата: " + random.choice(messages).content)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("шо, бля? | wtf!?")


@client.event
async def on_message(message):
    if message.channel.id in config["restricted_channels"]:
        if len(message.content) >= 3 \
                and not message.content.startswith(("!", "http")) \
                and message.author != client.user:
            language = translator.detect(message.content)
            message_text = ""
            response_message = ""
            if message.channel.id != int(config["english_channel"]):
                if language in config["language_choice"].keys():
                    for key, value in config["language_choice"][language].items():
                        message_text = message_text + f"{value}{translator.translate(message.content, src=language, dest=key).text}\n"
                response_message = f"{message.author.nick} - sorry, I don't understand you" if message_text == "" else \
                    f'{message.author.nick} said:\n>>> {message_text} '
            elif message.channel.id == int(config["english_channel"]) and language != "en":
                message_text = f":flag_us: {translator.translate(message.content, src=language, dest='en').text}\n"
                response_message = f'{message.author.nick} said not in English. English text:\n>>> {message_text}'
            if response_message != "":
                await message.channel.send(response_message)
    await client.process_commands(message)


with open("config.yaml") as file:
    config = yaml.full_load(file)
translator = Translator()
logging.basicConfig(level=logging.INFO)
client.run(config["api_token"])
