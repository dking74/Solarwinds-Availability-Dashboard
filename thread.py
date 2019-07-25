import threading

class Thread(threading.Thread):
	"""Class to manage thread for application"""

	def __init__(self, function, *args, **kwargs):
		threading.Thread.__init__(self, target=lambda: function(*args, **kwargs))
		self.function = function
		self.args = args
		self.kwargs = kwargs
		self.is_running = False
		self.startThread()

	def __repr__ ( self ):
		
		"""Get high-level repr of object"""
		return "Thread('{}')".format(function.__name__)

	def startThread ( self ):
		
		"""If the thread isn't currently running, setup timer and start"""
		if not self.is_running:
			self.is_running = True
			self.start()

	def stopThread ( self ):
		
		"""Stop the thread from running"""
		if self.is_running:
			self.is_running = False

	def joinThread(self, timeout=None):
		self.join(timeout=timeout)