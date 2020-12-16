import discord
import requests
import random
import json

import phrases

# lc start random
# lc start easy
# 
# current idea have competitions (fastests to complete problem, )
# keep track of peoples progress
#   ranking system (problems solved)
#       apprentice, noice, normal, experienced, expert, master, Engineer, God
#       0           10     30      60           100     150     210       280
# give fake rewards (new emojies, etc)
# answer bad when talked bad too
# present difficulty of the problem with its rating
# allow members to submit code and check if its accepted
# compare code with others (check runtimes, check space, lines of code, time to complete)
class Client(discord.Client):
    # def __init__(self):
    #     self.r = ''

    async def send_msg(msg):
        await msg.channel.send(msg)

    async def on_ready(self):
        r = requests.get('https://leetcode.com/api/problems/algorithms/')
        print('Leetcode problems obtained')

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith(phrases.PREFIX):
            msg = message.content.replace(phrases.PREFIX, '')
            args = msg.strip().split(' ')
            if args[0].lower() == 'start':
                if len(args) <= 1:
                    await self.send_msg("Invalid amount of arguments. Try again you weeb")

                await self.start(args[1:])


            elif args[0].lower() == 'stop':
                pass
            else:
                await self.send_msg(phrases.HOSTILE_RESPONSE[random.randint(0, len(phrases.HOSTILE_RESPONSE))])

    # async def start(self, args):
    #     response = json.dumps(self.r)
    #     choice = random.randint(1,len(response['stat_status_pairs']))

        # check that it is non paid
        # check difficulty

if __name__ == "__main__":
    client = Client()
    with open('token.txt', 'r') as f:
        token = f.readline()
        client.run(token)
