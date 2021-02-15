import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import os

bot = commands.Bot(command_prefix='lc ', description='hello world')

db_file = 'db.json'

@bot.event
async def on_ready():
    with open(db_file, 'r') as f:
        data = json.load(f)
        # create database with new data
        if not 'guilds' in data:
            data['guilds'] = list()
            for i in range(len(bot.guilds)):
                guild = create_guild_json(
                    bot.guilds[i].name, bot.guilds[i].id, False, list())
                data['guilds'].append(guild)

        # lacking one or more guilds, updates database with new guild
        if len(data['guilds']) != len(bot.guilds):
            for guild in bot.guilds:
                is_new_guild = True
                for db_guild in data['guilds']:
                    if guild.name == db_guild['name']:
                        is_new_guild = False
                if is_new_guild:
                    data['guilds'].append(create_guild_json(guild.name, guild.id, False, list()))

        update_db(db_file, data)


def update_db(name: str, data: dict):
    with open(name, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def create_guild_json(name: str, id: int, isPosting: bool, schedules: list):
    return {'name': name, 'id': id, 'isPosting': isPosting, 'schedules': schedules}


load_dotenv()
bot.run(os.getenv('TOKEN'))
