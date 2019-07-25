import plotly.graph_objs as graph
#from solarwinds import getAvailabilityData
import itertools
import abc

num_to_str_date = {
	'1' : 'Jan.',
	'2' : 'Feb.',
	'3' : 'Mar.',
	'4' : 'Apr.',
	'5' : 'May.',
	'6' : 'Jun.',
	'7' : 'Jul.',
	'8' : 'Aug.',
	'9' : 'Sep.',
	'10': 'Oct.',
	'11': 'Nov.',
	'12': 'Dec.'
}

num_to_str_weekday = {
	'0' : 'Sun.',
	'1' : 'Mon.',
	'2' : 'Tue.',
	'3' : 'Wed.',
	'4' : 'Thu.',
	'5' : 'Fri.',
	'6' : 'Sat.'
}

class Graph(abc.ABC):

	"""Class to provide basic functionality to children Graphs
	   Should not be instantiated directly"""

	def generateGraph(self):
		
		"""Generate the given graph"""
		dcc.Graph(
			figure=graph.Figure(
				data=self._data
			),
			layout=go.Layout(
				self._layout
			),
			style=self._style,
			id=self._id
		)

	def _getInitialData(self):
		try:
			self._day_init     = self._query_res['results'][0]['Day']
			self._weekDay_init = num_to_str_weekday[str(query_res['results'][0]['WeekDay'])]
			self._month_init   = num_to_str_date[str(query_res['results'][0]['Month'])]
			
			#create the initial lists for creating data
			infoString_init = " ".join (
									[
										self._weekDay_init,
										self._month_init,
										str(self._day_init)
									]
								) 
			self._x_axis  = [infoString_init]
			self._y_axis = [0/720, 24/720, 48/720, 72/720, 96/720, 120/720, 144/720, \
							168/720, 192/720, 216/720, 240/720, 264/720, 288/720 ]
			self._z_axis = []
			self._day_data = []
			self._num_days = 1
			
			self._end_entry = self._query_res [ 'results' ][ -1 ]
		except:
			pass
			
	def getActualDataAndAxes(self, entryTerm, fillValue):
	
		self._getInitialData()
		for it_num, entry in enumerate(self._query_res['results']):
	
			#read the values from the results item
			day        = entry              [           'Day'             ]
			hour       = entry              [           'Hour'            ]
			minute     = entry              [          'Minute'           ]
			weekDay    = num_to_str_weekday [ str ( entry [ 'WeekDay' ] ) ]
			month      = num_to_str_date    [ str ( entry [  'Month'  ] ) ]
			
			#see if the day has changed --> if so:
			# 1. add the new string to the x-axis
			# 2. add the day data to the z-axis data
			# 3. clear out the temporary list for the data for the day
			# 4. change the comparision day
			if day != self._day_init:
				infoString = " ".join (
									[
										weekDay,
										month,
										str ( day )
									]
								)
				self._x_axis.append ( infoString )
				self._z_axis.append (  day_data  )
				self._day_data   = []
				day_init   = day
				num_days   = num_days + 1
			
			#add the entry to the the data for the day
			self._day_data.append(entry[entryTerm])	
			
			#if we are at the last entry, append the last
			#day data to the final entry in the z-axis
			if entry == end_entry:
				self._z_axis.append(self._day_data)
				
			self._convertZAxis(fillValue)
			self._layout = graph.Layout(**self._layout)
				
	def _convertZAxis(self, fillvalue):
		
		"""To convert the z-axis into appropriate data"""
		self._z_axis = list(itertools.zip_longest(*self._z_axis, fillvalue=fillvalue))

	def graph(self):

		"""Graph the object"""
		self.graphCreated = dcc.Graph(
								figure=graph.Figure(data=self._data , layout=self._layout),
								style=self._style,
								id=self._id
							)
	
	def createLabel(self, days):
	
		"""Create the axes labels"""
		pass
	
	@abc.abstractmethod
	def getResults(self):
		"""To be implemented in children classes"""
			
			
def HeatGraph(Graph):
	
	def __init__(self, id, **layout):
		self._id = id
		self._style = {'height': 300}
		self._layout = layout
		self._x_axis = []
		self._y_axis = []
		self._z_axis = []
		self._data = [
			graph.Heatmap(
				x = self._x_axis,
				y = self._y_axis,
				z = self._z_axis
			)
		]
		self.graph()
		
	def getResults(self, entity, name, days):
		
		"""Get the results of the action"""
		self._query_res = getAvailabilityData(entity, name, days)
		self.getActualDataAndAxes('Available', '100.0')
		
def Line_Graph(Graph):
	def __init__(self, id, style={}, **layout):
		self._id = id
		self._style = style
		self._layout = layout
		self._data = None
	
	def getResults(self, name, days):
		pass
	
def Bar_Graph(Graph):
	def __init__(self, id, style={}, **layout):
		self._id = id
		self._style = style
		self._layout = layout
		self._data = None
		
	def getResults(self, name, days):
		pass
	
def Figure():
	pass