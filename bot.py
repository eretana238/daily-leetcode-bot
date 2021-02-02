import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import os
from random import randint
import requests
from requests.exceptions import HTTPError
import time

import constants

bot = commands.Bot(command_prefix='lc ')

info = list()
t = ''
stop_posting = False


@bot.event
async def on_ready():
    global info
    res = requests.get('https://leetcode.com/api/problems/algorithms/')
    info = res.json()['stat_status_pairs']
    print('Ready')


@bot.command()
async def stop(ctx):
    if 'daily_post_time' not in db.keys():
        await ctx.send('Mmmm...there\'s nothing to stop')
        return
    global stop_posting
    stop_posting = True


@bot.command()
async def reset(ctx):
    if 'daily_post_time' not in db.keys():
        await ctx.send('There\'s nothing to reset')
        return
    global stop_posting
    stop_posting = True
    del db['daily_post_time']


@bot.command()
async def resume(ctx):
    if 'daily_post_time' not in db.keys():
        await ctx.send('There\'s no daily posting to resume. Use an **lc start** command instead')
        return
    await ctx.send('Resumed daily posting!')
    await ctx.invoke(bot.get_command('start random'))


@bot.group()
async def start(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid start command. Example command **lc start random**')


@start.command()
async def random(ctx, t='12:00'):
    global stop_posting
    stop_posting = False
    if t is not None:
        print('starting to post problems')
        if 'daily_post_time' not in db.keys():
            db['daily_post_time'] = t
        while not stop_posting:
            await start_random(parse_time(db['daily_post_time']), ctx)


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


async def start_random(t, message):
    global stop_posting
    while not stop_posting:
        gm_time = time.gmtime()
        if t[0] == gm_time[3] and t[1] == gm_time[4] and gm_time[5] == 0:
            await message.channel.send('Daily coding practice %d!' % db['problem_counter'])
            await choose_problem(message, 1)
            await choose_problem(message, 2)
            await choose_problem(message, 3)
            db['problem_counter'] += 1
        await asyncio.sleep(1)
    print('stopped daily posting')
    await message.channel.send('Stopped daily posting!')


def get_problem_counter():
    if 'daily_counter' in db.keys():
        counter = int(db['daily_counter'])
        counter += 1
        db['daily_counter'] = counter


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
    query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    libraryUrl\n    __typename\n  }\n}\n
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

load_dotenv()
bot.run(os.getenv('TOKEN'))
