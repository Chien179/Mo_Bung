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
async def botngu(ctx):
    await ctx.send('Mày mới ngu á, thằng gà')


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
        await ctx.send(url)
    song = os.path.isfile('song.mp3')

    try:
        if song:
            os.remove('song.mp3')
    except PermissionError:
        await ctx.send('Lỗi rồi thằng ngáo đá, lỗi này tao chưa biết sửa')
        return

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice == None:
        await connect(ctx)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            os.rename(file, 'song.mp3')

    voice.play(discord.FFmpegPCMAudio('song.mp3'))


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
        await ctx.send("i'm already connected to a voice channel.")
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
