#!/usr/local/bin/python3.6
from datetime import datetime
import config
import discord
import discord.ext.commands.errors
import botoptions
import datetime
import traceback
import asyncio
import git
import subprocess
import os
import modules.wowhead as wow
from discord.ext import commands

DESCRIPTION = "An Elimere bot that really doesn't like to be asked questions!"
BOT_PREFIX = "$eli "


INITIAL_EXTENSIONS = (
    'modules.errorhandling',
    'modules.commands',
    'modules.dev',
    'modules.warcraftlogs',
    'modules.raiderio'
)


def RunBot():
    bot = ElimereBot()
    bot.run()


class ElimereBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=BOT_PREFIX, description=DESCRIPTION, pm_help=None, help_attrs=dict(hidden=True))
        self.guild_only = True
        self.event_loop = asyncio.get_event_loop()

        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)  # Load the extension, so you don't have to import it
                print(f'Loaded {extension} extension')
            except Exception as e:
                print(e)
                print(f'Failed to load extension {extension}')

    async def on_ready(self):  # This fires once the bot has connected
        print('-------------')
        print('Logged in as: ' + self.user.name)
        print('Bot ID: ' + str(self.user.id))
        print('Discord.py Version: ' + str(discord.__version__))
        print('-------------')
        self.check_for_update()
        self.event_loop.create_task(self.check_articles())

    async def check_articles(self):
        await self.wait_until_ready()
        a = wow.Wowhead()
        await a.PostNewArticle(self)
        await asyncio.sleep(18000)
        asyncio.ensure_future(self.check_articles())

    async def on_member_join(self, member):  # This is fired every time a user joins a server with this bot on it
        channel = self.get_guild(config.guildServerID).get_channel(config.guildGenChanID)  # Select the top most text channel in the server
        # Send this message
        await channel.send("Hello "+member.mention+"! Hope you enjoy your stay here! We're all happy you decided to join us!")

    async def on_message(self, message):
        async def check_for_string(msg):
            """Checks the message to see if it matches the hey eli strings"""
            for string in botoptions.hey_eli:  # For each string in hey_eli list
                if msg.content.lower().rfind(string) != -1:  # If it is found, return True
                    return True

        async def check_response_string(dict, msg):
            """This checks a dictionary of strings and returns appropriately"""
            for key in dict.keys():  # This looks at all the keys in the dictionary
                if msg.content.lower().rfind(key) != -1:  # If the key is found
                    return dict.get(key)  # Return the value of the key
            return ''  # Else return and empty string

        def check_dev(uid):
            """Checks whether the passed ID matches"""
            return uid == 167419045128175616 or uid == 167419045128175616

        try:
            if message.embeds:  # If the message sent was an embed
                if message.author.name == "GitHub":  # If the author is the github bot
                    embeds = message.embeds[0].to_dict()  # Look to see if the branch is the master branch then pull the new update
                    if embeds['title'].lower().rfind('elimerebot:master') != -1:
                        message.content = '$eli PullUpdate'
                        await self.process_commands(message)
                        return

            if message.author.bot is False:  # So the bot won't process bot messages
                if message.content.rfind(config.secretID) != -1:
                    if datetime.datetime.now().hour < 14:
                        await self.get_guild(message.guild.id).get_channel(message.channel.id).send(
                            botoptions.no_tag_please)
                if message.content == '':
                    return
                if message.content[0] == '$':  # If the message is actually a command, process it
                    await self.process_commands(message)  # This part processes the actual command
                    return  # Return so it doesn't run any other part of this
                response = await check_response_string(botoptions.eli_main_responses, message)  # Check to see if it's a keyword
                god_response = await check_response_string(botoptions.god_responses, message)  # Checks if a keyword from the gods
                if god_response != '':
                    if check_dev(message.author.id):
                        # If either author is the devs
                        message.content = god_response  # Send a god response
                        await message.channel.send(message.content)
                elif response != '':  # Else, send a normal response
                    message.content = response
                    await message.channel.send(message.content)
                elif await check_for_string(message) is True:  # If it's not a keyword, run the BotRespond command
                    message.content = "$eli BotRespond"
                    await self.process_commands(message)
        except AttributeError as e:
            await self.get_guild(config.devServerID).get_channel(config.errorChanID).send(e.__str__() + " in server " + str(message.guild))
            return

    def check_for_update(self):
        """Checks to see if the local repo is different and then updates"""
        local_repo = git.Repo(search_parent_directories=True)
        local_sha = local_repo.head.object.hexsha
        # local_short_sha = local_repo.git.rev_parse(local_sha)
        remote_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=local_repo.git_dir).decode(
            'ascii').strip()
        if local_sha != remote_sha:
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            g = git.cmd.Git(path)
            g.pull()
            os.system('sudo systemctl restart elimerebot.service')

    def run(self):
        super().run(config.token)

    async def on_error(self, event, *args, **kwargs):
        """Default error handler"""
        e = discord.Embed(title="Event Error", colour=0x32952)
        e.add_field(name="Event", value=event)
        e.add_field(name="args", value=str(args))
        e.add_field(name="kwargs", value=str(kwargs))
        e.description = f'```py\n{traceback.format_exc()}\n```'
        e.timestamp = datetime.datetime.utcnow()
        await self.get_guild(config.devServerID).get_channel(config.errorChanID).send(embed=e)


RunBot()
