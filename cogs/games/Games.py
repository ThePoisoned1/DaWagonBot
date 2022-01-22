import asyncio
import time
from random import shuffle

import discord


async def getPlayers(embMsg, bot, ctx, limit=10):
    """
    Gathers the players for the Russian Roulette game

    Parameters
    --------------------
    embMsg : discord.Embed
    actionEmbedMsg : discord.Embed
    bot : discord.ext.commands.Bot
    ctx : discord.ext.commands.Context
    limit : int
    """
    embContent = ""
    players = []

    def check(msg):
        return msg.channel == ctx.channel and msg.content.lower() == "bang"\
            and (len(players)) < limit and msg.author not in players

    while True:
        try:
            msg = await bot.wait_for("message", check=check,
                                     timeout=10)  # 10 seconds to reply
        except asyncio.TimeoutError:
            break
        embContent += msg.author.name + "\n"
        players.append(msg.author)
        embed = discord.Embed(title="Welcome to Russian Roulette",
                              description="type \"bang\" to join",
                              color=0x00ffff)
        embed.add_field(name=f"Players ({len(players)}/{limit})",
                        value=embContent,
                        inline=False)
        embed.set_footer(
            text="Game will start after 10 secs with no new players")
        await msg.delete()
        await embMsg.edit(embed=embed)
    return players


async def gameRound(players, deadPlayers, chamber, roundNum, roundEmbedMsg,
                    actionEmbedMsg):
    """
    Plays one round of the Russian Roulette

    Parameters
    --------------------
    players : list
    deadPlayers : list
    chamber : list
    roundNum : int
    roundEmbedMsg : discord.Embed
    actionEmbedMsg : discord.Embed
    """

    turn = 0
    shuffle(players)
    roundChamber = chamber.copy()
    shuffle(roundChamber)
    playerNames = ""
    for player in players:
        playerNames += player.name + " "
    deadNames = ""
    for deadPlayer in deadPlayers:
        deadNames += deadPlayer.name + " "

    embed = discord.Embed(title=f"Round {roundNum} starting", color=0x8000ff)
    embed.add_field(name=f"Players alive ({len(players)})",
                    value=playerNames,
                    inline=False)
    if len(deadPlayers) >= 1:
        embed.add_field(name=f"Players dead ({len(deadPlayers)})",
                        value=deadNames,
                        inline=False)
    await roundEmbedMsg.edit(embed=embed)
    while len(roundChamber) >= 1:
        embed = discord.Embed(title=f"{players[turn].name} pulls the trigger",
                              color=0x00ffff)
        await actionEmbedMsg.edit(embed=embed)
        time.sleep(1)

        if roundChamber.pop(0) == "bullet":
            embed = discord.Embed(
                title=f"{players[turn].name} pulls the trigger",
                color=0xff0000)
            embed.add_field(name="BANG!",
                            value=f"{players[turn].name} gets shot",
                            inline=False)
            await actionEmbedMsg.edit(embed=embed)
            deadPlayers.append(players.pop(turn))
            break
        else:
            embed = discord.Embed(
                title=f"{players[turn].name} pulls the trigger",
                color=0x00ff00)
            embed.add_field(name="Click!",
                            value=f"{players[turn].name} is safe",
                            inline=False)
            await actionEmbedMsg.edit(embed=embed)
        turn += 1
        if turn >= len(players):
            turn = 0
        time.sleep(1)
    return players, deadPlayers


async def russianRoulette_(ctx, bot, chamberSize=6):
    """
    Starts the russian roulette

    Parameters
    --------------------
    ctx : discord.ext.commands.Context
    bot : discord.ext.commands.Bot
    chamberSize : int
    """

    chamber = ["bullet"]
    for x in range(chamberSize-1):
        chamber.append("empty")
    embed = discord.Embed(title="Welcome to Russian Roulette",
                          description="type \"bang\" to join",
                          color=0x00ffff)
    embed.add_field(name="Players", value=u"\u200B", inline=False)
    embed.set_footer(text="Game will start after 10 secs with no new players")
    embMsg = await ctx.send(embed=embed)

    players = await getPlayers(embMsg, bot, ctx)

    if len(players) < 2:
        embed = discord.Embed(
            title="You need at least 2 players for this game", color=0xff0000)
        await ctx.send(embed=embed)
        return

    roundNum = 1
    embed = discord.Embed(title=u"\u200B", color=0x000000)
    roundEmbedMsg = await ctx.send(embed=embed)
    actionEmbedMsg = await ctx.send(embed=embed)
    deadPlayers = []
    while (len(players) > 1):
        players, deadPlayers = await gameRound(players, deadPlayers, chamber,
                                               roundNum, roundEmbedMsg,
                                               actionEmbedMsg)
        roundNum += 1
        time.sleep(2)

    embed = discord.Embed(title="Game ended",
                          description=f"{players[0].name} is the survivor",
                          color=0xff00ff)
    await ctx.send(embed=embed)
