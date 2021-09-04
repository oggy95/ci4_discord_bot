import asyncio
import logging
import re
import json
import random

import discord
import yaml

from discord import Embed
from discord.ext import commands
from aiohttp import ClientSession
from textblob import TextBlob, exceptions
from discord import FFmpegPCMAudio
from discord.utils import get
from youtube_dl import YoutubeDL

client = commands.Bot(command_prefix='!')

TIMEOUT = 30


@client.command()
async def play(ctx, url):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        await channel.connect()
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        video_title = info.get('title', None)
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()

        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=video_title))
        await ctx.send('Bot is playing')
        print(info["duration"])
        await asyncio.sleep(info["duration"] + 60)
        await client.change_presence(status=None)
        await ctx.send("I'm leaving")
        await ctx.guild.voice_client.disconnect()
    # check if the bot is already playing
    else:
        await ctx.send("Bot is already playing")
        return


@client.command()
async def leave(ctx):
    if ctx.voice_client:  # If the bot is in a voice channel
        await ctx.guild.voice_client.disconnect()  # Leave the channel
        await ctx.send('Bot left')
        await client.change_presence(status=None)
    else:  # But if it isn't
        await ctx.send("I'm not in a voice channel, use the join command to make me join")


# command to resume voice if it is paused
@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming')


# command to pause voice if it is playing
@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


# command to stop voice
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')
        await client.change_presence(status=None)


@client.command(aliases=['мем', 'meme'], help="['мем', 'memes'] Випадковий мем")
async def memes(ctx):
    async with ClientSession() as client_session:
        async with client_session.get(config["api_link"]) as response:
            res = await response.json()  # returns dict
            await ctx.send(res['url'])


@client.command(name='рандом', help='Випадкова цитата гільдії')
async def random_quote(ctx):
    channel_id = client.get_channel(config["ci4_guild"]["channel_quotes"])
    messages = await channel_id.history(limit=123).flatten()
    await ctx.send(ctx.message.author.mention + ", що ти хочеш? От тобі цитата: " + random.choice(messages).content)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("шо, бля? | wtf!?")


@client.event
async def on_member_join(member):
    guest_role = client.get_guild(config["ci4_guild"]["guild_id"]).get_role(config["ci4_guild"]["guest_role"])
    await member.add_roles(guest_role)
    channel_id = client.get_channel(config["ci4_guild"]["main_channel"])
    await channel_id.send(f"Welcome {member.display_name}. You are a guest for this server, with time @⭐Officer⭐Генеральна Старшина will give you a role :)")


@client.command(aliases=['p'], help="['p'] NSFW 18+")
async def nsfw(ctx):
    if ctx.channel.id != config["ci4_guild"]["perv_corner"]:
        sent_message = await ctx.send("Sorry, this chat if not for NSFW. Try another chat.")
        await sent_message.delete(delay=TIMEOUT)
    else:
        async with ClientSession() as client_session:
            async with client_session.get(config["porn_link"] + "/random_json.php") as response:
                json_data = json.loads(await response.read())
                await ctx.send(f"{config['porn_link']}{json_data['src']}")


@client.event
async def on_message(message):
    if message.channel.id in config["restricted_channels"] \
            and message.author != client.user and message.content.startswith("!") is False:
        nick = message.author.nick if message.author.nick is not None else str(message.author).split("#", maxsplit=1)[0]
        print(f"{nick} said: ", message.content)
        formatted_message = format_message(message.content).strip()
        if 3 <= len(formatted_message) <= 4000:
            blob = TextBlob(formatted_message)
            language = blob.detect_language()
            response_message = ""
            if message.channel.id != int(config["ci4_guild"]["english_channel"]) and message.channel.id != int(config["ci4_guild"]["brm"]):
                response_message = translate_message(message, language, nick, blob)
            elif message.channel.id == int(config["ci4_guild"]["english_channel"]) and language != "en":
                try:
                    response_message = f'{nick} said not in English. English text:\n>>> :flag_us: {blob.translate(to="en")}\n'
                except exceptions.NotTranslated:
                    print(f"Author: {nick}. Message: {message.content}. Error translate from {language} to en")
            elif message.channel.id == int(config["ci4_guild"]["brm"]):
                try:
                    flag = ":flag_us:" if language != "en" else ":flag_ua:"
                    to_lang = "en" if language != "en" else "uk"
                    response_message = f'>>> {flag} {blob.translate(to=to_lang)}\n'
                except exceptions.NotTranslated:
                    print(f"Author: {nick}. Message: {message.content}. Error translate from {language} to en")
            if response_message != "":
                try:
                    if isinstance(response_message, Embed):
                        await message.reply(embed=response_message)
                    else:
                        await message.reply(response_message)
                except Exception as exception:
                    print(f"Error send message to {message.channel.name} in guild {message.channel.guild}. "
                          f"Channel id: {message.channel.id}. Detail: {exception}")
        else:
            await client.process_commands(message)
    else:
        await client.process_commands(message)


@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if 3 <= len(message.content) <= 4000 and user != client.user:
        blob = TextBlob(message.content)
        language = detect_language(reaction.emoji)
        if language != "":
            try:
                result_message = blob.translate(to=language)
            except exceptions.NotTranslated:
                result_message = message.content
            message_text = f"{user.display_name} said:\n>>> {reaction.emoji} {result_message}\n"
            sent_message = await reaction.message.channel.send(message_text)
            await sent_message.delete(delay=TIMEOUT)
    else:
        await client.process_commands(message)


def translate_message(message, language, nick, blob):
    message_text = ""
    if language in config["language_choice"].keys():
        for key, value in config["language_choice"].items():
            if key == language or (key == "uk" and language == "ru") or key == "ru":
                continue
            try:
                message_text += f"{value} **{blob.translate(to=key)}**\n"
            except exceptions.NotTranslated:
                print(f"Author: {nick}. Message: {message.content}. Error translate from {language} to {key}")
                continue
            except Exception as exception:
                print(exception, exception.__class__)
                continue
    else:
        try:
            message_text = f":flag_us: {blob.translate(to='en')}"
        except exceptions.NotTranslated:
            message_text = ""
    return "" if message_text == "" else Embed(description=message_text)


def detect_language(received_emoji):
    for name, emoji in config["language_choice"].items():
        if emoji == received_emoji:
            return name
    return ""


def format_message(message):
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        "]+", flags=re.UNICODE)
    regular_list = [r"<\s*\S*>", r"https?:\/\/.*[\r\n]*", regrex_pattern]
    for reg in regular_list:
        message = re.sub(reg, "", message)
    return message


with open("config.yaml") as file:
    config = yaml.full_load(file)
logging.basicConfig(
    level=logging.DEBUG,
    filename="logger.log",
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S')
client.run(config["api_token"])
