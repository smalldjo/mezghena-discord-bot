import discord
from discord.ext import commands
import asyncio
from time import time

from tools.db import db_manager


class mod:

    def __init__(self,bot):
        self.bot = bot
        self.intros_channels= db_manager.get_introduction_channels()

        #config
        self.intro_minimum_len = 10
        self.intro_minimum_len_to_dm = 40



    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return
        if msg.author.bot:
            await msg.delete()
            await msg.channel.send("Bots need no introduction",delete_after=2)
            return
        if msg.guild.id in self.intros_channels and self.intros_channels[msg.guild.id] == msg.channel.id:
            await self.handle_intros(msg)
            return


    async def handle_intros(self,msg):
        #config
        if len(msg.content.strip()) < self.intro_minimum_len:
            await msg.delete()
            await msg.channel.send("Introduction too short",delete_after=5)
            return
        prev_msg = await msg.channel.history().find(lambda m:(m.id != msg.id and m.author==msg.author))
        if not prev_msg is None:
            #print()
            if len(msg.content.strip()) > self.intro_minimum_len_to_dm:
                await msg.author.send("just so you don't lose all of what you wrote: \n {}".format(msg.content))
            await msg.delete()
            await msg.channel.send("You already introduced yourself",delete_after=5)
            return


    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def intros(self,context,action:str='',param:discord.TextChannel=None):
        if action == '':
            await context.send("```No action specified```")
            return

        guild_id = context.message.guild.id
        channel_id = context.message.channel.id
        if action.lower() == 'setchannel':
            print('before')
            if type(param)==discord.TextChannel:
                print('after')
                if (guild_id in self.intros_channels) and (param.id == self.intros_channels[guild_id]):
                    await context.send("This channel is already set as introduction channel for this server")
                    return
                db_manager.set_server_introduction_channel(guild_id,param.id)
                self.intros_channels[guild_id] = param.id
                await context.send('{0} has been set as introduction channel for this server'.format(param.mention))
                return
            else:
                await context.send('no Text Channel specified')
                return
        if action.lower() == 'disable':
            del self.intros_channels[guild_id]
            db_manager.remove_introduction_channel(guild_id)
            print('removed intro channel on server: {0}@{1} request from user:{2}@{3}'.format(guild_id,context.message.guild.name,context.message.author.id,context.message.author.display_name))
            await context.send("Introduction channel disabled")
            return

    @intros.error
    async def intros_error(self,ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('no valid text channel provided...')


def setup(bot):
    bot.add_cog(mod(bot))
