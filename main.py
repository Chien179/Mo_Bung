import os
import discord
import youtube_dl
from dotenv import load_dotenv
from discord.ext import commands, tasks
from youtubesearchpython import VideosSearch
from hehe import keep_alive
load_dotenv()

token = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='!')

musicQueue = []
nowPlaying = ''


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
        await ctx.send(embed=message_embed('You need to be connected in a voice channel first'))
        return
    if voice == None:
        await connected.channel.connect()

    try:
        playing.start(ctx)
    except RuntimeError:
        return
    finally:
        print('Added to queue')
        message = 'Queued ' + inforVideo[1] + '\t*(Channel: ' + inforVideo[2] + ')*'
        await ctx.send(embed=message_embed(message))


def message_embed(message):
    return discord.Embed(color=discord.Colour.blue(), description=message)


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
        global nowPlaying
        nowPlaying = infor_video(url)[1]

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']

        voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        print('playing ' + url)
        message = 'Now playing ' + url
        await ctx.send(embed=message_embed(message))
        print('played ' + url)


@bot.command(help='Tạm dừng phát nhạc')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send(embed=message_embed('Currently no audio is playing'))
    except AttributeError:
        await ctx.send(embed=message_embed('Currently no audio is playing'))


@bot.command(help='Tiếp tục phát nhạc')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        if voice.is_paused():
            voice.resume()
        else:
            if not voice.is_playing():
                await ctx.send(embed=message_embed('Bot not playing audio'))
            else:
                await ctx.send(embed=message_embed('The audio is not pause'))
    except AttributeError:
        await ctx.send(embed=message_embed('Bot not playing audio'))


@bot.command(help='Bot ngắt kết nối khỏi voice channel')
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None:
        await stop(ctx)
        await voice.disconnect()
        await ctx.send(embed=message_embed('Goodbye, have a nice day!!!'))
    else:
        await ctx.send(embed=message_embed('The bot is not connected to a voice channel'))


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
    global nowPlaying
    nowPlaying = ''


@bot.command(help='Danh sách chờ phát nhạc')
async def queue(ctx):
    if musicQueue:
        for idx, val in enumerate(musicQueue):
            inforvideo = infor_video(val)
            message = str(idx+1)+', '+inforvideo[1]+'  *(Channel: '+inforvideo[2] + ')*   '+inforvideo[3]+'\n'
            await ctx.send(embed=message_embed(message))
    else:
        await ctx.send(embed=message_embed('Queue empty!!!'))


@bot.command(help='Xoá danh sách chờ')
async def clear(ctx):
    musicQueue.clear()


@bot.command(help='Bài hát đang được phát')
async def nowplaying(ctx):
    if nowPlaying == '':
        await ctx.send(embed=message_embed("The audio isn't playing"))
    else:
        message = 'Now playing ' + nowPlaying
        await ctx.send(embed=message_embed(message))

keep_alive()
bot.run(token)
