import discord, youtube_dl, subprocess, datetime, json, os, re

sys_loop = 1
sys_data = 772380469094252554
command_prefix = os.getenv('BOT_PREFIX')
client = discord.Client()
vcch = int(os.getenv('VCID'))
queuech = int(os.getenv('QUEUEID'))
#reverse = advancedtime.fetchtime
#now_date = advancedtime.checktime
#now_month = advancedtime.checkmonth
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
color1 = 0x377EF0
color2 = 0xF8C63D
first = ['Not Converted']
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': "%(id)s" + '.%(ext)s',
    'ignoreerrors': True,
    'noplaylist': True,
    'quiet': True,
    'no-overwrite': True,
}
ydl = youtube_dl.YoutubeDL(ydl_opts)

def time():
    return datetime.datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S.%f")
def timestamp():
    return datetime.datetime.utcnow().timestamp()

class Queue:
    def __init__(self):
        self.queue = []
        self._volume = 1
        self.skipped = False
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
    def nvol(self):
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
        self._voice.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.queue[0]['path'], **self.options), volume=self._volume), after=self.next)

q = Queue()

async def commands(command, message):
    arg = message.content.split(' ')[1:]


    if command == 'nowplaying':
        info = q.np1()[0]
        link = 'https://youtu.be/' + info['id']
        sendms = discord.Embed(title='Now Playing', colour=color1)
        sendms.add_field(name='Title', value='[{}]({})'.format(info['title'], link), inline=False)
        sendms.add_field(name='Uploader',value='[{}]({})'.format(info['uploader'],info['uploader_url']),inline=False)
        nowti = timestamp()
        nowpl = int(float(nowti - q.np3()))
        duration = info['duration']
        if nowpl > duration:
            nowpl = duration
        sendms.add_field(name='Time', value='{} / {}'.format(datetime.timedelta(seconds=int(nowpl)),datetime.timedelta(seconds=int(info['duration']))),inline=False)
        sendms.add_field(name='Codec', value=info['streams'][0]['codec_long_name'], inline=False)
        sendms.add_field(name='Bitrate', value='{}kbps / {}'.format(str(int(info['format']['bit_rate'])/1000),  info['streams'][0]['channel_layout']), inline=False)
        try:
            sendms.add_field(name='Volume', value='{}%'.format(str(int(float(client.get_channel(vcch).guild.voice_client.source.volume)*100))), inline=False)
        except:
            pass
        sendms.add_field(name='Equalizer', value='Bass: x{}'.format(q.np4()))
        sendms.set_thumbnail(url=str(info['thumbnails'][len(info['thumbnails']) - 1]['url']))
        sendms.set_footer(text='Started at {} | FireEqualizer from FFmpeg'.format(q.np2()))
        await message.channel.send(embed=sendms)


    elif command == 'play':
        editms = await message.channel.send(':arrows_counterclockwise: **Searching...**')
        info = download(' '.join(arg))
        if info == 'Failed':
            await message.channel.send(':x: **No result**')
        else:
            sendms = discord.Embed(title='Successfully Added', colour=color1)
            sendms.add_field(name='Title', value='[{}](https://youtu.be/{})'.format(info['title'], info['id']), inline=False)
            sendms.add_field(name='Uploader',value='[{}]({})'.format(info['uploader'],info['uploader_url']),inline=False)
            sendms.add_field(name='Duration', value=datetime.timedelta(seconds=int(info['duration'])))
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
                return
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
        await message.add_reaction('✅')
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


    elif command == 'bass':
        q.seteq({'options':'-reconnect 1 -vn -ac 2 -af \"firequalizer=gain_entry=\'entry(0,{});entry(50,0);entry(2500,0);entry(6300,0);entry(16000,5)\'\"'.format(arg[0]),})
        q.bass(arg[0])
        await message.add_reaction('✅')


    elif command == 'playlist':
        playlists = json.loads(await loaddata())
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
                    download(links[n])
                await message.add_reaction('✅')
            except:
                await message.channel.send('Sorry. Not found playlist {} '.format(arg[1]))
        else:
            queues = []
            for n in range(len(playlists[arg[0]])):
                queues.append(playlists[arg[0]][n])
            sendms = discord.Embed(title='Playlist : {}'.format(arg[0]), description='\n'.join(queues), colour=color2)
            await message.channel.send(embed=sendms)


    elif command == 'clear':
        q.clear()
        await message.add_reaction('✅')

@client.event
async def on_ready():
    print('Bot Started')
    if len(first) == 1:
        print('Loading queue...')
        messages = await client.get_channel(queuech).history(limit=1).flatten()
        for message in messages:
            links = str(message.content).split('\n')
        for n in range(len(links)):
            download(links[n])
        print('Loaded queue')
        first.append('Converted')
    q.seteq({'options': '-reconnect 1 -vn -ac 2 -af \"firequalizer=gain_entry=\'entry(0,4);entry(50,0);entry(2500,0);entry(6300,0);entry(16000,5)\'\"',})
    q.bass('4')
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
        print(start)
        if start == 'pl':
            await commands('playlist', message)
            return
        if start == 'playlist':
            await commands('playlist', message)
            return
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
            if start == 'bass':
                await commands('bass', message)
                return
            if start == 'b':
                await commands('bass', message)
                return
            if start == 'pl':
                await commands('playlist', message)
                return
            if start == 'playlist':
                await commands('playlist', message)
                return
        except:
            await message.channel.send(':x: **Failed run command**')

def finalize(info_dict):
    try:
	#result = requests.get('https://www.320youtube.com/v21/watch?v={}'.format(info_dict['id'])).text
	#info_dict['path'] = str(str(result).split('href=')[8])[1:].split('" rel')[0]
        for data in info_dict['formats']:
            if data['format_id'] == '251':
                info_dict['path'] = data['url']
        data = json.loads(subprocess.run("ffprobe -i \"{}\" -print_format json -show_streams  -show_format -loglevel quiet".format(info_dict['path']), stdout=subprocess.PIPE, shell=True).stdout)
        info_dict['format'] = data['format']
        info_dict['streams'] = data['streams']
        return info_dict
    except:
        return 'Failed'

def download(value):
    for n in range(1, 3):
        try:
            if value.startswith('https://'):
                info_dict = ydl.extract_info(value, download=False, process=False)
                finalize(info_dict)
            else:
                search = ydl.extract_info("ytsearch:{}".format(value), download=False, process=True)
                if not search:
                    raise DLError
                else:
                    download  =  ydl.extract_info('https://youtu.be/{}'.format(search['entries'][0]['id']), download=False, process=False)
                    info_dict = finalize(download)
                    if info_dict == 'Failed':
                        raise DLError
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

async def loaddata():
    messages = await client.get_channel(sys_data).history(limit=1).flatten()
    for message in messages:
        return message.content

async def savedata(value):
    messages = await client.get_channel(sys_data).history(limit=1).flatten()
    for message in messages:
        try:
            await message.edit(content=json.dumps(value))
        except:
            await message.channel.send(json.dumps(value))

client.run(os.getenv('DISCORD_TOKEN'))
