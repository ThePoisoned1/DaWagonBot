import random
import discord
from utils import utils


def choose_(stringChoice, separator='|'):
    """
    Retruns a random option from a string of choices
    Parameters
    ------------------
    stringChoice : str
        string of choices
    separator: str
        the separator of the string
    """
    if separator not in stringChoice:
        return f"You need to input at least 2 statements, separated by {separator}"
    return f"{random.choice(stringChoice.split(separator))} is the best choice"


def eightBall_():
    """
    Retruns a random answer form the 8ball responses
    """
    answers = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely', 'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good', 'Yes Signs point to yes', 'Reply hazy',
               'try again', 'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again', 'Dont count on it', 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']
    return random.choice(answers)


def iq_(user:discord.User):
    """
    Retruns a a string telling the iq of the user
    Parameters
    ------------------
    user : discord.user
        user to get the iq from
    """
    random.seed(user.id)
    iq = random.randint(-200, 400)
    return f"{utils.parse_possesive(user.name)} iq is {iq}."


def ppSize_(user):
    """
    Retruns a a string telling the pp size of the user
    Parameters
    ------------------
    user : discord.user
        user to get the pp size from
    """
    random.seed(user.id*3)
    ppLength = random.randint(-10, 30)
    return f"{utils.parse_possesive(user.name)} pp is {ppLength}cm long."

def sus():
    susPics =  [
        'https://cdn.discordapp.com/attachments/832316966714212352/936023965393096724/ezgif-5-527ae4b584.gif',
        'https://cdn.discordapp.com/attachments/832316966714212352/936023965795758131/ezgif-7-fb3e67af24.gif',
        'https://cdn.discordapp.com/attachments/832316966714212352/936023966001291304/ezgif-5-88bb9a44c5.gif',
        'https://cdn.discordapp.com/attachments/832316966714212352/935953743709601792/unknown.png',
        'https://cdn.discordapp.com/attachments/832316966714212352/935952499515478106/unknown.png',
        'https://cdn.discordapp.com/attachments/832316966714212352/937132635958960158/ezgif-5-06be9b2596.jpg'
    ]
    return random.choices(susPics)[0]

def hello(user:discord.User):
    msg = f'Hello {user.mention}, I noticed you have a profile picture of a very beautiful (but also intelligent looking!) female, and I am under the presumption that this goddess is you? It is quite astonishing to see a female here in the Pummel Party Official discord. I am quite popular around here in this server, so if you require and guidance, please, throw me a mention. I will assist you at any hour, day or night. And, before you are mistaken, I do not seek your hand in a romantic way; although, I am not opposed in the event you are interested in me, as many women often are. I am a man of standard, and I do not bow to just any female that comes my way, unlike my peers... So rest assured that I will not be in the way of your gaming and socializing experience. Consider me a Player 2.. a companion, a partner, and perhaps we can enjoy some video games together some time. I see you play pummel party, and are you good at mini games? am a mini-game aficionado, So I would be happy to assist you in games. Platonically of course, unless you (like many others) change your mind on that. I look forward to our future together (as friends of course.) '
    return msg