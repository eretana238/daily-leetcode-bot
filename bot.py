import discord
import requests
import random

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
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

        self.r = requests.get('https://leetcode.com/api/problems/algorithms/')

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith(prefix):
            msg = message.content.replace('*', '')
            args = msg.strip().split(' ')
            if args[0].lower() == 'start':
                pass
            elif args[0].lower() == 'stop':
                pass
            elif args[0].lower() == 'publish':
                pass
            else:
                await message.channel.send(hostile_responses[random.randint(0, len(hostile_responses))])


if __name__ == "__main__":
    prefix = '*'
    hostile_responses = ['No u', 
                        'Stop being dumb', 
                        'Shut the hell up', 
                        'Sorry I can\'t understand stupid.', 
                        'The fuck are you sayin.', 
                        'Is your typing speed 1 word/min?',
                        'Go back to your mommy and cry bitch.',
                        'Just stop.',
                        'I\'m sure 99% of your beauty can be removed with a kleenex.',
                        'I think you\'re the impostor']
    client = Client()
    token = ''
    with open('token.txt', 'r') as f:
        token = f.readline()
    client.run(token)    

    # r.json()