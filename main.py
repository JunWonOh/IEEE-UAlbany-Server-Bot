import os

from dotenv import load_dotenv
import discord
import random

load_dotenv()
TOKEN = os.getenv('TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    if message.guild is None: return
    channel = str(message.channel.name)
    print(message)
    if channel == 'general':
        if message.content == '!verify':
            await message.author.send(f'Hello, {username}!\n'
                                      f'Your SSH login is is: ```Username: \n'
                                      f'Password:```\n'
                                      f'Please do not share this with anyone!')

client.run(TOKEN)