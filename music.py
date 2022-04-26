from main import *
queues = {}

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
#Commands:

async def embed(ctx,song,voice):
    content = f'1. {song[0]["title"]}\n2. {song[1]["title"]}\n3. {song[2]["title"]}\n4. {song[3]["title"]}\n5. {song[4]["title"]}'
    embeded = discord.Embed(title='Choose a song:', color=4770532,description=content)
    embeded.set_footer(text='Type anything else to cancel the selection.')
    embed_msg = await ctx.send(embed=embeded)
    message = await bot.wait_for('message')
    await message.delete(delay=5)
    await pick_song(ctx,message,song,voice,embed_msg)
async def get_song(ctx,query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        if query.startswith('https://www.youtube.com/'):
            info = ydl.extract_info(query, download=False)
            voice = get(bot.voice_clients, guild=ctx.guild)
            id = ctx.guild.id
            if id in queues:
                queues[id].append(info)
            else:
                queues[id] = [info]
            if len(queues[id]) > 0:
                msg = await ctx.send(f'Added {info["title"]} to the queue.')
                await delete_msg(msg)
            if not voice.is_playing():
                check_queue(ctx)
        else:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            return(info)

async def pick_song(ctx,message,song,voice,embed_msg):
    id = ctx.guild.id
    selected = ''
    num = 0
    cancelled = False
    if message.author == ctx.author and message.content.lower() == '1':
        num = 0
    elif message.author == ctx.author and message.content.lower() == '2':
        num = 1
    elif message.author == ctx.author and message.content.lower() == '3':
        num = 2
    elif message.author == ctx.author and message.content.lower() == '4':
        num = 3
    elif message.author == ctx.author and message.content.lower() == '5':
        num = 4
    elif message.author == ctx.author:
        msg = await ctx.send('Cancelled.')
        cancelled = True
    if not cancelled:
        selected = song[num]
        await delete_msg(embed_msg)
        if id in queues:
            queues[id].append(selected)
        else:
            queues[id] = [selected]
        if len(queues[id]) > 0:
            msg = await ctx.send(f'Added {selected["title"]} to the queue.')
            await delete_msg(msg)
        if not voice.is_playing():
            check_queue(ctx)
    else:
        await delete_msg(embed_msg)
        return
@bot.command(aliases=['p','P','PLAY'],case_sensitive=False)
async def play(ctx,query):
    channel = ctx.message.author.voice.channel
    await ctx.message.delete(delay=5)
    voice = await join(ctx,channel)
    song = await get_song(ctx,query)
    if song != None: # If song is None they used a URL.
        await embed(ctx,song,voice)
    

@bot.command(aliases=['st','ST','STOP'],case_sensitive=False)
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    id = ctx.guild.id
    if voice and voice.is_connected:
        await voice.disconnect()
        queues[id].clear()
    else:
        msg = await ctx.send('Nothing is playing right now.')
        await delete_msg(msg)

@bot.command(aliases=['s','S','SKIP'],case_sensitive=False)
async def skip(ctx):
    await ctx.message.delete(delay=5)
    voice = get(bot.voice_clients, guild=ctx.guild)
    id = ctx.guild.id
    if len(queues[id]) > 1 and voice.is_playing():
        await voice.stop()
        msg = await ctx.send(f'Skipped')
        await delete_msg(msg)
        await play_song(ctx,queues[id][0]['formats'][0]['url'],voice,id)
    elif len(queues[id]) == 1 and voice.is_playing():
        await voice.stop()
        msg = await ctx.send(f'Skipped')
        await delete_msg(msg)
    elif voice.is_playing() and len(queues[id]) == 0:
        await voice.stop()
        msg = await ctx.send(f'That was the last song so I left.')
        await voice.disconnect()
        await delete_msg(msg)
    else:
        msg = await ctx.send('Nothing is playing right now.')
        await msg.delete(delay=5)
@bot.command(aliases=['ps','PS','PAUSE'],case_sensitive=False)
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        msg = await ctx.send('Paused')
        await delete_msg(msg)
    else:
        msg = await ctx.send('Nothing is playing right now.')
        await delete_msg(msg)

@bot.command(aliases=['r','R','RESUME'],case_sensitive=False)
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        msg = await ctx.send('Resumed.')
        await delete_msg(msg)
    else:
        msg = await ctx.send('Nothing is paused right now.')
        await delete_msg(msg)

@bot.command(aliases=['l','L','LOOP'])
async def loop(ctx, query):
    await ctx.send('Not implemented yet ;\.')

#Helper functions for the commands:
async def join(ctx,channel):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected:
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    return voice

async def play_song(ctx,source,voice,id):
    ctx.voice_client.stop()
    if voice is not None:
        await voice.play(FFmpegPCMAudio(source,executable='C:/ffmpeg/bin/ffmpeg.exe', **FFMPEG_OPTS), after=lambda e: print('Player error: %s' % e) if e else after_song(ctx,voice,id))
def check_queue(ctx):
    id = ctx.guild.id
    voice = get(bot.voice_clients, guild=ctx.guild)
    if len(queues[id]) > 0:
        source = queues[id][0]['formats'][0]['url']
        asyncio.run_coroutine_threadsafe(play_song(ctx,source,voice,id), bot.loop)
    elif len(queues[id]) < 1 and queues[id] == [] and voice.is_playing() and voice.is_connected():
        msg = asyncio.run_coroutine_threadsafe(ctx.send('I left because the queue is empty.'),bot.loop)
        asyncio.run_coroutine_threadsafe(delete_msg(msg),bot.loop)
        asyncio.run_coroutine_threadsafe(voice.disconnect(),bot.loop)
    else:
        pass # No code needed here.    
    
def after_song(ctx,voice,id):
    queues[id].pop(0)
    if len(queues[id]) > 0:
        check_queue(ctx)
    else:
        asyncio.run_coroutine_threadsafe(disconnect(ctx,voice),bot.loop)
        
async def disconnect(ctx,voice):
    await voice.disconnect()
    msg = await ctx.send('I left because the queue is empty.')
    await delete_msg(msg)
async def delete_msg(message):
    await message.delete(delay=5)