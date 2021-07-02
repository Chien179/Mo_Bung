import os
import discord
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands
from youtubesearchpython import VideosSearch

load_dotenv()

token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print('ready')


@bot.command()
async def great(ctx):
    await ctx.send('Thanks, I love you')


@bot.command()
async def hello(ctx):
    await ctx.send('hello')


@bot.command()
async def start(ctx):
    await ctx.send('Thằng lập trình mình ngu vl các bạn ạ!!!')


@bot.command(help='Phát nhạc trên Youtube.')
async def play(ctx, *args):
    url = ' '.join(args)
    if 'https://www.youtube.com/' not in url:
        videosSearch = VideosSearch(url, limit=1)
        url = videosSearch.result()['result'][0]['link']

    while True:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice == None:
            await connect(ctx)
        else:
            break

    ydl_opts = {'format': 'bestaudio/best'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']

    voice.play(discord.FFmpegPCMAudio(URL))
    await ctx.send('Now playing ' + url)


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('Currently no audio is playing')


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('The audio is not pause')


@bot.command(help='Kết nối đến kênh âm thanh')
async def connect(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    connected = ctx.author.voice
    if not connected:
        await ctx.send('You need to be connected in a voice channel first')
        return
    if voice != None:
        await ctx.send("I'm already connected to a voice channel.")
        return
    await connected.channel.connect()

@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None:
        await voice.disconnect()
    else:
        await ctx.send('The bot is not connected to a voice channel')


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()

bot.run(token)
