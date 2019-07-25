import os
import dash
import exceptions
import dash_html_components as html
import dash_core_components as dcc

class Dashboard(dash.Dash):

	"""
		Class Name: Dashboard
		Class Purpose: To create a dashboard object
	"""
	
	def __init__(self, dash_name, server):
	
		"""
			Method Name: __init__
			Method Purpose: To create a dashboard instance
			
			Parameters:
				- dash_name (string): The name for the dashboard
				- server (Flask): The server to build dashboard on
				
			Returns: None
		"""
		
		super().__init__(dash_name, server=server)
		self._dashboard_name = dash_name
		self.children = []
	
	def __repr__(self):
		
		"""Create String representation of instance"""
		return "Dashboard('{}')".format(self._dashboard_name)

	def createDashboardLayout(self):
	
		"""Create layout for the dashboard based on inputted children"""
		self.layout = self._updateChildren
		
	def _updateChildren(self):
	
		"""Function that will update screen on every reload"""
		return html.Div(id='dashboard', children=self.children, style=dict(borderStyle='solid', backgroundColor='green', borderWidth='10px', borderColor='green'))
	
	def addChildren(self, *children):
		"""Function that can add an arbitrary number of children to layout"""
		
		for child in children:
			try:
				self.children.append(child)
			except:
				pass
			
	def removeChildren(self, *children):
		"""Function that can remove an arbitrary number of children from layout"""
		
		for child in children:
			try:
				self.children.remove(child)
			except:
				pass
	
	def changeTitle(self, newTitle):

		"""Change title of screen"""
		self.title = newTitle
	
	def createFavicon(self, faviconName='favicon.ico', faviconDirectory='static'):
	
		"""To create a favicon image for dashboard"""
		self.interpolate_index(favicon='<link rel="shortcut icon" \
		            href="{{ url_for({}, filename={}) }}">'.format(faviconDirectory, faviconName))

	def runDashboard(self, host='0.0.0.0', port=8050, processes=6, *args, **kwargs):
	
		"""Start hosting the dashboard"""
		self.run_server(host=host, port=port, *args, **kwargs)
	
		
	
	
		