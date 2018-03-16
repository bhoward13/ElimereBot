import traceback
import config
import discord
import botoptions
import random
import datetime
import modules.database as database
from discord.ext import commands


class ErrorHandling:

    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        """This event is triggered when an error is raised while invoking a command."""

        try:
            if isinstance(error.original, discord.errors.Forbidden):
                try:
                    await ctx.send("I don't have the required permissions to run this command.")
                except:
                    pass
                finally:
                    return
        except AttributeError:
            pass

        if isinstance(error, commands.MissingPermissions):
            try:
                await ctx.send("You don't have the required permissions for that command.")
            except Exception as e:
                print(e)
            finally:
                return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send("This bot doesn't accept private messages.")
            except Exception as e:
                print(e)
            finally:
                return

        elif isinstance(error, commands.MissingRequiredArgument):
            try:
                strippedCommand = ctx.message.content.replace(ctx.message.content[0], '')
                strippedCommand = strippedCommand[0:len(strippedCommand)]
                prefix = self.bot.command_prefix
                await ctx.send(f"{error}")
                await ctx.send(f"Do {prefix} help {strippedCommand} to see the correct usage.")
            except Exception as e:
                print(e)
            finally:
                return

        elif isinstance(error, commands.CommandNotFound):
            try:
                prefix = self.bot.command_prefix
                await ctx.send(f"There is no command called {ctx.message.content}.")
                await ctx.send(f"Use {prefix} help to see a list of available commands.")
            except Exception as e:
                print(e)
                pass
            finally:
                return

        elif isinstance(error, commands.CommandOnCooldown):
            try:
                await ctx.send(random.choice(botoptions.eli_annoyed))
            except Exception as e:
                print(e)
                pass
            finally:
                return
        
        elif isinstance(error, commands.errors.BadArgument):
            try:
                prefix = self.bot.command_prefix
                await ctx.send(f"You entered an invalid value. Type {prefix} help <command> to see the correct usage.")
            except Exception as e:
                print(e)
                pass
            finally:
                return

        elif isinstance(error, commands.CheckFailure):
            return

        var = traceback.format_exception(type(error), error, error.__traceback__)
        e = discord.Embed(title="Command Error", colour=0x32952)
        e.description = f'```py\n{var}\n```'
        e.add_field(name='Command', value=ctx.command)
        e.add_field(name='Server', value=ctx.guild)
        e.add_field(name='Error', value=error)
        logger = ErrorLogging()
        await logger.LogError(server=ctx.guild, command=ctx.command, error=error)
        await self.bot.get_guild(config.devServerID).get_channel(config.errorChanID).send(embed=e)


class ErrorLogging:

    async def LogError(self, server, command, error):
        db = database.Database()
        await db.insert_error_data(datetime.datetime.now(), server, command, error)


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
