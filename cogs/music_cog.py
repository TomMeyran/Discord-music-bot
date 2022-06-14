import discord
from discord.ext import commands
from playlists import *
import numpy as np
import random
from pydub import AudioSegment
import asyncio                          # the bot runs as an an asynchronous function

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    queue = []
    musicFolder = r'.\\'      # folder for playlists
    botMusicFolder = r'.\\'   # folder for individual files

    # connect to voice channel
    @commands.command(aliases=['c'])
    async def connect(self, ctx, *, vcName=""):
            vc = self.bot.get_cog('Server').vcID(ctx, vcName) # calls vcID form the Server cog, which returns the voice channel
            print('connecting to',vc)
            if ctx.voice_client is None : # ctx.voice_client checks if the bot is already connected to a voice channel
                await vc.connect()
                await ctx.send('BOOM! Connected')
            else :
                await ctx.voice_client.disconnect()
                await vc.connect()

    @commands.command(aliases=['bb'])
    async def leaveVC(self, ctx):
        if ctx.voice_client is not None:
            await ctx.send('BYeeeeeeeeee! :D')
            await ctx.voice_client.disconnect()
        else:
            await ctx.send('Already not connected to a voice channel')

    @commands.command(aliases=['p'])
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send('No audio playing')

    @commands.command(aliases=['r'])
    async def resume(self, ctx):
        if ctx.voice_client.is_paused() :
            ctx.voice_client.resume()
        elif ctx.voice_client.is_playing() :
            await ctx.send('Music already playing')
        else :
            await ctx.send('Music is not paused. Can\'t resume')

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        self.queue.clear()  # clears the queue so there'll be no skipping but a full stop
        ctx.voice_client.stop()  # stop the current song. If there's a queue it'll skip to the next song

    @commands.command(aliases=['n'])
    async def nextSong(self, ctx):
        ctx.voice_client.stop()  # stop the current song. If there's a queue it'll skip to the next song

    @commands.command(aliases=['po'])
    async def start_song_again(self, ctx):
        self.queue.insert(1, self.queue[0])   # create duplicate of first song in queue and place it after itself because the stop
        ctx.voice_client.stop()                # command will cause it to pop
        print('starting song over')

    @commands.command(aliases=['sq'])
    async def showQueue(self, ctx):
        maxCharacters = self.bot.get_cog('Server').maxCharacters
        if self.queue == []:
            await ctx.send('The queue is empty')
        else:                 # if queue > 2000 characters, split to smaller lists.
            if len(str(self.queue)) > maxCharacters:  # if the queue is longer than the max
                    rest = len(str(self.queue)) % maxCharacters  # number of characters in the last sublist
                    if rest != 0:  # if another sublist for rest needs to be created
                        subListNum = (len(str(self.queue)) // maxCharacters) + 1  # number of sublists. +1 for the last list
                    else:
                        subListNum = len(str(self.queue)) // maxCharacters  # one less sublist if the rest is 0
                    queueTemp = self.queue  # copy the queue to a temp list
                    subQueue = []  # define
                    for i in range(subListNum):  # list comprehension to make
                        subQueue.append([])  # a list of lists to hold the smaller queues
                    for subList in subQueue:  # for each of the smaller lists
                        for song in queueTemp:  # take the song from the temp queue
                            subList.append(song)  # add the song to the smaller queue
                            queueTemp.remove(song)  # remove it from the temp queue
                            if len(str(subList)) > maxCharacters:  # if the smaller queue reached max
                                subList.pop()  # subQueue[subList].pop()    # remove the last song added for a good size
                                queueTemp.insert(0, song)  # put it back
                    await ctx.send('The songs on queue are: \n \n')
                    for subList in subQueue:
                        await ctx.send(str(subList))
            else:  # if the queue is shorter than the max
                await ctx.send('The songs on queue are: \n \n' + str(self.queue))
                print(queue)

# method that plays a playlist (with a queue)
    async def queuePlayer(self, ctx, queue, vcName):  # how can I put ctx first?
        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=str(vcName))
        if not ctx.voice_client.is_connected():  # check if the bot is connected to vc
            await voiceChannel.connect()
        #    if voice == None:
        #            await voiceChannel.connect()
        else:
            songPlaying = AudioSegment.from_file(self.musicFolder + queue[0] + '.mp3', format="mp3")
            ctx.voice_client.play(discord.FFmpegPCMAudio(self.musicFolder + queue[0] + '.mp3'),
                       after=lambda e: self.coro(ctx, queue, vcName))  # result calls the coro
            await ctx.send('Playing ' + queue[0] + ' ' + self.song_details(songPlaying))

    def song_details(self, songPlaying):
        songLengthHours = int(len(songPlaying) / 3600000)
        songLengthMinutes = int(len(songPlaying) / 60000 % 60)
        songLengthSeconds = int(len(songPlaying) / 1000 % 60)
        songLength = ''
        if (songLengthHours > 0): songLength = str(songLengthHours) + ':'
        if (songLengthMinutes > 0): songLength += str(songLengthMinutes) + ':'
        if (songLengthSeconds > 0): songLength += str(songLengthSeconds)
        return songLength

# facilitates the queue in the function voice_client.play()
    def coro(self, ctx, queue, vcName):  # this function is placed in after because it both runs queuePlayer() and awaits it all in one line
        if not queue == []:  # queue could be cleared by the stop command, if that happens the pop will cause an error
            queue.pop(0)  # remove the song that just played from the queue
        if queue == []:  # after the last song has played queue will be empty
            print('Queue ended')
        else:
            coro = asyncio.run_coroutine_threadsafe(self.queuePlayer(ctx, queue, vcName), self.bot.loop)
            print('queue in coro: ' + str(queue))
            coro.result()

    def build_queue(self, queue_list):
        if self.queue == []:            # queue will be empty only when the command is given by the user
            print('building queue')
            for item in np.arange(len(queue_list)):  # make the queue as long as the list
                song = random.choice(queue_list)
                self.queue.append(song) # add a randomly selected song to end of queue
                queue_list.remove(song) # shortens the list and prevents duplications
            print('queue', self.queue)
        return self.queue

    async def play_list(self, ctx, List):
        vcName = ctx.voice_client.channel
        print('queue in play_', List, ': ' + str(self.queue))
        queue_list = List.copy()
        await self.queuePlayer(ctx, self.build_queue(queue_list), vcName)  # call queuePlayer()

# commands for playlists

    @commands.command(aliases=['playlist'])
    async def play_playlist(self, ctx, aList= playlist): # playlist is a list from playlists file that contains strings of file names without mp3 ending
        await self.play_list(ctx, aList)

# commands for single files
    @commands.command(aliases = ['file'])
    async def play_file(self, ctx):
        vcName = ctx.voice_client.channel
        # check if on the right vc
        if not ctx.voice_client.is_connected():
            await voiceChannel.connect()
        ctx.voice_client.play(discord.FFmpegPCMAudio(self.botMusicFolder+'file.mp3'))

# custom command example for 2 similar files 
    @commands.command(aliases=['similar'])
    async def play_similar(self, ctx, fileIsB=False) :
        if fileIsB.lower() == 'true' :
            print('Playing type b')
            songPlaying = AudioSegment.from_file(musicFolder + 'fileB.mp3', format="mp3")
            ctx.send(self.song_details(songPlaying))
            if ctx.voice_client.is_connected() and not ctx.voice_client.is_playing() :
                ctx.voice_client.play(discord.FFmpegPCMAudio(self.musicFolder + 'fileB.mp3'))
                await ctx.send('Playing file b ' + self.song_details(songPlaying))
        elif fileIsB.lower() == 'false' :
            print('Playing file a')
            songPlaying = AudioSegment.from_file(musicFolder + 'fileA.mp3', format="mp3")
            ctx.send(self.song_details(songPlaying))
            if ctx.voice_client.is_connected() and not ctx.voice_client.is_playing():
                ctx.voice_client.play(discord.FFmpegPCMAudio(self.musicFolder + 'fileA.mp3'))
                await ctx.send('Playing file a ' + self.song_details(songPlaying))

def setup(bot):
    bot.add_cog(Music(bot))
