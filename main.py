import os
import secrets
from dotenv import load_dotenv
from pymongo import MongoClient
from pprint import pprint
import discord
# import urllib.parse
import subprocess

# connect to MongoDB server and Discord client
load_dotenv()
TOKEN = os.getenv('TOKEN')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
SUDO_PASSWORD = os.getenv('SUDO_PASSWORD')
client = discord.Client()
mongo_client = MongoClient('mongodb+srv://ieeeserver:'f'{MONGO_PASSWORD}''@cluster0.v7iyp.mongodb.net/ieeeserverDB?retryWrites=true&w=majority')
# username = urllib.parse.quote_plus(os.getenv('USERNAME'))
# password = urllib.parse.quote_plus(os.getenv('PASSWORD'))
# mongo_client = MongoClient('mongodb://%s:%s@localhost:27017/ieeeserverDB' % (username, password))
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
    channel = str(message.channel.name)
    role_name = 'Server Contributor'
    # if bot is in the right channel and the user doesn't have the Server Contributor role..
    if channel == 'bot-spam' and discord.utils.get(message.author.roles, name=role_name) is None:
        if message.content == '!verify':
            print(ieee_user_db.find().limit(4).toString())
            tag = str(message.author).split('#')[1]
            if message.guild is None: return
            print(message)
            # if the user is not registered in the website, alert the user of this. end the function.
            if ieee_user_db.find_one({"discord_id": message.author.id}) is None:
                await message.channel.send(
                    f'Hi {username}! You must first connect your Discord account here before verifying: https://ieeeualbany.org/server')
                return
            print(f'[IEEE Server Bot]: {username} (id: {message.author.id}) is requesting verification')
            user_query = {"discord_id": str(message.author.id)}
            # assign messenger role
            await message.author.add_roles(discord.utils.get(message.guild.roles, name=role_name))
            await message.author.send(f'Hello, {username}! We are processing your account on the server, '
                                      f'please hold for another message!')
            ubuntu_username = username.lower().replace(" ", "") + tag
            ubuntu_password = secrets.token_hex(16)
            print(f'[IEEE Server Bot]: generated username and password for {username}')

            # create user on server with m flag to create respective directory and p flag to set their password
            print(f'[IEEE Server Bot]: creating user {username} in server...')
            os.system('echo %s|sudo -S %s' % (MONGO_PASSWORD, f'useradd -m -p $(openssl passwd -1 {ubuntu_password}) {ubuntu_username}'))
            print(f'[IEEE Server Bot]: user {username} has been created')

            # set up user's conda environment (commented out - implementation moved to adduser.local script)
            print(f'creating and setting conda environment for {username}...')
            create_env = f'conda create -n {ubuntu_username}'.split()
            activate_env = f'conda activate {ubuntu_username}'.split()
            subprocess.Popen(create_env, shell=True).wait()
            subprocess.Popen(activate_env, shell=True).wait()
            # edit user bashrc to load conda venv on ssh login
            print(f'setting bashscript for {username}...')
            os.system(f'cd /home/{ubuntu_username} && '
                      f'echo \'if [[ -n $SSH_CONNECTION ]] ; then \n '
                      f'conda activate {ubuntu_username} \n '
                      f'fi\' >> .bashrc')

            # update on the database that user has been verified
            ieee_user_db.update_one(user_query, update_verified_status)
            # DM the user instructions
            await message.author.send(f'Thank you for waiting!\n'
                                      f'Your SSH login is: ```Username: {ubuntu_username}\n'
                                      f'Password: {ubuntu_password}```\n'
                                      f'Please do not share this with anyone!')

client.run(TOKEN)