#! /usr/bin/python

#
# Description:
# ================================================================
# Time-stamp: "2022-09-15 15:24:31 trottar"
# ================================================================
#
# Author:  Richard L. Trotta III <trotta@cua.edu>
#
# Copyright (c) trottar
#
import os, asyncio
import starfindercombat as combat

import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.all() # or .all() if you ticked all, that is easier
intents.members = True # If you ticked the SERVER MEMBERS INTENT

from config import config
import voicebot.commands.music as music
from voicebot.audiocontroller import AudioController
from voicebot.settings import Settings
from voicebot.utils import guild_to_audiocontroller, guild_to_settings

initial_extensions = ['voicebot.commands.music', 'voicebot.commands.general', 'voicebot.commands.palpatine', 'voicebot.plugins.button']
bot = commands.Bot(command_prefix=config.BOT_PREFIX,pm_help=True, case_insensitive=True,intents=intents)

if __name__ == '__main__':

    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    if config.BOT_TOKEN == "":
        print("Error: No bot token!")
        exit

@bot.event
async def on_ready():
    print(config.STARTUP_MESSAGE)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Music, type {}help".format(config.BOT_PREFIX)))

    for guild in bot.guilds:
        await register(guild)
        print("Joined {}".format(guild.name))

    await setup_hook()
    print(config.STARTUP_COMPLETE_MESSAGE)

@bot.event
async def on_guild_join(guild):
    print(guild.name)
    await register(guild)

async def setup_hook():
    for extension in initial_extensions:
        try:
            print(extension)
            bot.load_extension(extension)
        except Exception as e:
            print(e)    

async def register(guild):

    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    sett = guild_to_settings[guild]

    try:
        await guild.me.edit(nick=sett.get('default_nickname'))
    except:
        pass

    if config.GLOBAL_DISABLE_AUTOJOIN_VC == True:
        return

    vc_channels = guild.voice_channels

    if sett.get('vc_timeout') == False:
        if sett.get('start_voice_channel') == None:
            try:
                await guild_to_audiocontroller[guild].register_voice_channel(guild.voice_channels[0])
            except Exception as e:
                print(e)

        else:
            for vc in vc_channels:
                if vc.id == sett.get('start_voice_channel'):
                    try:
                        await guild_to_audiocontroller[guild].register_voice_channel(vc_channels[vc_channels.index(vc)])
                    except Exception as e:
                        print(e)        
                        
@bot.command(name='initialize', help=f'Generate initiative roll order for players and npcs')
async def initializeRoll(ctx, npc_mentions, npc_rolls, *mentions: discord.Member):
	npc_mentions = npc_mentions.split(',')
	npc_rolls = npc_rolls.split(',')
	npcs = [i for i in zip(list(npc_mentions),list(npc_rolls))]
	print(npcs)
	await ctx.send('Waiting for everyone to roll initiative...')
        # Converting the tuple to list so we can remove from it
	mentions = list(mentions)
	mentionDict = {}
	def check(message):
		if message.channel == ctx.channel and message.author in mentions :
			character = ""
			for key, val in combat.char_stat["discord"].items():
				print(mentions[0],"=?=",val)
				if str(mentions[0]) == val:
					character = key
			init_roll = combat.initialize(character, int(message.content), bonus=0)
			print("--->",init_roll,character)
			mentionDict[message.author.name] = int(init_roll)
			# Removing the member from the mentions list
			mentions.remove(message.author)
			# If the length of the mentions list is 0 means that everyone accepted the invite
			print("loop ",mentionDict)
			if len(mentions) == 0:
				return True
		return False
	await bot.wait_for('message', check=check)	
	for i,npc in enumerate(npc_mentions):
		init_roll = combat.initialize(npc, int(npc_rolls[i]), bonus=0)
		mentionDict[npc] = int(init_roll)
	print("out ",mentionDict)
	sorted_mentionDict = dict(sorted(mentionDict.items(),key=lambda x: x[1],reverse=True))
	print("sort ",sorted_mentionDict)
	await ctx.send(f'The attack order is...\n')
	for i,key in enumerate(sorted_mentionDict):
		print("------")
		print(i+1,") ",key)
		await ctx.send(f'{i+1}) {key}, {sorted_mentionDict[key]}')
	
@bot.command(name='attack', help='Armor check for a player attacking an npc')
async def damagecheck(ctx, combat_type, damage_type, mentions: discord.Member, d_char, d_roll, a_bonus=0, d_bonus=0):
	await ctx.send(f'Waiting for {mentions.name}\'s attack roll...')
        # Converting the tuple to list so we can remove from it
	def check(message):
		if message.channel == ctx.channel and message.author == mentions :
			check.a_roll = message.content
			return True
		return False
	a_char = ""
	for key, val in combat.char_stat["discord"].items():
		if str(mentions) == val:
			a_char = key		
	if a_char == "":
		await bot.wait_for('message', check=check)
		await ctx.send(f'No character found for {mentions}')
	else:
		await bot.wait_for('message', check=check)
		response = combat.damage_check(combat_type, damage_type, a_char, int(check.a_roll), d_char, int(d_roll), int(a_bonus), int(d_bonus))
		await ctx.send(response)	
		
@bot.command(name='defend', help='Armor check for an npc attacking a player')
async def damagecheck(ctx, combat_type, damage_type, mentions: discord.Member, a_char, a_roll, a_bonus=0, d_bonus=0):
	await ctx.send(f'Waiting for {mentions.name}\'s attack roll...')
        # Converting the tuple to list so we can remove from it
	def check(message):
		if message.channel == ctx.channel and message.author == mentions :
			check.d_roll = message.content
			return True
		return False
	d_char = ""
	for key, val in combat.char_stat["discord"].items():
		if str(mentions) == val:
			d_char = key		
	if d_char == "":
		await bot.wait_for('message', check=check)
		await ctx.send(f'No character found for {mentions}')
	else:
		await bot.wait_for('message', check=check)
		response = combat.damage_check(combat_type, damage_type, a_char, int(a_roll), d_char, int(check.d_roll), int(a_bonus), int(d_bonus))
		await ctx.send(response)		
	
@bot.command(name='stats', help='Check your character stats, specify stat by adding an argument')
async def statcheck(ctx, stat=None):
	user = ctx.message.author
	for key, val in combat.char_stat["discord"].items():
		if str(user) == val:
			character = key
	response = combat.stat_check(character, stat)
	await ctx.send(response)	
	
@bot.command(name='item', help='Check the stats of an item, use format from handbook \n e.g. flare axe, blue star')
async def itemcheck(ctx, *item):
	item = ' '.join(item)
	response = combat.item_check(item)
	await ctx.send(response)

bot.run(config.BOT_TOKEN, reconnect=True)
