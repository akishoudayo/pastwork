import discord, advancedtime, random
now_date = advancedtime.checktime

class Queue:
	def __init__(self):
		self.queue = []
		self._volume = 0.1
		self.skipped = False
	def add(self, value):
		self.queue.append(value)
		try:
			self.start()
		except:
			self.np = True
	def seteq(self, value):		
		self.options = value
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
		self._start = now_date('off', 9)
		self._start2 = now_date('on', 9)
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
			self._start = now_date('off', 9)
			self._start2 = now_date('on', 9)
			self.skipped = False
			self.play()
			return
		if len(self.queue) == 1:
			self._start = now_date('off', 9)
			self._start2 = now_date('on', 9)
			self.play()
			return
		self.played = self.queue[0]
		self.queue = self.queue[1:]
		self.queue.append(self.played)
		self._start = now_date('off', 9)
		self._start2 = now_date('on', 9)
		self.play()
	def np1(self):
		return self.queue
	def np2(self):
	    return self._start
	def np3(self):
		return self._start2
	def nvol(self):
		return self._volume
	def skip(self, value):
		if not self.queue:
			return
		self.skipped = True
		if len(self.queue) == 1:
			self._start = now_date('off', 9)
			self._start2 = now_date('on', 9)
			self.stop()
		if value == 1:
			self.played = self.queue[0]
			self.queue = self.queue[1:]
			self._start = now_date('off', 9)
			self._start2 = now_date('on', 9)
			self.queue.append(self.played)
			self.stop()
		else:
			for n in range(value):
				self.played = self.queue[0]
				self.queue = self.queue[1:]
				self.queue.append(self.played)
			self._start = now_date('off', 9)
			self._start2 = now_date('on', 9)
			self.stop()
	def stop(self):
		self._voice.stop()
	def setvolume(self, value):
		self._volume = value
	def play(self):
		self._voice.play(discord.FFmpegOpusAudio(self.queue[0]['path'], **self.options, bitrate=256), after=self.next)
