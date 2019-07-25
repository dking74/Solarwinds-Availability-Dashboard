from orionsdk import SwisClient
from exceptions import *
import ssl
from configuration import USERNAME, PASSWORD
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Solarwinds(SwisClient):
	
	"""
		Class Name: Solarwinds
		Class Purpose: To manage Solarwinds objects
	"""
	
	def __init__(self, domain, username, password):
		
		"""
			Method Name: __init__
			Method Purpose: To create a Solarwinds instance
			
			Parameters:
				- domain (string): The domain name for the solarwinds instance
				- username (string): The username logging in
				- password (string): The password for the user
			Returns: None
		"""
		
		ssl._create_default_https_context = ssl.create_default_context
		super().__init__ (domain, username, password)
		self._username = username
		self._password = password
		self.__testSolarLogin()
				
	def __testSolarLogin ( self ):
		"""This is a simple function to query and make sure that
		   the right credentials are in play; should not be used otherwise"""
		
		try:
			testConnection = self.query("SELECT AccountID FROM Orion.Accounts")
		except (OSError, Exception):
			raise BadLoginInformation ( self._username, self._password )
			
class SolarNode():

	"""
		Class Name: SolarNode
		Class Purpose: To manage Solarwinds Node
	"""
	
	def __init__(self, loginInstance, node=""):
		self._solar = loginInstance
		self._node = node
		self._interfaces = ()
		if node != "":
			self._interfaces = self._getInterfaces(node)
			
		self.customQuery = self._solar.query
		
	def setNode(self, nodeName):
		"""Set what the node name to query on is"""
	
		self._node = nodeName
		
	def _getInterfaces(self, nodeName):
		"""Gets all the interface names for the node"""
	
		result = self._solar.query(
				"""
				SELECT
					n.Interfaces.InterfaceCaption
				FROM
					Orion.Nodes n
				WHERE
					n.Caption='{}'
				""".format(nodeName)
			)
		
		interfaces = []
		for result in result['results']:
			interfaces.append(result['InterfaceCaption'])
		interfaces = tuple(interfaces)
		return interfaces
	
	def getNode(self):
		"""Gets the node name"""
		
		return self._node
	
	def getInterfaces(self):
		"""Gets all the interfaces for the user"""
		
		return self._interfaces
		
	def getAllNodes(self):
		"""Get all the nodes from system"""
		
		nodes = self._solar.query(
					"""
					SELECT
						n.Caption
					FROM
						Orion.Nodes n
					ORDER BY
						n.Caption
					"""
				)
		return nodes
		
	def getNodesByGroup(self, groupName):
		"""Get all the nodes by the group name"""
		
		nodes = self._solar.query(
					"""
					SELECT
						g.Members.Name as Caption
					FROM
						Orion.Container g
					WHERE
						g.Members.MemberEntityType='Orion.Nodes' AND
						g.Name LIKE '{}%'
					""".format(groupName)
				)
		return nodes
		
	def getNodesByStart(self, startNode):
		"""Get all the nodes based on beginning of string"""
		
		nodes = self._solar.query(
					"""
					SELECT
						n.Caption as Caption
					FROM
						Orion.Nodes n
					WHERE
						n.Caption LIKE '{}%'
					""".format(startNode)
				)
		return nodes
		
	def getNodesByIP(self, ip):
		"""Get all the nodes by the IP address"""
		
		nodes = self._solar.query(
					"""
					SELECT
						n.Caption
					FROM
						Orion.Nodes n
					WHERE
						n.IPAddress LIKE '{}%'
					ORDER BY
						n.Caption
					""".format(ip)
				)
		return nodes
		
	def getNodeAvailability(self, days):
		"""Get all the availability numbers from set days"""
		
		result = self._solar.query(   
				"""
				SELECT
					Year    ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Year,
					Month   ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Month,
					Day     ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Day,
					Hour    ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Hour,
					Minute  ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Minute,
					Second  ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Second,
					WeekDay ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as WeekDay,
					r.ResponseTimeHistory.Availability as Data,
					Tolocal(r.ResponseTimeHistory.DateTime) as CurrentDate
				FROM
					Orion.Nodes r
				WHERE 
					r.Caption='{}' AND
					DayDiff ( Tolocal ( r.ResponseTimeHistory.DateTime ) , GetDate ( ) ) < {}
				ORDER BY
					r.ResponseTimeHistory.DateTime
				""".format(self._node, days)
		)
		return result

	def getNodeAvailabilityCached(self, old_date):
		"""Get all availability data from last date"""
		
		result = self._solar.query(
				"""
				SELECT
					Year    ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Year,
					Month   ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Month,
					Day     ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Day,
					Hour    ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Hour,
					Minute  ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Minute,
					Second  ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as Second,
					WeekDay ( Tolocal ( r.ResponseTimeHistory.DateTime ) ) as WeekDay,
					r.ResponseTimeHistory.Availability as Data,
					Tolocal ( r.ResponseTimeHistory.DateTime ) as CurrentDate
				FROM
					Orion.Nodes r
				WHERE 
					r.Caption='{}' AND
					Tolocal ( r.ResponseTimeHistory.DateTime ) >= DateTime('{}')
				ORDER BY
					r.ResponseTimeHistory.DateTime
				""".format(self._node, old_date)
		)
		return result
		
	def getNodeCPULoad(self, days):
		"""Get the average cpu load for set days"""
		
		result = self._solar.query(
				"""
				SELECT
					Year    ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Year,
					Month   ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Month,
					Day     ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Day,
					Hour    ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Hour,
					Minute  ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Minute,
					Second  ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Second,
					WeekDay ( Tolocal ( r.CPULoadHistory.DateTime ) ) as WeekDay,
					r.CPULoadHistory.AvgLoad as Data,
					Tolocal(r.CPULoadHistory.DateTime) as CurrentDate
				FROM
					Orion.Nodes r
				WHERE 
					r.Caption='{}' AND
					DayDiff ( Tolocal (r.CPULoadHistory.DateTime ) , GetDate ( ) ) < {}
				ORDER BY
					r.CPULoadHistory.DateTime
				""".format(self._node, days)
		)
		return result

	def getNodeCPULoadCached(self, old_date):
		"""Get all CPULoad data from last date"""
		
		result = self._solar.query(
				"""
				SELECT
					Year    ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Year,
					Month   ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Month,
					Day     ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Day,
					Hour    ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Hour,
					Minute  ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Minute,
					Second  ( Tolocal ( r.CPULoadHistory.DateTime ) ) as Second,
					WeekDay ( Tolocal ( r.CPULoadHistory.DateTime ) ) as WeekDay,
					r.CPULoadHistory.AvgLoad as Data,
					Tolocal ( r.CPULoadHistory.DateTime ) as CurrentDate
				FROM
					Orion.Nodes r
				WHERE 
					r.Caption='{}' AND
					Tolocal ( r.CPULoadHistory.DateTime ) >= DateTime('{}')
				
				ORDER BY
					r.CPULoadHistory.DateTime
				""".format(self._node, old_date)
		)
		return result	
		
	def getNodeInterfaceUtil(self, interface, days):
		"""Get util percentages of interface"""
		
		result = self._solar.query(
				"""
				SELECT
					Year    ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Year,
					Month   ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Month,
					Day     ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Day,
					Hour    ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Hour,
					Minute  ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Minute,
					Second  ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Second,
					WeekDay ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as WeekDay,
					n.Interfaces.Traffic.PercentUtil as Data,
					Tolocal(n.Interfaces.Traffic.DateTime) as CurrentDate
				FROM
					Orion.Nodes n
				WHERE
					n.Caption='{}' AND
					n.Interfaces.InterfaceCaption='{}' AND
					DayDiff ( Tolocal ( n.Interfaces.Traffic.DateTime ) , GetDate ( ) ) < {}
				ORDER BY
					n.Interfaces.Traffic.DateTime
				""".format(self._node, interface, days)
			)
		return result	
		
	def getNodeInterfaceUtilCached(self, interface, old_date):
		"""Get all Interface data from last date"""
		
		result = self._solar.query(
				"""
				SELECT
					Year    ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Year,
					Month   ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Month,
					Day     ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Day,
					Hour    ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Hour,
					Minute  ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Minute,
					Second  ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as Second,
					WeekDay ( Tolocal ( n.Interfaces.Traffic.DateTime ) ) as WeekDay,
					n.Interfaces.Traffic.PercentUtil as Data,
					Tolocal ( n.Interfaces.Traffic.DateTime ) as CurrentDate
				FROM
					Orion.Nodes r
				WHERE 
					n.Caption='{}' AND
					n.Interfaces.InterfaceCaption='{}' AND
					Tolocal ( n.Interfaces.Traffic.DateTime ) >= DateTime('{}')
				ORDER BY
					n.Interfaces.Traffic.DateTime
				""".format(self._node, interface, old_date)
		)
		return result		
		
	def getIngressBytes(self, days):
		"""Get the ingress byte numbers for last inputted days"""
		
		result = self._solar.query(
				"""
				SELECT TOP 5
					TimeStamp
				FROM
					Orion.Netflow.Flows
				"""
		)
		return result
	
	def getDownNodes(self):
		"""Get all the nodes that are currently down"""
		
		result = self._solar.query(
				"""
				SELECT
					n.Caption
				FROM
					Orion.Nodes n
				WHERE
					n.Status=2
				"""
		)
		return result
		
class SolarGroup():

	"""
		Class Name: SolarGroup
		Class Purpose: To manage Solarwinds Groups
	"""
	
	def __init__(self, loginInstance):
		self._solar = loginInstance
		self.customQuery = self._solar.query
		
	def getAllGroups(self):
		"""Get all the nodes from system"""
		
		groups = self._solar.query(
					"""
					SELECT
						c.Name
					FROM
						Orion.ContainerMemberSnapshots s
					INNER JOIN
						Orion.Container c on c.ContainerID=s.ContainerID
					WHERE
						s.EntityType='Orion.Nodes'
					ORDER BY
						c.Name
					"""
				)
		return groups
		
	def getGroupsByName(self, name):
		"""Search groups by name"""
		
		groups = self._solar.query(
					"""
					SELECT
						c.Name
					FROM
						Orion.ContainerMemberSnapshots s
					INNER JOIN
						Orion.Container c on c.ContainerID=s.ContainerID
					WHERE
						s.EntityType='Orion.Nodes' and
						c.Name LIKE '{}%'
					ORDER BY
						c.Name
					""".format(name)
				)
		return groups
	
	def getGroupAvailability(self, group, days):
		"""Get all the availability numbers from set days"""
		
		result = self._solar.query(   
					"""
					SELECT
						Year    ( Tolocal ( c.ContainerStatus.DateTime ) ) as Year,
						Month   ( Tolocal ( c.ContainerStatus.DateTime ) ) as Month,
						Day     ( Tolocal ( c.ContainerStatus.DateTime ) ) as Day,
						Hour    ( Tolocal ( c.ContainerStatus.DateTime ) ) as Hour,
						Minute  ( Tolocal ( c.ContainerStatus.DateTime ) ) as Minute,
						Second  ( Tolocal ( c.ContainerStatus.DateTime ) ) as Second,
						WeekDay ( Tolocal ( c.ContainerStatus.DateTime ) ) as WeekDay,
						c.ContainerStatus.PercentAvailability as Available
					FROM
						Orion.Container c
					WHERE 
						c.Name='{}' AND
						DayDiff ( Tolocal ( c.ContainerStatus.DateTime ) , GetDate ( ) ) < {}
					ORDER BY
						c.ContainerStatus.DateTime
					""".format(group, days)
				)
		return result
	
	def getDownGroups(self):
		"""Get all the groups that have down status"""
		
		result = self._solar.query(
				"""
				SELECT
					c.Name
				FROM
					Orion.Container c
				WHERE
					c.Status=2
				"""
		)
		return result

solarInstance = Solarwinds("", USERNAME, PASSWORD) # Excluded for security reasons

###
 # Functions to manipulate API in solarwinds
 ## 
def allGroupInfo():
	group = SolarGroup(solarInstance)
	return group.getAllGroups()['results']
	
def allNodeInfo():
	node = SolarNode(solarInstance)
	return node.getAllNodes()['results']

def getDownGroups():
	group = SolarGroup(solarInstance)
	return group.getDownGroups()['results']
	
def getDownNodes():
	node = SolarNode(solarInstance)
	return node.getDownNodes()['results']
	
def groupByName(name):
	group = SolarGroup(solarInstance)
	return group.getGroupsByName(name)['results']

def nodesByGroup(name):
	node = SolarNode(solarInstance)
	return node.getNodesByGroup(name)['results']
	
def nodesByStart(name):
	node = SolarNode(solarInstance)
	return node.getNodesByStart(name)['results']

def nodesByIP(ip):
	node = SolarNode(solarInstance)
	return node.getNodesByIP(ip)['results']	
	
def nodeInterfaces(nodeName):
	node = SolarNode(solarInstance, nodeName)
	return node.getInterfaces()

def getNodeAvailability(nodeName, days):
	"""Get the availability of a node over certain time period"""
	
	node = SolarNode(solarInstance, nodeName)
	return node.getNodeAvailability(days)['results']

def getNodeAvailabilityCached(nodeName, old_date):
	"""Get the availability of a node since last date"""
	
	node = SolarNode(solarInstance, nodeName)
	return node.getNodeAvailabilityCached(old_date)['results']
	
def getNodeCPULoad(nodeName, days):
	"""Get the avg CPU Load of a node over certain time period"""
	
	node = SolarNode(solarInstance, nodeName)
	return node.getNodeCPULoad(days)['results']
	
def getNodeCPULoadCached(nodeName, old_date):
	"""Get the avg CPU Load of a node since last date"""
	
	node = SolarNode(solarInstance, nodeName)
	return node.getNodeCPULoadCached(old_date)['results']

def getNodeIngressBytes(nodeName, days):
	"""Get the ingress bytes for the node over certain time period"""
	
	node = SolarNode(solarInstance, nodeName)
	return node.getIngressBytes(days)['results']

def getNodeInterfaceUtil(nodeName, interfaceName, days):
	"""Get the util percentages of node for specific interface"""
	
	node = SolarNode(solarInstance, nodeName)
	return node.getNodeInterfaceUtil(interfaceName, days)['results']
	
def getNodeInterfaceUtilCached(nodeName, interfaceName, old_date):
	"""Get the util percentages of node for specific interface"""
	
	node = SolarNode(solarInstance, nodeName)
	return node.getNodeInterfaceUtil(interfaceName, old_date)['results']
	
def getGroupAvailability(groupName, days):
	"""Get the availability of a group over certain time period"""
	
	group = SolarGroup(solarInstance)
	return group.getGroupAvailability(groupName, days)['results']

	
###
 #	Helper functions for Solarwinds functionality
 ##
def buildNodeUrl(node_id):
	"""Help build a URL to link to specific node object"""
	
	return "" + str(node_id) # Excluded for security reasons

def buildGroupUrl(group_id):
	"""Help build a URL to link to specific group object"""
	
	return "" + str(group_id) # Excluded for security reasons
 
def resolveEntitiesToUrls(entities, type='node'):
	"""Takes in a list of groups or nodes and uses the type to determine how to resolve url"""
	
	if type == 'node':
		convert_func = buildNodeUrl
		query = """
				SELECT
					n.NodeID as ID
				FROM
					Orion.Nodes n
				WHERE
					n.Caption='{}'
				"""
	elif type == 'group':
		convert_func = buildGroupUrl
		query = """
				SELECT
					c.ContainerID as ID
				FROM
					Orion.Container c
				WHERE
					c.Name='{}'
				"""					
	else:
		raise BadEntityType("The entity type entered must be one of 'node' or group'")
	
	entity_mapping = {}
	for entity in entities:
		results = solarInstance.query(query.format(entity))
		try:
			entity_mapping[entity] = convert_func(results['results'][0]['ID'])
		except IndexError:
			print("Index error occurred")
	return entity_mapping
 
def errorCheck(func):
	"""To take care of simple errors"""
	
	def wrapper(*args, **kwargs):
		try:
			value = func(*args, **kwargs)
		except:
			value = []
		return value
	return wrapper	 

@errorCheck
def getNodeOptions(nodeFunc, *args, **kwargs):
	options = nodeFunc(*args, **kwargs)
	convertedOptions = deleteDuplicateDictionaries(options)
	nodeOptions = [{'label': node['Caption'], 'value': node['Caption']} for node in convertedOptions]
	return nodeOptions

@errorCheck
def getGroupOptions(groupFunc, *args, **kwargs):
	options = groupFunc(*args, **kwargs)
	convertedOptions = deleteDuplicateDictionaries(options)
	groupOptions = [{'label': group['Name'][0:80], 'value': group['Name']} for group in convertedOptions]
	return groupOptions

def deleteDuplicateDictionaries(initList):
	"""Deletes duplicate dictionary entries in list"""
	
	itemsSeen = set()
	newList = []
	for dictionary in initList:
		tupleItem = tuple(dictionary.items())
		if tupleItem not in itemsSeen:
			itemsSeen.add(tupleItem)
			newList.append(dictionary)		
	return newList