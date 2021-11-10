import logging, discord, datetime
from json import loads as json_loads
from json import dumps as json_dumps
from youtube_dl import YoutubeDL
from subprocess import run as subprocess_run
from subprocess import PIPE
from requests import get
from os import getenv, path, rename, remove

class Queue:
    def __init__(self):
        self.queue = []
        self._volume = 1
        self.skipped = False
        self.bitrate = 200
        self.conv = False
    def add(self, value):
        self.queue.append(value)
        try:
            self.start()
        except:
            self.np = True
    def seteq(self, value):		
        self.options = value
    def bass(self, value):
        self._bass = value
    def shuffle(self):
        random.shuffle(self.queue)
    def remove(self, value):
        try:
            del self.queue[int(value)]
            return 'Done'
        except:
            return 'Failed'
    def start(self):
        if not self.queue:
            return
        self._start = time()
        self._start2 = timestamp()
        self.play()
    def set(self, value):
        self._voice = value
    def clear(self):
        self.queue.clear()
    def next(self, error):
        if not self.queue:
            return
        if not self._voice:
            return
        try:
            self.stop()
        except:
            print('Stop Failed : Not Playing')
        if self.skipped == True:
            self._start = time()
            self._start2 = timestamp()
            self.skipped = False
            self.play()
            return
        if len(self.queue) == 1:
            self._start = time()
            self._start2 = timestamp()
            self.play()
            return
        self.played = self.queue[0]
        self.queue = self.queue[1:]
        self.queue.append(self.played)
        self._start = time()
        self._start2 = timestamp()
        self.play()
    def np1(self):
        return self.queue
    def np2(self):
        return self._start
    def np3(self):
        return self._start2
    def np4(self):
        return self._bass
    def vol(self):
        return self._volume
    def skip(self, value):
        if not self.queue:
            return
        self.skipped = True
        if len(self.queue) == 1:
            self._start = time()
            self._start2 = timestamp()
            self.stop()
        if value == 1:
            self.played = self.queue[0]
            self.queue = self.queue[1:]
            self._start = time()
            self._start2 = timestamp()
            self.queue.append(self.played)
            self.stop()
        else:
            for n in range(value):
                self.played = self.queue[0]
                self.queue = self.queue[1:]
                self.queue.append(self.played)
                self._start = time()
                self._start2 = timestamp()
                self.stop()
    def stop(self):
        self._voice.stop()
    def setvolume(self, value):
        self._volume = value
    def play(self):
        try:
            test = get(self.queue[0]['url'], timeout=0.5).status_code
        except:
        	test = 200
        if test != 403:
        	if self.queue[0]['streams'][0]['codec_name'] == 'opus':
        		self._voice.play(discord.FFmpegOpusAudio(self.queue[0]['url'], **self.options), after=self.next)
        	else:
        		self._voice.play(discord.FFmpegPCMAudio(self.queue[0]['url'], **self.options), after=self.next)
        else:
        	self.queue[0] = download(self.queue[0]['webpage_url'])
        	if self.queue[0]['streams'][0]['codec_name'] == 'opus':
        		self._voice.play(discord.FFmpegOpusAudio(self.queue[0]['url'], **self.options), after=self.next)
        	else:
        		self._voice.play(discord.FFmpegPCMAudio(self.queue[0]['url'], **self.options), after=self.next)

q = Queue()
sys_loop = 1
sys_data = 772380469094252554
cache_data = 793030006221307915
command_prefix = 'z.'
client = discord.Client(timeout=5)
vcch = 890507102529941525
queuech = 890498594015150121
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
color1 = 0x377EF0
color2 = 0xF8C63D
debug = False
if debug == True:
    quiet = False
else:
    quiet = True
first = ['Not Converted']
ydl = YoutubeDL({'cookiefile': 'cookies.txt', 'format': 'bestaudio/best', 'outtmpl': "cache/" + "%(id)s" + '.%(ext)s', 'ignoreerrors': True, 'noplaylist': True, 'quiet': True, 'no-overwrite': True, 'retries': 3, 'geo_bypass': True, 'noprogress': True, 'default_search': 'auto'})
def setup():
	import logging
	logging.addLevelName(1, 'INFO')
	logging.addLevelName(2, 'WARNING')
	logging.addLevelName(3, 'DEBUG')
	logging.addLevelName(4, 'ERROR')
	log = logging.getLogger()
	logging.basicConfig(format='[{asctime}] [{levelname}] : {message}', datefmt="%H:%M:%S",style='{')
	log.setLevel('INFO')
	logging.getLogger("discord").setLevel(logging.ERROR)
	logging.getLogger("urllib3").setLevel(logging.WARNING)
	return log
logger = setup()
if debug == True:
    logger.log(3, 'Module Loaded')

async def commands(command, message):
    arg = message.content.split(' ')[1:]
    #-----------------------------------------------------------#
    if command == 'nowplaying':
        info = q.np1()[0]
        sendms = discord.Embed(title='Now Playing', colour=color1, timestamp=datetime.datetime.now())
        if info['extractor_key'] == 'Generic':
            try:
                sendms.add_field(name='Title', value='[{}]({})'.format(info['format']['tags']['title'], info['url']), inline=False)
            except:
                sendms.add_field(name='Title', value='[{}]({})'.format(' '.join(info['format']['filename'].split('/')[len(info['format']['filename'].split('/'))-1:]), info['url']), inline=False)
        else:
            sendms.add_field(name='Title', value='[{}]({})'.format(info['title'], info['link']), inline=False)
        if info['extractor_key'] == 'Generic':
            try:
                sendms.add_field(name='Artist', value='{}'.format(info['format']['tags']['artist']), inline=False)
            except:
                pass
        else:
            sendms.add_field(name='Uploader',value='[{}]({})'.format(info['uploader'], info['uploader_url']),inline=False)
        temp = float(info['format']['duration'])
        duration = timestamp() - q.np3()
        if duration > temp:
        	duration = temp
        sendms.add_field(name='Time', value='{} / {}'.format(datetime.timedelta(seconds=int(duration)), datetime.timedelta(seconds=int(temp)),inline=False))
        sendms.add_field(name='Codec', value=info['streams'][0]['codec_long_name'], inline=False)
        sendms.add_field(name='Bitrate', value='{}kbps / {}'.format(str(int(info['format']['bit_rate'])/1000),  str(info['streams'][0]['channel_layout']).capitalize()), inline=False)
        try:
            sendms.add_field(name='Volume', value='{}%'.format(str(int(float(client.get_channel(vcch).guild.voice_client.source.volume)*100))), inline=False)
        except:
            pass
        sendms.add_field(name='Equalizer', value='Bass: {}db'.format(q.np4()), inline=False)
        sendms.add_field(name='Channel', value='<#{}>'.format(client.get_channel(vcch).guild.voice_client.channel.id), inline=False)
        try:
            sendms.set_thumbnail(url=str(info['thumbnails'][len(info['thumbnails']) - 1]['url']))
        except:
            pass
        sendms.set_footer(text='Extracted from {}'.format(info['extractor']))
        await message.channel.send(embed=sendms)
    #-----------------------------------------------------------#
    elif command == 'play':
        editms = await message.channel.send(':arrows_counterclockwise: **Searching...**')
        info = download(' '.join(arg))
        if info['extractor_key'] == 'Generic':
        	info = await albumart(info)
        if not info:
            await editms.edit(content=':x: **No Result**')
            return
        q.add(info)
        sendms = discord.Embed(title='Successfully Added', colour=color1)  
        if info['extractor_key'] == 'Generic':
            try:
                sendms.add_field(name='Title', value='[{}]({})'.format(info['format']['tags']['title'], info['url']), inline=False)
            except:
                sendms.add_field(name='Title', value='[{}]({})'.format(' '.join(info['format']['filename'].split('/')[len(info['format']['filename'].split('/'))-1:]), info['url']), inline=False)
        else:
            sendms.add_field(name='Title', value='[{}]({})'.format(info['title'], info['link']), inline=False)
        if info['extractor_key'] == 'Generic':
            try:
                sendms.add_field(name='Artist', value='{}'.format(info['format']['tags']['artist']), inline=False)
            except:
                pass
        else:
            sendms.add_field(name='Uploader',value='[{}]({})'.format(info['uploader'], info['uploader_url']),inline=False)
        sendms.add_field(name='Duration', value=datetime.timedelta(seconds=int(float(info['format']['duration']))))
        sendms.add_field(name='Codec', value=info['streams'][0]['codec_long_name'], inline=False)
        sendms.add_field(name='Bitrate', value='{}kbps / {}'.format(str(int(info['format']['bit_rate'])/1000),  str(info['streams'][0]['channel_layout']).capitalize()), inline=False)
        try:
            sendms.set_thumbnail(url=str(info['thumbnails'][len(info['thumbnails']) - 1]['url']))
        except:
            pass
        sendms.set_footer(text='Extracted from {}'.format(info['extractor']))
        await editms.edit(content=None, embed=sendms)
        await save()
    #-----------------------------------------------------------#
    elif command == 'skip':
        arg = message.content.split(' ')
        if len(arg) == 1:
            q.skip(1)
            await message.channel.send(':fast_forward: **Skipped**')
        else:
            if arg[1] == '1':
                q.skip(1)
                await message.channel.send(':fast_forward: **Skipped**')
                return
            if int(arg[1]) > 1000000:
                await message.channel.send('**Sorry. I can\'t skip over 1000000 songs. Please use 1-1000000**')
            else:
                q.skip(int(arg[1]))
                await message.channel.send(':fast_forward: **{} songs skipped**'.format(arg[1]))
    #-----------------------------------------------------------#
    elif command == 'remove':
        arg = message.content.split(' ')
        info = q.remove(int(arg[1]))
        if info == 'Failed':
            await message.channel.send(':x: **Failed : Invalid arg**')
            return
        await message.add_reaction('✅')
        await save()
    #-----------------------------------------------------------#
    elif command == 'join':
        await client.get_channel(vcch).connect()
        await message.add_reaction('✅')
        q.set(client.get_channel(vcch).guild.voice_client)
        q.start()
    #-----------------------------------------------------------#
    elif command == 'shuffle':
        q.shuffle()
        await message.add_reaction('✅')
    #-----------------------------------------------------------#
    elif command == 'volume':
	     try:
	            if 0 <= int(arg[0]) <= 100:
	            	client.get_channel(vcch).guild.voice_client.source.volume = float(int(arg[0])/100)
	            	q.setvolume(float(arg[0])/100)
	            	await message.add_reaction('✅')
	            else:
	            	await message.channel.send(':x: **Please input between 0-100**')
	     except:
	     	await message.channel.send(':x: **Please input int values**')
    #-----------------------------------------------------------#
    elif command == 'queue':
        queue = q.np1()
        queues = []
        if queue[0]['extractor_key'] == 'Generic':
            try:
                queues.append('**Now Playing : [{}]({})**'.format(queue[0]['format']['tags']['title'], queue[0]['url']))
            except:
                queues.append('**Now Playing : [{}]({})**'.format(' '.join(queue[0]['format']['filename'].split('/')[len(queue[0]['format']['filename'].split('/'))-1:]), queue[0]['url']))
        else:
            queues.append('**Now Playing : [{}](https://youtu.be/{})**'.format(queue[0]['title'], queue[0]['id']))
        for n in range(1, len(queue)):
            if queue[n]['extractor_key'] == 'Generic':
                try:
                    queues.append('**{} : [{}]({})**'.format(n, queue[n]['format']['tags']['title'], queue[n]['url']))
                except:
                	queues.append('**{} : [{}]({})**'.format(n, ' '.join(queue[n]['format']['filename'].split('/')[len(queue[n]['format']['filename'].split('/'))-1:]), queue[n]['url']))
            else:
                queues.append('**{} : [{}](https://youtu.be/{})**'.format(n, queue[n]['title'], queue[n]['id']))
        sendms = discord.Embed(title='Queue', description='\n'.join(queues), colour=color2)
        await message.channel.send(embed=sendms)
    #-----------------------------------------------------------#
    elif command == 'leave':
        await client.get_channel(vcch).guild.voice_client.disconnect()
        await message.add_reaction('✅')
    #-----------------------------------------------------------#
    elif command == 'bass':
        try:
            if str(float(arg[0])) == arg[0]:
             	q.seteq({'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 20', 'options':'-hls_allow_cache allowcache -read_ahead_limit -1 -segment_list_flags cache -buffer_size -1 -vn -ac 2 -af \"firequalizer=gain_entry=\'entry(50,{});entry(500,0);entry(6300,0);entry(16000,2);entry(22000,2)\'\"'.format(arg[0]),})
             	q.bass(arg[0])
             	await message.add_reaction('✅')
             	return
            if str(int(arg[0])) == arg[0]:
             	q.seteq({'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 20', 'options':'-hls_allow_cache allowcache -read_ahead_limit -1 -segment_list_flags cache -buffer_size -1 -vn -ac 2 -af \"firequalizer=gain_entry=\'entry(50,{});entry(500,0);entry(6300,0);entry(16000,2);entry(22000,2)\'\"'.format(arg[0]),})
             	q.bass(arg[0])
             	await message.add_reaction('✅')
             	return
        except:
        	await message.channel.send(':x: **Please input float values**')
    #-----------------------------------------------------------#
    elif command == 'playlist':
        playlists = json_loads(await loaddata())
        if arg[0] == 'delete':
            try:
                del playlists[arg[1]]
                await message.add_reaction('✅')
                await savedata(playlists)
            except:
                await message.channel.send('Failed. {}playlist delete <name>'.format(command_prefix))		
        elif arg[0] == 'remove':
            try:
                del playlists[arg[1]][int(arg[2])]
                await message.add_reaction('✅')
                await savedata(playlists)
            except:
                await message.channel.send('Failed. {}playlist remove <name> <number>'.format(command_prefix))
        elif arg[0] == 'create':
            if len(arg[1:]) == 1:
                name = arg[1]
            else:
                name = ' '.join(arg[1:])
            if name.find(' ') != -1:
                name = re.sub(' ', '-', name)
                await message.channel.send('Found some spaces in name. replaced \"-\"')
            try:
                check = playlists[name]
                await message.channel.send('Already Created!')
            except:
                playlists[name] = []
                await savedata(playlists)
                await message.add_reaction('✅')
        elif arg[0] == 'add':
            try:
                playlists[arg[1]].append(' '.join(arg[2:]))
                await message.add_reaction('✅')
                await savedata(playlists)
            except:
                await message.channel.send('Not found playlist {}'.format(arg[1]))
        elif arg[0] == 'load':
            try:
                links = playlists[arg[1]]
                for n in range(len(links)):
                    await download(links[n])
                await message.add_reaction('✅')
            except:
                await message.channel.send('Sorry. Not found playlist {} '.format(arg[1]))
        else:
            queues = []
            for n in range(len(playlists[arg[0]])):
                queues.append(playlists[arg[0]][n])
            sendms = discord.Embed(title='Playlist : {}'.format(arg[0]), description='\n'.join(queues), colour=color2)
            await message.channel.send(embed=sendms)
    #-----------------------------------------------------------#
    elif command == 'clear':
        q.clear()
        await message.add_reaction('✅')

@client.event
async def on_ready():
    logger.log(1, 'Bot Started')
    if len(first) == 1:
        logger.log(1, 'Loading Queue...')
        messages = await client.get_channel(queuech).history(limit=1).flatten()
        for message in messages:
            links = str(message.content).split('\n')
        for n in range(len(links)):
            logger.log(1, 'Downloading {}'.format(str(n+1)))
            info = download(links[n])
            if info['extractor_key'] == 'Generic':
            	info = await albumart(info)
            if not info:
            	pass
            else:
            	q.add(info)
        first.append('Converted')
    q.seteq({'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 20', 'options': ' -vn -hls_allow_cache allowcache -read_ahead_limit -1 -segment_list_flags cache -buffer_size -1 -ac 2 -af \"firequalizer=gain_entry=\'entry(50,0);entry(500,0);entry(6300,0);entry(16000,5);entry(22000,5)\'\"',})
    q.bass('0')
    logger.log(1, 'Loaded Queue')
    try:
        await client.get_channel(vcch).connect()
        q.set(client.get_channel(vcch).guild.voice_client)
    except:
        q.set(client.get_channel(vcch).guild.voice_client)
    q.start()

@client.event
async def on_message(message):
	if message.content.startswith(command_prefix):
		prefix = message.content[len(command_prefix):]
		start = prefix.split(' ')[0]
		try:
			if start == 'stop':
				sys.exit()
			if start == 'sh':
				await commands('shuffle', message)
				return
			if start == 'shuffle':
				await commands('shuffle', message)
				return
			if start == 'start':
				await commands('start', message)
				return
			if start == 'pl':
				await commands('playlist', message)
				return
			if start == 'playlist':
				await commands('playlist', message)
				return
			if start == 'clear':
				await commands('clear', message)
				return
			if start == 'c':
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
			if start == 'bass':
				await commands('bass', message)
				return
			if start == 'b':
				await commands('bass', message)
				return
		except Exception as e:
			await message.channel.send(':x: **Failed run command** ({})'.format(e))

def time():
    temp = datetime.datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S.%f")
    return temp

def timestamp():
    temp = datetime.datetime.utcnow().timestamp()
    return temp

async def albumart(data):
    try:
    	subprocess_run("ffmpeg -i \"{}\" -loglevel quiet cache/cover.png".format(data['url']), stdout=PIPE, shell=True)
    	thumburl = await client.get_channel(cache_data).send(file=discord.File('cache/cover.png'))
    	data['thumbnails'] = []
    	data['thumbnails'].append({'url': thumburl.attachments[0].url})
    	remove('cache/cover.png')
    except:
    	logger.log(2, 'Album Art Not Found.')
    return data

def finalize(data):
    try:
    	if data['extractor_key'] == 'Bandcamp':
    		data['link'] = data['webpage_url']
    		data['uploader_url'] = '/'.join(data['webpage_url'].split('/')[:len(data['webpage_url'].split('/'))-2])
    	if data['extractor_key'] == 'Soundcloud':
    		data['extractor'] = 'SoundCloud'
    		data['link'] = data['webpage_url']
    	if data['extractor_key'] == 'Generic':
    		data['extractor'] = 'Direct File'
    		data['link'] = data['url']
    	if data['extractor_key'] == 'Youtube':
    		data['extractor'] = 'YouTube'
    		data['link'] = 'https://youtu.be/' + data['id']
    	info = json_loads(subprocess_run("ffprobe -i \"{}\" -print_format json -show_streams  -show_format -loglevel quiet".format(data['url']), stdout=PIPE, shell=True).stdout)
    	data['format'] = info['format']
    	data['streams'] = info['streams']
    	return data
    except Exception as e:
    	logger.log(4, e)
    	return

def download(value):
    for n in range(1, 3):
        try:
            temp = ydl.extract_info(value, download=False, process=True)
            try:
            	data = temp['entries'][0]
            except:
            	data = temp
            if not data:
                raise Exception('Search Failed')
            data = finalize(data)
            if not data:
            	raise Exception('Finalize Failed')
            return data
        except Exception as e:
            logger.log(2, 'Retrying... ({})'.format(e))
    return

async def save():
    messages = await client.get_channel(queuech).history(limit=1).flatten()
    queues = []
    for n in range(len(q.np1())):
        if q.np1()[n]['extractor_key'] == 'Generic':
            queues.append(q.np1()[n]['url'])
        else:
            queues.append(q.np1()[n]['webpage_url'])
    for message in messages:
        try:
            await message.edit(content='\n'.join(queues))
        except:
            await message.channel.send(content='\n'.join(queues))

async def loaddata():
    messages = await client.get_channel(sys_data).history(limit=1).flatten()
    for message in messages:
        return message.content

async def savedata(value):
    messages = await client.get_channel(sys_data).history(limit=1).flatten()
    for message in messages:
        try:
            await message.edit(content=json_dumps(value))
        except:
            await message.channel.send(json_dumps(value))


client.run(getenv('DISCORD_TOKEN'))
