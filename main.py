import os

import secrets
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
    tag = str(message.author).split('#')[1]
    if message.guild is None: return
    channel = str(message.channel.name)
    print(message)
    # add 'and discord.utils.get(message.author.roles, name=role_name) is None'
    if channel == 'general':
        role_name = 'Server Contributor'
        if message.content == '!verify':
            user_query = {"discord_id": str(message.author.id)}
            print('id: ' + str(message.author.id))
            # assign messenger role
            await message.author.add_roles(discord.utils.get(message.guild.roles, name=role_name))
            await message.author.send(f'Hello, {username}! We are processing your account on the server, '
                                      f'please hold for another message!')
            ubuntu_username = username.lower().replace(" ", "") + tag
            ubuntu_password = secrets.token_hex(16)
            # create user on server
            await os.system(f'sudo useradd -m {ubuntu_username}')
            await os.system(f'sudo passwd {ubuntu_username}')
            # 2x - once to set and once to verify
            await os.system(f'{ubuntu_password}')
            await os.system(f'{ubuntu_password}')
            # set up user's conda environment
            await os.system(f'cd /home/{ubuntu_username}')
            await os.system(f'conda create -n {ubuntu_username}')
            await os.system(f'conda activate {ubuntu_username}')
            # edit user bashrc to load conda venv on ssh login
            await os.system(f'echo \'if [[ -n $SSH_CONNECTION ]] ; then\' >> .bashrc')
            await os.system(f'echo \'conda activate ubuntu_username\' >> .bashrc')
            await os.system(f'echo \'fi\' >> .bashrc')

            # update on the database that user has been verified
            ieee_user_db.update_one(user_query, update_verified_status)
            # DM the user instructions
            await message.author.send(f'Thank you for waiting!\n'
                                      f'Your SSH login is: ```Username: {ubuntu_username}\n'
                                      f'Password: {ubuntu_password}```\n'
                                      f'Please do not share this with anyone!')

client.run(TOKEN)