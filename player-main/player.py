import env
from asyncio import sleep
from discord import  FFmpegOpusAudio, FFmpegPCMAudio, Embed, Intents
from discord.ext.commands import Bot
import psutil
from os import getenv
from youtube_dl import YoutubeDL
from requests import post as rpost
from threading import Thread
from wsgiref import simple_server
from flask import Flask, request

class Bot(Bot):
	def __init__(self):
		super().__init__(intents=Intents.all(), command_prefix='wjwjjsndndjdjjdd')
		self.app = Flask(__name__, static_folder='.', static_url_path='')
		self.channels = []
	
	def webrun(self):
		bot = self
		class customlog(simple_server.WSGIRequestHandler):
			def log_message(self, format, *args):
				print( "%s > %s" %(self.client_address[0],format%args))
		server = simple_server.make_server('0.0.0.0', int(getenv('PORT', 9000)), self.app, handler_class=customlog)
		server.serve_forever()
	def webstart(self):
		Thread(target=self.webrun).start()
	
	def web(self):
		app = self.app
		@app.route("/")
		def main():
			return 'Database'
	
	async def on_ready(self):
		print('Logged In')
		self.web()
		self.webstart()
		while True:
			for ch in self.channels:
				if self.get_channel(ch).guild.voice_client == None:
					self.channels.remove(ch)
				try:
					if self.get_channel(ch).guild.voice_client.is_playing() == False:
						await self.get_channel(887420575914545193).send('c.ended {}'.format(ch))
						self.channels.remove(ch)
				except:
					pass
			await sleep(0.5)

	async def on_message(self, message):
		if message.content.startswith(getenv('UUID', 'test')):
			arg = message.content.split(' ')[1:]
			start = arg[0]
			if start == 'play':
				voice_id = int(arg[1])
				guild_id = int(arg[2])
				opus = arg[3]
				low = arg[4]
				high = arg[5]
				bitrate = int(arg[6])
				ss = arg[7]
				volume = arg[8]
				link = str(arg[9])
				try:
					if self.get_guild(guild_id).voice_client == None:
						try:
							await self.get_channel(voice_id).connect()
						except:
							return
					if self.get_guild(guild_id).voice_client.is_playing() == True:
						self.get_guild(guild_id).voice_client.stop()
					if opus == 'True':
						self.get_guild(guild_id).voice_client.play(FFmpegOpusAudio(link, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 20', options='-vn -ac 2 -ss {0} -af \"volume={1}dB, firequalizer=gain_entry=\'entry(50,{2});entry(500,0);entry(6300,0);entry(16000,{3});entry(22000,{3})\'\"'.format(ss, volume, low, high), bitrate=bitrate))
					else:
						self.get_guild(guild_id).voice_client.play(FFmpegPCMAudio(link, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 20', options='-vn -ac 2 -ss {0} -af \"volume={1}dB,firequalizer=gain_entry=\'entry(50,{2});entry(500,0);entry(6300,0);entry(16000,{3});entry(22000,{3})\'\"'.format(ss, volume, low, high)))
					await sleep(1)
					if self.get_guild(guild_id).voice_client.is_playing() == True:
						await self.get_channel(887420575914545193).send('c.start {}'.format(guild_id))
						self.channels.append(voice_id)
				except Exception as e:
					print(e)
			elif start == 'skip':
				guild_id = int(arg[1])
				self.get_guild(guild_id).voice_client.stop()
			elif start == 'leave':
				guild_id = int(arg[1])
				await self.get_guild(guild_id).voice_client.disconnect()
		if message.content == 'player':
			if message.author.id == 749013126866927713:
				sendms = Embed(title="Status (Player)", colour=0x7ED6DE)
				response = rpost('https://discord.com/api/', timeout=3)
				sendms.add_field(name='API', value='{:.2f}ms'.format(float(response.elapsed.total_seconds())*1000), inline=False)
				sendms.add_field(name="Client", value='{:.2f}ms'.format(self.latency*1000), inline=False)
				sendms.add_field(name='CPU', value='{}%, {}C{}T, {:.2f}MHz'.format(psutil.cpu_percent(), str(psutil.cpu_count(logical=False)), str(psutil.cpu_count()), psutil.cpu_freq().current), inline=False)
				sendms.add_field(name='Memory Usage', value='{:.1f}/{:.1f}GB ({}%)'.format(psutil.virtual_memory().used/1073741824, psutil.virtual_memory().total/1073741824, psutil.virtual_memory().percent), inline=False)
				sendms.add_field(name='Working Count', value='{}'.format(len(channels)), inline=False)
				sendms.add_field(name='Bot ID', value=getenv('UUID'), inline=False)
				sendms.set_footer(text='Powered by Heroku')
				await message.channel.send(embed=sendms)
		if message.content == 'process':
			if message.author.id == self.user.id:
				await message.channel.send('c.set {}'.format(getenv('UUID', 'test')))
			if message.author.id == 749013126866927713:
				await message.channel.send('c.set {}'.format(getenv('UUID', 'test')))

if __name__ == "__main__":
	bot = Bot()
	bot.run(env.token)