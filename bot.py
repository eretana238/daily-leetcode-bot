import discord
import requests

prefix = '*'

class Client(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))


    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith(prefix):
            await message.channel.send('Hello!')


if __name__ == "__main__":
    client = Client()
    token = ''
    with open('token.txt', 'r') as f:
        token = f.readline()
    client.run(token)    

    # r = requests.get('https://leetcode.com/api/problems/algorithms/')
    
    # r.json()