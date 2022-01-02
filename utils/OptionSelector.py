import discord
import asyncio
from . import utils



emojiOptions = '1️⃣,2️⃣,3️⃣,4️⃣,5️⃣,6️⃣,7️⃣,8️⃣,9️⃣,🔟,❌'.split(',')
emojiVal = [range(1, 11)]
emojiCancel = '❌'
emojiCancelVal = 'Cancel'


async def option_selector(bot, ctx, options, timeout: int = 30):
    if len(options) > 10:
        raise Exception('Max options is 10')
    choosen = None
    desc = []
    for option in options:
        desc.append(f'{emojiOptions[len(desc)]} {option}')
    embed = discord.Embed(title='Chose one of the options bellow',
                          description='\n'.join(desc), color=discord.Color.og_blurple())
    msg = await utils.send_embed(ctx, embed)
    for x in range(len(options)):
        msg.add_reaction(emojiOptions[x])
    try:
        reaction, user = await bot.wait_for(
            "reaction_add",
            timeout=timeout,
            check=lambda reaction, user: str(
                reaction.emoji) in emojiOptions
            and user.id != bot.user.id
            and reaction.message.id == msg.id
            and user.id == ctx.author.id
        )
    except asyncio.TimeoutError:
        await utils.clearReactions(msg, embed)
    else:
        if str(reaction.emoji) != emojiCancel:
            choosen = emojiOptions.index(str(reaction.emoji))
    return choosen, msg
