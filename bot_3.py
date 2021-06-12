import logging
import random
import yaml
import requests
import json

from aiohttp import ClientSession
from discord.ext import commands
from textblob import TextBlob, exceptions

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


@client.command(aliases=['p', 'porn', 'порно'], help="['nsfw', 'porn', 'порно'] NSFW 18+")
async def nsfw(ctx):
    response = requests.get(config["porno_link"] + "/random_json.php")
    json_data = json.loads(response.text)
    await ctx.send(f"{config['porno_link']}{json_data['src']}")


@client.event
async def on_message(message):
    if message.channel.id in config["restricted_channels"]:
        if len(message.content) >= 3 \
                and not message.content.startswith(("!", "http")) \
                and message.author != client.user:
            nick = message.author.nick if message.author.nick is not None else str(message.author).split("#")[0]
            blob = TextBlob(message.content)
            language = blob.detect_language()
            message_text = ""
            response_message = ""
            if message.channel.id != int(config["english_channel"]):
                if language in config["language_choice"].keys():
                    for key, value in config["language_choice"][language].items():
                        message_text = message_text + f"{value}{blob.translate(from_lang=language, to=key)}\n"
                else:
                    message_text = f":flag_us:{blob.translate(from_lang=language, to='us')}"
                response_message = f"{nick} - sorry, I don't understand you" if message_text == "" else \
                    f'{nick} said:\n>>> {message_text} '
            elif message.channel.id == int(config["english_channel"]) and language != "en":
                message_text = f":flag_us: {blob.translate(from_lang=language, to='en')}\n"
                response_message = f'{nick} said not in English. English text:\n>>> {message_text}'
            if response_message != "":
                await message.channel.send(response_message)
    await client.process_commands(message)


@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    nick = message.author.nick if message.author.nick is not None else str(message.author).split("#")[0]
    if reaction.count == 1:
        blob = TextBlob(message.content)
        lg = blob.detect_language()
        received_emoji = reaction.emoji
        country_name = get_country(received_emoji)
        language = ""
        if country_name is not None:
            if country_name["name"]["common"] == "France":
                language = "fr"
            elif country_name["name"]["common"] == "Germany":
                language = "de"
            elif country_name["name"]["common"] == "United States":
                language = "us"
            elif country_name["name"]["common"] == "Spain":
                language = "es"
            elif country_name["name"]["common"] == "Russia":
                language = "ru"
            elif country_name["name"]["common"] == "Portugal":
                language = "pr"
            elif country_name["name"]["common"] == "Ukraine":
                language = "uk"
            elif country_name["name"]["common"] == "Turkey":
                language = "tr"
            elif country_name["name"]["common"] == "Poland":
                language = "pl"
            else:
                language = None
        if language != "":
            try:
                translated_text = blob.translate(from_lang=lg, to=language)
                message_text = f"{nick} said:\n>>> {reaction.emoji} {translated_text}\n"
            except exceptions.NotTranslated:
                message_text = f"{nick}: I'm sorry, cannot translate. Maybe languages is identical?"
            finally:
                await reaction.message.channel.send(message_text)
    await client.process_commands(message)


def get_country(flag):
    with open("required_data.json", "r") as datafile:
        jsondata = json.loads(datafile.read())

    for every in jsondata:
        if every["flag"] == flag:
            return every


with open("config.yaml") as file:
    config = yaml.full_load(file)
logging.basicConfig(
    level=logging.DEBUG,
    filename="logger.log",
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S')
client.run(config["api_token"])
