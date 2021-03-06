import os
import config
import git
import discord
import asyncio
from discord.ext import commands

INITIAL_EXTENSIONS = (
    'modules.errorhandling',
    'modules.commands',
    'modules.warcraftlogs',
    'modules.raiderio',
    'modules.tags'
)


# noinspection PyPep8Naming
async def IsDev(ctx):
    """Used to check if a Dev is calling the command"""
    return ctx.author.id == 198574477347520513 or ctx.author.id == 167419045128175616 or ctx.author.name == 'GitHub'


class Dev:
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyPep8Naming
    @commands.check(IsDev)
    @commands.command(aliases=['restart'])
    async def Restart(self, ctx):
        """-Restart the bot"""
        await self.bot.logout()
        await asyncio.sleep(10)
        os.system('sudo systemctl restart discordbot.service')

    # noinspection PyPep8Naming
    @commands.check(IsDev)
    @commands.command(aliases=['shutdown'])
    async def Shutdown(self, ctx):
        """-Shuts the bot down"""
        e = discord.Embed(title='Bot Shutdown', colour=discord.Colour.purple())
        e.description = 'Bot has been shutdown, please restart the service directly.'
        channel = self.bot.get_guild(config.devServerID).get_channel(config.reportChanID)
        await channel.send(embed=e)
        await self.bot.logout()
        await asyncio.sleep(10)
        os.system('sudo systemctl stop discordbot.service')

    # noinspection PyPep8Naming
    @commands.check(IsDev)
    @commands.command(aliases=['pullupdate'])
    async def PullUpdate(self, ctx):
        """-This pulls from the master branch"""
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        g = git.cmd.Git(path)
        g.pull()
        os.system('sudo systemctl restart discordbot.service')

    # noinspection PyPep8Naming
    @commands.check(IsDev)
    @commands.command(aliases=['reloadcogs'])
    async def ReloadCogs(self, ctx):
        """This will reload all cogs"""
        for module in INITIAL_EXTENSIONS:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)

    @commands.check(IsDev)
    @commands.command()
    async def logout(self, ctx):
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Dev(bot))
