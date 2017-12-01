import discord
from discord.ext import commands
import asyncio

from tools.db import db_manager
from private import tokens
import Config



description = 'Mezghana-Bot'
bot = commands.Bot(command_prefix=Config.prefix, description=Config.description)

#db
db_manager.connect()



@bot.event
async def on_ready():
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')


bot.load_extension("cogs.games")
bot.load_extension("cogs.mod")
bot.load_extension("cogs.utils")

bot.run(tokens.DISCORD_API_KEY)
