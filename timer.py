from database import Database
from solarwinds import getGroupOptions, getNodeOptions, allNodeInfo, allGroupInfo
from dictionaries import nodes, groups
from thread import Semaphore
import time


class Timing():

	"""Class to maintain timing mechanisims in program"""
	
	@staticmethod
	def updatedEntityInformation(interval):
		
		"""Updated Groups and Nodes every minute"""
		while True:
			try:	
				groups = getGroupOptions()
				nodes = getNodeOptions()
			except:
				pass
			time.sleep(interval)