import logging
import random
import json
import yaml
import requests

from aiohttp import ClientSession
from discord.ext import commands
from textblob import TextBlob, exceptions

client = commands.Bot(command_prefix='!')


@client.command(aliases=['мем', 'meme'], help="['мем', 'memes'] Випадковий мем")
async def memes(ctx):
    async with ClientSession() as client_session:
        async with client_session.get(config["api_link"]) as response:
            res = await response.json()  # returns dict
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
    response = requests.get(config["porn_link"] + "/random_json.php")
    json_data = json.loads(response.text)
    await ctx.send(f"{config['porn_link']}{json_data['src']}")


@client.event
async def on_message(message):
    if message.channel.id in config["restricted_channels"] \
            and 3 <= len(message.content) <= 4000 \
            and not message.content.startswith(("!", "http")) \
            and message.author != client.user \
            and not (message.content.startswith("<") and message.content.endswith(">")):
        nick = message.author.nick if message.author.nick is not None else str(message.author).split("#")[0]
        blob = TextBlob(message.content)
        language = blob.detect_language()
        response_message = ""
        if message.channel.id != int(config["english_channel"]):
            response_message = translate_message(message, language, nick, blob)
        elif message.channel.id == int(config["english_channel"]) and language != "en":
            try:
                response_message = f'{nick} said not in English. English text:\n>>> :flag_us: {blob.translate(from_lang=language, to="en")}\n'
            except exceptions.NotTranslated:
                print(f"Author: {nick}. Message: {message.content}. Error translate from {language} to en")
        if response_message != "":
            try:
                await message.channel.send(response_message)
            except Exception as exception:
                print(f"Error send message to {message.channel.name} in guild {message.channel.guild}. Channel id: {message.channel.id}. Error type: {exception.__class__}")
    else:
        await client.process_commands(message)


@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if 3 <= len(message.content) <= 4000:
        blob = TextBlob(message.content)
        detected_language = blob.detect_language()
        received_emoji = reaction.emoji
        country_name = get_country(received_emoji)
        language = ""
        if country_name is not None:
            language = languages.get(country_name["name"]["common"], "")
        if language != "":
            try:
                translated_text = blob.translate(from_lang=detected_language, to=language)
                message_text = f"{user.display_name} said:\n>>> {reaction.emoji} {translated_text}\n"
            except exceptions.NotTranslated:
                message_text = f"{user.display_name} said:\n>>> {reaction.emoji} {message.content}\n"
            if message_text != "":
                await reaction.message.channel.send(message_text)
    else:
        await client.process_commands(message)


def get_country(flag):
    with open("required_data.json", "r") as datafile:
        jsondata = json.loads(datafile.read())

    for every in jsondata:
        if every["flag"] == flag:
            return every
    return None


def translate_message(message, language, nick, blob):
    message_text = ""
    if language in config["language_choice"].keys():
        for key, value in config["language_choice"].items():
            if key == language:
                continue
            try:
                message_text += f"{value}{blob.translate(from_lang=language, to=key)}\n"
            except exceptions.NotTranslated:
                print(f"Author: {nick}. Message: {message.content}. Error translate from {language} to {key}")
                continue
            except Exception as exception:
                print(exception, exception.__class__)
                continue
    else:
        message_text = f":flag_us:{blob.translate(from_lang=language, to='us')}"
    return f"{nick} - sorry, I don't understand you" if message_text == "" else f'{nick} said:\n>>> {message_text} '


with open("config.yaml") as file:
    config = yaml.full_load(file)
with open("languages.json") as lang_json:
    languages = json.load(lang_json)
logging.basicConfig(
    level=logging.DEBUG,
    filename="logger.log",
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S')
client.run(config["api_token"])
