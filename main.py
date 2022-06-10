# -*- coding: utf-8 -*-
"""
Created on Tue May 18 14:40:27 2021

@author: Tom

TODO:
- make youtube links playable
- posting gifs to text channels
- posting pre made character details, place details and maps
-set optional time passed as argument with a default to each list and it will choose the number of songs to best fit that time
- be able to skip time in a song
- if possible play a song and another sound effect without having to pause the song
- make a help command to list to commands and explain how they work
"""
#TODO
#   make a check for member hazilon and only allow me to operate music commands.

import discord                          # no discord without this library or discord.py
from discord.ext import commands        # commands for the bot
import youtube_dl                       # for url music command
import os                               # always good to have
import random                           # helps with randomising the order of music in the queue
import numpy as np                      # helps with list comprehension for the queue
import asyncio                          # the bot runs as an an asynchronous function
from pydub import AudioSegment          # manipulation of the music files for things like duration etc.
from pydub.playback import play
# code from other files
from playlists import *                 # import playlists - made by user
from secrets import *                   # import functions that only the person who owns the bot should know
#import logging # debugging tools
#logging.basicConfig(filename='Tom\'s DMing assistant buglog', level=logging.DEBUG)
# general bot variables
bot = commands.Bot(command_prefix=prefix)
@bot.command()
async def load(ctx, extension):                 # loads the cog, can be done dynamically
    bot.load_extension(f'cogs.{extension}')  # searches the cog in the cogs folder

@bot.command()
async def unload(ctx, extension):               # unloads the cog, can be done dynamically
    bot.unload_extension(f'cogs.{extension}')# unloads the cog in cogs folder

@bot.command()
async def reload(ctx, extension):               # updates the cog without killing the script, must use filename in the command
    bot.unload_extension(f'cogs.{extension}')# unloads the cog in cogs folder
    bot.load_extension(f'cogs.{extension}')  # searches the cog in the cogs folder
    print(f'reloaded {extension}')

# loads all cogs at startup
for filename in os.listdir('./cogs'):           # lists all files in cogs folder
    if filename.endswith('.py') and not filename == 'games_cog.py':                # only py files are cogs
        bot.load_extension(f'cogs.{filename[:-3]}')  # removes the ending .py from the filename in order for it to load the cog

bot.run(token)

queue = []  # should be in the music cog
badFiles = []
volumeReady = False  # this is a global variable, every time I use it in a function I must have the line 'global volumeReady' once on top of the function and then I can use it in that scope. globals can't be sent as parameters to a function
volumeNext = 1.0

# variables regarding music flow
queue = []

