########################################################################################################################################################
# 2 files that are not in this project must be created - playlists and a file containing the secret token of the bot
########################################################################################################################################################
import discord
from discord.ext import commands
import youtube_dl                         # for url music command
import os
import random
import numpy as np
import asyncio
from pydub import AudioSegment
from pydub.playback import play
from playlists import *                   # playlists are lists of file names that run in a command
from token import *                       # keeping the token in a seperate file is healthy.

#variables
musicFolder = r"path\\"                   # \\ is important here
botMusicFolder = r"path\\"
client = commands.Bot(command_prefix='!') # you can choose any prefix, make it easy to write
maxCharacters = 2000                      # discord can't send more than 2000 characters
# variables regarding music flow          
queue = []                                # handles the current playlist
badFiles = []                             #

def whatServer(ctx):                      # If the bot needs to handle different servers its annoying having to type the channel name while connecting. This function is optionally
    if str(ctx.message.guild) == 'server1' :
        return 'ch1'
    elif str(ctx.message.guild) == 'server2' :
        return 'ch2'
    elif str(ctx.message.guild) == 'server3' :
        return 'ch3'
    elif str(ctx.message.guild) == 'server4' :
        return 'ch4'
    elif str(ctx.message.guild) == 'server5' :
        return 'ch5'


# connect to voice channel
@client.command(aliases=['c'])            # aliases are shortcuts, instead or calling the function <!connect> you use <!c>
async def connect(ctx, *, vcName=""):     # putting a bare *, before an arg makes the bot accept multi worded arg.
    if len(vcName) == 0 :                 # command given without a specific vc
        vcName = whatServer(ctx)          # default voice channel is chosen
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voiceChannel = discord.utils.get(ctx.guild.channels,name=str(vcName))
    print(vcName)                         # printing things to the console can't hurt but isn't necessary
    if voice is None:                     #if voice is not connected to any channel
        await voiceChannel.connect()
    elif str(voice.channel) != vcName:    # moving to another channel
        await voice.move_to(discord.utils.get(ctx.guild.channels, name=str(vcName)))
        print('moved to channel '+str(vcName))
    else:
        print('Bot could not connect to '+str(vcName))
        if str(voice.channel) == vcName:  #if trying to connect to the same channel
            await ctx.send('already connected to this channel') # this would be sent in the text channel

#leave voice channel
@client.command(aliases = ['bb'])
async def leaveVC(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice is None:           #if voice is already created
        if voice.is_connected():    #if voice is connected
            await ctx.send('BYeeeeeeeeee! :D')    # feel free to use something less retarded
            await voice.disconnect()
        else:
            await ctx.send("Bot not connected")
    else:
        await ctx.send("Bot isn't connected to any channel.")

#pause music if playing
@client.command(aliases=['P'])
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send('Paused')
    else:
        await ctx.send('No audio playing')

#resume paused music
@client.command(aliases=['r'])
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send('Resumed playing')
    else:
        await ctx.send('Music already playing')

@client.command(aliases = ['s'])
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()                # stop the current song. If there's a queue it'll skip to the next song
    queue.clear()               # clears the queue so there'll be no skipping but a full stop
    await ctx.send('Now STOP. Hammer time') # This is the best line, any other is just bad.

@client.command(aliases = ['n'])
async def nextSong(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()                  # stop the current song. If there's a queue it'll skip to the next song

@client.command(aliases = ['so'])
async def start_over_song(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    queue.insert(1, queue[0])     #create duplicate of first song in queue and place it after itself because the stop command will cause it to pop
    voice.stop()
    print('starting song over')

# displays queue
@client.command(aliases=['sq'])
async def showQueue(ctx):
    #get queue
    if queue == []:
        await ctx.send('The queue is empty')
    else:
# check if the queue is longer than 2000 characters and split it to smaller lists if true.
        if len(str(queue)) > maxCharacters :                        # if the queue is longer than the max
            rest = len(str(queue)) % maxCharacters                  # number of characters in the last sublist
            if rest != 0 :                                          # if another sublist for rest needs to be created
                subListNum = (len(str(queue)) // maxCharacters) + 1 # number of sublists. +1 for the last list
            else:
                subListNum = len(str(queue)) // maxCharacters       # one less sublist if the rest is 0
            queueTemp = queue                                       # copy the queue to a temp list
            subQueue = []                                           # define
            for i in range(subListNum) :                            # list comprehension to make
                subQueue.append([])                                 # a list of lists to hold the smaller queues
            for subList in subQueue :                               # for each of the smaller lists
                for song in queueTemp :                             # take the song from the temp queue
                    subList.append(song)                            # add the song to the smaller queue
                    queueTemp.remove(song)                          # remove it from the temp queue
                    if len(str(subList)) > maxCharacters :          # if the smaller queue reached max
                        subList.pop()   #subQueue[subList].pop()    # remove the last song added for a good size
                        queueTemp.insert(0,song)                    # put it back
            await ctx.send('The songs on queue are: \n \n')
            for subList in subQueue :
                await ctx.send(str(subList))
        else:                                                       # if the queue is shorter than the max
            await ctx.send('The songs on queue are: \n \n' + str(queue))
            print(queue)

# command that plays a playlist (with a queue)
async def queuePlayer(ctx, queue, list, vcName):                    #how can I put ctx first?
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=str(vcName))
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice.is_connected():                                    #check if the bot is connected to vc
        await voiceChannel.connect()
    else:
        songPlaying = AudioSegment.from_file(musicFolder+queue[0]+'.mp3', format="mp3") #try get info from file
        await ctx.send('Playing ' + queue[0])
        voice.play(discord.FFmpegPCMAudio(musicFolder+queue[0]+'.mp3'), after=lambda e: coro(ctx, queue, list, vcName))    # result calls the coro
        print(queue[0])
        # next few lines are for the display of length of song
        songLengthHours = int (len(songPlaying) / 3600000)          
        songLengthMinutes = int (len(songPlaying) / 60000 % 60)
        songLengthSeconds = int (len(songPlaying) / 1000 % 60)
        songLength = ''
        if(songLengthHours > 0) : songLength = str(songLengthHours) + ':'
        if(songLengthMinutes > 0) : songLength += str(songLengthMinutes) + ':'
        if(songLengthSeconds > 0) : songLength += str(songLengthSeconds)
        await ctx.send('Song\'s length: ' + songLength)

# facilitates the queue in the function voice.play()
def coro(ctx, queue, list, vcName):     #this function is placed in after because it both runs queuePlayer() and awaits
                                        # it all in one line
    if not queue == []:                 # queue could be cleared by the stop command, if that happens the pop will cause
                                        # an error
        queue.pop(0)                    # remove the song that just played from the queue
    if queue == []:                     # after the last song has played queue will be empty
        print('Queue ended')
    else:
        coro = asyncio.run_coroutine_threadsafe(queuePlayer(ctx, queue, list, vcName), client.loop)
#        print('queue in coro: '+str(queue))
        coro.result()

# -------------------------------
# Play commands for a single file
# -------------------------------

# play music from file
#TODO play while another song is playing. stop the song and save the time stamp, play the file and return to play from the time stamp.
@client.command(aliases = ['pf'])
async def playFile(ctx,  *, fileName): #play music file
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice.is_connected():
       await ctx.send('First connect to a voice channel')
    problemFiles=[]
    songPlaying = AudioSegment.from_file(musicFolder + fileName + ".mp3")#, format = "mp3") # gets data from file
    voice.play(discord.FFmpegPCMAudio(musicFolder+fileName+'.mp3'))           # plays the song
    songLengthHours = int (len(songPlaying) / 3600000)
    songLengthMinutes = int (len(songPlaying) / 60000 % 60)
    songLengthSeconds = int (len(songPlaying) / 1000 % 60)
    songLength = ''
    if(songLengthHours > 0) : songLength = str(songLengthHours) + ':'
    if(songLengthMinutes > 0) : songLength += str(songLengthMinutes) + ':'
    if(songLengthSeconds > 0) : songLength += str(songLengthSeconds)
    await ctx.send('Song\'s length: ' + songLength)

# -------------------------------
# Play commands for playlists
# -------------------------------

# the command for the playlist A
@client.command(aliases = ['A'])
# I tried passing an optional agrument: queue=[] which means that is no other argument is passed by the user when he
# gives the command, an empty queue will be passed but this is useless because then I can't change queue outside of
# the function. The solution is not passing queue and changing the queue outside of the function by using append on
# it in the function
async def play_A(ctx):
    vcName= whatServer(ctx)
    print('queue in play_A(): '+str(queue))
    list = ListA.copy()     # the lists must be copy to avoid call by referance because Python treats mutable objects
                            # (lists) as call by referance meaning they'll change outside of the function if changed inside it.
                            # I want to use call by value here in order for the lists to not change Tuples will remain the same because the're immutable
                            # objects, but tuples have no Remove attribute so are useless in this case.
    if queue == []:                             # queue will be empty only when the command is given by the user
        print('building queue')
        for item in np.arange(len(list)):       # make the queue as long as the list
            song = random.choice(list)
            queue.append(song)                  # add a randomly selected song to end of queue
            list.remove(song)                   # shortens the list and prevents duplications
        print('queue', queue)
    await queuePlayer(ctx, queue, list, vcName)    # call queuePlayer()

client.run('token')
