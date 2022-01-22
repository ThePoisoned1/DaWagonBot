import random
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


def iq_(user):
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
    susPics = [
        'https://cdn.discordapp.com/attachments/798602292521598986/934241049302425650/images.png',
        'https://cdn.discordapp.com/attachments/798602292521598986/934241071511261214/31aa14f0-bc99-4e6b-b785-26ae420971dd-screen-shot-2020-10-31-at-52151-pm.png',
        'https://tenor.com/view/among-us-gif-23586211',
        'https://tenor.com/view/among-us-dance-dance-among-us-purple-sus-gif-18888988',
        'https://cdn.discordapp.com/attachments/832316966714212352/934579533758230598/unknown.png',
        'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/f4d35c9b-436c-42b3-9286-41af3f78b828/dee9sqs-9d29c37a-0f0a-4e96-a62b-f78550513770.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2Y0ZDM1YzliLTQzNmMtNDJiMy05Mjg2LTQxYWYzZjc4YjgyOFwvZGVlOXNxcy05ZDI5YzM3YS0wZjBhLTRlOTYtYTYyYi1mNzg1NTA1MTM3NzAuZ2lmIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.hnJpwdr9maSezysGRKHP_axzvuPkI_BB296M2Hq8GOo'
    ]
    return random.choices(susPics)[0]