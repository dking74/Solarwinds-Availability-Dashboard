import dash_html_components as HTML
import dash_core_components as dcc

#######################################################################
#
#       NOTE: Classes in this module are not designed to be used
#             directly. They are used by other classes in order
#             to be more useful. DO NOT instantiate directly.
#
#######################################################################

class Table():
	
	"""Class implementing table component
		Kwargs must include components list,
		which is a list of dictionaries containing
		elements and styles for each row"""
	def __init__(self, children, id, style={}, **kwargs):
		table_comp = []
		for row in range(len(children)):
			table_row = []
			rowStyle = {}
			for child in children[row]['elements']:
				rowStyle = self._defineRow(table_row, row, child, children[row])
			table_comp.append(HTML.Tr(table_row, style=rowStyle))
		self._component = HTML.Table(children=table_comp, id=id, style=style, **kwargs)
	
	def getComponent(self):
		return self._component

	def _defineRow(self, rowList, row, child, children):	

		"""Define the properties of that specific data element"""
		try:
			colData = child['colSpan']
		except:
			colData = None
		try:
			rowData = child['rowSpan']
		except:
			rowData = None
		
		try:
			rowList.append(HTML.Td(children=child['element'], 
								   colSpan=colData,
								   rowSpan=rowData))
		except:
			pass
							   
		try:
			style = children['style']
		except:
			style = {}
		return style
		
	def updateTable(self, newComponents):
		pass