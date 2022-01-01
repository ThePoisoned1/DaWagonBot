from discord import file
from discord.errors import Forbidden
import discord
import asyncio
from datetime import datetime
import os.path
import csv
import sys
import re
import cv2
import requests
import numpy as np
from PIL import Image
import io
from pprint import pprint
import struct


async def send_embed(ctx, embed, view=None):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        msg = await ctx.send(embed=embed, view=view)
        return msg
    except Forbidden:
        send_msg(ctx, view=view)


async def send_img(ctx, fileArray: np.ndarray, channel=None):
    cv2.imwrite('file.png', cv2.cvtColor(fileArray, cv2.COLOR_RGB2BGR))
    if channel:
        return await channel.send(file=discord.File('file.png'))
    else:
        return await ctx.send(file=discord.File('file.png'))


async def send_msg(ctx, msg=None, view=None):
    if not msg:
        msg = f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}"
    try:
        await ctx.send(msg, view=view)
    except Forbidden:
        await ctx.author.send(msg)


async def send_cancel_msg(ctx, msg='Operaction canceled'):
    await send_msg(ctx, msg=msg)


def errorMsg():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    return "ERROR: " + str(exc_type) + " " + str(exc_obj) + " | Line: " + str(exc_tb.tb_lineno)


def errorEmbed(title):
    return discord.Embed(
        title=title, color=0xff0000)


def successEmbed(title):
    return discord.Embed(
        title=title, color=0x00ff00)


def info_embed(title):
    return discord.Embed(
        title=title, color=discord.Color.blue())


def removeMatches(theList, toDelete):
    newList = []
    for item in theList:
        if item not in toDelete:
            newList.append(item)
    return newList


async def clearReactions(msg, embed):
    embed.set_footer(text="Timed Out!")
    await msg.edit(embed=embed)
    await msg.clear_reactions()


async def elementsInPages(bot, ctx, elementEmbeds):
    if len(elementEmbeds) == 1:
        await send_embed(ctx, elementEmbeds[0])
        return
    reactions = {"⬛": "Non-element", "🟥": "Fire", "🟦": "Water",
                 "🟩": "Wind", "🟫": "Earth", "🟨": "Holy", "🟪": "Dark",
                 "❌": "Cancel"}
    elements = {element.title: element for element in elementEmbeds}
    msgReactions = {}
    for emoji, element in reactions.items():
        if element in elements.keys() or emoji == '❌':
            msgReactions[emoji] = element
    msg = await send_embed(ctx, elementEmbeds[0])

    for reaction in msgReactions.keys():
        await msg.add_reaction(reaction)
    cache_msg = discord.utils.get(bot.cached_messages, id=msg.id)
    emojistr = str(cache_msg.reactions[0])
    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                timeout=25,
                check=lambda reaction, user: str(
                    reaction.emoji) in msgReactions.keys()
                and user.id != bot.user.id
                and reaction.message.id == msg.id
                and user.id == ctx.author.id
            )
        except asyncio.TimeoutError:
            embed = elements[msgReactions[emojistr]]
            await clearReactions(msg, embed)
            break
        else:
            previous = emojistr
            emojistr = str(reaction.emoji)
            pg = msgReactions.get(element)
            await reaction.remove(user)
            if previous != emojistr:
                if emojistr == "❌":
                    await clearReactions(msg, elements[msgReactions[previous]])
                    break
                await msg.edit(embed=elements[msgReactions[emojistr]])


def addToLog(time, author, authorid, server, serverid, content):
    headers = ["Time (UTC)", "Author", "Author ID", "Server",
               "Server ID", "Message content"]
    time = datetime.utcnow().strftime('%Y-%m-%d')
    if os.path.isfile(f'logs/{time}.log.csv'):
        with open(f'logs/{time}.log.csv', 'a') as log:
            writer = csv.writer(log)
            writer.writerow(
                [datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S'), author, authorid, server, serverid, content])
    else:
        with open(f'logs/{time}.log.csv', 'w') as log:
            writer = csv.writer(log)
            writer.writerow(headers)
            writer.writerow(
                [datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S'), author, authorid, server, serverid, content])


async def getMsgFromUser(ctx, bot, timeout=30):
    def check(msg):
        return msg.channel == ctx.channel and msg.author == ctx.message.author
    msg = None
    try:
        msg = await bot.wait_for("message", check=check,
                                 timeout=timeout)  # x seconds to reply
    except asyncio.TimeoutError:
        pass
    return msg


async def getMulitpleMsgs(ctx, bot, timeout=30, endLoop='end'):
    msg = "random msg"
    allMsg = []
    while msg and msg != endLoop:
        msg = getMsgFromUser(ctx, bot, timeout=timeout)
        if msg and msg.lower() != endLoop:
            allMsg.append(msg)


def cancelChecker(toCkeck, cancelstr='cancel'):
    if not toCkeck or (toCkeck and toCkeck.lower() == cancelstr):
        return True
    else:
        return False


async def getAtatchment(ctx, bot, timeout=40):
    def check(msg):
        return msg.channel == ctx.channel and msg.author == ctx.message.author and len(msg.attachments) > 0
    file = None
    msg = None
    try:
        msg = await bot.wait_for("message", check=check,
                                 timeout=timeout)  # x seconds to reply
        file = msg.attachments[0].url
    except asyncio.TimeoutError:
        pass
    return file, msg


def writeToFile(path, content):
    with open(path, 'w') as file:
        file.write(str(content))


def parseTime(timeToParse: datetime):
    return timeToParse.strftime('%Y-%m-%d %H:%M:%S')


def getDatetimeFromParsedString(date: str):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def beautifyDate(datetimeToParse: datetime):
    return datetimeToParse.strftime('%H:%M - %a %d-%b-%Y')


def getPrettyStringFromDict(toBeautify: dict):
    beautifulStuff = ''
    for key, val in toBeautify.items():
        beautifulStuff += f'{key} => {val}\n'
    return beautifulStuff


def getBotActivity(activityType: str, msg, url=None):
    """
    Returns the bot activity and its content based on the input parameters

    Parameters
    ---------------
    activityType : str
    msg : str
    url : str
    """
    if activityType.lower() == "playing":
        activity = discord.Game(name=msg)
    elif activityType.lower() == "streaming":
        activity = discord.Streaming(
            name=msg, url=url)
    elif activityType.lower() == "listening":
        activity = discord.Activity(
            type=discord.ActivityType.listening, name=msg)
    elif activityType.lower() == "watching":
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=msg)
    else:
        activity = None

    return activity


def getBotStatus(status):
    """
    Returns the discord bot status

    Parameters
    ---------------
    status : str
    """
    if status.lower() == "dnd":
        return discord.Status.dnd
    elif status.lower() == "invisible":
        return discord.Status.invisible
    elif status.lower() == "idle":
        return discord.Status.idle
    else:
        return discord.Status.online


def getDiscordColor(color: str):
    colors = {
        'light grey': discord.Color.light_grey(),
        'red': discord.Color.red(),
        'blue': discord.Color.blue(),
        'green': discord.Color.green(),
        'orange': discord.Color.orange(),
        'yellow': discord.Color.yellow(),
        'purple': discord.Color.purple()
    }
    return colors.get(color.lower())


def camel_case(s: str):
    s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def hconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = min(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)


def vconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
    w_min = min(im.shape[1] for im in im_list)
    im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                      for im in im_list]
    return cv2.vconcat(im_list_resize)


def convert_string_to_bytes(string):
    bytes = b''
    for i in string:
        bytes += struct.pack("B", ord(i))
    return bytes


def binary_str_to_nparray(binstr):
    imgData = io.BytesIO(binstr)
    img = Image.open(imgData).convert('RGB')
    img = np.asarray(img)
    return img


def downloadImgFromUrl(url):
    r = requests.get(url)
    if r.status_code == 200:
        r.raw.decode_content = True
        return r.content
