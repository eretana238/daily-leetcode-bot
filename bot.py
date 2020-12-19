import random
import discord
import requests
import re
import threading
import time

from core import phrases

client = discord.Client()
threading.Thread(target=client)
stop_threads = False

@client.event
async def on_ready():
    global info
    res = requests.get('https://leetcode.com/api/problems/algorithms/')
    info = res.json()['stat_status_pairs']
    print('Ready')

@client.event
async def on_message(message):
    global stop_threads
    if message.author == client.user:
        return

    if message.content.startswith(phrases.PREFIX):
        msg = message.content.replace(phrases.PREFIX, '')
        args = msg.strip().split(' ')
        # checks if argument is empty
        if re.search('^\s*$', args[0]):
            await invalid_args_msg(message)
        elif args[0] == 'start':
            if len(args) != 3:
                await invalid_args_msg(message)
            elif args[1] == 'random':
                t = parse_time(args[2])
                r = threading.Thread(target=await start_random(t, message))
   
        elif args[0] == 'stop' and len(args) == 1:
            stop_threads = True
            
        else:
            await message.channel.send(phrases.hostile_response())

async def invalid_args_msg(message):
    await message.channel.send('Invalid amount of arguments. Try again you weeb')
    
def parse_time(time):
    if ':' not in time:
        return None
    t = time.split(':')
    return (int(t[0]) + 7) % 24, int(t[1])

def random_problem(level):
    while True:
        problem = info[random.randint(0, len(info)-1)]
        if not problem['paid_only'] and problem['difficulty']['level'] == level:
            return problem
        

async def start_random(t, message):
    global stop_threads
    while not stop_threads:
        gm_time = time.gmtime()
        if t[0] == gm_time[3] and t[1] == gm_time[4]:
            await message.channel.send('Grind time!')
            await choose_problem(message,1)
            await choose_problem(message,2)
            await choose_problem(message,3)
        time.sleep(60)
    stop_threads = False

async def choose_problem(message, level):
    problem = random_problem(level)
    difficulty = 'easy'
    if level == 2:
        difficulty = 'medium'
    elif level == 3:
        difficulty = 'hard'
    embedVar = discord.Embed(title=problem['stat']['question__title'], url="https://leetcode.com/problems/" + problem['stat']['question__title_slug'], description='Leetcode #' + str(problem['stat']['question_id']), color=0x00ff00)
    embedVar.add_field(name="Difficulty", value=difficulty, inline=True)
    embedVar.add_field(name="Paid only?", value=problem['paid_only'], inline=True)
    embedVar.add_field(name="Total submitted", value=problem['stat']['total_submitted'], inline=True)
    embedVar.set_footer(text="Lonely boy studios")
    await message.channel.send(embed=embedVar)

with open('token.txt', 'r') as f:
    token = f.readline()
    client.run(token)
