import discord, youtube_dl, subprocess, datetime, json, advancedtime, player, os

sys_loop = 1
command_prefix = os.getenv('BOT_PREFIX')
client = discord.Client(activity=discord.Game('Loading queue... | {}play | v2.3.9'.format(command_prefix)))
vcch = int(os.getenv('VCID'))
queuech = int(os.getenv('QUEUEID'))
reverse = advancedtime.fetchtime
now_date = advancedtime.checktime
now_month = advancedtime.checkmonth
color1 = 0x377EF0
color2 = 0xF8C63D
q = player.Queue()
first = ['Not Converted']
playlist = {}
ydl_opts = {
	'format': 'bestaudio/best',
	'outtmpl': "%(id)s" + '.%(ext)s',
	'ignoreerrors': True,
	'noplaylist': True,
	'quiet': True,
	'no-overwrite': True,
}

async def commands(command, message):
	arg = message.content.split(' ')[1:]
	if command == 'nowplaying':
		info = q.np1()[0]
		start = q.np2()
		start2 = q.np3()
		link = 'https://youtu.be/' + info['id']
		sendms = discord.Embed(title='Now Playing', colour=color1)
		sendms.add_field(name='Title', value='[{}]({})'.format(info['title'], link), inline=False)
		sendms.add_field(name='Uploader',value='[{}]({})'.format(info['uploader'],info['uploader_url']),inline=False)
		nowti = now_date('off', 9)
		nowpl = int(float(nowti - start))
		duration = info['duration']
		if nowpl > duration:
			nowpl = duration
		sendms.add_field(name='Time', value='{} / {}'.format(reverse(nowpl),reverse(info['duration'])),inline=False)
		sendms.add_field(name='Codec', value=info['streams'][0]['codec_long_name'], inline=False)
		sendms.add_field(name='Bitrate', value='{}kbps / {}'.format(str(int(info['format']['bit_rate'])/1000),  info['streams'][0]['channel_layout']), inline=False)
		sendms.add_field(name='Volume', value='{}%'.format(str(int(float(client.get_channel(vcch).guild.voice_client.source.volume)*100))), inline=False)
		sendms.add_field(name='Equalizer', value='Bass: x5.0 Truble: x9.0')
		sendms.set_thumbnail(url=str(info['thumbnails'][len(info['thumbnails']) - 1]['url']))
		sendms.set_footer(text='Started at {} | FireEqualizer from FFmpeg'.format(start2))
		await message.channel.send(embed=sendms)
	elif command == 'play':
		editms = await message.channel.send(':arrows_counterclockwise: **Searching...**')
		info = download(' '.join(arg))
		if info == 'Failed':
			await message.channel.send(':x: **No result**')
		else:
			sendms = discord.Embed(title='Successfully Added', colour=color1)
			link = 'https://youtu.be/' + info['id']
			sendms.add_field(name='Title', value='[{}]({})'.format(info['title'], link), inline=False)
			sendms.add_field(name='Uploader',value='[{}]({})'.format(info['uploader'],info['uploader_url']),inline=False)
			sendms.add_field(name='Duration', value=reverse(info['duration']))
			sendms.add_field(name='Codec', value=info['streams'][0]['codec_long_name'], inline=False)
			sendms.add_field(name='Bitrate', value='{}kbps / {}'.format(str(int(info['format']['bit_rate'])/1000),  info['streams'][0]['channel_layout']), inline=False)
			sendms.set_thumbnail(url=str(info['thumbnails'][len(info['thumbnails']) - 1]['url']))
			sendms.set_footer(text='Extracted from {} | FireEqualizer from FFmpeg'.format(info['extractor']))
			await editms.edit(content=None, embed=sendms)
			await save()
	elif command == 'skip':
		arg = message.content.split(' ')
		if len(arg) == 1:
			q.skip(1)
			await message.channel.send(':fast_forward: **Skipped**')
		else:
			if arg[1] == '1':
				q.skip(1)
				await message.channel.send(':fast_forward: **Skipped**')
			if int(arg[1]) > 1000000:
				await message.channel.send('**Sorry. I can\'t skip over 1000000 songs. Please use 1-1000000**')
			else:
				q.skip(int(arg[1]))
				await message.channel.send(':fast_forward: **{} songs skipped**'.format(arg[1]))
	elif command == 'remove':
		arg = message.content.split(' ')
		info = q.remove(int(arg[1]))
		if info == 'Failed':
			await message.channel.send(':x: **Failed : Invalid arg**')
			return
		await message.channel.send(':white_check_mark: **Removed**')
		await save()
	elif command == 'join':
	    await client.get_channel(vcch).connect()
	    await message.add_reaction('✅')
	    q.start()
	elif command == 'volume':
		if 0 <= int(arg[0]) <= 100:
			client.get_channel(vcch).guild.voice_client.source.volume = float(int(arg[0])/100)
			q.setvolume(float(arg[0])/100)
			await message.channel.send(':white_check_mark: **Successfully changed volume {}%**'.format(arg[0]))
		else:
			await message.channel.send(':x: **Please input between 0-100**')
	elif command == 'queue':
		queue = q.np1()
		queues = []
		queues.append('**Now Playing : [{}](https://youtu.be/{})**'.format(queue[0]['title'], queue[0]['id']))
		for n in range(1, len(queue)):
			queues.append('{}: [{}](https://youtu.be/{})'.format(n, queue[n]['title'], queue[n]['id']))
		sendms = discord.Embed(title='Queue', description='\n'.join(queues), colour=color2)
		await message.channel.send(embed=sendms)
	elif command == 'leave':
		await client.get_channel(vcch).guild.voice_client.disconnect()
		await message.add_reaction('✅')
	elif command == 'playlist':
		try:
			chid = await str(arg[1])
			try:
				if arg[2].startswith('clear'):
					q.clear()
					links = str(await create_queue(chid)).split('\n')
			except:
				links = str(await create_queue(chid)).split('\n')
			for n in range(len(links)):
				download(links[n])
		except:
			await message.channel.send('Sorry. Playlist {} can\'t found'.format(arg[1]))
	elif command == 'clear':
		q.clear()

@client.event
async def on_ready():
	print('Bot Started')
	if len(first) == 1:
		print('Loading queue...')
		links = str(await create_queue()).split('\n')
		for n in range(len(links)):
		    download(links[n])
		print('Loaded queue')
		first.append('Converted')
	q.seteq({'options': '-vn -af \"firequalizer=gain_entry=\'entry(0,6);entry(10,3);entry(30,-5);entry(2500,-5);entry(8000, 0);entry(9000,10);entry(22000,10)\'\"',})
	try:
		await client.get_channel(vcch).connect(timeout=3000, reconnect=3)
		q.set(client.get_channel(vcch).guild.voice_client)
	except:
		q.set(client.get_channel(vcch).guild.voice_client)
	q.start()
	await client.change_presence(activity=discord.Game('{}play | v2.3.9'.format(command_prefix)))

@client.event
async def on_message(message):
	if message.content.startswith(command_prefix):
		prefix = message.content[len(command_prefix):]
		start = prefix.split(' ')[0]
		print(start)
		try:
			if start == 'start':
				await commands('start', message)
			if start == 'clear':
				await commands('clear', message)
				return
			if start == 'c':
				await commands('clear', message)
				return
			if start == 'cl':
				await commands('clear', message)
				return
			if start == 'volume':
				await commands('volume', message)
				return
			if start == 'vol':
				await commands('volume', message)
				return
			if start == 'v':
				await commands('volume', message)
				return
			if start == 'q':
			    await commands('queue', message)
			    return
			if start == 'n':
			    await commands('nowplaying', message)
			    return
			if start == 'd':
			    await commands('remove', message)
			    return
			if start == 'del':
		   	 await commands('remove', message)
		   	 return
			if start == 'dc':
			    await commands('leave', message)
			    return
			if start == 'l':
			    await commands('leave', message)
			    return
			if start == 'p':
				await commands('play', message)
				return
			if start == 'join':
			   await commands('join', message)
			   return
			if start == 'r':
			   await commands('remove', message)
			   return
			if start == 's':
				await commands('skip', message)
				return
			if start == 'np':
				await commands('nowplaying', message)
				return
			if start == 'play':
				await commands('play', message)
				return
			if start == 's':
				await commands('skip', message)
				return
			if start == 'skip':
				await commands('skip', message)
				return
			if start == 'now':
				await commands('nowplaying', message)
				return
			if start == 'nowplaying':
				await commands('nowplaying', message)
				return
			if start == 'remove':
				await commands('remove', message)
				return
			if start == 'delete':
				await commands('remove', message)
				return
			if start == 'j':
				await commands('join', message)
				return
			if start == 'leave':
				await commands('leave', message)
				return
			if start == 'queue':
				await commands('queue', message)
				return
		except:
			await message.channel.send(':x: **Failed run command**')

async def create_queue():
	messages = await client.get_channel(queuech).history(limit=1).flatten()
	for message in messages:
		return message.content

async def np():
	data = q.np1()[0]
	duration = float(data['format']['duration'])
	await client.get_channel(782863961153339403).edit(topic='Title: {}\nUploader : {}\nDuration : {}\nCodec : {}\nBitrate : {}kbps / {}'.format(data['title'], data['uploader'], str(reverse(duration)), data['streams'][0]['codec_long_name'], str(int(data['format']['bit_rate'])/1000), data['streams'][0]['channel_layout']))

def finalize(info_dict):
	try:
		if os.path.isfile('{}.m4a'.format(info_dict['id'])):
			data = json.loads(subprocess.run("ffprobe -i {}.m4a -print_format json -show_streams  -show_format -loglevel quiet".format(info_dict['id']), stdout=subprocess.PIPE, shell=True).stdout)
			info_dict['format'] = data['format']
			info_dict['streams'] = data['streams']
			info_dict['path'] = info_dict['id'] + '.m4a'
			return info_dict
		else:
			data = json.loads(subprocess.run("ffprobe -i {}.webm -print_format json -show_streams  -show_format -loglevel quiet".format(info_dict['id']), stdout=subprocess.PIPE, shell=True).stdout)
			info_dict['format'] = data['format']
			info_dict['streams'] = data['streams']
			info_dict['path'] = info_dict['id'] + '.webm'
			return info_dict
	except:
		return 'Failed'
	
def download(value):
	for n in range(1, 3):
		try:
			import youtube_dl
			if value.startswith('https://'):
				info_dict = youtube_dl.YoutubeDL(ydl_opts).extract_info(value, download=True, process=True)
				finalize(info_dict)
			else:
				search = youtube_dl.YoutubeDL(ydl_opts).extract_info("ytsearch:{}".format(value), download=False, process=True)
				if not search:
					error = raiseerror
				else:
					download  =  youtube_dl.YoutubeDL(ydl_opts).extract_info('https://youtu.be/{}'.format(search['entries'][0]['id']), download=True, process=True)
					info_dict = finalize(download)
			if info_dict == 'Failed':
				error = raiseerror
			q.add(info_dict)
			return info_dict
		except:
			print('Retrying... ({})'.format(n))
	return 'Failed'

async def save():
	messages = await client.get_channel(queuech).history(limit=1).flatten()
	queues = []
	for n in range(len(q.np1())):
	    queues.append('https://youtu.be/{}'.format(q.np1()[n]['id']))
	for message in messages:
	    try:
	    	await message.edit(content='\n'.join(queues))
	    except:
	    	await message.channel.send(content='\n'.join(queues))

async def loadqueue():
	messages = await client.get_channel(787261880589746177).history(limit=1).flatten()
	for message in messages:
		return message.content

async def savequeue(value):
	messages = await client.get_channel(787261880589746177).history(limit=1).flatten()
	for message in messages:
	    try:
	    	await message.edit(content=value)
	    except:
	    	await message.channel.send(value)

client.run(os.getenv('DISCORD_TOKEN'))
