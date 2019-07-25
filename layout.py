from board import Dashboard
from dash.dependencies import Input, Output, State, Event
from solarwinds import * 
import dash_core_components as dcc
import dash_html_components as html
from html_css import Table
from graph_tools import getXYZData, getXYZDataFromCached, getHoverInfo
import plotly.graph_objs as graph
from thread import Thread
from threading import Lock
from flask import session
from logger import ACTIVITYLOGGER
from werkzeug.contrib.cache import SimpleCache

# global variables needed to make sure 
# we are quickly adding all interface data
interface_lock = Lock()

def generateInterfaceData(nodeInput, prev_node, interfaceName, days, prev_days, cache):
	"""To generate a graph for the specific interface"""
	
	# get the data if we have input
	# interface_data = cache.get('Interface')
	# print(interface_data)
	# if interface_data is not None:
		# node_saved = list(interface_data.keys())[0]
		# If the node is the same as the one we had, just update the data
		# if interfaceName in interface_data[node_saved] and \
			# prev_days == days and prev_node == nodeInput:
			# print("Cache data should be used")
			# data = []
			# interface_data 
		#if ('node' in session and 'day' in session) and \
			# interfaceName in session['node'] and \
			# (session['node'][interfaceName] == interfaceName and session['day'] == days):
			# data = interface_data[nodeInput] if node_saved is not None else node_saved
		# else:
			# data = generateGraphData(getNodeInterfaceUtil, nodeInput, interfaceName, days)
	# else:
	data = generateGraphData(getNodeInterfaceUtil, nodeInput, interfaceName, days)
	# interface_data[node_saved][interfaceName] = data
	if not data:
		return "Data is not available at this time for Availability graph"
		
	# If we have data append
	layout = buildGraphLayout(title="Utilization Percentage: " + interfaceName)
	layout.update(
		dict(shapes=[
			{
				'type': 'line',
				'x0': dayNum - .5,
				'x1': dayNum - .5,
				'y0': 0,
				'y1': 24,
				'line': {
					'color': 'rgb(0, 0, 0)',
					'width': 2
				}
			} for dayNum in range(days)
		] 
	))

	# convert the data to x, y and z axes --> then generate graph
	x_axis, y_axis, z_axis, max_data, last_data = getXYZData(data)
	hoverInfo = getHoverInfo(x_axis, z_axis, max_data)
	
	heatGraph = None
	if not data:
		heatGraph = html.Label("No data available for interface: " + interfaceName,
						style=dict(width=300, fontSize=40, align='center', textAlign='center', marginLeft=150, marginRight='auto'))
	else:
		heatGraph = dcc.Graph(
			figure=graph.Figure(
				data=[graph.Heatmap(
						x=x_axis,
						y=y_axis,
						z=z_axis,
						zauto=False,
						zmin=0,
						zmax=100,
						colorbar=dict(
							tickmode= 'array',
							tickvals=[0, 20, 40, 60, 80, 100],
							ticktext=[0, 20, 40, 60, 80, 100]
						),
						colorscale=[
							[0, 'rgb(0, 0, 255)'],
							[0.13, 'rgb(0, 130, 150)'],
							[0.25, 'rgb(0, 250, 0)'],
							[0.38, 'rgb(100, 250, 0)'],
							[0.5, 'rgb(100, 200, 0)'],
							[0.63, 'rgb(133, 150, 0)'],
							[0.75, 'rgb(255, 100, 0)'],
							[0.88, 'rgb(255, 36, 0)'],
							[1.0, 'rgb(255, 0, 0)']
						],
						hoverinfo='text',
						text=hoverInfo
				)],
				layout=layout
			),
			style=dict(height=500, width=900, marginBottom=100),
			id=interfaceName
		)
	
	# make sure we are only updating the children one at a time
	interface_lock.acquire()
	children = cache.get('childrenToAdd')
	if children is not None:
		children.append(heatGraph)
	cache.set('childrenToAdd', children)
	interface_lock.release()
	
xaxisdefault = dict(
			mirror=True,
			ticks='outside',
			showline=True,
			showgrid=False,
			tickangle=45,
			title='Date',
			zeroline=False
		)
yaxisdefault = dict(
			mirror=True,
			ticks='outside',
			showline=True,
			showgrid=False,
			title='Hour of Day',
			zeroline=False,
		)

def buildGraphLayout(xaxis=xaxisdefault, yaxis=yaxisdefault, title=""):
	"""Copy general graph layout and then return layout"""
	
	layout = graph.Layout(xaxis=xaxis.copy(), yaxis=yaxis.copy(), title=title)
	return layout	
	
def generateGraphData(func, *args):
	"""Function that generates data compatible for a graph"""
	
	try:
		availData = func(*args)
		data = availData
		return data
	except:
		return None
	
def createDashCallbacks(dash_instance, cache):
	
	####################################################
	#
	# Callback to update the node values for searching
	#
	####################################################
	@dash_instance.callback(
		Output('NodeDropDown', 'options'),
		[Input('GroupDropDown', 'value'),
		 Input('SearchRadio', 'value'),
		 Input('SearchBar', 'value')]
	)
	def updateNodesBasedOnSearch(value3, value1, value2):
		if value3 is not None and value3 != '':
			return getNodeOptions(nodesByGroup, value3)
		elif value1 == 'NName' and value2 != '':
			return getNodeOptions(nodesByStart, value2)
		elif value1 == 'IP' and value2 != '':
			return getNodeOptions(nodesByIP, value2)
		return [{'label': 'No Results', 'value': 'None'}]
	
	###################################################
	#
	# Callback to update the group values for searching
	#
	####################################################
	@dash_instance.callback(
		Output('GroupDropDown', 'options'),
		[Input('SearchRadio', 'value'),
		 Input('SearchBar', 'value')]
	)
	def updateGroupsBasedOnSearch(value1, value2):
		if value1 == 'GName' and value2 != '':
			return getGroupOptions(groupByName, value2)
		else:
			return getGroupOptions(allGroupInfo)
	
	####################################################
	#
	# Callback to update the div for interfaces on button click
	#
	####################################################
	@dash_instance.callback(
		Output('interfaceTable', 'children'),
		[Input('searchButton', 'n_clicks')],
		[State('NodeDropDown', 'value'),
		 State('DayRadio', 'value'),
		 State('dayInput', 'value')]
	)
	def updateInterfaceDiv(n_clicks, nodeInput, daysRadio, daysInput):
		
		# Find the correct number of days to query on
		days = 7
		if not nodeInput and 'node' in session and 'day' in session:
			nodeInput = session['node']
			if session['day'] != daysRadio:
				days = daysRadio
			else:
				days = session['day']
		else:	
			if daysRadio == "Custom": 
				try:
					days = int(daysInput)
				except:
					pass
			else: 
				days = daysRadio
		
		# get the interfaces for the node if there is node input
		if nodeInput:
			interfaces = nodeInterfaces(nodeInput)
		
			# see if there are interfaces available
			if interfaces and interfaces[0]:
				cache.set('childrenToAdd', [])
			
				# iterate through every interface and graph it
				threads_running = []
				for counter, interfaceName in enumerate(interfaces):
					try:
						threads_running.append(Thread(generateInterfaceData, nodeInput, session['node'], interfaceName, days, session['day'], cache))
					except:
						ACTIVITYLOGGER.error("Error starting thread for interface: " + interfaceName)
				
				# make sure threads finish before continuing
				for thread in threads_running:
					thread.joinThread()
					
				# add all interfaces to the table
				interfacesToAdd = []
				rowData = {'elements': []}
				cached_data = cache.get('childrenToAdd')
				for counter, element in enumerate(cached_data):
					if counter % 2 == 0:
						rowData = {'elements': []}
						rowData['elements'].append({'element': element})
					else:
						rowData['elements'].append({'element': element})
						interfacesToAdd.append(rowData)
					
					# if this is last element, add the ending row data to interfaces
					if counter == len(interfaces)-1 and counter % 2 == 0:
						interfacesToAdd.append(rowData)
				
				interfaceTable = Table(id="interfaces",
										children=interfacesToAdd,
										style=dict()).getComponent()		
				return [interfaceTable]
			else:
				return [html.Label(children="No interfaces for node", style=dict(marginLeft=50))]
		else:
			return [html.Label(children="No node has been entered yet for interfaces to be graphed", style=dict(marginLeft=50))]
	
	####################################################
	#
	# Callback to update the availability graph for interfaces on button click
	#
	####################################################		
	@dash_instance.callback(
		Output('Availability Graph', 'children'),
		[Input('searchButton', 'n_clicks')],
		[State('NodeDropDown', 'value'),
		 State('DayRadio', 'value'),
		 State('dayInput', 'value')]
	)
	def generateAvailabilityHeatGraph(n_clicks, nodeInput, daysRadio, daysInput):
	
		# check if we have input from user and there is no saved data --> if not, return
		days = 7
		if not nodeInput and 'node' not in session and 'day' not in session:
			return "No node has been entered yet for CPU graph"
		elif not nodeInput and 'node' in session and 'day' in session:
			nodeInput = session['node']
			if session['day'] != daysRadio:
				days = daysRadio
			else:
				days = session['day']
		else:	
			if daysRadio == "Custom": 
				try:
					days = int(daysInput)
				except:
					pass
			else: 
				days = daysRadio 

		# get the data if we have input
		node_saved = None
		availability_data = cache.get('Availability')
		if availability_data is not None:
			node_saved = list(availability_data.keys())[0]
			last_date = availability_data[node_saved]['last_data'][-1]['CurrentDate'] if 'last_data' in \
									availability_data[node_saved] else {}
			# If the node is the same as the one we had, just update the data
			if ('node' in session and 'day' in session) and (session['node'] == nodeInput and session['day'] == days):
				data = generateGraphData(getNodeAvailabilityCached, nodeInput, last_date)
				x_axis, y_axis, z_axis, max_data, last_data = getXYZDataFromCached(data, availability_data[node_saved]['last_data'])
			else:
				data = generateGraphData(getNodeAvailability, nodeInput, days)
				x_axis, y_axis, z_axis, max_data, last_data = getXYZData(data)
		else:
			data = generateGraphData(getNodeAvailability, nodeInput, days)
			x_axis, y_axis, z_axis, max_data, last_data = getXYZData(data)
			
		if not data:
			return "Data is not available at this time for Availability graph"
		hoverInfo = getHoverInfo(x_axis, z_axis, max_data)
			
		# Set the attributes available in availability to be cached
		cache.set('Availability', {nodeInput: {
									"graph_data": data, 
									"last_data": last_data}})
		
		nodeInput = " - " + nodeInput
		layout = buildGraphLayout(title="Average Availability" + nodeInput)
		layout.update(dict(shapes=[
				{
					'type': 'line',
					'x0': dayNum - .5,
					'x1': dayNum - .5,
					'y0': 0,
					'y1': 24,
					'line': {
						'color': 'rgb(0, 0, 0)',
						'width': 2
					}
				} for dayNum in range(days)
			] 
		))
		
		return [dcc.Graph(
					figure = {
						'data': [graph.Heatmap(
								x=x_axis,
								y=y_axis,
								z=z_axis,
								zauto=False,
								zmin=0,
								zmax=100,
								colorbar=dict(
									tickmode= 'array',
									tickvals=[0, 20, 40, 60, 80, 100],
									ticktext=[0, 20, 40, 60, 80, 100]
								),
								colorscale=[
									[0, 'rgb(255, 0, 0)'],
									[0.13, 'rgb(255, 36, 0)'],
									[0.25, 'rgb(255, 100, 0)'],
									[0.38, 'rgb(133, 150, 0)'],
									[0.5, 'rgb(100, 200, 0)'],
									[0.63, 'rgb(100, 250, 0)'],
									[0.75, 'rgb(0, 250, 0)'],
									[0.88, 'rgb(0, 130, 150)'],
									[1.0, 'rgb(0, 0, 255)']
								],
								hoverinfo='text',
								text=hoverInfo
						)],
						'layout': layout
					},
					id='availGraph'
				)]	
			
	####################################################
	#
	# Callback to update the CPU availability on button click
	#
	####################################################
	@dash_instance.callback(
		Output('CPU Load Graph', 'children'),
		[Input('searchButton', 'n_clicks')],
		[State('NodeDropDown', 'value'),
		 State('DayRadio', 'value'),
		 State('dayInput', 'value')]
	)
	def generateCPUHeatGraph(n_clicks, nodeInput, daysRadio, daysInput):
		
		# find the number of days to track
		days = 7
		if not nodeInput and 'node' not in session and 'day' not in session:
			return "No node has been entered yet for CPU graph"
		elif not nodeInput and 'node' in session and 'day' in session:
			nodeInput = session['node']
			if session['day'] != daysRadio:
				days = daysRadio
			else:
				days = session['day']
		else:	
			if daysRadio == "Custom": 
				try:
					days = int(daysInput)
				except:
					pass
			else: 
				days = daysRadio
	
		# get the data if we have input
		node_saved = None
		cpu_data = cache.get('CPU')
		if cpu_data is not None:
			node_saved = list(cpu_data.keys())[0]
			last_date = cpu_data[node_saved]['last_data'][-1]['CurrentDate'] if 'last_data' in \
									cpu_data[node_saved] else {}
			# If the node is the same as the one we had, just update the data
			if ('node' in session and 'day' in session) and (session['node'] == nodeInput and session['day'] == days):
				data = generateGraphData(getNodeCPULoadCached, nodeInput, last_date)
				x_axis, y_axis, z_axis, max_data, last_data = getXYZDataFromCached(data, cpu_data[node_saved]['last_data'])
			else:
				data = generateGraphData(getNodeCPULoad, nodeInput, days)
				x_axis, y_axis, z_axis, max_data, last_data = getXYZData(data)
		else:
			data = generateGraphData(getNodeCPULoad, nodeInput, days)
			x_axis, y_axis, z_axis, max_data, last_data = getXYZData(data)

		if not data:
			return "Data is not available at this time for CPU load graph"
		hoverInfo = getHoverInfo(x_axis, z_axis, max_data)
		
		# Set the attributes available in availability to be cached
		cache.set('CPU', {nodeInput: {
							"graph_data": data, 
							"last_data": last_data}})
		
		# Set the session variables so we are able to retrieve the data later on 
		session['node'] = nodeInput
		session['day'] = days
		
		nodeInput = " - " + nodeInput
		layout = buildGraphLayout(title="CPU Load" + nodeInput)
		layout.update(dict(shapes=[{
				'type': 'line',
				'x0': dayNum - .5,
				'x1': dayNum - .5,
				'y0': 0,
				'y1': 24,
				'line': {
					'color': 'rgb(0, 0, 0)',
					'width': 2
				}
			} for dayNum in range(days)] 
		))

		return [dcc.Graph(
					figure = {
						'data': [graph.Heatmap(
								x=x_axis,
								y=y_axis,
								z=z_axis,
								zauto=False,
								zmin=0,
								zmax=100,
								colorbar=dict(
									tickmode= 'array',
									tickvals=[0, 20, 40, 60, 80, 100],
									ticktext=[0, 20, 40, 60, 80, 100]
								),
								colorscale=[
									[0, 'rgb(0, 0, 255)'],
									[0.13, 'rgb(0, 130, 150)'],
									[0.25, 'rgb(0, 250, 0)'],
									[0.38, 'rgb(100, 250, 0)'],
									[0.5, 'rgb(100, 200, 0)'],
									[0.63, 'rgb(133, 150, 0)'],
									[0.75, 'rgb(255, 100, 0)'],
									[0.88, 'rgb(255, 36, 0)'],
									[1.0, 'rgb(255, 0, 0)']
								],
								hoverinfo='text',
								text=hoverInfo
						)],
						'layout': layout
					},
					id='cpuGraph'
				)]	
	
def createLogo(dash_instance):

	"""To create the logo on screen"""
	
	amerenImage = html.Img(id='AmerenLogo', 
	                       style=dict(border='3px solid green', borderRadius='5px', height='150', width='400', margin='auto', align='center', verticalAlign='middle', display='block'), 
						   src='/assets/ameren.jpg')
	return amerenImage

def createSearchOption(dash_instance):

	"""To create the option to search"""
	searchLabel = html.Label(id='SearchLabel', 
	                         style=dict(fontWeight='bold', width=50, marginLeft='100', marginRight='20', display='block'), 
							 children='Search By: ')
	radioOptions = [{'label': 'Group Caption', 'value': 'GName'}, {'label': 'Node Caption', 'value': 'NName'}, {'label': 'IP Address', 'value': 'IP'}]
	searchRadio = dcc.RadioItems(id="SearchRadio", 
								 options=radioOptions, 
								 style=dict(width=350, marginRight='25', marginLeft='50', marginTop='30', display='block', textAlign='left'), 
								 labelStyle={'display': 'block'}, value='NName')
	searchBar = dcc.Input(id='SearchBar', 
						  style=dict(width=240, height=30, marginLeft='175', marginBottom='30', marginRight='25'), 
						  value='', type='text', placeholder='Enter search term...')
						  
	return searchLabel, searchRadio, searchBar
	
def createGroupMenu(dash_instance):

	"""To create the group label and dropdown"""
	groupLabel = html.Label(id='GroupLabel', 
							style=dict(fontWeight='bold', width=50, marginLeft='100', marginRight='20', marginBottom='1px', display='block'), 
							children='Groups: ') 
	groupOptions = getGroupOptions(allGroupInfo)
	groupDropDown = dcc.Dropdown(id="GroupDropDown", 
	                             options=groupOptions,
								 style=dict(width=350, marginRight='50', display='block'), 
								 placeholder='Select a group...', clearable=True, value='')

	return groupLabel, groupDropDown
	
def createNodeMenu(dash_instance):

	"""To create the node label and dropdown"""
	nodeLabel = html.Label(id='NodeLabel', 
	                       style=dict(fontWeight='bold', width=50, marginLeft='100', marginRight='20', marginTop='0px', display='block'), 
						   children='Nodes: ')
	nodeOptions = [{'label': 'Select a group first or search for specific node', 'value': 'None'}]
	nodeDropDown = dcc.Dropdown(id="NodeDropDown", 
	                            options=nodeOptions,
								style=dict(width=350, marginRight='20', marginBottom='50', display='block'), 
								placeholder='Select a node...', clearable=True, value='')

	return nodeLabel, nodeDropDown
	
def createDayRadio(dash_instance):

	"""To create the radio to allow choosing days of data"""
	dayLabel = html.Label(id='DayLabel', 
	                       style=dict(fontWeight='bold', marginLeft='100', width=50, display='block'), 
						   children='Days of data: ')
	dayOptions = [{'label': '7 days', 'value': 7}, {'label': '30 days', 'value': 30}, {'label': 'Custom', 'value': 'Custom'}]
	dayRadio = dcc.RadioItems(id="DayRadio", 
							  options=dayOptions, 
							  style=dict(), 
							  value=7)
	custDay = dcc.Input(id='dayInput', type='text', value='', style=dict(width=50, marginRight='150'))

	return dayLabel, dayRadio, custDay
	
def createSearchButton(dash_instance):
	"""To create the button to search for data"""
	
	searchButton = html.Button(id='searchButton', n_clicks=0, children='View', style=dict(marginTop='25', marginLeft=450, width=100, height=50))
	updatingLabel = html.Div(id='updatingArea')
	return searchButton, updatingLabel

def defineDownItemFieldset(dash_instance):
	"""Method to create a fieldset containing all down items"""
	
	down_nodes = getDownNodes()
	down_groups = getDownGroups()
	down_nodes = [node['Caption'] for node in down_nodes]
	down_groups = [group['Name'] for group in down_groups]
	
	node_mappings = resolveEntitiesToUrls(down_nodes, "node")
	group_mappings = resolveEntitiesToUrls(down_groups, "group")
	
	# Create Navigation pane for both nodes and groups
	down_nodes_nav_label = html.Label("Down Nodes", style=dict(margin="25px auto", fontWeight="bold", textDecoration="underline", fontSize=24))
	down_nodes_nav_list = html.Ul(
		children=[html.Li(html.A(key, href=value, target="_blank")) for key, value, in node_mappings.items()])
	down_groups_nav_label = html.Label("Down Groups", style=dict(margin="25px auto", fontWeight="bold", textDecoration="underline", fontSize=24))
	down_groups_nav_list = html.Ul(
		children=[html.Li(html.A(key, href=value, target="_blank", style=dict(wordBreak="break-all"))) for key, value, in group_mappings.items()])
	
	# Create containers for nav menus
	down_nodes_nav = html.Div(
		children=[down_nodes_nav_label, down_nodes_nav_list],
		style=dict(display="inline-block", textAlign="center", float="left", marginRight="50px"))
	down_groups_nav = html.Div(
		children=[down_groups_nav_label, down_groups_nav_list],
		style=dict(display="inline-block", textAlign="center", float="left", width="200px"))
	down_nav = html.Div(
		children=[down_nodes_nav, down_groups_nav],
		style=dict(maxWidth="600px", margin="0 auto"))
	
	# Add the containers to a fieldset
	field_legend = html.Legend(
						"Down Items", 
						style=dict(fontSize=36, fontWeight="bold", position="relative", top="8px"))
	fieldset = html.Fieldset(
					[field_legend, down_nav], 
					title="Down Items",
					style=dict(width="60%", backgroundColor="white", border="1px solid black", marginLeft="auto", marginRight="auto"))
	return fieldset

def defineStatisticsFieldset(dash_instance):
	"""Method to create a fieldset for all statistics data"""
	
	# create search props
	searchLabel, \
	searchRadio, \
	searchBar = createSearchOption(dash_instance)
	
	# create group props
	groupLabel, \
	groupDropDown = createGroupMenu(dash_instance)

	# create node props
	nodeLabel, \
	nodeDropDown = createNodeMenu(dash_instance)

	# create radio for days of data
	dayLabel, \
	dayRadio, \
	custDay = createDayRadio(dash_instance)
	
	# create search button and updating area
	searchButton, updatingLabel = createSearchButton(dash_instance)
	
	# components list and styles
	components = [
					{'elements': [{'element': searchLabel}, {'element': searchRadio, 'colSpan': '2'}]}, 
					{'elements': [{'element': searchBar, 'colSpan': '3'}]},
					{'elements': [{'element': groupLabel}, {'element': groupDropDown, 'colSpan': '2'}]},
					{'elements': [{'element': nodeLabel}, {'element': nodeDropDown, 'colSpan': '2'}]},
					{'elements': [{'element': dayLabel}, {'element': dayRadio}, {'element': custDay}]},
					{'elements': [{'element': searchButton, 'colSpan': '3'}]},
					{'elements': [{'element': updatingLabel, 'colSpan': '3'}]}
				 ]
				
	#create the table and return it
	selection_table = Table(children=components, 
			      id="DashTable",
			      style=dict(align='center', marginLeft='auto', marginRight='auto', marginBottom='30', marginTop='30', paddingBottom='20', textAlign='left', border='1px solid black', width='30%')).getComponent()

	# create space for updated dash
	avlayout = buildGraphLayout(title="Percent Availability")
	availabilityGraph = html.Div(
			children=[],
			style=dict(marginBottom=100, height=500, width=900),
			id='Availability Graph'
		)
	
	cpulayout = buildGraphLayout(title='CPU Load')
	cpuGraph = html.Div(
			children=[],
			style=dict(marginBottom=100, height=500, width=900),
			id='CPU Load Graph'
		)
		
	graphsPlaced = [{'elements': [{'element': cpuGraph}, {'element': availabilityGraph}]}] 
	av_cpu_table = Table(children=graphsPlaced,
						id='DashGraphs',
					    style=dict(textAlign='center')).getComponent()
	
	# create legend for fieldset
	field_legend = html.Legend(
						"Node Statistics", 
						style=dict(fontSize=36, fontWeight="bold", position="relative", top="8px"))

	# Create fieldset for all tables and stats
	fieldset = html.Fieldset(
					[field_legend, 
					 selection_table, 
					 av_cpu_table, 
					 html.Div(id="interfaceTable", style=dict(marginBottom=200))], 
					title="Down Items",
					style=dict(backgroundColor="white", border="1px solid black", marginLeft="30px", marginBottom="30px"))
	
	return fieldset					

def createPageBreak(dash_instance):
	"""Create a page break on page"""
	
	page_break = html.Hr([], style=dict(border="15px solid green"))
	return page_break
	
def createInitialChildren(dash_instance):
	"""Create children for initial dashboard process"""
	
	# create the header for the page
	amerenImage = createLogo(dash_instance)
	header = html.Div([
			amerenImage,
			html.Label(
				"Solarwinds Dashboard",
				style=dict(fontSize=60, fontWeight='bold', fontStyle='italic')
			)
		],
		id='header',
		style={
			'height': '250px',
            'backgroundColor': 'green',
			'textAlign': 'center',
			'verticalAlign': 'middle',
			'align': 'center'
		}
	)
	
	down_item_fieldset = defineDownItemFieldset(dash_instance)
	statistics_fieldset = defineStatisticsFieldset(dash_instance)
	page_break = createPageBreak(dash_instance)
	
	# add the children
	dash_instance.addChildren(
		header,
		down_item_fieldset,
		page_break,
		statistics_fieldset,
		dcc.Location(id='startPage', refresh=False)
	)

def createLayout(dash_instance):	
	"""Create layout for initial dashboard process"""
	
	createInitialChildren(dash_instance)
	dash_instance.createDashboardLayout()
	
def createInitialDashboard(server):
	"""To create the dashboard instance, to initialize
	   layout, and to create dash callbacks"""

	dashboard = Dashboard("Solarwinds", server)
	cache = SimpleCache(threshold=500, default_timeout=1200)
	dashboard.createDashboardLayout()
	dashboard.changeTitle("Solarwinds Dashboard")
	dashboard.createFavicon()
	createLayout(dashboard)
	createDashCallbacks(dashboard, cache)
	return dashboard