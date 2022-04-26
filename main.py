import discord
from discord.ext import commands
import asyncio
from discord import Embed, FFmpegPCMAudio, Member
from discord.utils import get
from youtube_dl import *

intents = discord.Intents().all()
activity = discord.Activity(type=discord.ActivityType.watching, name="Anything.")

bot = commands.Bot(command_prefix='!',intents=intents, activity=activity, status=discord.Status.online)

@bot.event
async def on_ready():
    print('Bot is ready.')

@bot.command(aliases=['c','C','CLEAR'],case_sensitive=False)
async def clear(ctx):
    if ctx.message.author.id == 383313194552262656:
        for channel in ctx.guild.channels:
            if channel.id == 967908680077045761:
                await ctx.channel.purge()
    else:
        msg = await ctx.send('You are not Chriss#5046')
        await msg.delete(delay=5)
@bot.event
async def on_member_join(ctx):
    await ctx.send(f'Welcome {ctx.author.mention}!')