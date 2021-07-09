import os
import discord
import youtube_dl
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv
from discord.ext import commands, tasks
from youtubesearchpython import VideosSearch

load_dotenv()

token = os.getenv('WTOKEN')

bot = commands.Bot(command_prefix='$')

musicQueue = []


@bot.event
async def on_ready():
    print('ready')


@bot.command(help='Khen mình đi')
async def great(ctx):
    await ctx.send('Thanks, I love you hihi')


@bot.command(help='Chào')
async def hello(ctx):
    await ctx.send("Hello, i'm Mỡ Bụng\nNice to meet you")


@bot.command(help='???!!!')
async def start(ctx):
    await ctx.send('Thằng lập trình mình ngu vl các bạn ạ!!!')


@bot.command(help='Phát nhạc trên Youtube.')
async def play(ctx, *args):
    url = ' '.join(args)

    inforVideo = infor_video(url)

    musicQueue.append(inforVideo[0])

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    connected = ctx.author.voice
    if not connected:
        await ctx.send('You need to be connected in a voice channel first')
        return
    if voice == None:
        await connected.channel.connect()

    try:
        playing.start(ctx)
    except RuntimeError:
        return
    finally:
        print('Added to queue')
        await ctx.send('Queued ' + inforVideo[1] + '\t*(Channel: ' + inforVideo[2] + ')*')


def infor_video(url):
    videosSearch = VideosSearch(url, limit=1)
    url = videosSearch.result()['result'][0]['link']
    title = videosSearch.result()['result'][0]['title']
    channel = videosSearch.result()['result'][0]['channel']['name']
    duration = videosSearch.result()['result'][0]['duration']

    return [url, title, channel, duration]


@tasks.loop(seconds=0)
async def playing(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing() is False and musicQueue:
        ydl_opts = {'format': 'bestaudio/best'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}

        url = musicQueue.pop(0)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']

        voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        print('playing ' + url)
        await ctx.send('Now playing ' + url)
        print('played ' + url)


@bot.command(help='Tạm dừng phát nhạc')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send('Currently no audio is playing')
    except AttributeError:
        await ctx.send('Currently no audio is playing')


@bot.command(help='Tiếp tục phát nhạc')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        if voice.is_paused():
            voice.resume()
        else:
            if not voice.is_playing():
                await ctx.send('Bot not playing audio')
            else:
                await ctx.send('The audio is not pause')
    except AttributeError:
        await ctx.send('Bot not playing audio')


@bot.command(help='Bot ngắt kết nối khỏi voice channel')
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None:
        await stop(ctx)
        await voice.disconnect()
        await ctx.send('Goodbye, have a nice day!!!')
    else:
        await ctx.send('The bot is not connected to a voice channel')


@bot.command(help='chuyển bài')
async def skip(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.command(help='Dừng nhạc')
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    musicQueue.clear()
    playing.stop()


@bot.command(help='Danh sách chờ phát nhạc')
async def queue(ctx):
    if musicQueue:
        for idx, val in enumerate(musicQueue):
            inforvideo = infor_video(val)
            await ctx.send(str(idx+1)+', '+inforvideo[1]+'  *(Channel: '+inforvideo[2] + ')*   '+inforvideo[3]+'\n')
    else:
        await ctx.send('Queue empty!!!')


@bot.command(help='Xoá danh sách chờ')
async def clear():
    musicQueue.clear()

bot.run(token)
