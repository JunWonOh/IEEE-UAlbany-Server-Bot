import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pprint import pprint
import discord

# connect to MongoDB server and Discord client
load_dotenv()
TOKEN = os.getenv('TOKEN')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
client = discord.Client()
mongo_client = MongoClient('mongodb+srv://ieeeserver:'f'{MONGO_PASSWORD}''@cluster0.v7iyp.mongodb.net/ieeeserverDB?retryWrites=true&w=majority')
db = mongo_client.admin
serverStatusResult = db.command("serverStatus")
pprint(serverStatusResult)

ieee_db = mongo_client["ieeeserverDB"]
ieee_user_db = ieee_db["users"]
update_verified_status = {"$set": {"verifiedUser": True}}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    if message.guild is None: return
    channel = str(message.channel.name)
    print(message)
    # add 'and discord.utils.get(message.author.roles, name=role_name) is None'
    if channel == 'general':
        role_name = 'Something'
        if message.content == '!verify':
            user_query = {"id": message.author.id}
            # assign messenger role
            await message.author.add_roles(discord.utils.get(message.guild.roles, name=role_name))
            ieee_user_db.update_one(user_query, update_verified_status)
            await message.author.send(f'Hello, {username}!\n'
                                      f'Your SSH login is is: ```Username: \n'
                                      f'Password:```\n'
                                      f'Please do not share this with anyone!')

client.run(TOKEN)