import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import os
from random import randint
import re
import requests
from requests.exceptions import HTTPError
import time

import constants

bot = commands.Bot(command_prefix='lc ', description='A simple discord bot that enslaves your life with leetcode')

info = list()
t = ''
db_file = 'db.json'
stop_posting = False
data = list()

@bot.event
async def on_ready():
    global info
    global data
    res = requests.get('https://leetcode.com/api/problems/algorithms/')
    info = res.json()['stat_status_pairs']

    with open(db_file, 'r') as f:
        data = json.load(f)
        # create database with new data
        if not 'guilds' in data:
            data['guilds'] = list()
            for i in range(len(bot.guilds)):
                guild = create_guild_json(
                    bot.guilds[i].name, bot.guilds[i].id, False, list(), 0)
                data['guilds'].append(guild)
            update_db(db_file, data)

        # lacking one or more guilds, updates database with new guild
        if len(data['guilds']) != len(bot.guilds):
            for guild in bot.guilds:
                is_new_guild = True
                for db_guild in data['guilds']:
                    if guild.name == db_guild['name']:
                        is_new_guild = False
                if is_new_guild:
                    data['guilds'].append(create_guild_json(guild.name, guild.id, False, list(), 0))
            update_db(db_file, data)
        
    print('ready')


@bot.event
async def on_disconnect():
    global data
    for guild in data['guilds']:
        guild['isPosting'] = False
    update_db(db_file, data)
    print('bot disconnected')

@bot.command()
async def stop(ctx):
    global data
    guild = get_guild(ctx.guild.id)
    if guild['isPosting']:
        guild['isPosting'] = False
    else:
        await ctx.send('Mmmm...there\'s nothing to stop')
        return
        
    global stop_posting
    stop_posting = True
    update_db(db_file, data)
    await ctx.send('Stopped daily posting!')


@bot.command()
async def reset(ctx):
    global data
    guild = get_guild(ctx.guild.id)
    if guild['id'] == ctx.guild.id:
        guild['schedules'] = list()
        guild['isPosting'] = False
    global stop_posting
    stop_posting = True
    update_db(db_file, data)
    await ctx.send('Reset daily posting!')


@bot.command()
async def resume(ctx):
    global data
    guild = get_guild(ctx.guild.id)
    if len(guild['schedules']) > 0 and not guild['isPosting']:
        guild['isPosting'] = True
        global stop_posting
        stop_posting = False
        await ctx.send('Resumed daily posting!')
        update_db(db_file, data)
        command = bot.get_command('start random')
        await ctx.invoke(command, guild['schedules'][0])
    else:
        await ctx.send('No daily posting to resume or daily posting is already running.')


@bot.group()
async def start(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid start command. Example command **lc start random**')

@start.command()
async def random(ctx, t="12:00"):
    print(t)
    global stop_posting
    stop_posting = False
    if t is None or not re.match('\d\d:\d\d', t):
        await ctx.send('Invalid time format provided. Make sure to provide a 24-hour format.')
        return
    global data
    guild = get_guild(ctx.guild.id)
    guild['isPosting'] = True
    if t not in guild['schedules']:
        guild['schedules'].append(t)
        update_db(db_file, data)
    while not stop_posting:
        await start_random(parse_time(t), ctx, guild)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith(constants.PREFIX):
        args = message.content.split(' ')
        if args[1].lower() == 'start' or args[1].lower() == 'stop' or args[1].lower() == 'reset' or args[1].lower() == 'resume':
            await bot.process_commands(message)
        else:
            await message.channel.send(hostile_response())


def parse_time(t):
    if ':' not in t:
        return None
    ti = t.split(':')
    return (int(ti[0]) + 7) % 24, int(ti[1])


def random_problem(level):
    while True:
        problem = info[randint(0, len(info) - 1)]
        if not problem['paid_only'] and problem['difficulty']['level'] == level:
            return problem


async def start_random(t, message, db_guild):
    global stop_posting
    global data
    guild = get_guild(message.guild.id)
    while not stop_posting:
        gm_time = time.gmtime()
        if t[0] == gm_time[3] and t[1] == gm_time[4] and gm_time[5] == 0:
            guild['problemCounter'] += 1
            await message.channel.send('Daily coding practice %d!' % guild['problemCounter'])
            await choose_problem(message, 1)
            await choose_problem(message, 2)
            await choose_problem(message, 3)
            update_db(db_file, data)
        await asyncio.sleep(1)


async def choose_problem(message, level):
    while True:
        problem = random_problem(level)
        ql_res = get_quest_info(problem['stat']['question__title_slug'])
        if ql_res.get('likes') > (ql_res.get('dislikes') * 2):
            embedVar = discord.Embed(title=ql_res.get('title'),
                                     type="rich",
                                     url="https://leetcode.com/problems/" +
                                     ql_res.get('titleSlug'),
                                     description='Leetcode #' +
                                     str(ql_res.get('questionFrontendId')),
                                     color=0xfcba03)
            embedVar.add_field(name="Difficulty",
                               value=ql_res.get('difficulty'),
                               inline=True)
            embedVar.add_field(name="Paid only?",
                               value=ql_res.get('isPaidOnly'),
                               inline=True)
            embedVar.add_field(name="Total submitted",
                               value=problem['stat']['total_submitted'],
                               inline=True)
            embedVar.add_field(name="Likes",
                               value=ql_res.get('likes'),
                               inline=True)
            embedVar.add_field(name="Dislikes",
                               value=ql_res.get('dislikes'),
                               inline=True)
            embedVar.set_footer(text="Lonely boy studios")
            await message.channel.send(embed=embedVar)
            break


def get_quest_info(slug):
    query = """
    query questionData($titleSlug: String!) {\n
        question(titleSlug: $titleSlug) {\n
            questionId\n    
            questionFrontendId\n    
            title\n    
            titleSlug\n    
            content\n    
            isPaidOnly\n    
            difficulty\n    
            likes\n    
            dislikes\n    
            isLiked\n    
            similarQuestions\n     
        }\n
    }\n
    """
    body = {
        "operationName": "questionData",
        "variables": {
            "titleSlug": slug
        },
        "query": query
    }

    url = "https://leetcode.com/graphql"
    try:
        response = requests.post(url, json=body)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        r_json = response.json()
        return r_json["data"]["question"]


def hostile_response():
    return constants.HOSTILE_RESPONSE[randint(
        0,
        len(constants.HOSTILE_RESPONSE) - 1)]

def update_db(name: str, data: dict):
    with open(name, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def create_guild_json(name: str, id: int, isPosting: bool, schedules: list, counter: int):
    return {'name': name, 'id': id, 'isPosting': isPosting, 'schedules': schedules, 'problemcounter': counter}

def get_guild(id: int):
    global data
    for guild in data['guilds']:
        if guild['id'] == id:
            return guild
        
load_dotenv()
bot.run(os.getenv('TOKEN'))
