#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2022-09-15 22:52:00 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#

import asyncio

import discord
from config import config
from discord.ext import commands

from voicebot.audiocontroller import AudioController
from voicebot import linkutils, utils

class Palpatine(commands.Cog):
    '''
    Voice commands by Emperor Palpatine
    
    '''
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='voice',  description=config.HELP_PALPATINE_LONG, help=config.HELP_PALPATINE_SHORT, aliases=['palpatine', 'v'])
    async def _palpatine_voice(self,ctx, voice_command):
        await ctx.send(file=discord.File('{0}/var/{1}.gif'.format(config.ABSOLUTE_PATH,voice_command)))
        # grab the user who sent the command
        author = ctx.message.author
        channel = author.voice.channel
        guild = utils.get_guild(self.bot, ctx.message)
        await AudioController(self.bot, guild).pause_played(voice_command)
        vc = guild.voice_client
        #vc.play(discord.FFmpegPCMAudio(executable='/usr/bin/ffmpeg',source='var/{}.mp3'.format(voice_command)), after=lambda e: print('done', e))
        # Sleep while audio is playing.
        #await asyncio.sleep(8.0)
        #await AudioController(self.bot, guild).resume_played()
        #await vc.disconnect()
        
def setup(bot):
    bot.add_cog(Palpatine(bot))
