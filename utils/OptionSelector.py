import discord
import asyncio
from . import utils

emojiOptions = '1️⃣,2️⃣,3️⃣,4️⃣,5️⃣,6️⃣,7️⃣,8️⃣,9️⃣,🔟'.split(',')
emojiVal = [range(1, 11)]
emojiCancel = '❌'
emojiCancelVal = 'Cancel'
emojiAccept = '✅'
emojiAcceptVal = 'Accept'


def getEmojiValue(emoji):
    count = 0
    for emojiOpt in emojiOptions:
        if emoji == emojiOpt:
            return count
        count += 1


async def option_selector(bot, ctx, options, title='Chose one of the options bellow', cancel=True, accept=False, msg=None, timeout: int = 30):
    if len(options) > 10:
        raise Exception('Max options is 10')
    chosen = None
    desc = []
    for option in options:
        desc.append(f'{emojiOptions[len(desc)]} {option}')
    if accept:
        desc.append(f'{emojiAccept} Accept')
    if cancel:
        desc.append(f'{emojiCancel} Cancel')
    embed = discord.Embed(title=title,
                          description='\n'.join(desc), color=discord.Color.og_blurple())
    if not msg:
        msg = await utils.send_embed(ctx, embed)
    else:
        await msg.edit(embed=embed)
    for x in range(len(options)):
        await msg.add_reaction(emojiOptions[x])
    if accept:
        await msg.add_reaction(emojiAccept)
    if cancel:
        await msg.add_reaction(emojiCancel)
    try:
        reaction, user = await bot.wait_for(
            "reaction_add",
            timeout=timeout,
            check=lambda reaction, user: str(
                reaction.emoji) in emojiOptions[:len(options)]+[emojiCancel]
            and user.id != bot.user.id
            and reaction.message.id == msg.id
            and user.id == ctx.author.id
        )
    except asyncio.TimeoutError:
        await utils.clearReactions(msg, embed)
    else:
        if accept and emojiAccept == str(reaction.emoji):
            chosen = -1
        elif str(reaction.emoji) != emojiCancel:
            chosen = getEmojiValue(str(reaction.emoji))
        else:
            await utils.clearReactions(msg, embed, timedOut=False)
    return chosen, msg
